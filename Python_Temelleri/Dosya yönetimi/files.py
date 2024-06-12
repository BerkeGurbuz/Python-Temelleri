# Dosya acmak ve olusturmak icin open() fonksiyonu kullanilir.
# Kullanimi: open(dosya_adi,dosya_erisme_modu)
# dosya_erisme_modu => dosyay1 hangi amacla actigimizi belirtir.

# "w": (Write) yazma modu. Dosyay1 konumda olusturur.
# Dosyayı konumda oluşturur.
# Dosya içeriğini siler ve yeniden ekleme yapar.

# file = open("textfile.txt","w",encoding='utf-8')
# #print(file)
# file.write("Berke Gürbüz")
# file.close()


# "a": (Append) ekleme. Dosya konumda yoksa olusturur.

# file = open("textfile.txt","a",encoding='utf-8')
# # file.write("\nBerke Gürbüz")
# file.write("Berke Gürbüz\n")
# file.close()


# "x": (Create) olusturma. Dosya zaten varsa hata verir.

file = open("newfile.txt","x",encoding='utf-8')

# "r": (Read) okuma. varsayilan. dosya konumda yoksa hata verir.
