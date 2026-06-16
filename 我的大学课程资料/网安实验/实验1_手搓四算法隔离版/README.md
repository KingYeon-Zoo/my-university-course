# 实验1：纯手写四算法加解密系统

本目录是隔离版新实现，不依赖原来的 `实验1_加解密系统/src/crypto_lab.py`，也不调用 `cryptography`、`Crypto`、`gmssl` 等第三方密码库。代码只使用 Python 标准库完成文件读写、随机数、哈希、HMAC、CSV/JSON/HTML 输出。

## 已实现算法

| 算法 | 实现方式 | 用途 |
| --- | --- | --- |
| AES-256-CBC | 手写 S 盒生成、密钥扩展、SubBytes、ShiftRows、MixColumns、轮密钥加、CBC、PKCS7 | 对称分组加密 |
| RSA-1024-OAEP-Hybrid | 手写 Miller-Rabin 素数检测、RSA 密钥生成、模幂、OAEP、MGF1；数据体用手写 AES-256 加密 | 混合加密大文件 |
| SM4-CBC | 手写国密 SM4 S 盒、轮函数、轮密钥、CBC、PKCS7 | 国密分组加密 |
| ZUC-128 | 手写 LFSR、比特重组、非线性函数 F、S0/S1、密钥流生成 | 国密流加密 |

说明：HMAC-SHA256 只用于密文完整性校验，避免 CBC/流加密被静默篡改；它不是用来替代四个加密算法的。

## 目录结构

```text
实验1_手搓四算法隔离版/
  src/handmade_crypto_lab.py      # 主程序和四算法实现
  tests/test_handmade_crypto.py   # 标准向量和功能测试
  sample_data/                    # 明文样本，可放文本、文件、图片、音频、视频
  verify_run/                     # 已验证过的快速运行输出
  README.md
  requirements.txt
```

## 环境隔离

建议在本目录单独建虚拟环境，避免使用全局 Python 包：

```bash
cd /Users/zoo/Desktop/网安/实验1_手搓四算法隔离版
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

`requirements.txt` 为空依赖声明，因为本实验不需要第三方库。若使用现有 conda 隔离环境，也可以直接运行：

```bash
cd /Users/zoo/Desktop/网安/实验1_手搓四算法隔离版
../.conda_envs/netsec_py/bin/python -m pytest tests -q
```

## 运行测试

```bash
cd /Users/zoo/Desktop/网安/实验1_手搓四算法隔离版
../.conda_envs/netsec_py/bin/python -m pytest tests -q
```

测试覆盖：

- AES-128 和 AES-256 标准分组测试向量。
- SM4 标准分组测试向量。
- ZUC 零密钥零 IV 前两个密钥流字测试向量。
- AES/RSA/SM4/ZUC 四算法加密后可解密还原。
- 篡改密文后必须拒绝解密。
- 批量样本运行会生成 JSON、CSV、HTML。

## 快速运行

使用已有样本目录时，建议先处理前几个小文件：

```bash
cd /Users/zoo/Desktop/网安/实验1_手搓四算法隔离版
../.conda_envs/netsec_py/bin/python src/handmade_crypto_lab.py \
  --input-dir sample_data \
  --output-dir quick_run \
  --key-dir quick_run/keys \
  --max-files 2
```

输出文件：

- `quick_run/keys/`：隔离生成的 AES/RSA/SM4/ZUC 密钥。
- `quick_run/outputs/`：各算法密文和还原文件。
- `quick_run/results/summary.json`：结构化结果。
- `quick_run/results/summary.csv`：表格结果。
- `quick_run/results/dashboard.html`：可截图的演示页面，页面内嵌学号、姓名和性能数据。

## 完整运行

如果要对 `sample_data` 中全部文本、文件、图片、音频、视频样本运行：

```bash
cd /Users/zoo/Desktop/网安/实验1_手搓四算法隔离版
../.conda_envs/netsec_py/bin/python src/handmade_crypto_lab.py \
  --input-dir sample_data \
  --output-dir full_run \
  --key-dir full_run/keys
```

注意：这是纯 Python 手写实现，没有 OpenSSL、AES-NI 或国密库加速。大图片和视频会明显慢于调库版，这是正常现象，也可以作为报告中“手写实现与库实现性能差异”的分析点。

## 从旧实验复制样本

```bash
cd /Users/zoo/Desktop/网安/实验1_手搓四算法隔离版
../.conda_envs/netsec_py/bin/python src/handmade_crypto_lab.py \
  --copy-samples-from ../实验1_加解密系统/sample_data \
  --input-dir sample_data \
  --output-dir quick_run \
  --key-dir quick_run/keys \
  --max-files 2
```

## 关键验收点

- 老师检查“不能调库”时，看 `src/handmade_crypto_lab.py` 顶部 imports，没有第三方密码库。
- 老师检查“四算法全实现”时，看 `AESAlgorithm`、`RSAHybridAlgorithm`、`SM4Algorithm`、`ZUCAlgorithm` 四个类。
- 老师检查正确性时，运行 `pytest`，再打开 `results/dashboard.html` 看 SHA256 是否一致。
- 老师检查密文敏感性时，看 `sensitivity_result`，篡改 1 bit 后四个算法都拒绝解密。
