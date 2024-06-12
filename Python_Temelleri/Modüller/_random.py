from random import *

result = random() #0.0 -1.0
result = random() * 100
result = int(uniform(0,100))
result = randint(1,100)

greeting = 'Hello There'
names = ['ali', 'veli', 'ayşe', 'mehmet']
# result = names[randint(0,len(names)-1)]
# result = choice(names)
# result = choice(greeting)

liste = list(range(10))
shuffle(liste)
result = liste

liste = range(100)

result = sample(liste,3)
result = sample(names,2)



print(result)