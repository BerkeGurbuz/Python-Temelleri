x = 6

result = 5 < x < 10

#and
result = (x > 5) and (x < 10)

#True,True => True
#True,False => False

#or
result = (x > 0) or (x %2 == 0)

#True,False => True
#False,False => False

#not
result = not(x > 0)

#x, 5-10 arasındaki bir çift sayı mı?

result = (x > 5) and (x < 10) and (x %2 == 0)




print(result)