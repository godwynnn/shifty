from rest_framework import serializers
# from main import models as cmodels
from django.contrib.auth.models import AnonymousUser, User
from rest_framework.authtoken.models import Token
from main.models import *
from knox.models import AuthToken
from django.core.exceptions import ObjectDoesNotExist


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=Profile
        fields='__all__'
        

class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model=Shift
        fields='__all__'
        


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model=Attendance
        fields='__all__'


class FacilitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model=Facility
        fields='__all__'
