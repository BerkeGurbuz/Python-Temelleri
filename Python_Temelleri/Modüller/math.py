# YÖNTEM 1
# import math
# import math as işlemler  #kütüphaneye isim atar


# value = dir(math) #kullanabileceğin fonlsiyonları gösterir
# value = help(math) #fonksiyonların ne işe yaradığını gösterir
# value = help(math.factorial) #factorial fonksiyonunun ne işe yaradığını gösterir

# value = math.pow(2,3)
# value = math.factorial(6)
# value = işlemler.ceil(5.6) #output: 6

# YÖNTEM 2
#from math import * # math kütüphanesindeki tüm fonksiyonları içerir
from math import factorial,ceil,pow #bu şekilde belli bi fonksiyonları alabilirsiniz


value = factorial(5) # başına math yazmaya gerek kalmaz
# value = sqrt(5)#bu fonksiyon çalışmaz çünkü tanımlı değil



print(value)