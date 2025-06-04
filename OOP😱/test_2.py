#Наследование - особенность ооп в котором мы наследуем все от родительского класса
class Building:
    year = None #Инкапсуляция это зашита данных, то есть нам надо защищить данные от внешнего воздействия 
    city = None #А доступ должен быть только через разные методы, а в питоне она не работает 

    def __init__(self, year, city):
        self.city = city
        self.year = year

    def get_info(self):
        print("Year:", self.year, " City:", self.city)


class School(Building): #Нету множественого наследования, в языках после C++ Нету такого
    pupils = 0

    def __init__(self, year, city, pupils):
        super(School, self).__init__(year, city) #<-- Вызывает класс родитель
        self.pupils = pupils
    
    def get_info(self): # <---- ееее а это полиморфизм 
        super().get_info()  
        print("Pupils:", self.pupils)


class House(Building):
    pass


class Shop(Building):
    pass


school1 = School(2000, "Moscow", 200)
school1.get_info()


house = House(2001, "Puter")


shop = Shop(2003, "London")