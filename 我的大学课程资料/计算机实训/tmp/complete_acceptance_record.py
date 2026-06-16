from pathlib import Path

from docx import Document


SOURCE = Path("/Users/zoo/Desktop/计算机实训/验收过程记录表 .docx")
OUTPUT = Path("/Users/zoo/Desktop/计算机实训/验收过程记录表（补充完整版）.docx")


def replace_paragraph(paragraph, text):
    paragraph.text = text
    paragraph.paragraph_format.keep_together = True
    paragraph.paragraph_format.widow_control = True


document = Document(SOURCE)
paragraphs = document.paragraphs

replace_paragraph(
    paragraphs[12],
    "老师提问1：你在这个实验里面主要做了什么？",
)
replace_paragraph(
    paragraphs[13],
    "回答1：我这边主要做了YOLO目标识别、自动投弹程序、阿里云服务器、虚拟机和泰山派三端互通，还有4G实时图传。简单说就是把识别、网络和ROS通信打通，最后能在虚拟机上看到机载摄像头传回来的画面。",
)

replace_paragraph(
    paragraphs[16],
    "老师提问2：三端互相ping通，你们具体是怎么做的？",
)
replace_paragraph(
    paragraphs[17],
    "回答2：我们先准备一台有固定公网IP的阿里云服务器，放开51820 UDP端口。然后三端都安装WireGuard，生成各自的公钥和私钥，再配wg0.conf。VPN地址是服务器10.0.0.1、虚拟机10.0.0.2、泰山派10.0.0.3。启动wg0以后互相ping，能通就说明隧道和路由基本配对了。",
)

replace_paragraph(
    paragraphs[19],
    "老师提问3：为什么要实现三端互相ping通？",
)
replace_paragraph(
    paragraphs[20],
    "回答3：以前图像主要存在SD卡里，要等飞机回来以后再看，飞的时候地面端看不到画面。三端互相ping通是先确认服务器、泰山派和虚拟机之间的链路已经通了，后面才能通过ROS把摄像头画面实时传到虚拟机。ping通只是测试手段，最终目的是实时图传和远程监控。\n\n老师提问4：这个过程是加密传输还是非加密传输？",
)
replace_paragraph(
    paragraphs[21],
    "回答4：是加密传输。WireGuard先用公钥和私钥确认通信双方，再把原来的IP数据包加密封装成UDP报文发到对端。对端收到以后再解密、解封装，所以公网里传的不是直接可读的原始数据。",
)

replace_paragraph(
    paragraphs[23],
    "老师提问5：为什么这个方案里需要服务器来实现三端互通？",
)
replace_paragraph(
    paragraphs[24],
    "回答5：因为虚拟机和泰山派通常都在NAT后面，泰山派走4G时地址还会变，外网很难直接连进去。云服务器有固定公网IP，两端都能主动连它，所以让服务器做中转最省事，也更稳定。只有两端都有公网IP，或者另外做了NAT穿透，才适合直接连接。",
)

# Preserve the original core properties while making the output title identifiable.
props = document.core_properties
props.title = "智能无人飞行器设计与应用验收过程记录表（补充完整版）"
props.subject = "现场提问记录"

document.save(OUTPUT)
print(OUTPUT)
