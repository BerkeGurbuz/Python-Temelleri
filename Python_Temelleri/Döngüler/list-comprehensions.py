# numbers = []

# for num in range(10):
#     numbers.append(num)
# print(numbers)



#number = [x for x in range(10)]     #[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

#number = [x*2 for x in range(10)]   #[0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

#number = [x*x for x in range(10)]    #[0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

#number = [x*x for x in range(10) if x % 3 == 0]   #[0, 9, 36, 81]

#number = [x if x%2==0 else 'TEK' for x in range(1,10)]  #['TEK', 2, 'TEK', 4, 'TEK', 6, 'TEK', 8, 'TEK']




#MyString = 'Hello'
#MyLetter = [letter for letter in MyString]    #['H', 'e', 'l', 'l', 'o']




# years = [1988, 1995, 2009, 2013]
# ages = [2023-year for year in years]          #[35, 28, 14, 10]



# numbers = []

# for x in range(3):
#     for y in  range(3):                 #[(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
#         numbers.append((x,y))

#numbers = [(x,y,z) for x in range(3) for y in range(3) for z in range(3)]      #[(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]