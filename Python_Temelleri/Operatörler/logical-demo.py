#x = float(input('x: '))

# result = (x > 0) and (x < 100)

# result = (x > 0) and (x % 2 == 0)

# email = str(input('Emailinizi giriniz: '))
# password = str(input('Parolanızı giriniz: '))

# t_email = 'Berke'
# t_password = '12345'

# result = (email == t_email) and (password == t_password)

# a = float(input('a: '))
# b = float(input('b: '))
# c = float(input('c: '))

# result = (a > b) and (a > c)
# print(f'a en büyük sayıdır: {result}')

# result = (b > a) and (b > c)
# print(f'b en büyük sayıdır: {result}')

# result = (c > b) and (c > a)
# print(f'c en büyük sayıdır: {result}')

# vize1 = float(input('1. Vize notunuzu giriniz: '))
# vize2 = float(input('2. Vize notunuzu giriniz: '))
# final = float(input('Final notunuzu giriniz: '))

# ortalama = (((vize1 + vize2) /2) * 0.4) + (final * 0.6)

# result = ((ortalama >= 50) and (final >= 50)) or (final >= 70)

# if result == True :
#     print('Geçtiniz.')

# else : 
#     print('Kaldınız.')    


kilo = float(input('Kilonuzu giriniz: '))
boy = float(input('Boyunuzu giriniz (m): '))

result = (kilo / pow(boy,2))

if result <= 18.4 :
    print('Zayıfsınız.')

elif (result > 18.4) and (result <= 24.9):
    print('Normalsiniz.')

elif (result > 24.9) and (result <= 29.9):
    print('Fazla kilolu.')

elif (result > 29.9) and (result <= 34.9):
    print('Obezsin.')

print(result)















