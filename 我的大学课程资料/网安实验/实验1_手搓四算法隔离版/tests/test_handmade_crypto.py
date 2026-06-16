from pathlib import Path

from src.handmade_crypto_lab import (
    AESAlgorithm,
    RSAHybridAlgorithm,
    SM4Algorithm,
    ZUCAlgorithm,
    aes_encrypt_block,
    create_key_material,
    run_full_demo,
    sm4_encrypt_block,
    zuc_keystream_words,
)


def test_aes_block_matches_known_vector():
    key = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
    plain = bytes.fromhex("00112233445566778899aabbccddeeff")
    assert aes_encrypt_block(plain, key).hex() == "69c4e0d86a7b0430d8cdb78070b4c55a"
    key256 = bytes.fromhex("000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f")
    assert aes_encrypt_block(plain, key256).hex() == "8ea2b7ca516745bfeafc49904b496089"


def test_sm4_block_matches_known_vector():
    key = bytes.fromhex("0123456789abcdeffedcba9876543210")
    plain = bytes.fromhex("0123456789abcdeffedcba9876543210")
    assert sm4_encrypt_block(plain, key).hex() == "681edf34d206965e86b3e94f536e4246"


def test_zuc_zero_vector_first_words():
    words = zuc_keystream_words(bytes(16), bytes(16), 2)
    assert [f"{word:08x}" for word in words] == ["27bede74", "018082da"]


def test_four_algorithms_round_trip_and_detect_tamper(tmp_path):
    keys = create_key_material(tmp_path / "keys")
    data = "实验1 四算法纯手搓实现 2023212290".encode("utf-8")
    algorithms = [
        AESAlgorithm(keys.aes_key),
        RSAHybridAlgorithm(keys.rsa_public_key, keys.rsa_private_key),
        SM4Algorithm(keys.sm4_key),
        ZUCAlgorithm(keys.zuc_key),
    ]

    for algorithm in algorithms:
        encrypted = algorithm.encrypt(data)
        assert encrypted != data
        assert algorithm.decrypt(encrypted) == data
        changed = bytearray(encrypted)
        changed[-1] ^= 1
        try:
            algorithm.decrypt(bytes(changed))
        except Exception:
            pass
        else:
            raise AssertionError(f"{algorithm.name} accepted modified ciphertext")


def test_run_full_demo_writes_reports_for_all_four_algorithms(tmp_path):
    sample_dir = tmp_path / "samples"
    sample_dir.mkdir()
    (sample_dir / "文本.txt").write_text("hello", encoding="utf-8")
    (sample_dir / "图片.jpg").write_bytes(b"fake image bytes")

    result = run_full_demo(
        input_dir=sample_dir,
        output_dir=tmp_path / "out",
        key_dir=tmp_path / "keys",
    )

    assert result.summary_json.exists()
    assert result.summary_csv.exists()
    assert result.dashboard_html.exists()
    assert len(result.records) == 8
    assert {record.algorithm for record in result.records} == {
        "AES-256-CBC",
        "RSA-1024-OAEP-Hybrid",
        "SM4-CBC",
        "ZUC-128",
    }
    assert all(record.restored_sha256 == record.original_sha256 for record in result.records)
