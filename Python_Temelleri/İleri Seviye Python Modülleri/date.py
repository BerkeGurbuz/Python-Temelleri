from datetime import datetime
from datetime import timedelta
# from datetime import time
# from datetime import date

result = datetime.now() # 2023-07-17 14:53:39.145179
simdi = datetime.now()

result = simdi.year #2023
result = simdi.day #17
result = simdi.hour #14
result = simdi.minute #53
result = simdi.second #39

result = datetime.ctime(simdi) #Mon Jul 17 14:56:56 2023
result = datetime.strftime(simdi, '%Y') #2023
result = datetime.strftime(simdi, '%X') #14:59:07
result = datetime.strftime(simdi, '%d') #17
result = datetime.strftime(simdi, '%A') #Monday
result = datetime.strftime(simdi, '%B') #July
result = datetime.strftime(simdi, '%Y %B %A') #2023 July Monday


t = '17 June 2023 Hour 15:03:30'
result = datetime.strptime(t,'%d %B %Y Hour %H:%M:%S')


birthday = datetime(2004,11,4,9,10,15)

result = datetime.timestamp(birthday) #milat ile aradaki farkı saniye türünde yazdırır
result = datetime.fromtimestamp(result) #saniye bilgisi tarihe dönüşür
result = datetime.fromtimestamp(0) #1970-01-01 03:00:00  milat


result = simdi - birthday #timedelta
result = simdi + timedelta(days=10) #10 gün ekler
result = simdi + timedelta(days=730, minutes=500)
result = simdi - timedelta(days=10) #10 gün çıkarır



print(result)



