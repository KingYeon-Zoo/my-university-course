from pathlib import Path

from educ_sqlite_common import create_educ_db, print_db_summary


EXPERIMENTS = [
    ("实验七 数据查询", "实验7_数据查询.db"),
    ("实验八 聚集函数 SELECT", "实验8_聚集函数.db"),
    ("实验九 视图", "实验9_视图.db"),
    ("实验十 触发器", "实验10_触发器.db"),
    ("实验十一 存储过程模拟", "实验11_存储过程模拟.db"),
]


def main():
    output_dir = Path(__file__).resolve().parent / "db"
    for name, filename in EXPERIMENTS:
        db_path = create_educ_db(output_dir / filename)
        print_db_summary(db_path, name)
        print()
    print("全部数据库已生成到代码/db。用 DBeaver 逐个连接对应 SQLite 文件后执行实验报告中的 SQL。")


if __name__ == "__main__":
    main()
