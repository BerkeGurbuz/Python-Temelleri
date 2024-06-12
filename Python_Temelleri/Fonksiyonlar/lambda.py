#def square(num): return num ** 2



numbers = [1,3,5,9]

#result = list(map(square,numbers)) # list içine almazsak anlamsız şeyler çıkıyor output: [1,9,25,81]

#for item in map(square,numbers):
#    print(item)  #teker teker listenin içindekileri yazdırır output: 1  9  25 81

#########################

#result = list(map(lambda num: num ** 2, numbers)) # fonksiyona gerek kalmadan lambda ile de aynı şey yapılabilir. lambda fonksiyonun yapıcağı işi yapar

############################

square = lambda num: num ** 2       #fonksiyonu bu şekilde de belirtebilirsin.
#result = list(map(square, numbers))   # bu şekilde de listeyi yazdırılıyor.
result = square(5) # bu şekilde de girilen değeri çevirir




print(result)






