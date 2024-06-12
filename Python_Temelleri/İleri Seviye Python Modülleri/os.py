import os

# result = os.name  # hanngi işletim sistemini kullandığını gösterir    nt = Windows   mac = MacOS 
#result = os.getcwd()  # Şuan hangi klasörün içinde olduğunu gösterir   output: C:\Users\Admin\Desktop\Python_Temelleri
# result = os.mkdirs("newdirectiory") # yeni klasör oluşturur.
# os.chdir("C:\\") # belirtilen klasöre geçer burda c klasörünün altına geçti
# os.chdir("..") #bir üst dizine geçer

#klasör oluşturma
# os.mkdir("newdirectory") #klasör oluşturur.
# os.makedirs("newdirectorys/yeniklasör") #klasör oluşturur.
# os.rename("newdirectory","yeniklasör") #adını değiştirir.
# os.rmdir("newdirectory") #klasoru siler. (alt dizin yoksa)
# os.removedirs("newdirectorys/yeniklasör") #belirtilen alt dizini siler.



# Listeleme
# result = os.listdir() # bulunduğun klasörü listeler.
# result = os.listdir("C:\\") # belirtilen klasörü listeler.

# for dosya in os.listdir():
#     if dosya.endswith(".py"):   # .py uzantılı dosyaları listeler.
#         print(dosya)

# result = os.stat("date.py") #dosyanın belirli özellikleri gösterir.


# os.system("notepad.exe") #belirlenen uygulamyı çalıştırır.


# path

# result = os.path.abspath("os.py") #soyanın konunumunu verir.
# result = os.path.dirname("C:/Users/Admin/Desktop/Python_Temelleri/os.py") #dosyanın dizinini bulur.
# result = os.path.dirname(os.path.abspath("os.py")) #tam yolunu bilmedğimiz dosyanın dizinini verir.
# result = os.path.exists("C:/Users/Admin/Desktop/Python_Temelleri/İleri Seviye Python Modülleri/os.py") #dosyanın olup olmadığını soler.
# result = os.path.isdir("C:/Users/Admin/Desktop/Python_Temelleri") #klasor ollup olmadıgına bakar.
# result = os.path.isfile("C:/Users/Admin/Desktop/Python_Temelleri") # dosya olup olmadıgına bakar.
# result = os.path.join("C:\\","deneme") #dizin olusturu ama gercekte o dizin yoktur sadece denemelik olusturur.
# result = os.path.split("C:\\deneme") #dizinleri boler liste olusturur.
# result = os.path.splitext("os.py") #dosyanın adını boler.



# print(result)