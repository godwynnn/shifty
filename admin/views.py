import secrets
import string
from django.template import loader

from email.policy import HTTP
from urllib import response
from main.models import *
from shiftyapp.email_sender import sendmail
from django.shortcuts import render
from admin.serializers import AttendanceSerializer, ProfileSerializer, ShiftSerializer,UserSerializer,FacilitiesSerializer
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView,RetrieveAPIView,ListCreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.contrib.auth.models import User
from main.models import *
from django.contrib.auth import (
    login,
    authenticate,
    logout
    )
from knox.auth import TokenAuthentication 
from knox.models import AuthToken
from rest_framework import generics
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import check_password, make_password
from django.db.models import Q
from rest_framework import filters
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
# Create your views here.



def sendallschedule(user):
    attendances = Attendance.objects.filter(user=user,start_date_time__gte=datetime.datetime.now()).order_by('-start_date_time').reverse()
    message = loader.render_to_string('admin/shift_email_template.html',{'attendances': attendances})
    subject = 'Shiftyapp - Shift Schedule'
    sendmail([user.email],message,message,subject)
    return Response({'success':True},status=status.HTTP_200_OK)  



def createattendance(user,shift,period='day', number=30,send_shedule=True):
    shift_start_hour =shift.start_time.hour
    shift_start_minute = shift.start_time.minute
    shift_start_seconds = shift.start_time.second
    shift_end_hour =shift.end_time.hour
    shift_end_minute = shift.end_time.minute
    shift_end_seconds = shift.end_time.second    
    current_time = datetime.datetime.now()
    created_attendances = []
    if current_time.weekday() == shift.day_num and current_time.time() < shift.start_time:
        shift_year = current_time.date().year
        shift_month =current_time.date().month
        shift_start_day =current_time.date().day
        start_date_time = datetime.datetime(shift_year,shift_month,shift_start_day,shift_start_hour,shift_start_minute,shift_start_seconds)
        end_date_time =  datetime.datetime(shift_year,shift_month,shift_start_day,shift_end_hour,shift_end_minute,shift_end_seconds)        
        attendance,created = Attendance.objects.get_or_create(user=user,shift=shift,start_date_time=start_date_time,end_date_time=end_date_time)
        created_attendances.append(attendance)
    still_creating = True
    day_count = 1
    if period == 'day':
        days = number
    elif period == 'month':
        days = number * 30
    elif period == 'week':
        days = number * 7
    while still_creating:
        next_shift_day = datetime.datetime.today()+datetime.timedelta(days=day_count)
        if next_shift_day.weekday() == shift.day_num:
            shift_year = next_shift_day.date().year
            shift_month =next_shift_day.date().month
            shift_start_day =next_shift_day.date().day
            start_date_time = datetime.datetime(shift_year,shift_month,shift_start_day,shift_start_hour,shift_start_minute,shift_start_seconds)
            end_date_time =  datetime.datetime(shift_year,shift_month,shift_start_day,shift_end_hour,shift_end_minute,shift_end_seconds)
            attendance,created = Attendance.objects.get_or_create(user=user,shift=shift,start_date_time=start_date_time,end_date_time=end_date_time)
            attendance.save()
            created_attendances.append(attendance)
        if day_count == days:
            still_creating = False
        day_count+=1
    # if send_shedule:
    #     message = loader.render_to_string('admin/shift_email_template.html',{'attendances': created_attendances})
    #     subject = 'Shiftyapp - Shift Schedule'
    #     sendmail([user.email],message,message,subject)
    return created_attendances








def getuser(request,):
    try:
        user = User.objects.get(pk=request.user.pk)
    except Exception:
        user = []
    return user



def authenticateadmin(func):
    def checkadmin(*args, **kwargs):
        if args[1].user.is_superuser:
            return func(*args, **kwargs)
        else:
            return Response({'status':'access_denied','error':'not_admin'})
    return checkadmin


