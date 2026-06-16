# 实验 2：Mac 公网攻击源 + 阿里云 ECS Suricata IPS + 实时可视化

本项目把原来的 `lo` 回环 IDS 告警实验升级为真正的公网攻击与防御演示：

1. Mac 通过公网向本人拥有的阿里云 ECS 发起受控 HTTP 攻击流量。
2. ECS 上的 Suricata 使用 Linux `NFQUEUE` 内联 IPS 模式检查流量。
3. `drop` 规则实际阻断 SQL 注入、XSS、目录穿越、命令注入、Log4Shell/JNDI 探测和 SQLMap 扫描器特征。
4. Python 浏览器仪表盘实时读取 `/var/log/suricata/eve.json`，展示 `action=blocked`。

> 本项目不修改你的阿里云安全组。你上传的截图中没有 `8080/tcp` 放行规则；保持该截图状态时，公网请求无法到达实验服务。演示前必须由你自行确认 `8080/tcp` 可达，否则 Suricata 无法检测。

## 目录

```text
实验 2/
├── environment.yml
├── README.md
├── 实验 2.md
├── rules/lab-ips.rules
├── src/
│   ├── attack_simulator.py
│   ├── dashboard.py
│   ├── eve_reader.py
│   ├── ipsctl.py
│   └── lab_server.py
├── templates/dashboard.html
├── static/dashboard.css
├── static/dashboard.js
├── examples/sample_eve.json
└── tests/
```

## 规则来源与重写说明

实验规则不是简单的 `IDS_TEST` 字符串，而是参考以下公开资料后重新编写的本地规则：

