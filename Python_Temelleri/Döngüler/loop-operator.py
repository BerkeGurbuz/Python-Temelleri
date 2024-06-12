
# for item in range(10,100,5):             # range(başlangıç, bitiş, artış miktarı)
#     print(item)


greeting = 'Merhaba'


for letter in enumerate(greeting):                  
    print(letter)                                   
# output:
# (0, 'M')
# (1, 'e')
# (2, 'r')
# (3, 'h')
# (4, 'a')
# (5, 'b')
# (6, 'a')       


for a,b in enumerate(greeting):                  
    print(f'index: {a} letter: {b}') 
#output:
#index: 0 letter: M
# index: 1 letter: e
# index: 2 letter: r
# index: 3 letter: h
# index: 4 letter: a
# index: 5 letter: b
# index: 6 letter: a             


list1 = [1,2,3,4,5]
list2 = [ 'a', 'b', 'c', 'd', 'e']
list3 = [100, 200, 300, 400, 500]

print(list(zip(list1, list2, list3)))        # zip listeleri birleştirir.

for a,b,c in zip(list1, list2, list3):
    print(a)
