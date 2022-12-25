from email.policy import HTTP
import imp
from inspect import classify_class_attrs
from logging import exception
import profile
from re import L
from time import timezone
from urllib import response
from urllib.parse import parse_qsl
from admin.views import AttendedView
from main.models import *
from django.shortcuts import render
from admin.serializers import AttendanceSerializer, ProfileSerializer, ShiftSerializer,UserSerializer,FacilitiesSerializer
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView,RetrieveAPIView,ListCreateAPIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from main.models import *
from main.models import Attendance
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
import datetime
import pytz
from django.utils import timezone
from django.core.mail import send_mass_mail
from copy import deepcopy

# Create your views here.

utc=pytz.UTC
now=datetime.datetime.now()


def updateuser(user,request):
    try:
        user.first_name = request.data['first_name']
        user.save()
    except Exception:
        pass
    try:
        user.last_name = request.data['last_name']
        user.save()
    except Exception:
        pass
    return None


def ObjectList(request):
    list_items={}

    try:
        user=User.objects.get(id=request.user.id)
        list_items['user']=UserSerializer(user,many=False).data
    except ObjectDoesNotExist:
        pass

    try:
        shifts=Shift.objects.filter(user=request.user,is_deleted=False).values
        list_items['shifts']=ShiftSerializer(shifts,many=True).data
    except:
        pass

    try:
        profile=Profile.objects.get(user=request.user)
        list_items['profile']=ProfileSerializer(profile,many=False).data
    except:
        pass

    try:
        attendance_list=Attendance.objects.filter(user=request.user).values
        list_items['attendance_list']=AttendanceSerializer(attendance_list,many=True).data
    except:
        pass

    return list_items



class StaffDashBoardView(APIView):

    authentication_classes =[TokenAuthentication,]
    def get(self,request,*args,**kwargs):
        items=ObjectList(request)
        # user=items['user']
    

        try:

            
            
            next_shift=Shift.objects.filter(staffs=request.user,start_time__gt=datetime.datetime.now().time())

            shifts=Shift.objects.filter(staffs=request.user,is_deleted=False)
            current_shift=filter(lambda x: x.start_time < now.time() < x.end_time ,shifts)

            try:
                attendance_list=Attendance.objects.filter(user=request.user,is_attended=False)
            except ObjectDoesNotExist:
                attendance_list=''


            missed_shift=[]
            for attendance in attendance_list:
                if attendance.shift.start_time < now.time():
                    missed_shift.append(attendance.shift)
                    

            # print(missed_shift)


            # profile=Profile.objects.get(user=request.user)
            # user=User.objects.get(id=request.user.id)

         
            items['next_shift']=ShiftSerializer(next_shift,many=True).data
            items['current_shift']=ShiftSerializer(current_shift,many=True).data
        
            items['missed_shift']=ShiftSerializer(missed_shift,many=True).data
           


            
            return Response(items)
        except ObjectDoesNotExist:
            return Response(status.HTTP_204_NO_CONTENT)


class AttendanceView(APIView):
    authentication_classes =[TokenAuthentication,]
    def get(self,*args,**kwargs):
        try:
            attendance_list=Attendance.objects.filter(user=self.request.user,is_attended=False)
            
        except ObjectDoesNotExist:
                attendance_list=[]
        shifts=Shift.objects.filter(staffs=self.request.user,is_deleted=False)
        next_shift=Shift.objects.filter(staffs=self.request.user,start_time__gt=datetime.datetime.now(),is_deleted=False)


        missed_shift=filter(lambda x: x.shift.start_time <now.time() and x.is_attended==False ,attendance_list)
        current_shift=filter(lambda x: x.start_time < now.time() < x.end_time ,shifts)

        return Response({
            'current_shift':ShiftSerializer(current_shift,many=True).data,
            'missed_shift':ShiftSerializer(missed_shift,many=True).data,
            'next_shift':ShiftSerializer(next_shift,many=True).data
        })


class PastShiftsView(APIView):
    authentication_classes =[TokenAuthentication,]
    def get(self,request,*args,**kwargs):
        shifts=Shift.objects.filter(staffs=self.request.user,is_deleted=False)

        past_shift=filter(lambda x: x.end_time < now.time(),shifts)
        return Response({
            'past_shift':ShiftSerializer(past_shift,many=True).data
        
        })




class ShiftsDetailView(RetrieveAPIView):
    queryset=Shift.objects.all()
    serializer_class=ShiftSerializer
    authentication_classes =[TokenAuthentication,]




class AccountView(APIView):
    
    serializer_class=ProfileSerializer
    authentication_classes =[TokenAuthentication,]
    def get(self,request,*args,**kwargs):
        profile=Profile.objects.get(user=request.user)
        user=User.objects.get(id=request.user.id)

        return Response({
            'profile':ProfileSerializer(profile,many=False).data,
             
            'user':UserSerializer(user,many=False).data
        })




class TakeStartAttendanceView(APIView):
    authentication_classes =[TokenAuthentication,]
    def put(self,request):

        time_in=datetime.datetime.now().time()
        attendance_id=request.GET.get('attendance_id')
        try:
            # attendance=Attendance.objects.filter(user=request.user,shift__day_num=datetime.datetime.now().weekday()).first()
            attendance=Attendance.objects.get(user=request.user,id=attendance_id)


        except ObjectDoesNotExist:
            return Response('this user have now shift assinged for today')
        

        attendance.clock_in_time=time_in
        attendance.save()

        return Response({
            'attendance': AttendanceSerializer(attendance, many=False).data,
            'time_in': True
        })


class TakeEndAttendanceView(APIView):
    authentication_classes =[TokenAuthentication,]
    def put(self,request):

        time_out=datetime.datetime.now().time()
        attendance_id=request.GET.get('attendance_id')
        try:
            # attendance=Attendance.objects.filter(user=request.user,shift__day_num=datetime.datetime.now().weekday()).first()
            attendance=Attendance.objects.filter(user=request.user,id=attendance_id).first()

            # if attendance.start_date_time <= datetime.datetime.today()<=attendance.end_date_time:
            #     pass


        except ObjectDoesNotExist:
            return Response('this user have now shift assinged for today')
        

        attendance.clock_out_time=time_out
        attendance.is_attended=True
        attendance.save()

        return Response({
            'attendance': AttendanceSerializer(attendance, many=False).data,
            'time_out': True
        })



class UpdateProfileView(APIView):
    queryset = Profile.objects.filter(is_deleted=False)
    serializer_class = ProfileSerializer
    authentication_classes =[TokenAuthentication,]

    def post(self,request):

        user = request.user
        try:
            profile = Profile.objects.get(user=user)
            data = deepcopy(request.data)
            try:
                del data['first_name']
                del data['last_name']
                del data['email']
            except Exception:
                pass
            serializer_class = ProfileSerializer(instance=profile, data=data,partial=True)
            updateuser(user,request)
        except ObjectDoesNotExist:
            serializer_class = ProfileSerializer(data=data)
            updateuser(user,request)

        if serializer_class.is_valid():
            serializer_class.save()
            profile = serializer_class.instance
            data = {}
            data['profile']=  ProfileSerializer(profile).data
            data['user'] = UserSerializer(user).data
            return Response(data,status=status.HTTP_200_OK)
        else:
            return Response({'invalid_data':True,'pay_load':request.data},status=status.HTTP_400_BAD_REQUEST)



class FacilitiesView(APIView):
    authentication_classes =[TokenAuthentication,]
    def get(self,request):
        facilities=Facility.objects.all()
        return Response({
            'facilities':FacilitiesSerializer(facilities,many=True).data
        })