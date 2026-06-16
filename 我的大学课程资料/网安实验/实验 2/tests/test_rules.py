from pathlib import Path


RULES_PATH = Path(__file__).resolve().parents[1] / "rules" / "lab-ips.rules"


def test_command_injection_rule_encodes_semicolon_content():
    rules = RULES_PATH.read_text(encoding="utf-8")

    assert 'content:";";' not in rules
    assert 'content:"|3b|";' in rules


def test_header_rules_match_network_safe_lab_markers():
    rules = RULES_PATH.read_text(encoding="utf-8")

    assert 'content:"${jndi:";' in rules
    assert 'content:"sqlmap";' in rules
    assert 'content:"JNDI-LAB-PROBE";' in rules
    assert 'content:"SQL-MAP-LAB";' in rules