def get_shifts(request):
    shifts=Shift.objects.filter(staff__id=request.user.id)
    return shifts

def get_staff_detail(request):
    try:
        staff=Profile.objects.get(user=request.user,is_staff=True)
    except:
        staff=[]
    
    return staff



class AllUsersView(ListAPIView):
    queryset=User.objects.all()
    serializer_class=UserSerializer
    authentication_classes =[TokenAuthentication,]




class SendSchedule(APIView):

    queryset = Shift.objects.filter(is_deleted=False)
    serializer_class = ShiftSerializer
    authentication_classes =[TokenAuthentication,]

    def post(self,request):
        try:    
            staff = Profile.objects.get(id=request.data['staff_id'])
            user = staff.user
            sendallschedule(user)
            return Response({'success':True},status=status.HTTP_200_OK)        
        except ObjectDoesNotExist:
            return Response({'staff_not_found':True,'pay_load':request.data})

        except Exception:
            return Response({'invalid':True,'pay_load':request.data})


class CreateSendSchedule(APIView):

    queryset = Shift.objects.filter(is_deleted=False)
    serializer_class = ShiftSerializer
    authentication_classes =[TokenAuthentication,]

    def post(self,request):
        try:    
            staff = Profile.objects.get(id=request.data['staff_id'])
            user = staff.user
            shifts = Shift.objects.filter(staffs =user )
            number =int(request.data['number'])
            period =str(request.data['period'])
            future_attendances = []
            for shift in shifts:
                created_attendances = createattendance(user,shift,period=period,number=number,send_shedule=False)
                future_attendances+=created_attendances
            sendallschedule(user)
            # message = loader.render_to_string('admin/shift_email_template.html',{'attendances': future_attendances})
            # subject = 'Shiftyapp - Shift Schedule'
            # sendmail([user.email],message,message,subject)
            return Response({'success':True},status=status.HTTP_200_OK)        
        except ObjectDoesNotExist:
            return Response({'staff_not_found':True,'pay_load':request.data})

        except Exception:
            return Response({'invalid':True,'pay_load':request.data})



class CreateAttendanceView(APIView):

    queryset = Shift.objects.filter(is_deleted=False)
    serializer_class = ShiftSerializer
    authentication_classes =[TokenAuthentication,]
    
    def post(self,request):
        number =int(request.data['number'])
        period =str(request.data['period'])

        try:
            shift = Shift.objects.get(id=request.data['shift_id'])
            staff = Profile.objects.get(id=request.data['staff_id'])
        except ObjectDoesNotExist:
            return Response({'invalid':True,'pay_load':request.data})

        created_attendances = createattendance(staff.user,shift,period =period, number = number)
        sendallschedule(staff.user)
        if staff in shift.staffs.all():
            pass
        else:
            shift.staffs.add(staff.user)

        shift = ShiftSerializer(shift).data
        attendances =AttendanceSerializer(created_attendances,many=True).data
        staff = UserSerializer(staff.user).data

        return Response({'shift':shift,'attendances':attendances,'staff':staff})

class ShiftView(APIView):

    queryset = Shift.objects.filter(is_deleted=False)
    serializer_class = ShiftSerializer
    authentication_classes =[TokenAuthentication,]
    
    def get(self,request):
        shifts = ShiftSerializer(Shift.objects.filter(is_deleted=False).order_by('-day_num'),many=True)
        return Response({'shifts':shifts.data})

    def post(self,request):

        shift=ShiftSerializer(data=request.data)
        if shift.is_valid():
            shift=shift.save()
            return Response({
                'shifts':ShiftSerializer(shift,many=False).data
            })
            
        else:
            return Response({'invalid':True,'pay_load':request.data})


