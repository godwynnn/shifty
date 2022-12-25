# from django.test import TestCase

# Create your tests here.
import calendar
import datetime

# print(calendar.month(2022,11))
# print(calendar.day_abbr(1))
# obj =calendar.Calendar(firstweekday=0)
# for obj in obj.iterweekdays():
#     print(obj)

# days=calendar.monthrange(2022,10)
# print(days)
# for day in range(days[0],days[-1]+1):
#     print(day)


# today=datetime.datetime.now().date()
# date_list=[]
# # print([today+datetime.timedelta(days=i)for i in range(0-today.weekday(),7-today.weekday())])
# for i in range(0-today.weekday(),7-today.weekday()):
#     today+=datetime.timedelta(days=1)
#     print(today)


# print(datetime.date)

# date_str="Wednesday, 10 Feb, 2022 12:19:47"
# # date_str=date_str.capitalize()

# date_obj=datetime.datetime.strptime(date_str,"%A,%d,%B,%Y ")
# print(date_obj)

shift_days=['Monday','Tuesday','Wednesday','Thursday','Saturday','Sunday']
day=input('Enter day: ').capitalize()
