from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework import permissions

from .serializers import SignUpSerializer
from .models import User

class CreateUserAPIView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny, )
    serializer_class = SignUpSerializer