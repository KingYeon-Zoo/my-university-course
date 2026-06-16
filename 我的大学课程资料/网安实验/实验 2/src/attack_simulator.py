"""Generate harmless HTTP attack signatures against an explicitly owned ECS."""

from __future__ import annotations

import argparse
import ipaddress
import socket
import sys
import time
from dataclasses import dataclass, field
from typing import Mapping
from urllib.parse import urlparse

import requests


@dataclass(frozen=True)
class Scenario:
    name: str
    description: str
    path: str
    method: str = "GET"
    headers: Mapping[str, str] = field(default_factory=dict)


SCENARIOS = {
    "normal": Scenario("normal", "正常请求，用于证明服务可访问", "/"),
    "sqli": Scenario(
        "sqli",
        "SQL 注入特征：UNION SELECT",
        "/search?q=1%20%75nion%20%73elect%20password%20from%20users",
    ),
    "xss": Scenario(
        "xss",
        "XSS 特征：script 标签",
        "/search?q=%3Cscript%3Ealert(1)%3C/script%3E",
    ),
    "traversal": Scenario(
        "traversal",
        "目录穿越特征：读取 /etc/passwd",
        "/download?file=%2e%2e%2f%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
    ),
    "command_injection": Scenario(
        "command_injection",
        "命令注入特征：分号连接命令",
        "/api/run?cmd=whoami;id",
    ),
    "log4shell": Scenario(
        "log4shell",
        "Log4Shell/JNDI 探测特征",
        "/",
        headers={"User-Agent": "JNDI-LAB-PROBE"},
    ),
    "scanner_user_agent": Scenario(
        "scanner_user_agent",
        "常见自动化扫描器 User-Agent",
        "/",
        headers={"User-Agent": "SQL-MAP-LAB"},
    ),
}


def validate_target(target: str, ownership_confirmed: bool) -> str:
    if not ownership_confirmed:
        raise ValueError("必须使用 --i-own-this-target 明确确认目标归你所有")

    parsed = urlparse(target)
    if parsed.scheme != "http" or not parsed.hostname:
        raise ValueError("目标必须是 http://公网IPv4:8080")

    try:
        address = ipaddress.ip_address(parsed.hostname)
    except ValueError as exc:
        raise ValueError("目标必须直接使用公网 IPv4，不能使用域名") from exc

    if address.version != 4 or not address.is_global:
        raise ValueError("目标必须直接使用公网 IPv4")
    if parsed.port != 8080:
        raise ValueError("本实验脚本只允许访问 8080 端口")
    if parsed.path not in ("", "/") or parsed.query or parsed.fragment:
        raise ValueError("目标必须是基础 URL，不能包含路径、查询参数或片段")

    return f"http://{address}:8080"


def build_scenarios(name: str) -> list[Scenario]:
    if name == "all":
        return list(SCENARIOS.values())
    try:
        return [SCENARIOS[name]]
    except KeyError as exc:
        choices = ", ".join(["all", *SCENARIOS])
        raise ValueError(f"未知场景 {name!r}，可选值：{choices}") from exc


def create_session() -> requests.Session:
    session = requests.Session()
    session.trust_env = False
    return session


def build_http_request(host: str, scenario: Scenario) -> bytes:
    headers = {
        "Host": host,
        "Connection": "close",
        **scenario.headers,
    }
    lines = [f"{scenario.method} {scenario.path} HTTP/1.1"]
    lines.extend(f"{name}: {value}" for name, value in headers.items())
    return ("\r\n".join(lines) + "\r\n\r\n").encode("ascii")


def run_segmented_scenario(target: str, scenario: Scenario, timeout: float) -> bool:
    parsed = urlparse(target)
    request = build_http_request(parsed.netloc, scenario)
    started = time.perf_counter()

    try:
        with socket.create_connection((parsed.hostname, parsed.port), timeout=timeout) as sock:
            sock.settimeout(timeout)
            for offset in range(len(request)):
                sock.sendall(request[offset : offset + 1])
                time.sleep(0.01)
            response = sock.recv(4096)
    except OSError as exc:
        elapsed = time.perf_counter() - started
        print(f"[BLOCKED] {scenario.name:<18} {elapsed:>5.2f}s  {exc.__class__.__name__}")
        return True

    elapsed = time.perf_counter() - started
    if not response:
        print(f"[BLOCKED] {scenario.name:<18} {elapsed:>5.2f}s  ConnectionClosed")
        return True

    status = response.split(b"\r\n", 1)[0].decode("ascii", errors="replace")
    print(f"[REACHED] {scenario.name:<18} {elapsed:>5.2f}s  {status}")
    return False


def run_scenario(
    target: str,
    scenario: Scenario,
    timeout: float,
    session: requests.Session | None,
) -> bool:
    if scenario.name != "normal":
        return run_segmented_scenario(target, scenario, timeout)

    if session is None:
        raise ValueError("normal scenario requires an HTTP session")

    url = f"{target}{scenario.path}"
    started = time.perf_counter()
    try:
        response = session.request(
            scenario.method,
            url,
            headers=dict(scenario.headers),
            timeout=timeout,
        )
    except requests.RequestException as exc:
        elapsed = time.perf_counter() - started
        print(f"[BLOCKED] {scenario.name:<18} {elapsed:>5.2f}s  {exc.__class__.__name__}")
        return True

    elapsed = time.perf_counter() - started
    print(
        f"[REACHED] {scenario.name:<18} {elapsed:>5.2f}s  "
        f"HTTP {response.status_code}"
    )
    return False


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="向本人拥有的 ECS 8080 端口发送受控 HTTP 攻击特征"
    )
    parser.add_argument("--target", required=True, help="例如 http://1.2.3.4:8080")
    parser.add_argument(
        "--scenario",
        default="all",
        choices=["all", *SCENARIOS],
        help="要运行的攻击场景",
    )
    parser.add_argument(
        "--i-own-this-target",
        action="store_true",
        help="确认目标服务器归你所有并授权本次测试",
    )
    parser.add_argument("--timeout", type=float, default=3.0)
    parser.add_argument("--pause", type=float, default=0.8)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        target = validate_target(args.target, args.i_own_this_target)
        scenarios = build_scenarios(args.scenario)
    except ValueError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2

    print(f"目标：{target}")
    print("说明：脚本只发送无害特征字符串，不执行任何漏洞利用命令。\n")
    blocked = 0
    with create_session() as session:
        for index, scenario in enumerate(scenarios):
            print(f"场景：{scenario.description}")
            blocked += int(run_scenario(target, scenario, args.timeout, session))
            if index < len(scenarios) - 1:
                time.sleep(args.pause)

    print(f"\n结果：{blocked}/{len(scenarios)} 个请求表现为被阻断。")
    print("请以 Suricata eve.json 和浏览器仪表盘中的 action=blocked 为最终证据。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
