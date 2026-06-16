import sqlite3
from pathlib import Path
from textwrap import dedent


def connect_educ():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    create_schema(conn)
    seed_data(conn)
    return conn


def create_educ_db(db_path):
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    create_schema(conn)
    seed_data(conn)
    conn.close()
    return db_path


def print_db_summary(db_path, experiment_name):
    conn = sqlite3.connect(db_path)
    print(f"{experiment_name} SQLite 数据库已生成:")
    print(db_path)
    for table in ("系", "专业", "教师", "学生", "课程", "学生选课"):
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"{table}: {count} 条")
    conn.close()


def create_schema(conn):
    conn.executescript(
        """
        CREATE TABLE 系 (
            系编号 TEXT PRIMARY KEY,
            系名称 TEXT NOT NULL,
            系主任 TEXT,
            联系电话 TEXT,
            地址 TEXT
        );

        CREATE TABLE 专业 (
            专业编号 TEXT PRIMARY KEY,
            专业名称 TEXT NOT NULL,
            所属系 TEXT,
            FOREIGN KEY (所属系) REFERENCES 系(系编号)
        );

        CREATE TABLE 教师 (
            教师编号 TEXT PRIMARY KEY,
            姓名 TEXT NOT NULL,
            所在系 TEXT,
            电话 TEXT,
            电子信箱 TEXT,
            FOREIGN KEY (所在系) REFERENCES 系(系编号)
        );

        CREATE TABLE 学生 (
            学号 TEXT PRIMARY KEY,
            姓名 TEXT NOT NULL UNIQUE,
            性别 TEXT CHECK (性别 IN ('男', '女')),
            年龄 INTEGER CHECK (年龄 BETWEEN 0 AND 120),
            专业号 TEXT,
            班级 TEXT,
            FOREIGN KEY (专业号) REFERENCES 专业(专业编号)
        );

        CREATE TABLE 课程 (
            课程号 TEXT PRIMARY KEY,
            课程名 TEXT NOT NULL UNIQUE,
            学分 REAL,
            学时 INTEGER,
            先修课 TEXT,
            选课人数 INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (先修课) REFERENCES 课程(课程号)
        );

        CREATE TABLE 学生选课 (
            学号 TEXT,
            课程号 TEXT,
            成绩 REAL CHECK (成绩 BETWEEN 0 AND 100),
            PRIMARY KEY (学号, 课程号),
            FOREIGN KEY (学号) REFERENCES 学生(学号),
            FOREIGN KEY (课程号) REFERENCES 课程(课程号)
        );
        """
    )


