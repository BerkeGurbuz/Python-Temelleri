# def my_decorators(func):
#     def wrapper(name):
#         print("fonksiyondan önceki işlem")
#         func(name)
#         print("fonksiyondan sonraki işlem")
#     return wrapper

# @my_decorators  # @ işareti o fonksiyonu diğer fonksiyona bağlar.
# def sayHello(name):  #  sayHello = func
#     print("Hello", name)

# sayHello("Berke")

import math
import time

def calculate_time(func):
    def inner(*args,**kwargs):
        start = time.time()
        time.sleep(1)
        func(*args,**kwargs)
        finish = time.time()
        print(func.__name__ + " fonksiyonu " + str(finish-start) + " saniye sürdü")
    return inner

@calculate_time
def usalma(a,b):
    print(math.pow(a,b))

@calculate_time
def faktoriyel(num):
    print(math.factorial(num))

@calculate_time
def toplama(a,b):
    print(a+b)


usalma(2,3)
faktoriyel(5)
toplama(78,95)
