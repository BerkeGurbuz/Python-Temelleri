users={}

number=input('Numara:')
name=input('Adınız:')
surname=input('Soyadınız:')
phone=input('Tel:')

users[number]={
    'ad': name,
    'soyad': surname,
    'telefon': phone,
}
print(users)