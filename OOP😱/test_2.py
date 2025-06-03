#Наследование
class Building:
    year = None
    city = None

    def __init__(self, year, city):
        self.city = city
        self.year = year

    def get_info(self):
        print("Year:", self.year, " City:", self.city)

school = Building(2000, "Moscow")
house = Building(2001, "Puter")
shop = Building(2003, "London")