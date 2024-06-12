# while True:
#     sayi = input("sayı: ")
#     if sayi == 'q':
#         break
    
#     try:
#         result = float(sayi)
#         print("girdi")

#     except ValueError:
#         print("geçersiz sayı girdiniz")
#         continue


# turkce_karakter = 'üğşçöİı'

# password = input("parolayı giriniz: ")

# for i in password:
#     if i in turkce_karakter:
#         raise TypeError("parola turkce karakter içeremez")
#     else:
#         pass

# print('geçerli')



def faktoriyel(sayi):
    sayi = int(sayi)
    if sayi < 0:
        raise ValueError("Sayı 0'dan küçük olamaz.")
    
    result = 1
    for i in range(1,sayi+1):
        result *= i

    return result

for x in [5,10,15,-3,'10a']:
    try:
        y = faktoriyel(x)
    except ValueError as err:
        print(err)
        continue
    print(y)

        




    
    
    


