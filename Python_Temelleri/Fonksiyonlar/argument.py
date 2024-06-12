# def changename(name):
#     name = 'Orhan'

# isim = 'Berke'
# changename(isim)
# print(isim) # output Berke

# def changecity(n):
#     n[0] = 'İstanbul'

# sehirler = ['ankara', 'Bursa']
# # changecity(sehirler)
# # print(sehirler) # output ['İstanbul', 'Bursa']

# n = sehirler[:] # sehirler listesini n'nin içine ayırdı.
# changecity(n)
# print(sehirler) #output ['ankara', 'Bursa']
# print(n) #output ['İstanbul', 'Bursa']


# def add(*params):   # 'params' le istediğin kadar parametre kullanabilirsin.   # tek yıldız kullanılırsa tuple'dır
#     # alternatif olaral add(a, b, c=0) gibi de kullanabilirsin bu 'c' kullanılmadığı zaman c'yi 0'a eşitler.
#     print(type(params)) # <class tuple>
#     print(params[0])
#     print(params[2])   # bu şekilde parametrelerin istediğn indeksine ulaşabilirsin.

#     return sum(params)      #sum fonksiyonu toplama işlemi yapar.         

# print(add(10,5,60))
# print(add(53,96,458,26,15,823))


# def DisplayUser(**args):
#     print(type(args))                #<class 'dict'>
#     print(args.items())              #dict_items([('name', 'Berke'), ('age', 18), ('city', 'Samsun')])
#     for key, value in args.items():
#         print(f'{key} is {value}.')

# DisplayUser(name = 'Berke', age = 18, city = 'Samsun')
# DisplayUser(name = 'Orhan', age = 50, city = 'İstanbul', number = '0521652655')
# DisplayUser(name = 'Nurten', age = 45, city = 'Ankara', number = '15611265', email = 'nurten@gmail.com')

def myfunc(a, b, c, *args, **kwargs):
    print(a) #10
    print(b) #20
    print(c) #30
    print(args) #(40,50,60) #tuple
    print(kwargs) #{'key1': 'value1', 'key2': 'value2'} #dictionary

myfunc(10,20,30,40,50,60,70, key1 = 'value1', key2 = 'value2')