class EditShiftView(APIView):

    queryset = Shift.objects.filter(is_deleted=False)
    serializer_class = ShiftSerializer
    authentication_classes =[TokenAuthentication,]

    def post(self,request):
        shift = Shift.objects.get(id=request.data['shift_id'])
        shift=ShiftSerializer(data=request.data,instance=shift)
        if shift.is_valid():
            shift=shift.save()
            return Response({
                'shifts':ShiftSerializer(shift,many=False).data
            })
            
        else:
            return Response({'invalid':True,'pay_load':request.data})





class StaffView(APIView):

    queryset = Profile.objects.filter(is_deleted=False)
    serializer_class = ProfileSerializer
    authentication_classes =[TokenAuthentication,]
    
    def get(self,request):
        staffs = ProfileSerializer(Profile.objects.all(),many=True).data
        for staff in staffs:
            try:
                user=User.objects.get(id=staff['user'])
                staff['user']=UserSerializer(user,many=False).data
            except ObjectDoesNotExist:
                return Response('no staff yet')
        return Response({'staff':staffs})


class CreateStaffView(APIView):

    queryset = Profile.objects.filter(is_deleted=False)
    serializer_class = ProfileSerializer
    authentication_classes =[TokenAuthentication,]
    
    def post(self,request):

        try:
            user,created = User.objects.get_or_create(first_name=request.data['first_name'], is_staff=True,
            last_name=request.data['last_name'],email=request.data['email'],username=str(request.data['email']).lower())
            secure_str = ''.join((secrets.choice(string.ascii_letters) for i in range(8)))
            user.set_password(secure_str)
            user.save()
            staff,staff_created = Profile.objects.get_or_create(user=user)
            staff.is_temporary_password=True
            staff.save()
            user = UserSerializer(user).data
            staff = ProfileSerializer(staff).data
            return Response({'staff':staff,'user':user,'temporary_password':secure_str})
        except Exception:
            return Response({'invalid_data':True,'pay_load':request.data})


class AssignShiftView(RetrieveAPIView):

    queryset = Shift.objects.filter(is_deleted=False)
    serializer_class = ShiftSerializer
    authentication_classes =[TokenAuthentication,]
    
    def post(self,request):
        try:
            shift = Shift.objects.get(id=request.data['shift_id'])
            user = User.objects.get(id=request.data['user_id'])

            facility=Facility.objects.get(user=user)
            shift.staffs.add(user)
            createattendance(user,shift)
            sendallschedule(user)
                # print( datetime.time(23,59).hour+1  - datetime.datetime.now().time().hour)
            attendance = Attendance.objects.filter(shift = shift,start_date_time__gte = datetime.datetime.now().date())
            attendance = AttendanceSerializer(attendance,many=True)
            shift=ShiftSerializer(shift,many=False)
            return Response({'status':'success',
                            'shift':shift.data,
                            'next_attendances':attendance.data,
                            'user':UserSerializer(user,many=False).data,})
        except Exception:
            return Response({'invalid':True,'pay_load':request.data})


class AccountView(APIView):
    authentication_classes =[TokenAuthentication,]

    @authenticateadmin
    def get(self,request,*args,**kwargs):
        try:
            user=User.objects.get(id=request.GET.get('id'))
            profile=Profile.objects.get(user=user)

            return Response({
                'user':UserSerializer(user,many=False).data,
                # 'profile':ProfileSerializer(profile,many=False).data,
            },status = status.HTTP_200_OK)
        
        except ObjectDoesNotExist:
            return Response(status.HTTP_204_NO_CONTENT)



class AllAttendanceView(APIView):
    authentication_classes =[TokenAuthentication,]

    @authenticateadmin
    def get(self,request,*args,**kwargs):
        allattendance=Attendance.objects.all().order_by('-date_time_added')
        serialized_attendances=AttendanceSerializer(allattendance,many=True).data

        return Response({
            'attendances':serialized_attendances
            })

    