- [Suricata 官方规则格式](https://docs.suricata.io/en/suricata-8.0.3/rules/intro.html)
- [Suricata 官方 HTTP sticky buffer 文档](https://docs.suricata.io/en/suricata-8.0.0/rules/http-keywords.html)
- [Suricata 官方 Linux NFQUEUE IPS 文档](https://docs.suricata.io/en/suricata-7.0.15/setting-up-ipsinline-for-linux.html)
- [Suricata 官方 suricata-update / ET Open 规则管理文档](https://docs.suricata.io/en/suricata-8.0.1/rule-management/suricata-update.html)
- [AWS GitHub：导入 Proofpoint Emerging Threats Open 规则集](https://github.com/aws-samples/aws-network-firewall-rulegroups-with-proofpoints-emerging-threats-open-ruleset)

重写后的规则使用 `flow:established,to_server`、`http.uri`、`http.uri.raw`、`http.user_agent`、`content`、`pcre` 和 `drop`，并且只作用于实验服务 `8080/tcp`。默认 `suricata-update` 获取的 ET Open 规则仍然保留。

## 一、Mac 创建 conda 环境

在 Mac 终端执行：

```bash
cd "/Users/zoo/Desktop/网安/实验 2"
conda env create -f environment.yml
conda activate suricata-ips-lab
pytest -q
```

如果你的 conda 全局默认源提示未接受 Anaconda 条款，可只使用 `conda-forge`：

```bash
conda create -y -n suricata-ips-lab --override-channels -c conda-forge \
  python=3.11 flask=3.1 requests=2.32 pytest=8.3
```

## 二、上传项目到 ECS

本实验使用 ECS 公网 IP `121.43.113.12`：

```bash
rsync -av --exclude ".pytest_cache" \
  "/Users/zoo/Desktop/网安/实验 2/" \
  root@121.43.113.12:/root/suricata-ips-lab/
```

登录服务器：

```bash
ssh root@121.43.113.12
cd /root/suricata-ips-lab
```

## 三、ECS 安装 Suricata 和 conda

```bash
sudo apt update
sudo apt install -y software-properties-common curl jq iptables
sudo add-apt-repository -y ppa:oisf/suricata-stable
sudo apt update
sudo apt install -y suricata
```

确认 Suricata 支持 NFQUEUE：

```bash
suricata --build-info | grep -i NFQ
```

安装 Miniforge conda：

```bash
curl -L -o /tmp/Miniforge3.sh \
  https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
bash /tmp/Miniforge3.sh -b -p /opt/miniforge3
/opt/miniforge3/bin/conda env create -f /root/suricata-ips-lab/environment.yml
```

## 四、安装 ET Open 和本地 IPS 规则

更新 ET Open 公开规则集：

```bash
sudo suricata-update
```

安装本项目重写的规则：

```bash
sudo install -m 0644 \
  /root/suricata-ips-lab/rules/lab-ips.rules \
  /var/lib/suricata/rules/lab-ips.rules
```

编辑 `/etc/suricata/suricata.yaml`，确认规则路径类似：

```yaml
default-rule-path: /var/lib/suricata/rules

rule-files:
  - suricata.rules
  - lab-ips.rules
```

检查配置和规则语法：

```bash
sudo suricata -T -c /etc/suricata/suricata.yaml -v
```

必须看到：

```text
Configuration provided was successfully loaded
```

## 五、启动 ECS 实验服务和可视化仪表盘

开第一个 SSH 终端，启动无漏洞实验服务：

```bash
cd /root/suricata-ips-lab
/opt/miniforge3/bin/conda run -n suricata-ips-lab \
  python -m src.lab_server --host 0.0.0.0 --port 8080
```

开第二个 SSH 终端，启动仪表盘。仪表盘只监听 ECS 本机：

```bash
cd /root/suricata-ips-lab
/opt/miniforge3/bin/conda run -n suricata-ips-lab \
  python -m src.dashboard --host 127.0.0.1 --port 8090 \
  --eve /var/log/suricata/eve.json
```

## 六、启动 Suricata 内联 IPS

开第三个 SSH 终端：

```bash
cd /root/suricata-ips-lab
sudo systemctl stop suricata
sudo rm -f /var/log/suricata/eve.json /var/log/suricata/fast.log
sudo /opt/miniforge3/bin/conda run -n suricata-ips-lab \
  python -m src.ipsctl enable
```

这个命令会：

1. 运行 `suricata -T` 检查配置。
2. 以 `suricata -q 0` 启动 NFQUEUE IPS。
3. 只把 ECS 的 `8080/tcp` 入站和回包送入队列。
4. 不处理 SSH、RDP，也不修改阿里云安全组。

查看状态：

```bash
sudo /opt/miniforge3/bin/conda run -n suricata-ips-lab \
  python -m src.ipsctl status
```

实时查看文本告警：

```bash
sudo tail -f /var/log/suricata/fast.log
```

## 七、Mac 浏览器打开可视化仪表盘

在 Mac 新开终端，建立 SSH 端口转发：

```bash
ssh -L 8090:127.0.0.1:8090 root@121.43.113.12
```

浏览器打开：

```text
http://127.0.0.1:8090
```

仪表盘每秒刷新一次，重点观察：

- `告警总数`
- `已阻断`
- `最近来源`
- 规则名称
- 动作为 `blocked`

## 八、Mac 发起公网攻击流量

先证明正常请求可达：

```bash
cd "/Users/zoo/Desktop/网安/实验 2"
conda activate suricata-ips-lab
python -m src.attack_simulator \
  --target http://121.43.113.12:8080 \
  --scenario normal \
  --i-own-this-target
```

正常结果应为：

```text
[REACHED] normal ... HTTP 200
```

再运行全部场景：

```bash
python -m src.attack_simulator \
  --target http://121.43.113.12:8080 \
  --scenario all \
  --i-own-this-target
```

预期结果：

| 场景 | 预期 |
| --- | --- |
| normal | `REACHED`，HTTP 200 |
| sqli | `BLOCKED` |
| xss | `BLOCKED` |
| traversal | `BLOCKED` |
| command_injection | `BLOCKED` |
| log4shell | `BLOCKED` |
| scanner_user_agent | `BLOCKED` |

最终证据以仪表盘和 `eve.json` 中的 `action=blocked` 为准：

```bash
sudo jq 'select(.event_type=="alert") |
  {time:.timestamp, action:.alert.action, signature:.alert.signature,
   src:.src_ip, dst:.dest_ip, dport:.dest_port}' \
  /var/log/suricata/eve.json
```

## 九、建议截图顺序

1. 阿里云 ECS 和现有安全组截图。
2. `suricata --build-info | grep -i NFQ`。
3. `lab-ips.rules` 六类规则。
4. `suricata -T` 配置检查成功。
5. `ipsctl status` 中 Suricata 进程和 INPUT/OUTPUT NFQUEUE 计数。
6. Mac 攻击模拟器中正常请求 `REACHED`、恶意请求 `BLOCKED`。
7. 浏览器仪表盘出现多条 `blocked` 告警。
8. `jq` 输出来源公网 IP、规则名称和 `action=blocked`。

## 十、停止与清理

先移除 NFQUEUE 规则：

```bash
cd /root/suricata-ips-lab
sudo /opt/miniforge3/bin/conda run -n suricata-ips-lab \
  python -m src.ipsctl disable
```

再停止进程：

```bash
sudo pkill suricata
pkill -f "src.lab_server"
pkill -f "src.dashboard"
```

## 故障排查

### Mac 开启 Clash/TUN 后，攻击请求没有出现在 ECS 告警中

为 ECS 公网 IP 添加最高优先级直连规则，并重新加载 Clash 配置：

```yaml
prepend:
  - 'IP-CIDR,121.43.113.12/32,DIRECT,no-resolve'
```

攻击模拟器会绕过系统 HTTP 代理，并把攻击请求分片发送。Suricata 在 ECS 上完成 TCP 流重组后检测，避免本机或上游代理先于实验 IPS 拦截无害特征。

### Mac 访问 `8080` 超时，Suricata 没有任何日志

公网流量没有到达 ECS。确认实验服务正在监听，并确认你现有安全组允许 `8080/tcp`：

```bash
sudo ss -lntp | grep 8080
```

### 恶意请求仍然返回 HTTP 200

检查是否真正运行在 NFQUEUE 模式，以及本地规则是否加载：

```bash
pgrep -a suricata
sudo iptables -vnL INPUT
sudo iptables -vnL OUTPUT
sudo suricata -T -c /etc/suricata/suricata.yaml -v
```

### 仪表盘为空

确认 EVE JSON 存在且包含告警：

```bash
sudo ls -l /var/log/suricata/eve.json
sudo tail -n 5 /var/log/suricata/eve.json
```

## 实验限制

- 该实验是可解释、可重复的教学型 IPS，不等同于生产环境完整 WAF。
- 实验故意使用明文 HTTP，因为 HTTPS 加密后 Suricata 无法直接检查 URI 和请求头内容。
- Python 攻击模拟器只允许公网 IPv4 的 `8080` 端口，并要求显式确认目标归本人所有。
