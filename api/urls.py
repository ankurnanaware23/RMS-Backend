from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    OTPVerificationAPIView,
    UserProfileView,
)

from api import views as api_views

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('tables.urls')),
    path('', include('menu.urls')),
    path('', include('orders.urls')),

    path('user/token/', api_views.MyTokenObtainPairView.as_view(), name='Token Obtain Pair View'),
    path('user/token/refresh/', api_views.MyTokenRefreshView.as_view(), name="Token Refresh View"),
    path('user/register/', api_views.RegisterView.as_view(), name="User Registration View"),
    path('user/password-reset/', api_views.PasswordResetEmailVerifyAPIView.as_view(), name="Password Reset View"),
    path('user/otp-verification/', OTPVerificationAPIView.as_view(), name="OTP Verification View"),
    path('user/password-change/', api_views.PasswordChangeAPIView.as_view(), name="User Registration View"),
    path('user/profile/', UserProfileView.as_view(), name='user-profile'),
]
