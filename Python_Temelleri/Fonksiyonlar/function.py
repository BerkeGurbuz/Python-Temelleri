# def Sayhello():
#     print('Hello')

# Sayhello()


# def sayhello(name):
#     print('Hello ' + name)

# sayhello('Berke')


# def sayhello(name):
#     return 'Hello ' + name

# msg = sayhello('Berke')
# print(msg)


# def Toplama(num1, num2):
#     return num1 + num2

# result = Toplama(10,20)
# print(result)


# def yashesapla(dogumyili):
#     return 2023 - dogumyili

# yas = yashesapla(2004)
# print(yas)


def emekliligekacyilvar(dogumyili, isim):
    '''
    DOCSTRING: Dogum yiliniza gore emekliliginize kac¢c yil kaldi
    INPUT: Dogum yil1
    OUTPUT: Emeklilige kalan sure
    '''


    yas = 2023 - dogumyili
    kalansure = 65 - yas

    if kalansure > 0:
        print(f'Emekli olmanıza {kalansure} yıl kaldı.')

    else:
        print('Zaten emeklisiniz.')

emekliligekacyilvar(1950,'Berke')

print(help(emekliligekacyilvar))            #    DOCSTRING: Dogum yiliniza gore emekliliginize kac¢c yil kaldi
                                            #INPUT: Dogum yil1
                                            #OUTPUT: Emeklilige kalan sure




















