from __future__ import annotations

import argparse
import csv
import hashlib
import hmac
import json
import secrets
import shutil
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


STUDENT_ID = "2023212290"
STUDENT_NAME = "朱清扬"
MAJOR_CLASS = "计算机科学与技术 23级3班"

BLOCK_SIZE = 16
TAG_SIZE = 32
MASK32 = 0xFFFFFFFF
MOD31 = 0x7FFFFFFF


@dataclass(frozen=True)
class KeyMaterial:
    aes_key: bytes
    rsa_public_key: tuple[int, int]
    rsa_private_key: tuple[int, int]
    sm4_key: bytes
    zuc_key: bytes


@dataclass(frozen=True)
class CryptoRecord:
    algorithm: str
    category: str
    file_name: str
    original_bytes: int
    encrypted_bytes: int
    encrypt_ms: float
    decrypt_ms: float
    original_sha256: str
    restored_sha256: str
    sensitivity_result: str


@dataclass(frozen=True)
class DemoResult:
    output_dir: Path
    summary_json: Path
    summary_csv: Path
    dashboard_html: Path
    records: list[CryptoRecord]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pkcs7_pad(data: bytes, block_size: int = BLOCK_SIZE) -> bytes:
    pad_len = block_size - len(data) % block_size
    return data + bytes([pad_len]) * pad_len


def pkcs7_unpad(data: bytes, block_size: int = BLOCK_SIZE) -> bytes:
    if not data or len(data) % block_size != 0:
        raise ValueError("PKCS7 填充长度非法")
    pad_len = data[-1]
    if pad_len < 1 or pad_len > block_size:
        raise ValueError("PKCS7 填充值非法")
    if data[-pad_len:] != bytes([pad_len]) * pad_len:
        raise ValueError("PKCS7 填充内容非法")
    return data[:-pad_len]


def xor_bytes(left: bytes, right: bytes) -> bytes:
    return bytes(a ^ b for a, b in zip(left, right))


def auth_tag(key: bytes, data: bytes) -> bytes:
    return hmac.new(key, data, hashlib.sha256).digest()


def verify_tag(key: bytes, data: bytes, tag: bytes) -> None:
    expected = auth_tag(key, data)
    if not hmac.compare_digest(expected, tag):
        raise ValueError("完整性校验失败，密文可能被篡改")


# ==================== AES-128 手写实现 ====================


def gf_mul(a: int, b: int) -> int:
    result = 0
    for _ in range(8):
        if b & 1:
            result ^= a
        carry = a & 0x80
        a = (a << 1) & 0xFF
        if carry:
            a ^= 0x1B
        b >>= 1
    return result


def gf_pow(a: int, power: int) -> int:
    result = 1
    while power:
        if power & 1:
            result = gf_mul(result, a)
        a = gf_mul(a, a)
        power >>= 1
    return result


def rotl8(value: int, shift: int) -> int:
    return ((value << shift) | (value >> (8 - shift))) & 0xFF


def aes_sbox_byte(value: int) -> int:
    inv = 0 if value == 0 else gf_pow(value, 254)
    return (inv ^ rotl8(inv, 1) ^ rotl8(inv, 2) ^ rotl8(inv, 3) ^ rotl8(inv, 4) ^ 0x63) & 0xFF


AES_SBOX = [aes_sbox_byte(i) for i in range(256)]
AES_INV_SBOX = [0] * 256
for _i, _value in enumerate(AES_SBOX):
    AES_INV_SBOX[_value] = _i
AES_MUL2 = [gf_mul(i, 2) for i in range(256)]
AES_MUL3 = [gf_mul(i, 3) for i in range(256)]
AES_MUL9 = [gf_mul(i, 9) for i in range(256)]
AES_MUL11 = [gf_mul(i, 11) for i in range(256)]
AES_MUL13 = [gf_mul(i, 13) for i in range(256)]
AES_MUL14 = [gf_mul(i, 14) for i in range(256)]


def aes_key_expansion(key: bytes) -> list[list[int]]:
    if len(key) not in {16, 24, 32}:
        raise ValueError("AES 密钥长度必须为 16/24/32 字节")
    nk = len(key) // 4
    nr = nk + 6
    words = [list(key[i : i + 4]) for i in range(0, 16, 4)]
    if nk > 4:
        words.extend([list(key[i : i + 4]) for i in range(16, len(key), 4)])
    rcon = 1
    for i in range(nk, 4 * (nr + 1)):
        temp = words[i - 1][:]
        if i % nk == 0:
            temp = temp[1:] + temp[:1]
            temp = [AES_SBOX[item] for item in temp]
            temp[0] ^= rcon
            rcon = gf_mul(rcon, 2)
        elif nk > 6 and i % nk == 4:
            temp = [AES_SBOX[item] for item in temp]
        words.append([a ^ b for a, b in zip(words[i - nk], temp)])
    return [sum(words[i : i + 4], []) for i in range(0, 4 * (nr + 1), 4)]


def aes_add_round_key(state: list[int], round_key: list[int]) -> None:
    for i in range(16):
        state[i] ^= round_key[i]


def aes_shift_rows(state: list[int]) -> None:
    old = state[:]
    for row in range(4):
        for col in range(4):
            state[4 * col + row] = old[4 * ((col + row) % 4) + row]


def aes_inv_shift_rows(state: list[int]) -> None:
    old = state[:]
    for row in range(4):
        for col in range(4):
            state[4 * col + row] = old[4 * ((col - row) % 4) + row]


def aes_mix_columns(state: list[int]) -> None:
    for col in range(4):
        i = 4 * col
        a0, a1, a2, a3 = state[i : i + 4]
        state[i + 0] = AES_MUL2[a0] ^ AES_MUL3[a1] ^ a2 ^ a3
        state[i + 1] = a0 ^ AES_MUL2[a1] ^ AES_MUL3[a2] ^ a3
        state[i + 2] = a0 ^ a1 ^ AES_MUL2[a2] ^ AES_MUL3[a3]
        state[i + 3] = AES_MUL3[a0] ^ a1 ^ a2 ^ AES_MUL2[a3]


