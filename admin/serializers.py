from rest_framework import serializers
from main.models import *
from django.contrib.auth.models import AnonymousUser, User
from rest_framework.authtoken.models import Token
from knox.models import AuthToken


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'password','id','is_staff','is_superuser','first_name','last_name')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
 
        user = User.objects.create(email=str(validated_data['email']).lower(),
        username=str(validated_data['email']).lower()
        )
        user.set_password(validated_data['password'])
        user.save()
        # tokens = AuthToken.objects.filter(user=user)
        # for token in tokens:
        #     token.delete()
        # try:
        #     token = AuthToken.objects.get(user=user)
        # except ObjectDoesNotExist:
        #     token = AuthToken.objects.create(user=user)
        # try:
        #     profile = Profile.objects.get(user=user)
        # except ObjectDoesNotExist:
        #     profile = Profile.objects.create(user=user)
        # # user.is_superuser  = True
        # # user.save()
        # return user, token[1]


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
