from django.http import JsonResponse

from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny

from core.api.serializers.authentications import (
    UserRegisterSerializer,
    UserLoginSerializer,
)


class UserRegisterView(CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "User registered successfully.",
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(CreateAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            response = JsonResponse(
                {
                    "access": data["access"],
                },
                status=status.HTTP_200_OK,
            )

            response.set_cookie(
                key="refresh",
                value=data["refresh"],
                httponly=True,
                secure=True,
                samesite="Strict",
            )
            return response

        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
