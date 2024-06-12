# try:
#     file = open("newfile.txt","r")
#     print(file)

# except FileNotFoundError:
#     print("dosya bulma hatası")

# finally:
#     print("dosya kapandı")
#     file.close()


file = open("newfile.txt","r", encoding = "utf-8")

#for döngüsü

# for i in file:
#     print(i, end = "")


#*******************read fonksiyonu

# content = file.read()
# print(content)

# content = file.read(5)
# content = file.read(3)
# content = file.read(3)

# print(content)


#*******************readline fonksiyonu


# print(file.readline(),end="")
# print(file.readline(),end="")
# print(file.readline(),end="")
# print(file.readline(),end="")
# print(file.readline())
# print(file.readline())


#*********************readlines fonksiyonu

liste = file.readlines()

print(liste[0],end="")
print(liste[1],end="")
print(liste[2],end="")












file.close()