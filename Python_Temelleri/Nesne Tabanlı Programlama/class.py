# class

class Person:
    #class attributes
    address = 'No information'
    #construction (yapıcı method)
    def __init__(self, name, year):
        #object attributes
        self.name = name
        self.year = year
        print('init fonksiyonu çalıştı.')

        #methods

#object (intance)
p1 = Person('Berke', 2004)
p2 = Person('Orhan', 1962)

#updating
p1.address = 'Samsun'
p2.name = 'Ahmet'

#accessing object attributes
print(f'name = {p1.name}, year = {p1.year}, address = {p1.address}')
print(f'name = {p2.name}, year = {p2.year}, address = {p2.address}')

print(p1)
print(p2)
print(type(p1)) #<class '__main__.Person'>
print(type(p2)) #<class '__main__.Person'>
        