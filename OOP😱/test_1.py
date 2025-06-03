class Cat: 
    #Поля переменные класса
    name = None
    age = None
    IsHappy = None
    some = {}

    def __init__(self, name = None, age = None, IsHappy = None): #<--- Конструктор по умолчанию
        self.name = name
        self.age = age
        self.IsHappy = IsHappy
        self.get_data()


    def set_data(self, name = None, age = None, IsHappy = None): #<--- здесь всегда должен быть self Метод=функция
        self.name = name
        self.age = age
        self.IsHappy = IsHappy
    
    def get_data(self):
        print(self.name, "age", self.age, ". Happe:", self.IsHappy)

        
#Тут мы общие характеристики добавили


# Это у нас полиморфизм?
cat1 = Cat()
cat1.set_data("Jonh")

cat2 = Cat("snesok", 2, False)

print("ИТОГ:")

cat1.get_data()
cat2.get_data()

