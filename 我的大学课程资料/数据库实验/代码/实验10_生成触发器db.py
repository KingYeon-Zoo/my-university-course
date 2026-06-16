from pathlib import Path

from educ_sqlite_common import create_educ_db, print_db_summary


def main():
    db_path = Path(__file__).resolve().parent / "db" / "实验10_触发器.db"
    create_educ_db(db_path)
    print_db_summary(db_path, "实验十 触发器")
    print("在 DBeaver 中连接该 SQLite 文件后，手动执行 CREATE TRIGGER、测试和 DROP TRIGGER SQL。")


if __name__ == "__main__":
    main()
