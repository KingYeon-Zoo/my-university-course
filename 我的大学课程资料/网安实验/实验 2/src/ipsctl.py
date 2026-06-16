"""Manage a narrowly scoped Suricata NFQUEUE path for TCP port 8080."""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
from typing import Sequence


def nfqueue_commands(port: int = 8080, queue: int = 0) -> dict[str, list[list[str]]]:
    queue_target = ["-j", "NFQUEUE", "--queue-num", str(queue), "--queue-bypass"]
    add = [
        ["iptables", "-I", "INPUT", "1", "-p", "tcp", "--dport", str(port), *queue_target],
        ["iptables", "-I", "OUTPUT", "1", "-p", "tcp", "--sport", str(port), *queue_target],
    ]
    delete = [
        ["iptables", "-D", "INPUT", "-p", "tcp", "--dport", str(port), *queue_target],
        ["iptables", "-D", "OUTPUT", "-p", "tcp", "--sport", str(port), *queue_target],
    ]
    return {"add": add, "delete": delete}


def run(command: Sequence[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    print("+", shlex.join(command))
    return subprocess.run(command, check=check, text=True)


def require_root() -> None:
    if os.geteuid() != 0:
        raise PermissionError("该操作必须使用 sudo 运行")


def enable(config: str, port: int, queue: int) -> None:
    require_root()
    commands = nfqueue_commands(port, queue)
    run(["suricata", "-T", "-c", config, "-v"])
    for command in commands["delete"]:
        run(command, check=False)
    run(["suricata", "-D", "-c", config, "-q", str(queue)])
    for command in commands["add"]:
        run(command)
    print(f"NFQUEUE 已启用：只处理 TCP {port}，队列 {queue}")


def disable(port: int, queue: int) -> None:
    require_root()
    for command in nfqueue_commands(port, queue)["delete"]:
        run(command, check=False)
    print(f"NFQUEUE 规则已移除：TCP {port}")


def status() -> None:
    run(["iptables", "-vnL", "INPUT"], check=False)
    run(["iptables", "-vnL", "OUTPUT"], check=False)
    run(["pgrep", "-af", "^suricata "], check=False)


def print_commands(port: int, queue: int) -> None:
    commands = nfqueue_commands(port, queue)
    for action in ("add", "delete"):
        print(f"[{action}]")
        for command in commands[action]:
            print(shlex.join(command))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["enable", "disable", "status", "commands"])
    parser.add_argument("--config", default="/etc/suricata/suricata.yaml")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--queue", type=int, default=0)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.action == "enable":
            enable(args.config, args.port, args.queue)
        elif args.action == "disable":
            disable(args.port, args.queue)
        elif args.action == "status":
            status()
        else:
            print_commands(args.port, args.queue)
    except (PermissionError, subprocess.CalledProcessError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
