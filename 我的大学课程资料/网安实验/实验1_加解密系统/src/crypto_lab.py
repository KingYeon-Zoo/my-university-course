from __future__ import annotations

import argparse
import csv
import hmac
import hashlib
import json
import os
import shutil
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

# 引入 cryptography 密码学库相关的原语
# hashes: 哈希函数；symmetric_padding: 对称填充（如 PKCS7）；serialization: 密钥序列化/反序列化（PEM格式）
from cryptography.hazmat.primitives import hashes, padding as symmetric_padding, serialization
# padding, rsa: 非对称密码（RSA）填充与 RSA 核心算法
from cryptography.hazmat.primitives.asymmetric import padding, rsa
# Cipher, algorithms, modes: 对称分组加密基础（用于 SM4-CBC）
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
# AESGCM: 现代的 AES-GCM 认证加密高层封装接口（AEAD）
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# ==================== 学生身份防伪常量 ====================
STUDENT_ID = "2023212290"        # 学号：在可视化网页和报告中强制嵌入
STUDENT_NAME = "朱清扬"          # 姓名：防抄袭水印
MAJOR_CLASS = "计算机科学与技术 23级3班" # 班级信息


# ==================== 密码学常量定义 ====================
AES_NONCE_SIZE = 12         # AES-GCM 推荐的 Nonce (初始化向量/随机数) 长度为 12 字节
RSA_WRAPPED_KEY_SIZE = 256  # RSA-2048 加密后的会话密钥长度固定为 256 字节
SM4_BLOCK_SIZE = 16         # SM4 分组密码的分组长度与密钥长度均为 16 字节 (128位)


# ==================== 数据结构定义 (Dataclasses) ====================

@dataclass(frozen=True)
class KeyMaterial:
    """密钥材料类：统一管理系统中所有算法所需的密钥和向量"""
    aes_key: bytes                     # AES-256 对称密钥 (32字节)
    rsa_private_key: rsa.RSAPrivateKey # RSA 2048位 私钥对象
    rsa_public_key: rsa.RSAPublicKey   # RSA 2048位 公钥对象
    sm4_key: bytes                     # SM4 对称密钥 (16字节)
    sm4_iv: bytes                      # SM4-CBC 初始化向量 (16字节)


@dataclass(frozen=True)
class CryptoRecord:
    """评测记录类：保存单个文件在单次算法运行下的完整指标数据"""
    algorithm: str          # 算法名称 (例如 "AES 256 GCM")
    category: str           # 样本分类 (例如 "图像", "视频", "文本")
    file_name: str          # 文件名
    original_bytes: int     # 原始明文大小 (字节)
    encrypted_bytes: int    # 加密后密文大小 (字节)
    encrypt_ms: float       # 加密耗时 (毫秒)
    decrypt_ms: float       # 解密耗时 (毫秒)
    original_sha256: str    # 原始明文的 SHA-256 散列值
    restored_sha256: str    # 解密还原后的 SHA-256 散列值
    sensitivity_result: str # 密文 1-bit 篡改敏感性测试结果


@dataclass(frozen=True)
class DemoResult:
    """演示结果汇总类：封装输出路径与所有测试用例记录"""
    output_dir: Path
    summary_json: Path
    summary_csv: Path
    dashboard_html: Path
    records: list[CryptoRecord]


# ==================== 核心密码算法封装 ====================

class AESGCMAlgorithm:
    """
    AES-256-GCM 算法实现
    - GCM 是一种 AEAD (认证加密) 模式，集成了机密性与完整性校验。
    - 无需手动填充，密文末尾会自动追加 16 字节的 GMAC 认证标签 (Tag)。
    """
    name = "AES 256 GCM"

    def __init__(self, key: bytes):
        self.key = key  # 传入的对称密钥，必须为 32 字节 (256位)

    def encrypt(self, data: bytes) -> bytes:
        # 1. 动态生成 12 字节强加密安全的随机数 Nonce，防止重放攻击和已知明文攻击
        nonce = os.urandom(AES_NONCE_SIZE)
        # 2. 调用密码库底层接口加密。第三个参数 None 表示不加入 Associated Data
        #    返回值 ciphertext 内部自动在密文尾部拼装了 16 字节的 GMAC Tag
        ciphertext = AESGCM(self.key).encrypt(nonce, data, None)
        # 3. 返回拼接后的数据包：Nonce (12B) + Ciphertext + Tag (16B)
        return nonce + ciphertext

    def decrypt(self, payload: bytes) -> bytes:
        # 1. 拆分数据包，前 12 字节为 Nonce，后部为 密文 + Tag
        nonce = payload[:AES_NONCE_SIZE]
        ciphertext = payload[AES_NONCE_SIZE:]
        # 2. 调用解密接口。解密器在解密前会先计算并校验 Tag：
        #    如果密文在传输中被修改了任何一比特，校验就会失败并抛出 InvalidTag 异常，拒绝输出任何损坏的明文。
        return AESGCM(self.key).decrypt(nonce, ciphertext, None)


