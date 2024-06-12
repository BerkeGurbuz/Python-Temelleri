#class

class Person:
    #class attributes
    pass
    #constructor (yapıcı method)
    def __init__(self,name,year):
        #object attributes
        self.name = name
        self.year = year

    #method
    def intro(self):
        print(f'Hello There. I am {self.name}.')

    def calculateAge(self):
        return 2023 - self.year

p1 = Person('Berke', 2004)
p2 = Person('Orhan', 1964)

p1.intro() #Hello There. I am Berke.
p2.intro() #Hello There. I am Orhan.

print(f'Adım {p1.name} yaşım {p1.calculateAge()}') #Adım Berke yaşım 19
print(f'Adım {p2.name} yaşım {p2.calculateAge()}') #Adım Orhan yaşım 59




class Circle:
    pi = 3.14

    def __init__(self,yaricap):
        self.yaricap = yaricap

    def cevrehesap(self):
        return 2 * self.pi * self.yaricap
    
    def alanhesap(self):
        return self.pi * (self.yaricap ** 2)
    
circle1 = Circle(1)
circle2 = Circle(5)

print(f'Birinci dairenin çeversi: {circle1.cevrehesap()}, alanı: {circle1.alanhesap()}') #Birinci dairenin çeversi: 6.28, alanı: 3.14
print(f'İkinci dairenin çeversi: {circle2.cevrehesap()}, alanı: {circle2.alanhesap()}') #İkinci dairenin çeversi: 31.400000000000002, alanı: 78.5
    

        