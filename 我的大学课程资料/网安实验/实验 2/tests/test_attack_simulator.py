import pytest

from src import attack_simulator
from src.attack_simulator import (
    build_http_request,
    build_scenarios,
    create_session,
    run_scenario,
    validate_target,
)


def test_validate_target_requires_explicit_ownership_confirmation():
    with pytest.raises(ValueError, match="归你所有"):
        validate_target("http://203.0.113.10:8080", ownership_confirmed=False)


def test_validate_target_rejects_private_and_hostname_targets():
    with pytest.raises(ValueError, match="公网 IPv4"):
        validate_target("http://127.0.0.1:8080", ownership_confirmed=True)

    with pytest.raises(ValueError, match="公网 IPv4"):
        validate_target("http://example.com:8080", ownership_confirmed=True)


def test_validate_target_accepts_public_ipv4_base_url():
    assert (
        validate_target("http://8.8.8.8:8080/", ownership_confirmed=True)
        == "http://8.8.8.8:8080"
    )


def test_all_scenarios_include_normal_and_six_attack_categories():
    scenarios = build_scenarios("all")
    names = {scenario.name for scenario in scenarios}

    assert names == {
        "normal",
        "sqli",
        "xss",
        "traversal",
        "command_injection",
        "log4shell",
        "scanner_user_agent",
    }
    assert all(scenario.path.startswith("/") for scenario in scenarios)


def test_single_scenario_can_be_selected():
    scenarios = build_scenarios("xss")

    assert len(scenarios) == 1
    assert scenarios[0].name == "xss"


def test_attack_session_bypasses_system_proxy_settings():
    session = create_session()

    assert session.trust_env is False


def test_traversal_scenario_uses_encoded_dot_segments():
    scenario = build_scenarios("traversal")[0]

    assert "%2e%2e%2f" in scenario.path.lower()


def test_sqli_scenario_encodes_keyword_initials():
    scenario = build_scenarios("sqli")[0]

    assert "%75nion" in scenario.path.lower()
    assert "%73elect" in scenario.path.lower()


def test_header_scenarios_use_network_safe_lab_markers():
    log4shell = build_scenarios("log4shell")[0]
    scanner = build_scenarios("scanner_user_agent")[0]

    assert log4shell.headers["User-Agent"] == "JNDI-LAB-PROBE"
    assert scanner.headers["User-Agent"] == "SQL-MAP-LAB"


def test_build_http_request_includes_path_host_and_headers():
    scenario = build_scenarios("log4shell")[0]

    request = build_http_request("121.43.113.12:8080", scenario)

    assert request.startswith(b"GET / HTTP/1.1\r\n")
    assert b"Host: 121.43.113.12:8080\r\n" in request
    assert b"User-Agent: JNDI-LAB-PROBE\r\n" in request
    assert request.endswith(b"\r\n\r\n")


def test_attack_scenarios_use_segmented_sender(monkeypatch):
    calls = []

    def fake_segmented(target, scenario, timeout):
        calls.append((target, scenario.name, timeout))
        return True

    monkeypatch.setattr(attack_simulator, "run_segmented_scenario", fake_segmented)

    blocked = run_scenario(
        "http://121.43.113.12:8080",
        build_scenarios("xss")[0],
        timeout=3.0,
        session=None,
    )

    assert blocked is True
    assert calls == [("http://121.43.113.12:8080", "xss", 3.0)]


def test_segmented_sender_uses_single_byte_chunks(monkeypatch):
    sent = []

    class FakeSocket:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def settimeout(self, timeout):
            pass

        def sendall(self, chunk):
            sent.append(chunk)

        def recv(self, size):
            return b""

    monkeypatch.setattr(attack_simulator.socket, "create_connection", lambda *args, **kwargs: FakeSocket())
    monkeypatch.setattr(attack_simulator.time, "sleep", lambda seconds: None)

    attack_simulator.run_segmented_scenario(
        "http://121.43.113.12:8080",
        build_scenarios("scanner_user_agent")[0],
        timeout=3.0,
    )

    assert sent
    assert all(len(chunk) == 1 for chunk in sent)
