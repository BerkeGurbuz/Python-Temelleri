# list = [1,2,3,4,5]

# iterator = iter(list)  #iterator aslında for döngüsünün çalışma mantığı

# print(next(iterator))
# print(next(iterator))
# print(next(iterator))
# print(next(iterator))
# print(next(iterator))



class MyNumbers:
    def __init__(self,start,stop):
        self.start = start
        self.stop = stop
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.start <= self.stop:
            x = self.start
            self.start += 1
            return x
        
        else:
            raise StopIteration
        

list = MyNumbers(20,50)

for i in list:
    print(i)

