# x = 10

# if x > 5:
#     raise Exception("x 5'ten küçük olmalı")

def check_password(psw):
    import re
    
    if len(psw) < 8:
        raise Exception("Parola en az 8 karakter içermeli")
    elif not re.search("[a-z]",psw):
        raise Exception("Parola küçük harf içermelidir")
    elif not re.search("[A-Z]",psw):
        raise Exception("Parola büyük harf içermelidir")
    elif not re.search("[0-9]",psw):
        raise Exception("Parola rakam içermelidir")
    elif not re.search("[_@$]",psw):
        raise Exception("Parola alfanumerik karakter içermelidir")
    else:
        print("geçerli şifre")

    

    
password = '12345678aA@'

try:
    check_password(password)

except Exception as ex:
    print(ex)

else:
    print("geçerli şifre(else)")

finally:
    print("validation tamamlandı")


class Person:
    def __init__(self,name,year):
        if len(name) > 10:
            raise Exception("İsim 10 karakterden fazla olamaz.")
        else:
            self.name = name

p = Person("Berkeeeeeeeeeeee",2004)
        


