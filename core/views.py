from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.views import APIView

from core.serializers import UserSerializer


class GetAllUsersView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


