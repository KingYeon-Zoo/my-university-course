from pathlib import Path

from educ_sqlite_common import create_educ_db, print_db_summary


def main():
    db_path = Path(__file__).resolve().parent / "db" / "实验11_存储过程模拟.db"
    create_educ_db(db_path)
    print_db_summary(db_path, "实验十一 存储过程模拟")
    print("SQLite 不支持 CREATE PROCEDURE；在 DBeaver 中连接该文件后，用报告中的 SELECT 语句模拟调用。")


if __name__ == "__main__":
    main()