def aes_inv_mix_columns(state: list[int]) -> None:
    for col in range(4):
        i = 4 * col
        a0, a1, a2, a3 = state[i : i + 4]
        state[i + 0] = AES_MUL14[a0] ^ AES_MUL11[a1] ^ AES_MUL13[a2] ^ AES_MUL9[a3]
        state[i + 1] = AES_MUL9[a0] ^ AES_MUL14[a1] ^ AES_MUL11[a2] ^ AES_MUL13[a3]
        state[i + 2] = AES_MUL13[a0] ^ AES_MUL9[a1] ^ AES_MUL14[a2] ^ AES_MUL11[a3]
        state[i + 3] = AES_MUL11[a0] ^ AES_MUL13[a1] ^ AES_MUL9[a2] ^ AES_MUL14[a3]


def aes_encrypt_block_with_round_keys(block: bytes, round_keys: list[list[int]]) -> bytes:
    if len(block) != BLOCK_SIZE:
        raise ValueError("AES 分组长度必须为 16 字节")
    state = list(block)
    aes_add_round_key(state, round_keys[0])
    for round_index in range(1, len(round_keys) - 1):
        state = [AES_SBOX[item] for item in state]
        aes_shift_rows(state)
        aes_mix_columns(state)
        aes_add_round_key(state, round_keys[round_index])
    state = [AES_SBOX[item] for item in state]
    aes_shift_rows(state)
    aes_add_round_key(state, round_keys[-1])
    return bytes(state)


def aes_decrypt_block_with_round_keys(block: bytes, round_keys: list[list[int]]) -> bytes:
    if len(block) != BLOCK_SIZE:
        raise ValueError("AES 分组长度必须为 16 字节")
    state = list(block)
    aes_add_round_key(state, round_keys[-1])
    for round_index in range(len(round_keys) - 2, 0, -1):
        aes_inv_shift_rows(state)
        state = [AES_INV_SBOX[item] for item in state]
        aes_add_round_key(state, round_keys[round_index])
        aes_inv_mix_columns(state)
    aes_inv_shift_rows(state)
    state = [AES_INV_SBOX[item] for item in state]
    aes_add_round_key(state, round_keys[0])
    return bytes(state)


def aes_encrypt_block(block: bytes, key: bytes) -> bytes:
    return aes_encrypt_block_with_round_keys(block, aes_key_expansion(key))


def aes_decrypt_block(block: bytes, key: bytes) -> bytes:
    return aes_decrypt_block_with_round_keys(block, aes_key_expansion(key))


def cbc_encrypt(data: bytes, key: bytes, block_encrypt) -> tuple[bytes, bytes]:
    iv = secrets.token_bytes(BLOCK_SIZE)
    previous = iv
    output = bytearray()
    padded = pkcs7_pad(data)
    for offset in range(0, len(padded), BLOCK_SIZE):
        block = padded[offset : offset + BLOCK_SIZE]
        encrypted = block_encrypt(xor_bytes(block, previous), key)
        output.extend(encrypted)
        previous = encrypted
    return iv, bytes(output)


def cbc_decrypt(iv: bytes, ciphertext: bytes, key: bytes, block_decrypt) -> bytes:
    if len(iv) != BLOCK_SIZE or len(ciphertext) % BLOCK_SIZE != 0:
        raise ValueError("CBC 数据长度非法")
    previous = iv
    output = bytearray()
    for offset in range(0, len(ciphertext), BLOCK_SIZE):
        block = ciphertext[offset : offset + BLOCK_SIZE]
        output.extend(xor_bytes(block_decrypt(block, key), previous))
        previous = block
    return pkcs7_unpad(bytes(output))


class AESAlgorithm:
    name = "AES-256-CBC"
    magic = b"AES1"

    def __init__(self, key: bytes):
        if len(key) != 32:
            raise ValueError("实验默认 AES-256，密钥必须为 32 字节")
        self.key = key
        self.round_keys = aes_key_expansion(key)

    def encrypt(self, data: bytes) -> bytes:
        iv, ciphertext = cbc_encrypt(data, self.key, lambda block, _key: aes_encrypt_block_with_round_keys(block, self.round_keys))
        body = self.magic + iv + ciphertext
        return body + auth_tag(self.key, body)

    def decrypt(self, payload: bytes) -> bytes:
        if not payload.startswith(self.magic):
            raise ValueError("AES 密文头不匹配")
        body, tag = payload[:-TAG_SIZE], payload[-TAG_SIZE:]
        verify_tag(self.key, body, tag)
        iv = body[4:20]
        ciphertext = body[20:]
        return cbc_decrypt(iv, ciphertext, self.key, lambda block, _key: aes_decrypt_block_with_round_keys(block, self.round_keys))


# ==================== RSA-1024 + OAEP 手写实现 ====================


