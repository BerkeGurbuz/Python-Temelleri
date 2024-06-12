import random

sayi = random.randint(1, 100)
hak = 5

while hak > 0:
    tahmin = int(input('Tahmin: '))
    hak -= 1
    if tahmin == sayi:
        print('Tebrikler kazandınız!!')
        break

    elif tahmin > sayi:
        print('Daha az.')

    else:
        print('Daha fazla.')

    if hak == 0:
        print(f'Hakkınız bitti. Tutulan sayı: {sayi}')

