import datetime
from email.policy import default
from operator import truediv
from random import choices
# from typing_extensions import Required
from django.db import models
from django.contrib.auth.models import User
# Create your models here.
import datetime




class Security(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING,blank=True,null= True,)
    secret_question = models.CharField(max_length=225,blank=True,default='')
    secret_answer = models.CharField(max_length=225,blank=True,default='')
    previous_email = models.CharField(max_length=225,blank=True,default='')
    last_token = models.CharField(max_length=225,blank=True,default='')
    profile_updated = models.BooleanField(default=False,blank=True)
    suspension_count = models.IntegerField(default=0,blank=True)
    briefly_suspended = models.BooleanField(default=False,blank=True)
    time_suspended = models.DateTimeField(null=True, blank=True)
    time_suspended_timestamp = models.IntegerField(default=0,blank=True)
    locked = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=45, blank=True, default ='')
    email_confirmed = models.BooleanField(default=False)
    two_factor_auth_enabled = models.BooleanField(default=False)
    email_change_request = models.BooleanField(default=False)
    pending_email = models.EmailField(default='',blank=True)
    login_attempt_count = models.IntegerField(default=0)
    class Meta:
        db_table = 'security'


    def save(self,*args, **kwargs):

        if self.suspension_count>2:
            self.briefly_suspended = True
            self.time_suspended =  datetime.datetime.now()
            self.time_suspended_timestamp = datetime.datetime.now().timestamp()
        secret_question=''
        for char in self.secret_question:
            if char ==  '?':
                continue
            else:
                secret_question = secret_question +char
        self.secret_question = secret_question+'?'
        super(Security,self).save()



class Picture(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    image=models.ImageField(null=True,blank=True)

    def __str__(self):
        return f"{self.user.first_name}: PROFILE"

    class Meta:
        db_table='pictures'


class Facility(models.Model):
    name=models.CharField(max_length=225,blank=True)
    location = models.CharField(max_length=225,blank=True)
    facility_id=models.PositiveBigIntegerField(default=0,null=True,blank=True)
    user=models.ManyToManyField(User,blank=True,related_name='users')

    date_added=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}: FACILITY"
    
    
    class Meta:
        db_table='facilities'

        

class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    picture=models.ImageField(null=True,blank=True)
    is_temporary_password=models.BooleanField(default=False,null=True)
    is_deleted = models.BooleanField(default=False)
    facility=models.ForeignKey(Facility,on_delete=models.DO_NOTHING,null=True,blank=True)
    is_updated = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.user.username}: PROFILE"

    class Meta:
        db_table='profiles'

  
    def save(self,*args,**kwargs):
        if self.picture and self.facility:
            self.is_updated = True
        super(Profile,self).save(*args,**kwargs)

class Shift(models.Model):
    staffs=models.ManyToManyField(User,blank=True)
    day=models.CharField(max_length=200,null=True,blank=True)
    start_time=models.TimeField(null=True,blank=True)
    end_time=models.TimeField(null=True,blank=True)
    date_time_added=models.DateTimeField(auto_now=True)
    day_num = models.IntegerField(null=True,blank=True)
    is_deleted = models.BooleanField(default=False)
    period = models.CharField(max_length=200,null=True,blank=True)
    facility=models.ForeignKey(Facility,on_delete=models.DO_NOTHING,null=True,blank=True)

    def delete(self,*args,**kwargs):
        self.is_deleted = True
        super(Shift,self).save(*args,**kwargs)    
    

    class Meta:
        db_table='shifts'

    
    def save(self,*args,**kwargs):
        days = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
        self.day_num = days.index(self.day)
        # if self.start_time.hour >= 12 and self.end_time <=15:
        #     self.period = 'Afternoon'
        # elif self.start_time.hour < 12 :
        #     self.period = 'Morning'
        # if self.start_time.hour >= 21 :
        #     self.period = 'Afternoon'
        super(Shift,self).save(*args,**kwargs)

    def __str__(self):
        return f"{self.day}"

class File(models.Model):
    file = models.FileField()


class Attendance(models.Model):
    user=models.ForeignKey(User,on_delete=models.DO_NOTHING,null=True,blank=True)
    shift=models.ForeignKey(Shift,on_delete=models.DO_NOTHING,null=True,blank=True)
    facility=models.ForeignKey(Facility,on_delete=models.DO_NOTHING,null=True,blank=True)
    day = models.CharField(max_length=50,default=' ',blank=True)
    is_attended=models.BooleanField(default=False,null=True,blank=True)
    files= models.ManyToManyField(File,blank=True,default= '')
    clock_in_time=models.TimeField(null=True,blank=True, default='00:00')
    clock_out_time=models.TimeField(null=True,blank=True, default='00:00')
    start_date_time=models.DateTimeField(null=True,blank=True)
    end_date_time=models.DateTimeField(null=True,blank=True)
    date_time_added=models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    
    # def delete(self,*args,**kwargs):
    #     self.is_deleted = True
    #     super(Attendance,self).save(*args,**kwargs)    
    
    

    class Meta:
        db_table='attendances'

    def save(self,*args,**kwargs):
        self.day = self.shift.day
        self.facility = self.shift.facility
        super(Attendance,self).save(*args,**kwargs)
    
    def __str__(self):
        return f"{self.user.username}-{self.shift.day}: ATTENDANCE"
