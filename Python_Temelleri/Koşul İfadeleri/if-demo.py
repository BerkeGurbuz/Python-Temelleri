# # input('Adınızı giriniz: ')
# # input('Soyadınızı giriniz: ')
# yas = str(input('Yaşınızı giriniz: '))
# ed = input('Eğitim durumunuz: ')

# ed1 = 'Lise'
# ed2 = 'Üniversite'

# if (yas >= str(18)) :
#     if (ed == ed1) or (ed == ed2):
#         print('Ehliyet alabilirsiniz.')

#     elif (ed == ''):
#         print('Lütfen eğitim kısmını doldurunuz.')    

#     else:
#         print('Eğitim durumunuz en az lise olmalıdır.')    

# elif (yas == ''):
#     print('Yaş kısmını doldurunuz.')  

# else:
#     print("Yaşınız 18'den büyük olmalıdır.")   


# exam1 = float(input('Birinci yazılı notounuzu giriniz: '))
# exam2 = float(input('İkinci yazılı notunuzu giriniz: '))

# mean = (exam1 + exam2)/2

# if (mean < 25):
#     print('0')

# elif (mean >= 25) and (mean < 45):
#     print('1')

# elif (mean >= 45) and (mean < 55):
#     print('2')        

# elif (mean >= 55) and (mean < 70):
#     print('3')

# elif (mean >= 70) and (mean < 85):
#     print('4')

# elif (mean >= 85) and (mean <= 100):
#     print('5')

# else:
#     print('Lütfen geçerli bir not giriniz.')    


# import datetime

# tarih = input('Aracınızın trafiğe çıkış tarihini yazınız(2021/9/9): ')
# tarih = tarih.split('/')
# trafigecikis = datetime.datetime(int(tarih[0]),int(tarih[1]),int(tarih[2]))
# simdi = datetime.datetime.now()
# fark = simdi - trafigecikis
# days = fark.days
# print(days)

# if (days > 0) and (days <= 365):
#     print('1. servis aralığı')

# elif (days > 365) and (days<= 365*2):
#     print('2. servis aralığı')

# elif (days > 365*2) and (days <= 365*3):
#     print('3. servis alanı')

# else:
#     print('Geçersiz değer girdiniz.')    

# sayı = int(input('Bir sayı giriniz: '))

# if (sayı > 0) and (sayı < 100):
#     print('sayı 0 ile 100 arasındadır.')

# elif (sayı == 0):
#     print("sayı 0'dır")

# elif (sayı == 100):
#     print("sayı 100'dür.")        

# else:
#     print('girilen sayı 0 ile 100 arasında değildir.')

# sayı = float(input('Bir sayı giriniz: '))

# if (sayı > 0) and (sayı %2 == 0):
#     print('sayı pozitif çift sayıdır.')

# elif (sayı > 0) and (sayı %2 != 0):
#     print('sayı pozitif tek sayıdır.')    

# elif (sayı < 0) and (sayı %2 == 0):
#     print('sayı negatif çift sayıdır')    

# else:
#     print('sayı negatif tek sayıdır') 