class DeleteAttendanceView(APIView):
    authentication_classes =[TokenAuthentication,]

    @authenticateadmin
    def get(self,request,*args,**kwargs):
        attendances=Attendance.objects.filter(id=request.GET.get('id'))
        count = 0

        for attendance in attendances:
            attendance.delete()
            count +=1
        return Response({'deleted':True,'delete_count':count})



class DeleteAllAttendanceView(APIView):
    authentication_classes =[TokenAuthentication,]

    @authenticateadmin
    def get(self,request,*args,**kwargs):
        attendances=Attendance.objects.filter()
        count = 0
        for attendance in attendances:
            attendance.delete()
            count +=1
        return Response({'deleted':True,'delete_count':count})

    
class DeleteShiftView(APIView):
    authentication_classes =[TokenAuthentication,]

    @authenticateadmin
    def get(self,request,*args,**kwargs):
        shifts = Shift.objects.filter(id=request.GET.get('id'))
        count = 0
        for shift in shifts:
            shift.delete()
            count +=1
        return Response({'deleted':True,'delete_count':count})



class DeleteAllShiftView(APIView):
    authentication_classes =[TokenAuthentication,]

    @authenticateadmin
    def get(self,request,*args,**kwargs):
        shifts=Shift.objects.filter()
        count = 0
        for shift in shifts:
            shift.delete()
            count +=1
        return Response({'deleted':True,'delete_count':count})

    
    
class AttendanceDetailView(APIView):
    authentication_classes =[TokenAuthentication,]

    @authenticateadmin
    def put(self,request,*args,**kwargs):
        serializer=AttendanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer=serializer.save()
            # serializer.instance.user=
            serialized_data=AttendanceSerializer(serializer,many=False).data
            return Response(serialized_data)

    @authenticateadmin
    def get(self,request,*args,**kwargs):
        try:
            attendance=Attendance.objects.get(id=request.GET.get('id'))
            return Response({
            'attendance':AttendanceSerializer(attendance,many=False).data
        })
        except:
            user=User.objects.get(id=request.GET.get('user_id'))
            attendances=Attendance.objects.all()
            upcoming_attendance=list(filter(lambda x: x.start_date_time > datetime.datetime.now() and x.user.id == user.id  ,attendances))
            past_attendance=list(filter(lambda x: x.end_date_time < datetime.datetime.now() and x.user.id == user.id  ,attendances))
            return Response({
            'upcoming_attendance':AttendanceSerializer(upcoming_attendance,many=True).data,
            'past_attendance':AttendanceSerializer(past_attendance,many=True).data
        })

        


class AttendedView(APIView):
    authentication_classes =[TokenAuthentication,]

    @authenticateadmin
    def get(self,request,*args,**kwargs):
        try:
            attendance=Attendance.objects.filter(is_attended=True).order_by('-date_time_added')
            serializer=AttendanceSerializer(attendance,many=True).data
            return Response(serializer)
        
        except ObjectDoesNotExist:
            return Response(status.HTTP_204_NO_CONTENT)


class ReAssignStaffsToShiftView(APIView):
    # permission_classes=[AllowAny]
    authentication_classes =[TokenAuthentication,]
    def post(self,request):
        user_ids=list(request.data.get('user_ids'))
        shift_id=request.data['shift_id']
        # print(user_ids)
        users=[]

        for id in user_ids:
            user=User.objects.get(id=id)
            users.append(user)
        print(users)
        shift=Shift.objects.get(id=shift_id)
        for staff in shift.staffs.all():
            if staff not in users:
                attendances=Attendance.objects.filter(user=staff,shift=shift,start_date_time__gt=datetime.datetime.now())
                for attendance in attendances:
                    attendance.delete()
                shift.staffs.remove(staff)
                
            else:
                pass
        try:
            for user in users:
                shift.staffs.add(user)

                createattendance(user,shift)
                sendallschedule(user)
            return Response({'success':True})
        except Exception:
            return Response({'invalid':True,'pay_load':request.data})

        # shifts=Shift.objects.all()
        # for user in users:
        #     for user_shift in shifts:
        #         if user in user_shift.staffs.all():
        #             user_shift.staffs.remove(user)
        #         else:
        #             pass

        # try:
            
        #     count=0
        #     shift=Shift.objects.get(id=shift_id)
        #     adding=True
        #     while adding:
        #         print(users[count])
        #         if users[count] in shift.staffs.all():
        #             pass
        #         else:
        #             shift.staffs.add(users[count])
        #             createattendance(users[count],shift)
                    
        #         count+=1
        #         if count>=len(users):
        #             adding=False
            
                
                
        

