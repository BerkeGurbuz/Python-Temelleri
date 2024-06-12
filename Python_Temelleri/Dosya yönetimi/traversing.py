# file = open("newfile2.txt", "a", encoding="utf-8")

# file.write("Hello World")

# file.close()

# (kendiliğinden kapanır)  as ile de bir objeye tanımlanabilir dosya.
with open("newfile2.txt", "r", encoding="utf-8") as file:   # with ile dosyanın komutlarını altına yazabilir ve dosyayı kapatmaya gerek kalmaz.
    content = file.read()
    print(content)
    file.seek(0) #imleci girilen indekse alır.
    print(file.tell()) #imlecin nerde olduğunu gösterir.
    content2 = file.read()
    print(content2)


                                                            