def egcd(a: int, b: int) -> tuple[int, int, int]:
    if b == 0:
        return a, 1, 0
    g, x1, y1 = egcd(b, a % b)
    return g, y1, x1 - (a // b) * y1


def mod_inverse(a: int, m: int) -> int:
    g, x, _ = egcd(a, m)
    if g != 1:
        raise ValueError("模逆不存在")
    return x % m


def is_probable_prime(n: int, rounds: int = 12) -> bool:
    if n < 2:
        return False
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    if n in small_primes:
        return True
    if any(n % p == 0 for p in small_primes):
        return False
    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2
    for _ in range(rounds):
        a = secrets.randbelow(n - 3) + 2
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def generate_prime(bits: int) -> int:
    while True:
        candidate = secrets.randbits(bits) | (1 << (bits - 1)) | 1
        if is_probable_prime(candidate):
            return candidate


def generate_rsa_keypair(bits: int = 1024) -> tuple[tuple[int, int], tuple[int, int]]:
    e = 65537
    while True:
        p = generate_prime(bits // 2)
        q = generate_prime(bits // 2)
        if p == q:
            continue
        n = p * q
        phi = (p - 1) * (q - 1)
        if phi % e != 0:
            d = mod_inverse(e, phi)
            return (n, e), (n, d)


def i2osp(value: int, length: int) -> bytes:
    if value >= 256**length:
        raise ValueError("整数过大，无法编码")
    return value.to_bytes(length, "big")


def os2ip(data: bytes) -> int:
    return int.from_bytes(data, "big")


def mgf1(seed: bytes, length: int) -> bytes:
    counter = 0
    output = bytearray()
    while len(output) < length:
        output.extend(hashlib.sha256(seed + counter.to_bytes(4, "big")).digest())
        counter += 1
    return bytes(output[:length])


def oaep_encode(message: bytes, encoded_len: int, label: bytes = b"") -> bytes:
    hlen = hashlib.sha256().digest_size
    if len(message) > encoded_len - 2 * hlen - 2:
        raise ValueError("OAEP 明文过长")
    lhash = hashlib.sha256(label).digest()
    ps = b"\x00" * (encoded_len - len(message) - 2 * hlen - 2)
    db = lhash + ps + b"\x01" + message
    seed = secrets.token_bytes(hlen)
    masked_db = xor_bytes(db, mgf1(seed, encoded_len - hlen - 1))
    masked_seed = xor_bytes(seed, mgf1(masked_db, hlen))
    return b"\x00" + masked_seed + masked_db


def oaep_decode(encoded: bytes, label: bytes = b"") -> bytes:
    hlen = hashlib.sha256().digest_size
    if len(encoded) < 2 * hlen + 2 or encoded[0] != 0:
        raise ValueError("OAEP 编码非法")
    masked_seed = encoded[1 : 1 + hlen]
    masked_db = encoded[1 + hlen :]
    seed = xor_bytes(masked_seed, mgf1(masked_db, hlen))
    db = xor_bytes(masked_db, mgf1(seed, len(masked_db)))
    lhash = hashlib.sha256(label).digest()
    if db[:hlen] != lhash:
        raise ValueError("OAEP 标签哈希校验失败")
    rest = db[hlen:]
    index = rest.find(b"\x01")
    if index < 0 or any(rest[:index]):
        raise ValueError("OAEP 分隔符非法")
    return rest[index + 1 :]


def rsa_oaep_encrypt(message: bytes, public_key: tuple[int, int]) -> bytes:
    n, e = public_key
    k = (n.bit_length() + 7) // 8
    encoded = oaep_encode(message, k)
    cipher_int = pow(os2ip(encoded), e, n)
    return i2osp(cipher_int, k)


def rsa_oaep_decrypt(ciphertext: bytes, private_key: tuple[int, int]) -> bytes:
    n, d = private_key
    k = (n.bit_length() + 7) // 8
    if len(ciphertext) != k:
        raise ValueError("RSA 密文长度非法")
    encoded_int = pow(os2ip(ciphertext), d, n)
    return oaep_decode(i2osp(encoded_int, k))


class RSAHybridAlgorithm:
    name = "RSA-1024-OAEP-Hybrid"
    magic = b"RSA1"

    def __init__(self, public_key: tuple[int, int], private_key: tuple[int, int]):
        self.public_key = public_key
        self.private_key = private_key
        self.key_bytes = (public_key[0].bit_length() + 7) // 8

    def encrypt(self, data: bytes) -> bytes:
        session_key = secrets.token_bytes(32)
        wrapped_key = rsa_oaep_encrypt(session_key, self.public_key)
        inner = AESAlgorithm(session_key).encrypt(data)
        return self.magic + wrapped_key + inner

    def decrypt(self, payload: bytes) -> bytes:
        if not payload.startswith(self.magic):
            raise ValueError("RSA 密文头不匹配")
        wrapped_key = payload[4 : 4 + self.key_bytes]
        inner = payload[4 + self.key_bytes :]
        session_key = rsa_oaep_decrypt(wrapped_key, self.private_key)
        return AESAlgorithm(session_key).decrypt(inner)


# ==================== SM4-CBC 手写实现 ====================


SM4_SBOX = [
    0xD6, 0x90, 0xE9, 0xFE, 0xCC, 0xE1, 0x3D, 0xB7, 0x16, 0xB6, 0x14, 0xC2, 0x28, 0xFB, 0x2C, 0x05,
    0x2B, 0x67, 0x9A, 0x76, 0x2A, 0xBE, 0x04, 0xC3, 0xAA, 0x44, 0x13, 0x26, 0x49, 0x86, 0x06, 0x99,
    0x9C, 0x42, 0x50, 0xF4, 0x91, 0xEF, 0x98, 0x7A, 0x33, 0x54, 0x0B, 0x43, 0xED, 0xCF, 0xAC, 0x62,
    0xE4, 0xB3, 0x1C, 0xA9, 0xC9, 0x08, 0xE8, 0x95, 0x80, 0xDF, 0x94, 0xFA, 0x75, 0x8F, 0x3F, 0xA6,
    0x47, 0x07, 0xA7, 0xFC, 0xF3, 0x73, 0x17, 0xBA, 0x83, 0x59, 0x3C, 0x19, 0xE6, 0x85, 0x4F, 0xA8,
    0x68, 0x6B, 0x81, 0xB2, 0x71, 0x64, 0xDA, 0x8B, 0xF8, 0xEB, 0x0F, 0x4B, 0x70, 0x56, 0x9D, 0x35,
    0x1E, 0x24, 0x0E, 0x5E, 0x63, 0x58, 0xD1, 0xA2, 0x25, 0x22, 0x7C, 0x3B, 0x01, 0x21, 0x78, 0x87,
    0xD4, 0x00, 0x46, 0x57, 0x9F, 0xD3, 0x27, 0x52, 0x4C, 0x36, 0x02, 0xE7, 0xA0, 0xC4, 0xC8, 0x9E,
    0xEA, 0xBF, 0x8A, 0xD2, 0x40, 0xC7, 0x38, 0xB5, 0xA3, 0xF7, 0xF2, 0xCE, 0xF9, 0x61, 0x15, 0xA1,
    0xE0, 0xAE, 0x5D, 0xA4, 0x9B, 0x34, 0x1A, 0x55, 0xAD, 0x93, 0x32, 0x30, 0xF5, 0x8C, 0xB1, 0xE3,
    0x1D, 0xF6, 0xE2, 0x2E, 0x82, 0x66, 0xCA, 0x60, 0xC0, 0x29, 0x23, 0xAB, 0x0D, 0x53, 0x4E, 0x6F,
    0xD5, 0xDB, 0x37, 0x45, 0xDE, 0xFD, 0x8E, 0x2F, 0x03, 0xFF, 0x6A, 0x72, 0x6D, 0x6C, 0x5B, 0x51,
    0x8D, 0x1B, 0xAF, 0x92, 0xBB, 0xDD, 0xBC, 0x7F, 0x11, 0xD9, 0x5C, 0x41, 0x1F, 0x10, 0x5A, 0xD8,
    0x0A, 0xC1, 0x31, 0x88, 0xA5, 0xCD, 0x7B, 0xBD, 0x2D, 0x74, 0xD0, 0x12, 0xB8, 0xE5, 0xB4, 0xB0,
    0x89, 0x69, 0x97, 0x4A, 0x0C, 0x96, 0x77, 0x7E, 0x65, 0xB9, 0xF1, 0x09, 0xC5, 0x6E, 0xC6, 0x84,
    0x18, 0xF0, 0x7D, 0xEC, 0x3A, 0xDC, 0x4D, 0x20, 0x79, 0xEE, 0x5F, 0x3E, 0xD7, 0xCB, 0x39, 0x48,
]
SM4_FK = [0xA3B1BAC6, 0x56AA3350, 0x677D9197, 0xB27022DC]
SM4_CK = [
    0x00070E15, 0x1C232A31, 0x383F464D, 0x545B6269, 0x70777E85, 0x8C939AA1, 0xA8AFB6BD, 0xC4CBD2D9,
    0xE0E7EEF5, 0xFC030A11, 0x181F262D, 0x343B4249, 0x50575E65, 0x6C737A81, 0x888F969D, 0xA4ABB2B9,
    0xC0C7CED5, 0xDCE3EAF1, 0xF8FF060D, 0x141B2229, 0x30373E45, 0x4C535A61, 0x686F767D, 0x848B9299,
    0xA0A7AEB5, 0xBCC3CAD1, 0xD8DFE6ED, 0xF4FB0209, 0x10171E25, 0x2C333A41, 0x484F565D, 0x646B7279,
]


def rotl32(value: int, shift: int) -> int:
    return ((value << shift) | (value >> (32 - shift))) & MASK32


def sm4_tau(value: int) -> int:
    return (
        (SM4_SBOX[(value >> 24) & 0xFF] << 24)
        | (SM4_SBOX[(value >> 16) & 0xFF] << 16)
        | (SM4_SBOX[(value >> 8) & 0xFF] << 8)
        | SM4_SBOX[value & 0xFF]
    )


def sm4_l(value: int) -> int:
    return value ^ rotl32(value, 2) ^ rotl32(value, 10) ^ rotl32(value, 18) ^ rotl32(value, 24)


def sm4_l_key(value: int) -> int:
    return value ^ rotl32(value, 13) ^ rotl32(value, 23)


def sm4_round_keys(key: bytes) -> list[int]:
    if len(key) != 16:
        raise ValueError("SM4 密钥必须为 16 字节")
    mk = [int.from_bytes(key[i : i + 4], "big") for i in range(0, 16, 4)]
    k = [mk[i] ^ SM4_FK[i] for i in range(4)]
    round_keys = []
    for i in range(32):
        rk = k[i] ^ sm4_l_key(sm4_tau(k[i + 1] ^ k[i + 2] ^ k[i + 3] ^ SM4_CK[i]))
        rk &= MASK32
        round_keys.append(rk)
        k.append(rk)
    return round_keys


def sm4_crypt_block_with_round_keys(block: bytes, round_keys: list[int]) -> bytes:
    if len(block) != 16:
        raise ValueError("SM4 分组长度必须为 16 字节")
    x = [int.from_bytes(block[i : i + 4], "big") for i in range(0, 16, 4)]
    for i in range(32):
        value = x[i] ^ sm4_l(sm4_tau(x[i + 1] ^ x[i + 2] ^ x[i + 3] ^ round_keys[i]))
        x.append(value & MASK32)
    return b"".join(item.to_bytes(4, "big") for item in [x[35], x[34], x[33], x[32]])


def sm4_crypt_block(block: bytes, key: bytes, decrypt: bool = False) -> bytes:
    round_keys = sm4_round_keys(key)
    if decrypt:
        round_keys = list(reversed(round_keys))
    return sm4_crypt_block_with_round_keys(block, round_keys)


def sm4_encrypt_block(block: bytes, key: bytes) -> bytes:
    return sm4_crypt_block(block, key, decrypt=False)


def sm4_decrypt_block(block: bytes, key: bytes) -> bytes:
    return sm4_crypt_block(block, key, decrypt=True)


class SM4Algorithm:
    name = "SM4-CBC"
    magic = b"SM41"

    def __init__(self, key: bytes):
        if len(key) != 16:
            raise ValueError("SM4 密钥必须为 16 字节")
        self.key = key
        self.round_keys = sm4_round_keys(key)
        self.decrypt_round_keys = list(reversed(self.round_keys))

    def encrypt(self, data: bytes) -> bytes:
        iv, ciphertext = cbc_encrypt(data, self.key, lambda block, _key: sm4_crypt_block_with_round_keys(block, self.round_keys))
        body = self.magic + iv + ciphertext
        return body + auth_tag(self.key, body)

    def decrypt(self, payload: bytes) -> bytes:
        if not payload.startswith(self.magic):
            raise ValueError("SM4 密文头不匹配")
        body, tag = payload[:-TAG_SIZE], payload[-TAG_SIZE:]
        verify_tag(self.key, body, tag)
        return cbc_decrypt(
            body[4:20],
            body[20:],
            self.key,
            lambda block, _key: sm4_crypt_block_with_round_keys(block, self.decrypt_round_keys),
        )


# ==================== ZUC-128 手写实现 ====================


ZUC_S0 = [
    0x3E, 0x72, 0x5B, 0x47, 0xCA, 0xE0, 0x00, 0x33, 0x04, 0xD1, 0x54, 0x98, 0x09, 0xB9, 0x6D, 0xCB,
    0x7B, 0x1B, 0xF9, 0x32, 0xAF, 0x9D, 0x6A, 0xA5, 0xB8, 0x2D, 0xFC, 0x1D, 0x08, 0x53, 0x03, 0x90,
    0x4D, 0x4E, 0x84, 0x99, 0xE4, 0xCE, 0xD9, 0x91, 0xDD, 0xB6, 0x85, 0x48, 0x8B, 0x29, 0x6E, 0xAC,
    0xCD, 0xC1, 0xF8, 0x1E, 0x73, 0x43, 0x69, 0xC6, 0xB5, 0xBD, 0xFD, 0x39, 0x63, 0x20, 0xD4, 0x38,
    0x76, 0x7D, 0xB2, 0xA7, 0xCF, 0xED, 0x57, 0xC5, 0xF3, 0x2C, 0xBB, 0x14, 0x21, 0x06, 0x55, 0x9B,
    0xE3, 0xEF, 0x5E, 0x31, 0x4F, 0x7F, 0x5A, 0xA4, 0x0D, 0x82, 0x51, 0x49, 0x5F, 0xBA, 0x58, 0x1C,
    0x4A, 0x16, 0xD5, 0x17, 0xA8, 0x92, 0x24, 0x1F, 0x8C, 0xFF, 0xD8, 0xAE, 0x2E, 0x01, 0xD3, 0xAD,
    0x3B, 0x4B, 0xDA, 0x46, 0xEB, 0xC9, 0xDE, 0x9A, 0x8F, 0x87, 0xD7, 0x3A, 0x80, 0x6F, 0x2F, 0xC8,
    0xB1, 0xB4, 0x37, 0xF7, 0x0A, 0x22, 0x13, 0x28, 0x7C, 0xCC, 0x3C, 0x89, 0xC7, 0xC3, 0x96, 0x56,
    0x07, 0xBF, 0x7E, 0xF0, 0x0B, 0x2B, 0x97, 0x52, 0x35, 0x41, 0x79, 0x61, 0xA6, 0x4C, 0x10, 0xFE,
    0xBC, 0x26, 0x95, 0x88, 0x8A, 0xB0, 0xA3, 0xFB, 0xC0, 0x18, 0x94, 0xF2, 0xE1, 0xE5, 0xE9, 0x5D,
    0xD0, 0xDC, 0x11, 0x66, 0x64, 0x5C, 0xEC, 0x59, 0x42, 0x75, 0x12, 0xF5, 0x74, 0x9C, 0xAA, 0x23,
    0x0E, 0x86, 0xAB, 0xBE, 0x2A, 0x02, 0xE7, 0x67, 0xE6, 0x44, 0xA2, 0x6C, 0xC2, 0x93, 0x9F, 0xF1,
    0xF6, 0xFA, 0x36, 0xD2, 0x50, 0x68, 0x9E, 0x62, 0x71, 0x15, 0x3D, 0xD6, 0x40, 0xC4, 0xE2, 0x0F,
    0x8E, 0x83, 0x77, 0x6B, 0x25, 0x05, 0x3F, 0x0C, 0x30, 0xEA, 0x70, 0xB7, 0xA1, 0xE8, 0xA9, 0x65,
    0x8D, 0x27, 0x1A, 0xDB, 0x81, 0xB3, 0xA0, 0xF4, 0x45, 0x7A, 0x19, 0xDF, 0xEE, 0x78, 0x34, 0x60,
]
ZUC_S1 = [
    0x55, 0xC2, 0x63, 0x71, 0x3B, 0xC8, 0x47, 0x86, 0x9F, 0x3C, 0xDA, 0x5B, 0x29, 0xAA, 0xFD, 0x77,
    0x8C, 0xC5, 0x94, 0x0C, 0xA6, 0x1A, 0x13, 0x00, 0xE3, 0xA8, 0x16, 0x72, 0x40, 0xF9, 0xF8, 0x42,
    0x44, 0x26, 0x68, 0x96, 0x81, 0xD9, 0x45, 0x3E, 0x10, 0x76, 0xC6, 0xA7, 0x8B, 0x39, 0x43, 0xE1,
    0x3A, 0xB5, 0x56, 0x2A, 0xC0, 0x6D, 0xB3, 0x05, 0x22, 0x66, 0xBF, 0xDC, 0x0B, 0xFA, 0x62, 0x48,
    0xDD, 0x20, 0x11, 0x06, 0x36, 0xC9, 0xC1, 0xCF, 0xF6, 0x27, 0x52, 0xBB, 0x69, 0xF5, 0xD4, 0x87,
    0x7F, 0x84, 0x4C, 0xD2, 0x9C, 0x57, 0xA4, 0xBC, 0x4F, 0x9A, 0xDF, 0xFE, 0xD6, 0x8D, 0x7A, 0xEB,
    0x2B, 0x53, 0xD8, 0x5C, 0xA1, 0x14, 0x17, 0xFB, 0x23, 0xD5, 0x7D, 0x30, 0x67, 0x73, 0x08, 0x09,
    0xEE, 0xB7, 0x70, 0x3F, 0x61, 0xB2, 0x19, 0x8E, 0x4E, 0xE5, 0x4B, 0x93, 0x8F, 0x5D, 0xDB, 0xA9,
    0xAD, 0xF1, 0xAE, 0x2E, 0xCB, 0x0D, 0xFC, 0xF4, 0x2D, 0x46, 0x6E, 0x1D, 0x97, 0xE8, 0xD1, 0xE9,
    0x4D, 0x37, 0xA5, 0x75, 0x5E, 0x83, 0x9E, 0xAB, 0x82, 0x9D, 0xB9, 0x1C, 0xE0, 0xCD, 0x49, 0x89,
    0x01, 0xB6, 0xBD, 0x58, 0x24, 0xA2, 0x5F, 0x38, 0x78, 0x99, 0x15, 0x90, 0x50, 0xB8, 0x95, 0xE4,
    0xD0, 0x91, 0xC7, 0xCE, 0xED, 0x0F, 0xB4, 0x6F, 0xA0, 0xCC, 0xF0, 0x02, 0x4A, 0x79, 0xC3, 0xDE,
    0xA3, 0xEF, 0xEA, 0x51, 0xE6, 0x6B, 0x18, 0xEC, 0x1B, 0x2C, 0x80, 0xF7, 0x74, 0xE7, 0xFF, 0x21,
    0x5A, 0x6A, 0x54, 0x1E, 0x41, 0x31, 0x92, 0x35, 0xC4, 0x33, 0x07, 0x0A, 0xBA, 0x7E, 0x0E, 0x34,
    0x88, 0xB1, 0x98, 0x7C, 0xF3, 0x3D, 0x60, 0x6C, 0x7B, 0xCA, 0xD3, 0x1F, 0x32, 0x65, 0x04, 0x28,
    0x64, 0xBE, 0x85, 0x9B, 0x2F, 0x59, 0x8A, 0xD7, 0xB0, 0x25, 0xAC, 0xAF, 0x12, 0x03, 0xE2, 0xF2,
]
ZUC_D = [
    0x44D7, 0x26BC, 0x626B, 0x135E, 0x5789, 0x35E2, 0x7135, 0x09AF,
    0x4D78, 0x2F13, 0x6BC4, 0x1AF1, 0x5E26, 0x3C4D, 0x789A, 0x47AC,
]


def add_mod31(a: int, b: int) -> int:
    value = a + b
    value = (value & MOD31) + (value >> 31)
    return value if value != 0 else MOD31


def mul_pow2_mod31(value: int, shift: int) -> int:
    return ((value << shift) | (value >> (31 - shift))) & MOD31


def zuc_l1(value: int) -> int:
    return value ^ rotl32(value, 2) ^ rotl32(value, 10) ^ rotl32(value, 18) ^ rotl32(value, 24)


def zuc_l2(value: int) -> int:
    return value ^ rotl32(value, 8) ^ rotl32(value, 14) ^ rotl32(value, 22) ^ rotl32(value, 30)


def zuc_s(value: int) -> int:
    return (
        (ZUC_S0[(value >> 24) & 0xFF] << 24)
        | (ZUC_S1[(value >> 16) & 0xFF] << 16)
        | (ZUC_S0[(value >> 8) & 0xFF] << 8)
        | ZUC_S1[value & 0xFF]
    )


class ZUCState:
    def __init__(self, key: bytes, iv: bytes):
        if len(key) != 16 or len(iv) != 16:
            raise ValueError("ZUC 密钥和 IV 必须均为 16 字节")
        self.s = [(key[i] << 23) | (ZUC_D[i] << 8) | iv[i] for i in range(16)]
        self.r1 = 0
        self.r2 = 0
        for _ in range(32):
            x0, x1, x2, _ = self.bit_reconstruction()
            w = self.f(x0, x1, x2)
            self.lfsr_init(w >> 1)
        x0, x1, x2, _ = self.bit_reconstruction()
        self.f(x0, x1, x2)
        self.lfsr_work()

    def bit_reconstruction(self) -> tuple[int, int, int, int]:
        x0 = ((self.s[15] & 0x7FFF8000) << 1) | (self.s[14] & 0xFFFF)
        x1 = ((self.s[11] & 0xFFFF) << 16) | (self.s[9] >> 15)
        x2 = ((self.s[7] & 0xFFFF) << 16) | (self.s[5] >> 15)
        x3 = ((self.s[2] & 0xFFFF) << 16) | (self.s[0] >> 15)
        return x0 & MASK32, x1 & MASK32, x2 & MASK32, x3 & MASK32

    def f(self, x0: int, x1: int, x2: int) -> int:
        w = ((x0 ^ self.r1) + self.r2) & MASK32
        w1 = (self.r1 + x1) & MASK32
        w2 = (self.r2 ^ x2) & MASK32
        u = zuc_l1(((w1 << 16) & MASK32) | (w2 >> 16))
        v = zuc_l2(((w2 << 16) & MASK32) | (w1 >> 16))
        self.r1 = zuc_s(u)
        self.r2 = zuc_s(v)
        return w

    def lfsr_next(self, u: int | None) -> None:
        f = self.s[0]
        f = add_mod31(f, mul_pow2_mod31(self.s[0], 8))
        f = add_mod31(f, mul_pow2_mod31(self.s[4], 20))
        f = add_mod31(f, mul_pow2_mod31(self.s[10], 21))
        f = add_mod31(f, mul_pow2_mod31(self.s[13], 17))
        f = add_mod31(f, mul_pow2_mod31(self.s[15], 15))
        if u is not None:
            f = add_mod31(f, u)
        self.s = self.s[1:] + [f if f != 0 else MOD31]

    def lfsr_init(self, u: int) -> None:
        self.lfsr_next(u)

    def lfsr_work(self) -> None:
        self.lfsr_next(None)

    def next_word(self) -> int:
        x0, x1, x2, x3 = self.bit_reconstruction()
        word = self.f(x0, x1, x2) ^ x3
        self.lfsr_work()
        return word & MASK32


def zuc_keystream_words(key: bytes, iv: bytes, count: int) -> list[int]:
    state = ZUCState(key, iv)
    return [state.next_word() for _ in range(count)]


def zuc_keystream_bytes(key: bytes, iv: bytes, length: int) -> bytes:
    words = zuc_keystream_words(key, iv, (length + 3) // 4)
    stream = b"".join(word.to_bytes(4, "big") for word in words)
    return stream[:length]


class ZUCAlgorithm:
    name = "ZUC-128"
    magic = b"ZUC1"

    def __init__(self, key: bytes):
        if len(key) != 16:
            raise ValueError("ZUC 密钥必须为 16 字节")
        self.key = key

    def encrypt(self, data: bytes) -> bytes:
        iv = secrets.token_bytes(16)
        ciphertext = xor_bytes(data, zuc_keystream_bytes(self.key, iv, len(data)))
        body = self.magic + iv + ciphertext
        return body + auth_tag(self.key, body)

    def decrypt(self, payload: bytes) -> bytes:
        if not payload.startswith(self.magic):
            raise ValueError("ZUC 密文头不匹配")
        body, tag = payload[:-TAG_SIZE], payload[-TAG_SIZE:]
        verify_tag(self.key, body, tag)
        iv = body[4:20]
        ciphertext = body[20:]
        return xor_bytes(ciphertext, zuc_keystream_bytes(self.key, iv, len(ciphertext)))


# ==================== 实验工程层 ====================


def save_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def create_key_material(key_dir: Path) -> KeyMaterial:
    key_dir.mkdir(parents=True, exist_ok=True)
    aes_path = key_dir / "aes_256.key"
    sm4_path = key_dir / "sm4_128.key"
    zuc_path = key_dir / "zuc_128.key"
    rsa_pub_path = key_dir / "rsa_public.json"
    rsa_pri_path = key_dir / "rsa_private.json"

    if not aes_path.exists():
        aes_path.write_bytes(secrets.token_bytes(32))
    if not sm4_path.exists():
        sm4_path.write_bytes(secrets.token_bytes(16))
    if not zuc_path.exists():
        zuc_path.write_bytes(secrets.token_bytes(16))
    if not rsa_pub_path.exists() or not rsa_pri_path.exists():
        public_key, private_key = generate_rsa_keypair()
        save_json(rsa_pub_path, {"n": str(public_key[0]), "e": str(public_key[1])})
        save_json(rsa_pri_path, {"n": str(private_key[0]), "d": str(private_key[1])})

    pub = load_json(rsa_pub_path)
    pri = load_json(rsa_pri_path)
    return KeyMaterial(
        aes_key=aes_path.read_bytes(),
        rsa_public_key=(int(pub["n"]), int(pub["e"])),
        rsa_private_key=(int(pri["n"]), int(pri["d"])),
        sm4_key=sm4_path.read_bytes(),
        zuc_key=zuc_path.read_bytes(),
    )


def build_algorithms(keys: KeyMaterial):
    return [
        AESAlgorithm(keys.aes_key),
        RSAHybridAlgorithm(keys.rsa_public_key, keys.rsa_private_key),
        SM4Algorithm(keys.sm4_key),
        ZUCAlgorithm(keys.zuc_key),
    ]


def detect_category(path: Path) -> str:
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
    files = sorted(
        (path for path in input_dir.iterdir() if path.is_file() and not path.name.startswith(".")),
        key=lambda item: (item.stat().st_size, item.name),
    )
    if max_files is not None:
        files = files[:max_files]
    return files


def sensitivity_check(algorithm, encrypted: bytes) -> str:
    changed = bytearray(encrypted)
    changed[-1] ^= 1
    try:
        algorithm.decrypt(bytes(changed))
    except Exception as exc:
        return f"拒绝解密: {exc.__class__.__name__}"
    return "未拒绝篡改密文"


def process_file(path: Path, output_dir: Path, algorithm) -> CryptoRecord:
    plain = path.read_bytes()
    algorithm_dir = output_dir / "outputs" / algorithm.name
    algorithm_dir.mkdir(parents=True, exist_ok=True)
    encrypted_path = algorithm_dir / f"{path.name}.enc"
    restored_path = algorithm_dir / f"{path.name}.restored{path.suffix}"

    start = time.perf_counter()
    encrypted = algorithm.encrypt(plain)
    encrypt_ms = (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    restored = algorithm.decrypt(encrypted)
    decrypt_ms = (time.perf_counter() - start) * 1000

    encrypted_path.write_bytes(encrypted)
    restored_path.write_bytes(restored)

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


def write_summary(records: list[CryptoRecord], output_dir: Path) -> tuple[Path, Path]:
    results_dir = output_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    summary_json = results_dir / "summary.json"
    summary_csv = results_dir / "summary.csv"
    summary_json.write_text(json.dumps([asdict(item) for item in records], ensure_ascii=False, indent=2), encoding="utf-8")
    with summary_csv.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(asdict(records[0]).keys()))
        writer.writeheader()
        for record in records:
            writer.writerow(asdict(record))
    return summary_json, summary_csv


def write_dashboard(records: list[CryptoRecord], output_dir: Path) -> Path:
    grouped: dict[str, list[CryptoRecord]] = {}
    for record in records:
        grouped.setdefault(record.algorithm, []).append(record)

    cards = []
    for algorithm, values in grouped.items():
        enc_avg = sum(item.encrypt_ms for item in values) / len(values)
        dec_avg = sum(item.decrypt_ms for item in values) / len(values)
        cards.append(
            f"<section class='card'><h2>{algorithm}</h2>"
            f"<p>平均加密 {enc_avg:.3f} ms</p><p>平均解密 {dec_avg:.3f} ms</p>"
            f"<p>样本数 {len(values)}</p></section>"
        )

    rows = []
    for record in records:
        ok = "一致" if record.original_sha256 == record.restored_sha256 else "不一致"
        rows.append(
            f"<tr><td>{record.algorithm}</td><td>{record.category}</td><td>{record.file_name}</td>"
            f"<td>{record.original_bytes}</td><td>{record.encrypted_bytes}</td>"
            f"<td>{record.encrypt_ms}</td><td>{record.decrypt_ms}</td><td>{ok}</td>"
            f"<td>{record.sensitivity_result}</td></tr>"
        )

    dashboard = output_dir / "results" / "dashboard.html"
    dashboard.write_text(
        f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>实验1 纯手写四算法加解密系统</title>
<style>
body {{ margin: 0; font-family: Arial, "PingFang SC", sans-serif; background: #f7f9fc; color: #182235; }}
header {{ padding: 22px 34px; background: #1f3b57; color: white; }}
h1 {{ margin: 0 0 8px; font-size: 28px; letter-spacing: 0; }}
main {{ padding: 26px 34px; }}
.identity {{ font-size: 17px; line-height: 1.7; }}
.cards {{ display: grid; grid-template-columns: repeat(4, minmax(180px, 1fr)); gap: 14px; margin-bottom: 22px; }}
.card {{ background: white; border: 1px solid #d7e0ea; border-radius: 8px; padding: 16px; }}
.card h2 {{ margin: 0 0 10px; font-size: 18px; }}
table {{ width: 100%; border-collapse: collapse; background: white; font-size: 14px; }}
th, td {{ border: 1px solid #d7e0ea; padding: 9px; text-align: left; vertical-align: top; }}
th {{ background: #e8eef5; }}
.note {{ margin-top: 16px; font-size: 15px; }}
</style>
</head>
<body>
<header>
<h1>实验1 纯手写四算法加解密系统</h1>
<div class="identity">学号：{STUDENT_ID}　姓名：{STUDENT_NAME}　专业班级：{MAJOR_CLASS}</div>
</header>
<main>
<div class="cards">{''.join(cards)}</div>
<table>
<thead><tr><th>算法</th><th>类型</th><th>文件</th><th>原始字节</th><th>密文字节</th><th>加密毫秒</th><th>解密毫秒</th><th>SHA256 校验</th><th>篡改测试</th></tr></thead>
<tbody>{''.join(rows)}</tbody>
</table>
<p class="note">本页面由 Python 标准库生成。AES、RSA、SM4、ZUC 的核心轮函数、密钥扩展、分组/流处理均在源码中手写实现。</p>
</main>
</body>
</html>
""",
        encoding="utf-8",
    )
    return dashboard


def run_full_demo(input_dir: Path, output_dir: Path, key_dir: Path, max_files: int | None = None) -> DemoResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    files = list(iter_sample_files(input_dir, max_files=max_files))
    if not files:
        raise ValueError(f"样本目录为空: {input_dir}")
    keys = create_key_material(key_dir)
    records: list[CryptoRecord] = []
    for path in files:
        for algorithm in build_algorithms(keys):
            print(f"正在处理: {algorithm.name} -> {path.name} ({path.stat().st_size} bytes)", flush=True)
            records.append(process_file(path, output_dir, algorithm))
    summary_json, summary_csv = write_summary(records, output_dir)
    dashboard_html = write_dashboard(records, output_dir)
    return DemoResult(output_dir, summary_json, summary_csv, dashboard_html, records)


def copy_samples(source_dir: Path, target_dir: Path) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    for path in iter_sample_files(source_dir):
        shutil.copy2(path, target_dir / path.name)


def main() -> None:
    parser = argparse.ArgumentParser(description="实验1：纯 Python 标准库手写 AES/RSA/SM4/ZUC 加解密系统")
    parser.add_argument("--input-dir", type=Path, default=Path("sample_data"), help="明文样本目录")
    parser.add_argument("--output-dir", type=Path, default=Path("."), help="输出目录")
    parser.add_argument("--key-dir", type=Path, default=Path("keys"), help="密钥目录")
    parser.add_argument("--max-files", type=int, help="可选：只处理前 N 个小文件，便于快速调试")
    parser.add_argument("--copy-samples-from", type=Path, help="可选：从旧实验目录复制样本")
    args = parser.parse_args()

    if args.copy_samples_from:
        copy_samples(args.copy_samples_from, args.input_dir)

    result = run_full_demo(args.input_dir, args.output_dir, args.key_dir, max_files=args.max_files)
    print(f"学号: {STUDENT_ID}")
    print(f"姓名: {STUDENT_NAME}")
    print(f"结果 JSON: {result.summary_json}")
    print(f"结果 CSV: {result.summary_csv}")
    print(f"演示页面: {result.dashboard_html}")
    for record in result.records:
        print(
            f"{record.algorithm} {record.category} {record.file_name} "
            f"加密 {record.encrypt_ms} ms 解密 {record.decrypt_ms} ms "
            f"SHA256 {'一致' if record.original_sha256 == record.restored_sha256 else '不一致'}"
        )


if __name__ == "__main__":
    main()