class DeleteAllShiftAttendanceView(APIView):
    # permission_classes=[AllowAny]
    authentication_classes =[TokenAuthentication,]
    def post(self,request):
        try:
            shift=Shift.objects.get(id=request.GET.get('shift_id'))
            attendances=Attendance.objects.filter(shift=shift)
            for attendance in attendances:

                attendance.delete()

            for staff in shift.staffs.all():
                shift.staffs.remove(staff)
            shift.delete()

            return Response('shift deleted sucessfully')
        except ObjectDoesNotExist:
            return Response('shift does not exist')

        


class FacilityView(APIView):
    authentication_classes =[TokenAuthentication,]
    def get(self,request):
        facilities=Facility.objects.all()
        return Response({
            'facilities':FacilitiesSerializer(facilities,many=True).data
        })
    
    def post(self,request):
        serializer=FacilitiesSerializer(data=request.data)
        if serializer.is_valid():
            serializer=serializer.save()
            serialized_data=FacilitiesSerializer(serializer,many=False).data

            return Response({
                'facility':serialized_data
            })
            



        
class AssignStaffToFacilityView(APIView):
    authentication_classes =[TokenAuthentication,]
    def post(self,request):

        user_ids=list(request.data.get('user_ids'))
        facility_id=request.data['shift_id']
        # print(user_ids)
        

        user=[]
        for id in user:
        
            user=User.objects.get(id=id)
        try:
            facility=Facility.objects.get(id=facility_id)
        except ObjectDoesNotExist:
            return Response({'facility_not_found':True})

        if user in facility.user.all():
            return Response('this user is already assinged to this facility')
        
        else:
            facility.user.add(user)
            return Response(f'user added to {facility.name}')
        


        

class RemoveStaffFacilityView(APIView):
    authentication_classes=[TokenAuthentication,]

    @authenticateadmin  
    def post(self,request):
        facility_id=request.GET.get('facility_id')
        user_id=request.GET.get('user_id')

        facility=Facility.objects.get(id=facility_id)
        try:
            user=User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            return Response('this user does not exist')
    
        if user not in facility.user.all():
            return Response('this user is not  assinged to this facility ')

        else:
            facility.user.remove(user)
            return Response({
                    'message':f'user removed from facility {facility.name}',
                    })


# class AttendanceFilterView(APIView):
#     def get(self,request):

#         try:
#             is_attended=request.GET.get('is_attended','') 
#             facility_name=request.GET.get('facility_name','') 
#             day=request.GET.get('day','')
#             email=request.GET.get('email','') 
#             username=request.GET.get('username','') 

#             attendance=Attendance.objects.filter(
                        
#                             Q(facility__name__icontains=facility_name)|
#                             Q(day__icontains=day)|
#                             Q(is_attended__icontains=is_attended)|
#                             Q(user__email__icontains=email)|
#                             Q(user__icontains=username)|
#                             Q(user__username__icontains=username)

            
#                                 )
            
#             return Response({
#                 'attendances':AttendanceSerializer(attendance,many=True).data
#             })
#         except ObjectDoesNotExist:
#             return Response('no related data found')
class AttendanceFilterView(generics.ListAPIView):
    
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields  = ['facility__name', 'day','is_attended','user__email','user','user__username']