from pathlib import Path

from src.crypto_lab import (
    AESGCMAlgorithm,
    RSAHybridAlgorithm,
    SM4CBCAlgorithm,
    create_key_material,
    run_full_demo,
)


def test_algorithms_round_trip_and_reject_wrong_key(tmp_path):
    key_dir = tmp_path / "keys"
    keys = create_key_material(key_dir)
    data = "学号 2023212290 的加密测试文本".encode("utf-8")

    algorithms = [
        AESGCMAlgorithm(keys.aes_key),
        RSAHybridAlgorithm(keys.rsa_private_key, keys.rsa_public_key),
        SM4CBCAlgorithm(keys.sm4_key, keys.sm4_iv),
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
            assert False, f"{algorithm.name} accepted modified ciphertext"


def test_run_full_demo_writes_results_for_sample_files(tmp_path):
    sample_dir = tmp_path / "samples"
    sample_dir.mkdir()
    (sample_dir / "文本.txt").write_text("hello 2023212290", encoding="utf-8")
    (sample_dir / "图片.jpg").write_bytes(b"fake image bytes")

    result = run_full_demo(
        input_dir=sample_dir,
        output_dir=tmp_path / "out",
        key_dir=tmp_path / "keys",
        max_files=2,
    )

    assert result.summary_json.exists()
    assert result.dashboard_html.exists()
    assert len(result.records) == 6
    assert all(record.restored_sha256 == record.original_sha256 for record in result.records)
