class Employee:
    def __init__(self, name, emp_id, base_salary):
        self.name = name
        self.emp_id = emp_id
        self.base_salary = base_salary
    
    def pay(self):
        return self.base_salary
    
    def show(self):
        return f"雇员信息 - 姓名：{self.name}，工号：{self.emp_id}，基本工资：{self.base_salary}"

class Manager(Employee):
    def __init__(self, name, emp_id, base_salary, bonus=5000):
        super().__init__(name, emp_id, base_salary)
        self.bonus = bonus
    
    def pay(self):
        return self.base_salary + self.bonus
    
    def show(self):
        return f"经理信息 - 姓名：{self.name}，工号：{self.emp_id}，基本工资：{self.base_salary}，奖金：{self.bonus}"

class Salesman(Employee):
    def __init__(self, name, emp_id, base_salary, sales=0, commission_rate=0.05):
        super().__init__(name, emp_id, base_salary)
        self.sales = sales
        self.commission_rate = commission_rate
    
    def pay(self):
        return self.base_salary + (self.sales * self.commission_rate)
    
    def show(self):
        return f"销售员信息 - 姓名：{self.name}，工号：{self.emp_id}，基本工资：{self.base_salary}，销售额：{self.sales}，提成率：{self.commission_rate}"

manager = Manager("a", "1", 15000)
print(manager.show())
print(f"经理月薪：{manager.pay()}")

salesman = Salesman("b", "2", 5000, 100000)
print(salesman.show())
print(f"销售员月薪：{salesman.pay()}")

