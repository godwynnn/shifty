from random import random
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from rest_framework.views import APIView,status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from main.models import *
from .serializers import *
from django.contrib.auth.models import AnonymousUser, User
from rest_framework.authtoken.models import Token
from rest_framework import generics,viewsets,status
from rest_framework.pagination import PageNumberPagination,LimitOffsetPagination
from django.contrib.auth import login, authenticate,logout
from shiftyapp.permissions import Check_API_KEY_Auth
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated,AllowAny
from shiftyapp.email_sender import sendmail
from django.views.decorators.csrf import csrf_exempt
from knox.auth import TokenAuthentication 
from knox.models import AuthToken
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from django.conf import settings




def getuser(request,):
    try:
        user = User.objects.get(pk=request.user.pk)
    except Exception:
        user = []
    return user


class RequestChangePasswordView(APIView):

    queryset = Security.objects.all()
    serializer_class = SecuritySerializer
    authentication_classes = ()
    permission_classes = ()

    def post(self,request):
        email =request.data.copy().get('email')
        try:
            user= User.objects.get(email=email)
            try:
                security = Security.objects.get(user=user)
                security_serializer_class = SecuritySerializer(security)
                db_token = str(round(9999999 * random()))[0:6]
                security.last_token= make_password(db_token)
                security.save()
                data = {'status':'success','6_digits':db_token}
                
            except ObjectDoesNotExist:
                security = Security.objects.create(user=user)
                security.refresh_from_db()
                db_token = str(round(9999999 * random()))[0:6]
                print(db_token)
                security.last_token= make_password(db_token)
                security.save() 
                data = {'status':'success','6_digits':db_token}
            message = """<p>Hi there!, <br> <br>You have requested to change your password. <br> <br>
            <b>Use """ + db_token + """ as your verification code</b></p>"""
            subject = 'Password Change Request'
            sendmail([user.email],message,message,subject)
            return Response(data,status=status.HTTP_202_ACCEPTED)
        except ObjectDoesNotExist:
            return Response({'user':False},status=status.HTTP_404_NOT_FOUND)


class VerifyPasswordRequestCode(APIView):

    queryset = Security.objects.all()
    serializer_class = SecuritySerializer
    authentication_classes = ()
    permission_classes = ()

    def post(self, request):
        verification_code = request.data.copy().get('code')
        email = request.data.copy().get('email')
        # '154914'
        try:
            user= User.objects.get(email=email)
            try:
                security = Security.objects.get(user=user)
                if check_password(verification_code,security.last_token):
                    user.set_password(request.data.get('password'))
                    user.save()
                    data = {'success':True}
                    security.last_token = ''
                    security.save()
                else:
                    data= {'invalid_verification_code':True}
                return Response(data,status=status.HTTP_202_ACCEPTED)

            except ObjectDoesNotExist:
                return Response({'invalid_request':True},status=status.HTTP_404_NOT_FOUND)


        except ObjectDoesNotExist:
            return Response({'user':False},status=status.HTTP_404_NOT_FOUND)


class CheckEmail(APIView):
    permission_classes = ()
    serializer_class = UserSerializer
    def post(self,request,*args,**kwargs):
        try:
            email=request.data.get('email').lower()        
            try:
                user=User.objects.get(email=email)
                return Response({
                                    'user_exist':True,
                                    })
            except ObjectDoesNotExist:
                return Response({
                    'user_exist':False,
                    })  
   
        except Exception:
                return Response({
                    'status':'Failed',
                    'data':request.data
                    })                           
        
class LoginView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = (BasicAuthentication,)
    serializer_class = UserSerializer
    # def get(self,request):
    #     return Response(status=status.HTTP_202_ACCEPTED)

    def post(self, request,):
        logout(request)
        email = request.data.get("email")
        password = request.data.get("password")
        
        try:
            user = User.objects.get(email=email)
            if check_password(password,user.password):
                serialized_data = UserSerializer(user)
                token=AuthToken.objects.create(user=user)[1]
                try:
                    profile_updated = Profile.objects.get(user = user).is_updated
                except ObjectDoesNotExist:
                    profile_updated = False
                return Response({'token':token,'user':serialized_data.data,'profile_updated':profile_updated},status=status.HTTP_202_ACCEPTED)
            else:
                return Response({"wrong_credentials": True}, status=status.HTTP_400_BAD_REQUEST)

        except ObjectDoesNotExist:

            return Response({"user_does_not_exist": True}, status=status.HTTP_400_BAD_REQUEST)





