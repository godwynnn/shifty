from email.policy import HTTP
import profile
from re import I, S
from urllib import response
from main.models import *
from django.shortcuts import render
from admin.serializers import AttendanceSerializer, NotesSerializer, ProfileSerializer, ShiftSerializer,UserSerializer
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView,RetrieveAPIView,ListCreateAPIView
from rest_framework.response import Response
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
# Create your views here.


def authenticateadmin(func):
    def checkadmin(*args, **kwargs):
        if args[1].user.is_superuser:
            return func(*args, **kwargs)
        else:
            return Response({'status':'access_denied','error':'not_admin'})
    return checkadmin


def get_shifts(request):
    try:
        shifts=Shift.objects.get(user=request.user)
    except:
        shifts=[]
    
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



class AdminDashBoardView(APIView):
    queryset = Notes.objects.all()
    serializer_class = NotesSerializer
    authentication_classes =[TokenAuthentication,]

    @authenticateadmin
    def get(self,request,*args,**kwargs):
        # recent_notes=self.queryset.order_by('-date_time_added')[:5]
        # notes=Notes.objects.all()
        recent_notes=list(self.queryset[:5])
        recent_notes.sort(key=lambda x: x.date_time_added,reverse=True)
        shifts=get_shifts(request)
        staff=get_staff_detail(request)

        return Response({
            'recent_notes':NotesSerializer(recent_notes,many=True).data,
            'shifts':ShiftSerializer(Shift.objects.all(),many=True).data,
            'staff':ProfileSerializer(Profile.objects.all(),many=True).data,
            'user':UserSerializer(User.objects.all(),many=True).data
        })





class NotesView(ListAPIView):
    queryset=Notes.objects.all()
    serializer_class=NotesSerializer
    authentication_classes =[TokenAuthentication,]
    
    
    # @authenticateadmin
    # def perform_create(self,serializer):
    #     serializer.save(user=self.request.user)
    

class NotesDetailView(RetrieveAPIView):
    queryset=Notes.objects.all()
    serializer_class=NotesSerializer
    authentication_classes =[TokenAuthentication,]




class ShiftView(RetrieveAPIView):

    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
    authentication_classes =[TokenAuthentication,]
    


class AccountView(APIView):
    authentication_classes =[TokenAuthentication,]

    @authenticateadmin
    def get(self,request,id,*args,**kwargs):
        try:
            user=User.objects.get(id=id)
            profile=Profile.objects.get(user=user)

            return Response({
                'user':UserSerializer(user,many=False).data,
                'profile':ProfileSerializer(profile,many=False).data,
                'status':status.HTTP_OK
            })
        
        except ObjectDoesNotExist:
            return Response(status.HTTP_204_NO_CONTENT)



class AttendanceView(APIView):
    authentication_classes =[TokenAuthentication,]

    @authenticateadmin
    def get(self,request,*args,**kwargs):
        attendance=Attendance.objects.all().order_by('-date_time_added')
        serialized_data=AttendanceSerializer(attendance,many=True)

        return Response(serialized_data.data)

    

class AttendanceDetailView(APIView):
    authentication_classes =[TokenAuthentication,]

    @authenticateadmin
    def put(self,request,id,*args,**kwargs):
        serializer=AttendanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer=serializer.save()
            # serializer.instance.user=
            serialized_data=AttendanceSerializer(serializer,many=False).data
            return Response(serialized_data)

    @authenticateadmin
    def get(self,request,id,*args,**kwargs):
        attendance=Attendance.objects.get(id=id)

        return Response({
            'attendance':AttendanceSerializer(attendance,many=False).data
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



class CreateShiftView(APIView):
    def post(self,request,*args,**kwargs):
        shift_days=['Monday','Tuesday','Wednesday','Thursday','Saturday','Sunday']
        
        user_id=request.data['userId']
        day=request.data.get('day').capitalize()
        date=request.data.get('date')
        time=request.data.get('time')


        try:
            user=User.objects.get(id=user_id)

        except ObjectDoesNotExist:
            user=None

        day_list=[]
        count=0
        # print(count)
        for i in range(shift_days.index(day),len(shift_days),2):
            if i>=count :
                day_list.append(shift_days[i])
            
        for day in day_list:
            shift=Shift.objects.create(
                user=user,
                days=day,
                
            )

        

        
            pass