from django.contrib import auth
from rest_framework import generics, status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import APIView
from .serializers import SignUpSerializer, UserActivationSerializer, LoginSerializer, ResendActivationEmailSerializer, UserProfileSerializer
from rest_framework.response import Response
from .models import User
import jwt
from django.conf import settings
from rest_framework.permissions import AllowAny
from .utils import send_activation_email
from rest_framework.permissions import IsAuthenticated


class RegisterAPIView(generics.GenericAPIView):
    serializer_class = SignUpSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        user = User.objects.get(email=user_data['email'])
        if not user.is_verified:
            send_activation_email(request, user)
        return Response(user_data, status=status.HTTP_201_CREATED)


class ResendActivationEmailAPIView(APIView):
    serializer_class = ResendActivationEmailSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

        if user.is_verified:
            return Response({"error": "User is already verified."}, status=status.HTTP_400_BAD_REQUEST)

        send_activation_email(request, user)
        return Response({"message": "Activation email has been resent successfully."}, status=status.HTTP_200_OK)


class EmailVerificationAPIView(APIView):
    serializer_class = UserActivationSerializer

    def get(self, request):
        token = request.GET.get('token')
        print(token)
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()
            return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        username = request.data['username']
        password = request.data['password']
        user = auth.authenticate(username=username, password=password)
        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_active:
            raise AuthenticationFailed('Account is disabled, contact admin')
        if not user.is_verified:
            raise AuthenticationFailed('Email is not verified, please activate')

        return Response(
            {
                'email': user.email,
                'username': user.username,
                'tokens': user.tokens()
            }, status=status.HTTP_200_OK
        )


class MyPageShowAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            profile = User.objects.get(id=request.user.id)
        except User.DoesNotExist:
            return Response({'data': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        profile_api = UserProfileSerializer(profile)
        content = {"Profile Info": profile_api.data}
        return Response(content, status=status.HTTP_200_OK)
