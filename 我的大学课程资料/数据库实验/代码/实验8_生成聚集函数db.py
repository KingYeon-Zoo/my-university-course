from pathlib import Path

from educ_sqlite_common import create_educ_db, print_db_summary


def main():
    db_path = Path(__file__).resolve().parent / "db" / "实验8_聚集函数.db"
    create_educ_db(db_path)
    print_db_summary(db_path, "实验八 聚集函数 SELECT")
    print("在 DBeaver 中连接该 SQLite 文件后，按实验报告中的 SQL 查询并截图。")


if __name__ == "__main__":
    main()
