from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import User

from .models import *


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email')


class MessagesSerializer(ModelSerializer):
    class Meta:
        model = Messages
        fields = ('message',)
