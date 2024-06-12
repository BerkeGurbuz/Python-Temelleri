x = 'global x'

# def function():
#     x = 'local x'

# function()   # output: global x,     
# print(x)


def function():
    x = 'local x'
    print(x)

function()  # output: local x         fonksiyonun içindeki değişkenler dışarıdaki değişkenleri etkilemez
print(x)    # output: global x      

#######################

#global
name = 'Berke'

def changename(new_name):
    global name
    name = new_name
    print(name)

changename('Orhan')
print(name)  #output: Orhan
#######################


name = 'global string'

def greeting():
    # name = 'Berke'

    def hello():
        # name = 'Orhan'
        print('Hello ' + name)

    hello()

greeting()
########################


#global
x = 50

def test():
    global x #dışardaki global değişkeni çağırır 
    
    print(f'x: {x}')   #x: 50

    x = 100
    print(f'changed x to {x}')   #changed x to 100

test()
print(x)   # output: 100

















