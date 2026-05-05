from rest_framework import viewsets, status, generics
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import requests
import pytz

from api import serializers as api_serializers
from userauth.models import User
from .serializers import UserSerializer, UserProfileSerializer


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = api_serializers.MyTokenObtainPairSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class()
        return Response(serializer.data, status=status.HTTP_200_OK)


class MyTokenRefreshView(TokenRefreshView):
    serializer_class = api_serializers.MyTokenRefreshSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = api_serializers.RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = api_serializers.MyTokenObtainPairSerializer.get_token(user)
        user.refresh_token = str(refresh)
        user.save(update_fields=["refresh_token"])

        return Response(
            {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )


def generate_otp(length):
    import random

    otp = "".join([str(random.randint(0, 9)) for _ in range(length)])
    return otp


def send_transactional_email(subject, to_email, text_body, html_body):
    if settings.BREVO_API_KEY:
        response = requests.post(
            settings.BREVO_API_URL,
            headers={
                "accept": "application/json",
                "api-key": settings.BREVO_API_KEY,
                "Content-Type": "application/json",
            },
            json={
                "sender": {
                    "name": settings.BREVO_FROM_NAME,
                    "email": settings.BREVO_FROM_EMAIL,
                },
                "to": [{"email": to_email}],
                "subject": subject,
                "htmlContent": html_body,
                "textContent": text_body,
            },
            timeout=settings.EMAIL_TIMEOUT,
        )
        response.raise_for_status()
        return

    msg = EmailMultiAlternatives(
        subject=subject,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
        body=text_body
    )
    msg.attach_alternative(html_body, "text/html")
    msg.send(fail_silently=False)


class PasswordResetEmailVerifyAPIView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = api_serializers.UserSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()

        if not user:
            raise NotFound("User with this email does not exist")

        user.otp = generate_otp(6)
        user.save()

        context = {
            'otp': user.otp,
            'user': user,
        }

        subject = 'DineEase Password Reset Request'
        text_body = render_to_string('email/password_reset.txt', context)
        html_body = render_to_string('email/password_reset.html', context)

        try:
            send_transactional_email(subject, user.email, text_body, html_body)
        except Exception:
            return Response(
                {"detail": "Unable to send email right now. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"detail": "Password reset OTP has been sent to your email."},
            status=status.HTTP_200_OK
        )

class OTPVerificationAPIView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = api_serializers.UserSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        otp = request.data.get('otp')

        user = User.objects.filter(email=email, otp=otp).first()

        if user:
            return Response({"detail": "OTP verification successful."}, status=status.HTTP_200_OK)
        return Response({"detail": "Invalid OTP or email."}, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = api_serializers.UserSerializer

    def create(self, request, *args, **kwargs):
        email = request.data.get('email')
        otp = request.data.get('otp')
        password = request.data.get('password')

        user = User.objects.filter(email=email, otp=otp).first()
        if user:
            user.set_password(password)
            user.otp = ""
            user.save()

            now_utc = timezone.now()
            ist = pytz.timezone('Asia/Kolkata')
            now_ist = now_utc.astimezone(ist)
            context = {
                'user': user,
                'timestamp': now_ist.strftime('%B %d, %Y at %I:%M %p %Z')
            }

            subject = 'Your DineEase Password Has Been Changed'
            text_body = render_to_string('email/password_changed.txt', context)
            html_body = render_to_string('email/password_changed.html', context)

            try:
                send_transactional_email(subject, user.email, text_body, html_body)
            except Exception:
                return Response(
                    {"detail": "Unable to send email right now. Please try again later."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )


            return Response({"detail": "Password reset successful."}, status=status.HTTP_201_CREATED)

        return Response({"detail": "Invalid OTP or user."}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_context(self):
        return {'request': self.request}


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
