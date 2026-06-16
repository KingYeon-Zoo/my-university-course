from src import ipsctl
from src.ipsctl import nfqueue_commands


def test_nfqueue_commands_only_queue_the_lab_service_port():
    commands = nfqueue_commands(port=8080, queue=0)
    rendered = [" ".join(command) for command in commands["add"]]

    assert len(rendered) == 2
    assert any("INPUT" in command and "--dport 8080" in command for command in rendered)
    assert any("OUTPUT" in command and "--sport 8080" in command for command in rendered)
    assert all("--queue-num 0" in command for command in rendered)
    assert all("--queue-bypass" in command for command in rendered)
    assert all("--dport 22" not in command and "--sport 22" not in command for command in rendered)


def test_protocol_is_declared_before_port_match_options():
    commands = nfqueue_commands(port=8080, queue=0)

    for command in commands["add"] + commands["delete"]:
        protocol_index = command.index("-p")
        port_index = command.index("--dport") if "--dport" in command else command.index("--sport")
        assert protocol_index < port_index


def test_status_matches_suricata_by_full_command_line(monkeypatch):
    commands = []

    def record(command, check=True):
        commands.append(list(command))

    monkeypatch.setattr(ipsctl, "run", record)

    ipsctl.status()

    assert ["pgrep", "-af", "^suricata "] in commands
