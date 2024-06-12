# def cube():
#     # result = []

#     for i in range(5):
#         yield i ** 3                   # yeild bir liste açıp yer kaplamaktansa sayıyı kullanır ve sonra işi biter depolamaz.
#     #     result.append(i**3)

#     # return result

# for i in cube():
#     print(i)


generator = (i**3 for i in range(5))  #parantez generator olusturur ve sayılar kullanıldıktan sonra işleri biter listeye gerek kalmaz.

for i in generator:
    print(i)
