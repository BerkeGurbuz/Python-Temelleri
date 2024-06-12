sayilar = [1,3,5,7,9,12,19,21]

# i = 0

# while (i < len(sayilar)):
#     print(sayilar[i])
#     i += 1



# bas = int(input('Başlangıç değerini giriniz [0, 7]: '))
# son = int(input('Bitiş değerini giriniz [0, 7]: ')  )

# while bas <= son:
#     print(sayilar[bas])
#     bas += 1



# i = 100

# while i > 0:
#     print(i)
#     i -= 1


# number = []

# i = 0

# while i < 5:
#     sayi = int(input('Sayı giriniz: '))
#     i += 1
#     number.append(sayi)

# number.sort()

# print(number)


urunler = []

i = int(input('Girilecek ürün sayısını belirleyiniz: '))
j = 0

while (j < i):
    name = input('Ürün adı: ')
    price = int(input('Ürün fiyatı: '))
    urunler.append({
        'name': name,
        'price': price
    })
    j += 1

for urun in urunler:
    print(f'Ürün adı: {urun["name"]}, Ürün fiyatı: {urun["price"]}')





