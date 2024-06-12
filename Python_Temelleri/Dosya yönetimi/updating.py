# with open("newfile2.txt", "r+", encoding="utf-8") as file: # r+ hem okuyup hem de güncelleyebilirsin.
#     file.seek(12)
#     file.write("deneme")


# ****** sayfa sonuna ekleme *********
# with open("newfile2.txt", "a", encoding="utf-8") as file:
#     file.write("\nBerke Gürbüz")

# with open("newfile2.txt", "r+", encoding="utf-8") as file:
#     print(file.read())


# ****** sayfa başına ekleme *********

# with open("newfile2.txt", "r+", encoding="utf-8") as file:
#     content = file.read()
#     content = "Berke Gürbüz" + content
#     file.seek(0)
#     file.write(content)
#     print(content)


# ******* syfa ortasına ekleme *********
with open("newfile2.txt", "r+", encoding="utf-8") as file:
    list = file.readlines()
    list.insert(2,"Nurten Gürbüz\n")
    print(list)
    file.seek(0)
    file.writelines(list)

with open("newfile2.txt", "r", encoding="utf-8") as file:
    print(file.read())

