from rest_framework import serializers
from django.contrib.auth.models import AnonymousUser, User
from rest_framework.authtoken.models import Token
from main.models import *
from knox.models import AuthToken
from django.core.exceptions import ObjectDoesNotExist


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'password','id','first_name','last_name','is_staff','is_superuser')
        extra_kwargs = {'password': {'write_only': True},'is_staff': {'read_only': True},'is_superuser': {'read_only': True}}

    def create(self, validated_data):
        # securities = Security.objects.all()
        # for security in securities:
        #     security.delete()
        # profiles = Profile.objects.all()
        # for profile in profiles:
        #     profile.delete()
        # users = User.objects.all()
        # for user in users:
        #     user.delete()

        user = User.objects.create(email=str(validated_data['email']).lower(),
        username=str(validated_data['email']).lower(),
        # first_name=str(validated_data['first_name']).lower(),last_name=str(validated_data['last_name']).lower()
        )
        user.set_password(validated_data['password'])
        user.save()
        # tokens = AuthToken.objects.filter(user=user)
        # for token in tokens:
        #     token.delete()
        try:
            token = AuthToken.objects.get(user=user)
        except ObjectDoesNotExist:
            token = AuthToken.objects.create(user=user)
        try:
            profile = Profile.objects.get(user=user)
        except ObjectDoesNotExist:
            profile = Profile.objects.create(user=user)
        # user.is_superuser  = True
        # user.save()
        return user, token[1]


class SecuritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Security
        fields = '__all__'

    
class UserTwoFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('password',)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=Profile
        fields='__all__'