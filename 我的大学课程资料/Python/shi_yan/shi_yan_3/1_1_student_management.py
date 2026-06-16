import numpy as np

class Student:
    def __init__(self, student_id, name, gender, age, grades):
        self.student_id = student_id
        self.name = name
        self.gender = gender
        self.age = age
        self.grades = grades 

    def calculate_average(self):
        return np.mean(list(self.grades.values()))

class Classroom:
    def __init__(self):
        self.students = []

    def input_student(self):
        num_students = int(input("请输入学生数量: "))
        for _ in range(num_students):
            student_id = input("请输入学号: ")
            name = input("请输入姓名: ")
            gender = input("请输入性别: ")
            age = int(input("请输入年龄: "))
            grades = {}
            print("请输入三门课程及其成绩:")
            for _ in range(3):
                course = input("课程名: ")
                grade = float(input(f"{course}成绩: "))
                grades[course] = grade
            student = Student(student_id, name, gender, age, grades)
            self.students.append(student)

    def calculate_averages_and_rank(self):
        averages = []
        for student in self.students:
            avg = student.calculate_average()
            averages.append((student, avg))

        averages.sort(key=lambda x: x[1], reverse=True)  

        for rank, (student, avg) in enumerate(averages, start=1):
            student.average = avg
            student.rank = rank

    def print_students_info(self):
        self.calculate_averages_and_rank()
        print("\n学号\t姓名\t性别\t年龄\t三门课程成绩\t\t平均值\t排名")
        for student in sorted(self.students, key=lambda s: s.rank):
            grades_str = ', '.join(f"{course}: {grade}" for course, grade in student.grades.items())
            print(f"{student.student_id}\t{student.name}\t{student.gender}\t{student.age}\t{grades_str}\t{student.average:.2f}\t{student.rank}")

    def save_to_file(self):
        with open('my_class.txt', 'w') as f:
            for student in self.students:
                grades_str = ';'.join(f"{course}:{grade}" for course, grade in student.grades.items())
                student_info = f"{student.student_id},{student.name},{student.gender},{student.age},{grades_str}\n"
                f.write(student_info)
        print("数据已保存到 my_class.txt")

    def load_from_file(self):
        try:
            with open('my_class.txt', 'r') as f:
                self.students = []
                for line in f:
                    data = line.strip().split(',') 
                    
                    student_id, name, gender, age = data[:4]

                    grades = {}
                    grade_pairs = data[4].split(';')
                    for pair in grade_pairs:
                        course, grade = pair.split(':')
                        grades[course] = float(grade)

                    student = Student(student_id, name, gender, int(age), grades)
                    self.students.append(student)
                print(f"已从 my_class.txt 读取 {len(self.students)} 名学生信息")
        except FileNotFoundError:
            print("未找到 my_class.txt 文件，请先创建文件或输入学生信息")

classroom = Classroom()
while True:
    print("\n学生信息管理系统")
    print("1. 手动输入学生信息")
    print("2. 从文件读取学生信息")
    print("3. 显示所有学生信息")
    print("4. 保存学生信息到文件")
    print("5. 退出")
    
    choice = input("\n请选择操作 (1-5): ")
    
    if choice == '1':
        classroom.input_student()
    elif choice == '2':
        classroom.load_from_file()
    elif choice == '3':
        classroom.print_students_info()
    elif choice == '4':
        classroom.save_to_file()
    elif choice == '5':
        print("感谢使用！再见！")
        break
    else:
        print("无效的选择，请重试。")