class ConfirmEmail(APIView):

    queryset = Security.objects.all()
    serializer_class = SecuritySerializer
    authentication_classes = ()
    permission_classes = ()

    # def get(self,request):
    #     email =request.GET.get('email')
    #     try:
    #         user= User.objects.get(email=email)
    #         try:
    #             security = Security.objects.get(user=user)
    #             security_serializer_class = SecuritySerializer(security)
    #             db_token = str(round(9999999 * random()))[0:6]
    #             print(db_token)
    #             security.last_token= make_password(db_token)
    #             security.save()
    #             data = {'status':'success'}
                
    #         except ObjectDoesNotExist:
    #             security = Security.objects.create(user=user)
    #             security.refresh_from_db()
    #             db_token = str(round(9999999 * random()))[0:6]
    #             print(db_token)
    #             security.last_token= make_password(db_token)
    #             security.save()
    #             security_serializer_class = SecuritySerializer(security)
    #             data = {'status':'success'}
    #         # message = '<p><b>Use ' + db_token + ' as your verification code</b></p>'
    #         # subject = 'Password Change Request'
    #         # sendmail([user.email],message,message,subject)
    #         return Response(data,status=status.HTTP_202_ACCEPTED)
    #     except ObjectDoesNotExist:
    #         return Response({'user':False},status=status.HTTP_404_NOT_FOUND)


    def post(self, request):
        verification_code = request.data.get('last_token')
        email = request.data.get('email')
        # '154914'
        try:
            user= User.objects.get(email=email)
            try:
                security = Security.objects.get(user=user)
                if check_password(verification_code,security.last_token):
                    user.set_password(request.data.get('secret_answer'))
                    user.save()
                    data = {'success':True}
                    security.last_toke = ''
                    security.save()
                    user.is_active = True
                    security.email_confirmed = True
                    user.save()
                    security.save()
                    login(request,user)
                else:
                    data= {'invalid_verification_code':True}
                return Response(data,status=status.HTTP_202_ACCEPTED)

            except ObjectDoesNotExist:
                return Response({'invalid_request':True},status=status.HTTP_404_NOT_FOUND)


        except ObjectDoesNotExist:
            return Response({'user':False},status=status.HTTP_404_NOT_FOUND)


class AllUserView(APIView):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = ()
    # authentication_classes =[TokenAuthentication,]

    def get(self,request):

        user = User.objects.all()
        user = UserSerializer(user,many = True )
        if len(user.data) > 0:
            return Response(user.data,status=status.HTTP_200_OK)

        return Response({'no_user':True},status=status.HTTP_400_BAD_REQUEST)


class Home(APIView):

    serializer_class = UserSerializer
    permission_classes = ()
    # authentication_classes =[TokenAuthentication,]

    def get(self,request):

        return Response({'API root':True},status=status.HTTP_202_ACCEPTED)

class DeleteUserView(APIView):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = ()

    def get(self,request):
        try:
            user = User.objects.get(id = str(request.GET.get('id')))
            # securities = Security.objects.filter(user=user)
            # for security in securities:
            #     security.delete()
            # profiles = Profile.objects.filter(user=user)
            # for profile in profiles:
            #     profile.delete()
            tokens = AuthToken.objects.filter(user=user)
            for token in tokens:
                token.delete()

            user.delete()            
            return Response({'deleted':True},status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({'error':'User does not exist'},status=status.HTTP_400_BAD_REQUEST)


class UserView(APIView):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = ()
    authentication_classes =[TokenAuthentication,]

    def get(self,request):

        user = getuser(request)
        user = UserSerializer(user)
        if len(user.data) > 0:
            return Response(user.data,status=status.HTTP_200_OK)

        return Response({'invalid_token':True},status=status.HTTP_400_BAD_REQUEST)



class CreateUserView(APIView):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def post(self,request):
        try:
            user = UserSerializer(User.objects.get(email = str(request.data['email']).lower()))
            return Response({'email_already_exist':True},status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            
            if request.data.get('admin')=='1':
                serializer = UserSerializer(data=request.data)
                if serializer.is_valid():
                    data = serializer.save()
                    user = data[0]
                    # print(user)
                    user.is_superuser = True
                    user.save()
                    serialized_data = UserSerializer(user)
                    # login(request,user)
                    
                    token= data[1]
                    # if len(token) > 0:
                    #     token = token[0]
                    # else:
                    #     token=AuthToken.objects.create(user=user)
                    #     token.refresh_from_db()

                    security = Security.objects.get_or_create(user=user)[0]
                    security_serializer_class = SecuritySerializer(security)
                    db_token = str(round(9999999 * random()))[0:6]
                    security.last_token= make_password(db_token)
                    security.save()
                    data = {'status':'success','6_digits':db_token,'token':token,'user':serialized_data.data}

                    message = """<p>Hi there!, <br> <br>Thank you for joing <b>Shifty</>. <br> <br>
                    <b>Use """ + db_token + """ as your activation code</b></p>"""
                    subject = 'Shifty - Account creation'
                    sendmail([user.email],message,message,subject)
                    return Response(data,status=status.HTTP_202_ACCEPTED)
                else:
                    return Response({'error':'invalid data'},status=status.HTTP_400_BAD_REQUEST)

            
            elif request.data.get('staff')=='1' :
                serializer = UserSerializer(data=request.data)
                if serializer.is_valid():
                    data = serializer.save()
                    user = data[0]
                    # print(user)
                    user.is_staff = True
                    user.save()
                    serialized_data = UserSerializer(user)
                    # login(request,user)
                    
                    token= data[1]
                    # if len(token) > 0:
                    #     token = token[0]
                    # else:
                    #     token=AuthToken.objects.create(user=user)
                    #     token.refresh_from_db()

                    security = Security.objects.get_or_create(user=user)[0]
                    security_serializer_class = SecuritySerializer(security)
                    db_token = str(round(9999999 * random()))[0:6]
                    security.last_token= make_password(db_token)
                    security.save()
                    data = {'status':'success','6_digits':db_token,'token':token,'user':serialized_data.data}

                    message = """<p>Hi there!, <br> <br>Thank you for joing <b>Shifty</>. <br> <br>
                    <b>Use """ + db_token + """ as your activation code</b></p>"""
                    subject = 'Shifty - Account creation'
                    sendmail([user.email],message,message,subject)
                    return Response(data,status=status.HTTP_202_ACCEPTED)
                else:
                    return Response({'error':'invalid data'},status=status.HTTP_400_BAD_REQUEST)



def LogoutView(request):
    logout(request)
    return Response({
        'message':'successfully logout',
        'status':True
    })