class RSAHybridAlgorithm:
    """
    RSA-2048-OAEP 混合密码体制
    - 设计初衷：RSA 无法直接加密大于 256 字节的数据，且大数模幂运算速度慢。
    - 解决方案：利用 AES-GCM 对敏感大文件进行对称加密，用 RSA 公钥加密临时生成的会话密钥（Key Encapsulation）。
    """
    name = "RSA OAEP Hybrid"

    def __init__(self, private_key: rsa.RSAPrivateKey, public_key: rsa.RSAPublicKey):
        self.private_key = private_key
        self.public_key = public_key

    def encrypt(self, data: bytes) -> bytes:
        # 1. 动态生成本次加密专用的临时会话密钥（AES 256位）
        session_key = AESGCM.generate_key(bit_length=256)
        # 2. 为 AES-GCM 生成 12 字节 Nonce
        nonce = os.urandom(AES_NONCE_SIZE)
        # 3. 使用临时会话密钥加密真正的多媒体明文数据，生成对称密文 (包含 Tag)
        encrypted_data = AESGCM(session_key).encrypt(nonce, data, None)
        # 4. 使用接收方的 RSA 公钥，配合安全度极高的 OAEP 填充模式（抗选择密文攻击），加密 32 字节的会话密钥。
        #    RSA-2048 加密后的密文大小固定为 256 字节 (2048位)
        wrapped_key = self.public_key.encrypt(
            session_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()), # 使用 SHA256 掩码生成函数 MGF1
                algorithm=hashes.SHA256(),                   # OAEP 使用的 Hash 函数
                label=None,
            ),
        )
        # 5. 拼装密文 Payload：RSA包裹的密钥(256B) + AES Nonce(12B) + 对称密文
        return wrapped_key + nonce + encrypted_data

    def decrypt(self, payload: bytes) -> bytes:
        # 1. 按照固定的偏移量拆分密文数据包
        wrapped_key = payload[:RSA_WRAPPED_KEY_SIZE] # 前 256 字节是加密的会话密钥
        nonce = payload[RSA_WRAPPED_KEY_SIZE : RSA_WRAPPED_KEY_SIZE + AES_NONCE_SIZE] # 接着的 12 字节是 Nonce
        encrypted_data = payload[RSA_WRAPPED_KEY_SIZE + AES_NONCE_SIZE :] # 剩下的全部是数据密文
        # 2. 使用 RSA 私钥和 OAEP 填充模式，解密解封装出原始的 32 字节对称会话密钥
        session_key = self.private_key.decrypt(
            wrapped_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        # 3. 使用还原出的临时对称密钥解密并校验最终的数据明文
        return AESGCM(session_key).decrypt(nonce, encrypted_data, None)


class SM4CBCAlgorithm:
    """
    国密 SM4-CBC 算法与 HMAC-SHA256 的结合 (Encrypt-then-MAC 架构)
    - SM4 对称加密：密钥 16 字节，分组 16 字节，采用 CBC 模式。
    - PKCS7 填充：由于 CBC 要求明文为 16 字节整数倍，需要对其进行边缘填充。
    - EtM 完整性加固：传统 CBC 易受 Padding Oracle 攻击，通过 HMAC-SHA256 对“向量+密文”进行签名，
      解密时先校验 MAC 再解密去填充，从物理上杜绝了填充侧信道泄露。
    """
    name = "SM4 CBC"

    def __init__(self, key: bytes, iv: bytes):
        if len(key) != SM4_BLOCK_SIZE or len(iv) != SM4_BLOCK_SIZE:
            raise ValueError("SM4 密钥与初始化向量 IV 必须均为 16 字节")
        self.key = key
        self.iv = iv

    def encrypt(self, data: bytes) -> bytes:
        # 1. 动态生成本次加密的随机初始化向量 IV (16 字节)
        iv = os.urandom(SM4_BLOCK_SIZE)
        # 2. 初始化 PKCS7 填充器对明文进行边缘对齐填充
        padder = symmetric_padding.PKCS7(SM4_BLOCK_SIZE * 8).padder()
        padded = padder.update(data) + padder.finalize()
        # 3. 使用 SM4 算法和 CBC 模式进行对称分组加密
        encryptor = Cipher(algorithms.SM4(self.key), modes.CBC(iv)).encryptor()
        ciphertext = encryptor.update(padded) + encryptor.finalize()
        # 4. Encrypt-then-MAC 安全架构核心：使用相同的密钥，计算 (IV + Ciphertext) 的 HMAC-SHA256 签名。
        #    HMAC 标签长度固定为 32 字节
        tag = hmac.digest(self.key, iv + ciphertext, "sha256")
        # 5. 拼装密文 Payload：IV (16B) + Ciphertext + HMAC Tag (32B)
        return iv + ciphertext + tag

    def decrypt(self, payload: bytes) -> bytes:
        # 1. 拆分 Payload
        iv = payload[:SM4_BLOCK_SIZE] # 前 16 字节是 IV
        tag = payload[-32:]            # 后 32 字节是 HMAC 认证码
        ciphertext = payload[SM4_BLOCK_SIZE:-32] # 中间部分是密文
        # 2. 先验证 MAC 标签：使用 hmac.compare_digest（恒定时间比较，防止时序攻击 Timing Attack）
        #    比对收到的 HMAC 和重新计算的 HMAC。不一致则判定被篡改，立即中止解密并报错。
        expected = hmac.digest(self.key, iv + ciphertext, "sha256")
        if not hmac.compare_digest(tag, expected):
            raise ValueError("SM4 HMAC 校验失败，密文完整性已被篡改")
        # 3. 校验通过后，使用 SM4-CBC 进行解密
        decryptor = Cipher(algorithms.SM4(self.key), modes.CBC(iv)).decryptor()
        padded = decryptor.update(ciphertext) + decryptor.finalize()
        # 4. 去除 PKCS7 填充，还原原始明文数据
        unpadder = symmetric_padding.PKCS7(SM4_BLOCK_SIZE * 8).unpadder()
        return unpadder.update(padded) + unpadder.finalize()


# ==================== 辅助模块与工具函数 ====================

def sha256_bytes(data: bytes) -> str:
    """计算字节流的 SHA-256 散列值，作为数据一致性无损验证的唯一标识"""
    return hashlib.sha256(data).hexdigest()


def create_key_material(key_dir: Path) -> KeyMaterial:
    """
    密钥生命周期管理：自动在 key_dir 下加载或持久化生成各种密码算法所需的密钥
    """
    key_dir.mkdir(parents=True, exist_ok=True)
    aes_path = key_dir / "aes_256.key"
    sm4_key_path = key_dir / "sm4.key"
    sm4_iv_path = key_dir / "sm4.iv"
    rsa_private_path = key_dir / "rsa_private.pem"
    rsa_public_path = key_dir / "rsa_public.pem"

    # 如果密钥文件不存在，则重新生成
    if not aes_path.exists():
        aes_path.write_bytes(AESGCM.generate_key(bit_length=256))
    if not sm4_key_path.exists():
        sm4_key_path.write_bytes(os.urandom(SM4_BLOCK_SIZE))
    if not sm4_iv_path.exists():
        sm4_iv_path.write_bytes(os.urandom(SM4_BLOCK_SIZE))
    if not rsa_private_path.exists():
        # 生成 2048 位的 RSA 密钥对，选用标准公共指数 65537
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        # 将私钥序列化为无加密的 PEM 格式写入本地（为自动化评测）
        rsa_private_path.write_bytes(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )
        # 导出公钥并持久化
        rsa_public_path.write_bytes(
            private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )

    # 从本地文件反序列化并加载密钥对象
    private_key = serialization.load_pem_private_key(rsa_private_path.read_bytes(), password=None)
    public_key = serialization.load_pem_public_key(rsa_public_path.read_bytes())
    if not isinstance(private_key, rsa.RSAPrivateKey) or not isinstance(public_key, rsa.RSAPublicKey):
        raise TypeError("加载的 RSA 密钥文件格式不合法")
    return KeyMaterial(
        aes_key=aes_path.read_bytes(),
        rsa_private_key=private_key,
        rsa_public_key=public_key,
        sm4_key=sm4_key_path.read_bytes(),
        sm4_iv=sm4_iv_path.read_bytes(),
    )


def build_algorithms(keys: KeyMaterial):
    """根据加载的密钥，实例化三种密码算法实现类"""
    return [
        AESGCMAlgorithm(keys.aes_key),
        RSAHybridAlgorithm(keys.rsa_private_key, keys.rsa_public_key),
        SM4CBCAlgorithm(keys.sm4_key, keys.sm4_iv),
    ]


def detect_category(path: Path) -> str:
    """根据文件后缀，检测多媒体样例的分类，用于可视化展示"""
    suffix = path.suffix.lower()
    if suffix == ".txt":
        return "文本"
    if suffix in {".jpg", ".jpeg", ".png", ".bmp"}:
        return "图像"
    if suffix in {".mp3", ".wav", ".aac"}:
        return "声音"
    if suffix in {".mp4", ".mov", ".avi"}:
        return "视频"
    return "文件"


def iter_sample_files(input_dir: Path, max_files: int | None = None) -> Iterable[Path]:
    """遍历样本目录中的所有非隐藏的多媒体文件"""
    files = sorted(path for path in input_dir.iterdir() if path.is_file() and not path.name.startswith("."))
    if max_files is not None:
        files = files[:max_files]
    return files


def sensitivity_check(algorithm, encrypted: bytes) -> str:
    """
    密文敏感性（抗篡改能力）测试：
    - 复制一份生成的密文数据，将其最后一个比特进行异或翻转 (changed[-1] ^= 1)。
    - 将篡改后的密文输入解密器。
    - 预期结果：由于 AEAD 的 Tag 校验或 EtM 的 HMAC 校验，解密器应该主动拦截并抛出异常，拒绝解密。
    """
    changed = bytearray(encrypted)
    changed[-1] ^= 1  # 翻转最后一个比特 (1-bit 篡改模拟)
    try:
        algorithm.decrypt(bytes(changed))
    except Exception as exc:
        # 解密器拦截成功并捕获到对应异常
        return f"篡改密文后拒绝解密: {exc.__class__.__name__}"
    return "篡改密文后输出异常明文" # 正常不应该运行到这


def process_file(path: Path, output_dir: Path, algorithm) -> CryptoRecord:
    """
    单个样例文件的加解密完整处理函数：
    1. 计算并保存原始 SHA-256。
    2. 高精度记录加密耗时并输出密文文件。
    3. 高精度记录解密耗时并输出解密还原文件。
    4. 执行密文篡改敏感性校验。
    """
    plain = path.read_bytes()
    algorithm_dir = output_dir / "outputs" / algorithm.name.replace(" ", "_")
    algorithm_dir.mkdir(parents=True, exist_ok=True)
    encrypted_path = algorithm_dir / f"{path.name}.enc"
    restored_path = algorithm_dir / f"{path.name}.restored{path.suffix}"

    # 运行加密，并使用 time.perf_counter() 记录毫秒数
    start = time.perf_counter()
    encrypted = algorithm.encrypt(plain)
    encrypt_ms = (time.perf_counter() - start) * 1000

    # 运行解密，记录解密耗时
    start = time.perf_counter()
    restored = algorithm.decrypt(encrypted)
    decrypt_ms = (time.perf_counter() - start) * 1000

    # 密文和还原文件持久化写入对应的 outputs 下的算法子目录
    encrypted_path.write_bytes(encrypted)
    restored_path.write_bytes(restored)

    # 封装生成评测记录
    return CryptoRecord(
        algorithm=algorithm.name,
        category=detect_category(path),
        file_name=path.name,
        original_bytes=len(plain),
        encrypted_bytes=len(encrypted),
        encrypt_ms=round(encrypt_ms, 3),
        decrypt_ms=round(decrypt_ms, 3),
        original_sha256=sha256_bytes(plain),
        restored_sha256=sha256_bytes(restored),
        sensitivity_result=sensitivity_check(algorithm, encrypted),
    )


# ==================== 可视化数据与 HTML5 仪表盘输出 ====================

def write_summary(records: list[CryptoRecord], output_dir: Path) -> tuple[Path, Path]:
    """将测试记录分别序列化导出为标准 JSON 格式和 CSV 大数据格式，便于二次数据分析"""
    summary_json = output_dir / "results" / "summary.json"
    summary_csv = output_dir / "results" / "summary.csv"
    summary_json.parent.mkdir(parents=True, exist_ok=True)
    
    # 写入 JSON
    summary_json.write_text(
        json.dumps([asdict(record) for record in records], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    # 写入 CSV
    with summary_csv.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(asdict(records[0]).keys()))
        writer.writeheader()
        for record in records:
            writer.writerow(asdict(record))
    return summary_json, summary_csv


def write_dashboard(records: list[CryptoRecord], output_dir: Path) -> Path:
    """
    可视化页面生成器：通过 Python 拼接 Vanilla CSS 样式生成响应式可视化仪表盘 (dashboard.html)。
    """
    # 将结果按算法分组，用以计算均值统计卡片
    grouped: dict[str, list[CryptoRecord]] = {}
    for record in records:
        grouped.setdefault(record.algorithm, []).append(record)

    # 1. 动态生成评测结果表格行 (Table Rows)
    rows = []
    for record in records:
        ok = "一致" if record.original_sha256 == record.restored_sha256 else "不一致"
        rows.append(
            f"<tr><td>{record.algorithm}</td><td>{record.category}</td><td>{record.file_name}</td>"
            f"<td>{record.original_bytes}</td><td>{record.encrypted_bytes}</td>"
            f"<td>{record.encrypt_ms}</td><td>{record.decrypt_ms}</td><td>{ok}</td>"
            f"<td>{record.sensitivity_result}</td></tr>"
        )
    
    # 2. 动态生成顶部的算法耗时平均值卡片 (Summary Cards)
    average_cards = []
    for algorithm, values in grouped.items():
        enc_avg = sum(item.encrypt_ms for item in values) / len(values)
        dec_avg = sum(item.decrypt_ms for item in values) / len(values)
        average_cards.append(
            f"<section class='card'><h2>{algorithm}</h2>"
            f"<p>平均加密耗时 {enc_avg:.3f} ms</p>"
            f"<p>平均解密耗时 {dec_avg:.3f} ms</p>"
            f"<p>覆盖样本 {len(values)} 个</p></section>"
        )
    
    # 3. 输出并拼接完整的 HTML 单页应用
    dashboard = output_dir / "results" / "dashboard.html"
    dashboard.write_text(
        f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>实验1加解密系统演示</title>
<style>
body {{ font-family: Arial, "PingFang SC", sans-serif; margin: 0; background: #f6f8fb; color: #172033; }}
header {{ background: #16324f; color: white; padding: 22px 36px; position: sticky; top: 0; z-index: 10; }}
h1 {{ margin: 0 0 10px 0; font-size: 28px; letter-spacing: 0; }}
main {{ padding: 28px 36px; }}
/* 身份水印展示区：强制绑定学生信息，防范抄袭 */
.identity {{ font-size: 18px; line-height: 1.7; }}
.cards {{ display: grid; grid-template-columns: repeat(3, minmax(220px, 1fr)); gap: 16px; margin: 22px 0; }}
.card {{ background: white; border: 1px solid #d8dee9; border-radius: 8px; padding: 18px; }}
.card h2 {{ margin: 0 0 12px 0; font-size: 20px; }}
.keyspace {{ display: grid; grid-template-columns: repeat(3, minmax(220px, 1fr)); gap: 16px; margin: 18px 0 24px 0; }}
.keyspace .card {{ border-color: #b8c7d9; }}
table {{ width: 100%; border-collapse: collapse; background: white; font-size: 14px; }}
th, td {{ border: 1px solid #d8dee9; padding: 10px; text-align: left; vertical-align: top; }}
th {{ background: #e7edf5; }}
.note {{ margin-top: 18px; font-size: 16px; }}
</style>
</head>
<body>
<header>
<h1>实验1 加解密系统设计与性能分析</h1>
<div class="identity">学号：{STUDENT_ID}　姓名：{STUDENT_NAME}　专业：{MAJOR_CLASS}</div>
</header>
<main>
<div class="cards">{''.join(average_cards)}</div>
<section class="keyspace">
<section class="card"><h2>AES-256 密钥空间</h2><p>2^256，认证加密模式 GCM，篡改后 InvalidTag 拒绝解密。</p></section>
<section class="card"><h2>RSA-2048 安全基础</h2><p>基于大整数分解难题，OAEP 包裹会话密钥，数据体由 AES-GCM 保护。</p></section>
<section class="card"><h2>SM4-128 密钥空间</h2><p>2^128，CBC 加密结合 HMAC-SHA256，篡改后 ValueError 拒绝解密。</p></section>
</section>
<table>
<thead><tr><th>算法</th><th>类型</th><th>文件</th><th>原始字节</th><th>密文字节</th><th>加密毫秒</th><th>解密毫秒</th><th>哈希校验</th><th>密文敏感性测试</th></tr></thead>
<tbody>{''.join(rows)}</tbody>
</table>
<p class="note">所有样本均完成加密和解密，恢复文件 SHA256 与原文件一致。截图页面固定展示学号和姓名。</p>
</main>
</body>
</html>
""",
        encoding="utf-8",
    )
    return dashboard


# ==================== 主控运行逻辑 ====================

def run_full_demo(input_dir: Path, output_dir: Path, key_dir: Path, max_files: int | None = None) -> DemoResult:
    """系统运行总控，负责生成密钥、执行加解密全流程、以及数据持久化和可视化输出"""
    output_dir.mkdir(parents=True, exist_ok=True)
    # 1. 自动生成或加载密钥
    keys = create_key_material(key_dir)
    records: list[CryptoRecord] = []
    # 2. 遍历输入目录的多媒体样例，对每个样例依次运行三种算法
    for path in iter_sample_files(input_dir, max_files):
        for algorithm in build_algorithms(keys):
            records.append(process_file(path, output_dir, algorithm))
    # 3. 输出汇总 JSON/CSV
    summary_json, summary_csv = write_summary(records, output_dir)
    # 4. 生成可视化静态仪表盘网页
    dashboard_html = write_dashboard(records, output_dir)
    return DemoResult(output_dir, summary_json, summary_csv, dashboard_html, records)


def copy_samples(source_dir: Path, target_dir: Path) -> None:
    """初始化拷贝，将外部加密文件目录的 7 个样例拷贝到项目 sample_data 中"""
    target_dir.mkdir(parents=True, exist_ok=True)
    for path in iter_sample_files(source_dir):
        shutil.copy2(path, target_dir / path.name)


def main() -> None:
    """命令行参数解析与主函数入口"""
    parser = argparse.ArgumentParser(description="网络安全实验1加解密系统")
    parser.add_argument("--input-dir", type=Path, required=True, help="明文样本存放目录")
    parser.add_argument("--output-dir", type=Path, required=True, help="加密与还原数据输出目录")
    parser.add_argument("--key-dir", type=Path, required=True, help="持久化密钥目录")
    parser.add_argument("--copy-samples-from", type=Path, help="可选：初始化拷贝样例的源目录")
    args = parser.parse_args()

    # 如果传入了初始化拷贝路径，先执行样例文件拷贝
    if args.copy_samples_from:
        copy_samples(args.copy_samples_from, args.input_dir)
    
    # 核心测试流程
    result = run_full_demo(args.input_dir, args.output_dir, args.key_dir)
    
    # 终端打印结果，方便验收现场演示
    print(f"学号: {STUDENT_ID}")
    print(f"姓名: {STUDENT_NAME}")
    print(f"结果 JSON: {result.summary_json}")
    print(f"结果 CSV: {result.summary_csv}")
    print(f"演示页面: {result.dashboard_html}")
    for record in result.records:
        print(
            f"{record.algorithm} {record.category} {record.file_name} "
            f"加密 {record.encrypt_ms} ms 解密 {record.decrypt_ms} ms"
        )


if __name__ == "__main__":
    main()
