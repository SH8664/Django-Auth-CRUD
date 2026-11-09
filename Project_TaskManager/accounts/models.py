from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
# Create your models here.



class CustomUser(AbstractUser):

    email = models.EmailField(unique=True) 
    phone = models.CharField(max_length=11, blank=True, null=True,
                             validators=[RegexValidator(
                regex='^(011|012|010|015)[0-9]{8}$',
                message='Phone number must be 11 digits and start with 011, 012, 010, or 015.',
                code='invalid_phone'
            )])
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    def __str__(self):
        return self.username    


