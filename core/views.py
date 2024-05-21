from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.views import APIView

from core.serializers import UserSerializer


class GetAllUsersView(generics.ListAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer


