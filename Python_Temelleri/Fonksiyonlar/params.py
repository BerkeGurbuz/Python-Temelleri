def toplama(a,b):
    return a+b

def cikarma(a,b):
    return a-b

def carpma(a,b):
    return a*b

def bolme(a,b):
    return a/b


def islem(a,b,f1,f2,f3,f4,islem_adi):
    if islem_adi == "toplama":
        print(f1(a,b))

    elif islem_adi == "cikarma":
        print(f2(a,b))

    elif islem_adi == "carpma":
        print(f3(a,b))

    elif islem_adi == "bolme":
        print(f4(a,b))

    else:
        print("geçersiz işlem....")


a = int(input("a: "))
b = int(input("b: "))
işlem = input("işlem: ")

islem(a,b,toplama,cikarma,carpma,bolme,işlem)

