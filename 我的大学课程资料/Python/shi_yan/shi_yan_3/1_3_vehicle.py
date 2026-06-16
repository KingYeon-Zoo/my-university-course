class Vehicle:
    def __init__(self, max_speed, weight):
        self.__max_speed = max_speed
        self.__weight = weight
    
    @property
    def max_speed(self):
        return self.__max_speed
    
    @max_speed.setter
    def max_speed(self, value):
        self.__max_speed = value
    
    @property
    def weight(self):
        return self.__weight
    
    @weight.setter
    def weight(self, value):
        self.__weight = value

class Bicycle(Vehicle):
    def __init__(self, max_speed, weight, height):
        super().__init__(max_speed, weight)
        self.__height = height
    
    def set_max_speed(self, speed):
        self.max_speed = speed
    
    @property
    def height(self):
        return self.__height
    
    @height.setter
    def height(self, value):
        self.__height = value


bike = Bicycle(25.0, 15.0, 1.0)

print(f"初始最大速度：{bike.max_speed} km/h")

bike.set_max_speed(30.0)
print(f"修改后最大速度：{bike.max_speed} km/h")

print(f"\n初始高度：{bike.height} m")
bike.height = 1.2
print(f"修改后高度：{bike.height} m")
