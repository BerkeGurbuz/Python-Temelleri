# Inheritance Kalıtım: Miras alma

#Person => fname, lname, age, eat(), sleep()
#Student(Person), Teacher(Person)

class Person:
    def __init__(self,fname,lname):
        self.fname = fname
        self.lname = lname
        print('Person Created')

    def who_am_i(self):
        print('I am a person')


class Student(Person): #Bu şekilde persondaki özellikleri studentda kullanabiliriz.
    def __init__(self, fname, lname, number):
        Person.__init__(self, fname, lname)
        self.number = number
    print('Student Created') 

    def who_am_i(self):
        #override; persondaki methodu ezer.
        print('I am a student')

    
class Teacher(Person):
    def __init__(self, fname, lname, branch):
        super().__init__(fname, lname) # bu şekilde de persondaki değişkenler çağırılabilir 
        self.branch = branch
        

p1 = Person('Berke', 'Gürbüz')
s1 = Student('Orhan', 'Gürbüz', '12345')
t1 = Teacher('Nurten', 'Gürbüz', 'Math')

print(p1.fname + ' ' + p1.lname) #Berke Gürbüz
print(s1.fname + ' ' + s1.lname + ' ' + s1.number) #Orhan Gürbüz 12345
print(t1.fname + ' ' + t1.lname + ' ' + t1.branch + ' Teacher') #Nurten Gürbüz Math Teacher
        
p1.who_am_i()#I am a person
s1.who_am_i()#I am a student
