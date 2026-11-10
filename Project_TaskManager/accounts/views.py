from django.shortcuts import render
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .serializers import *
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.conf import settings
# Create your views here.
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({"message" : "User created successfully"},status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        # Perform login logic here
        user = authenticate(request,email=serializer.validated_data['email'], password=serializer.validated_data['password'])
        if user is not None:
            # generate JWT token and return it in the response
            tokens = get_tokens_for_user(user)
            res = {
                'message': 'Login successful',
                'username': user.username, 
                'tokens': tokens,
            }
            return Response(res, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def refresh(request):
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        refresh = RefreshToken(refresh_token)
        access_token = refresh.access_token
        return Response({"access": str(access_token)}, status=status.HTTP_200_OK)
    except TokenError:
        return Response({"error": "Token is invalid or expired"},
                        status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout(request):
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        token = RefreshToken(refresh_token)
        if str(token['user_id']) != str(request.user.id):
            return Response({"error": "This token does not belong to you"},
                        status=status.HTTP_403_FORBIDDEN)

        token.blacklist()
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
    except TokenError:
        return Response({"error": "Token is invalid or expired"},
                        status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET' , 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def profile(request):
    user = request.user
    if request.method == 'GET':
        user_profile = ProfileSerializer(user).data
        return Response(user_profile,status=status.HTTP_200_OK)
    elif request.method == 'PATCH':
        serializer = ProfileSerializer(user,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    user = request.user
    serializer = ChangePasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    if not user.check_password(serializer.validated_data['old_password']):
        return Response({"old_password": "Old password is incorrect."},
                        status=status.HTTP_400_BAD_REQUEST)

    user.set_password(serializer.validated_data['new_password'])
    user.save()
    return Response({"message": "Password changed successfully."},
                    status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def password_reset(request):
    serializer = PasswordResetSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data['email']

    user = CustomUser.objects.filter(email=email).first()
    if user:
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        link = f"{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}"
        send_mail(
            "Task Management App - Reset your password",
            f"Hi {user.get_username()},\n\n"
                            f"Use this link to reset your password:\n{link}\n\n"
                            f"uid: {uid}\ntoken: {token}\n\n"
                            "If you didn't request this, ignore this email.",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )

    return Response({"message": "Password reset link sent to your email."}, status=status.HTTP_200_OK)
    

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def password_reset_confirm(request):
    serializer = PasswordResetConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data["user"]
    user.set_password(serializer.validated_data["new_password"])    
    user.save(update_fields=["password"])
    return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)