def seed_data(conn):
    conn.executemany(
        "INSERT INTO 系 VALUES (?, ?, ?, ?, ?)",
        [
            ("D001", "计算机系", "王主任", "05510001", "信息楼101"),
            ("D002", "数学系", "李主任", "05510002", "教学楼201"),
            ("D003", "电子系", "赵主任", "05510003", "实验楼301"),
            ("D004", "管理系", "钱主任", "05510004", "文科楼401"),
        ],
    )
    conn.executemany(
        "INSERT INTO 专业 VALUES (?, ?, ?)",
        [
            ("01", "计算机科学与技术", "D001"),
            ("02", "软件工程", "D001"),
            ("03", "网络工程", "D001"),
            ("04", "信息安全", "D001"),
            ("05", "数学与应用数学", "D002"),
            ("06", "电子信息工程", "D003"),
            ("07", "通信工程", "D003"),
            ("08", "工商管理", "D004"),
        ],
    )
    conn.executemany(
        "INSERT INTO 教师 VALUES (?, ?, ?, ?, ?)",
        [
            ("T000000001", "张老师", "D001", "13800000001", "zhang@educ.com"),
            ("T000000002", "李老师", "D001", "13800000002", "li@educ.com"),
            ("T000000003", "王老师", "D002", "13800000003", "wang@educ.com"),
            ("T000000004", "赵老师", "D003", "13800000004", "zhao@educ.com"),
            ("T000000005", "钱老师", "D004", "13800000005", "qian@educ.com"),
        ],
    )
    conn.executemany(
        "INSERT INTO 学生 VALUES (?, ?, ?, ?, ?, ?)",
        [
            ("20230001", "张三", "男", 19, "01", "计科2301"),
            ("20230002", "李四", "女", 20, "01", "计科2301"),
            ("20230003", "王五", "男", 19, "02", "软件2301"),
            ("20230004", "赵六", "女", 18, "02", "软件2301"),
            ("20230005", "钱七", "男", 21, "03", "网络2301"),
            ("20230006", "孙八", "女", 20, "03", "网络2301"),
            ("20230007", "周九", "男", 19, "04", "信安2301"),
            ("20230008", "吴十", "女", 18, "04", "信安2301"),
            ("20230009", "郑一", "男", 20, "05", "数学2301"),
            ("20230010", "冯二", "女", 21, "05", "数学2301"),
            ("20230011", "陈三", "男", 19, "06", "电子2301"),
            ("20230012", "褚四", "女", 20, "06", "电子2301"),
            ("20230013", "卫五", "男", 18, "07", "通信2301"),
            ("20230014", "蒋六", "女", 19, "07", "通信2301"),
            ("20230015", "沈七", "男", 20, "08", "管理2301"),
            ("20230016", "许八", "女", 26, "01", "计科2302"),
            ("20230017", "何九", "男", 22, "02", "软件2302"),
        ],
    )
    conn.executemany(
        "INSERT INTO 课程(课程号, 课程名, 学分, 学时, 先修课) VALUES (?, ?, ?, ?, ?)",
        [
            ("c101", "数据库原理", 4, 64, None),
            ("c102", "程序设计基础", 4, 64, None),
            ("c103", "高等数学", 5, 80, None),
            ("c104", "大学英语", 3, 48, None),
            ("c105", "计算机导论", 2, 32, None),
            ("c110", "离散数学", 3, 48, "c103"),
            ("c209", "C语言程序设计", 4, 64, "c102"),
            ("c210", "Java语言", 4, 64, "c209"),
            ("c218", "数据结构", 4, 64, "c209"),
            ("c331", "操作系统", 4, 64, "c218"),
            ("c332", "计算机网络", 4, 64, "c331"),
            ("c400", "人工智能基础", 3, 48, "c218"),
        ],
    )
    conn.executemany(
        "INSERT INTO 学生选课 VALUES (?, ?, ?)",
        [
            ("20230001", "c101", 86),
            ("20230001", "c110", 84),
            ("20230001", "c210", 88),
            ("20230001", "c218", 92),
            ("20230002", "c101", 81),
            ("20230002", "c102", 76),
            ("20230003", "c101", 90),
            ("20230003", "c210", 88),
            ("20230004", "c209", 58),
            ("20230004", "c218", 79),
            ("20230005", "c331", 83),
            ("20230006", "c332", 57),
            ("20230007", "c101", 95),
            ("20230008", "c103", 89),
            ("20230009", "c103", 91),
            ("20230010", "c104", 85),
            ("20230011", "c105", 73),
            ("20230012", "c209", 55),
            ("20230013", "c210", 80),
            ("20230014", "c218", 87),
            ("20230015", "c104", 60),
            ("20230015", "c105", 75),
        ],
    )
    conn.execute(
        """
        UPDATE 课程
        SET 选课人数 = (
            SELECT COUNT(*) FROM 学生选课 WHERE 学生选课.课程号 = 课程.课程号
        )
        """
    )
    conn.commit()


def run_query(conn, title, sql, params=()):
    print(f"\n{'=' * 72}\n{title}\nSQL:\n{dedent(sql).strip()}\n结果:")
    rows = conn.execute(dedent(sql), params).fetchall()
    print_rows(rows)
    return rows


def run_statement(conn, title, sql, params=()):
    print(f"\n{'=' * 72}\n{title}\nSQL:\n{dedent(sql).strip()}")
    try:
        conn.execute(dedent(sql), params)
        conn.commit()
        print("执行结果: 成功")
    except sqlite3.Error as exc:
        print(f"执行结果: 失败，{exc}")


def print_rows(rows):
    if not rows:
        print("(无记录)")
        return
    headers = rows[0].keys()
    widths = []
    for header in headers:
        max_value_width = max(len(str(row[header])) if row[header] is not None else 4 for row in rows)
        widths.append(max(len(header), max_value_width))
    print(" | ".join(header.ljust(width) for header, width in zip(headers, widths)))
    print("-+-".join("-" * width for width in widths))
    for row in rows:
        print(
            " | ".join(
                (str(row[header]) if row[header] is not None else "NULL").ljust(width)
                for header, width in zip(headers, widths)
            )
        )
