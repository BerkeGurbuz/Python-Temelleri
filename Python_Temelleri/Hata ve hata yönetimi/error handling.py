# try:
#     x = int(input('x: '))
#     y = int(input('y: '))
#     print(x/y)

# except (ZeroDivisionError, ValueError) as e: # hata varsa bu işlemi yapar.
#     print('yanlış bilgi girdiniz.')
#     print(e)  #hata kodunu yazdırır

while True:
    try:
        x = int(input('x: '))
        y = int(input('y: '))
        print(x/y)

    except (ZeroDivisionError, ValueError) as e: 
        print('yanlış bilgi girdiniz.')
        print(e)  

    else:#except çalışmadığında çalışır.
        break

    finally:#sonlandırmak için kullanılır.
        print('işlem tamamlandı')
