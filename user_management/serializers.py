from rest_framework import serializers
from .models import Users
from django.core.mail import send_mail
from django.conf import settings
import pyotp

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Users
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }

    
    def create(self, validate_data):
        return Users.objects.create_user(**validate_data)
   