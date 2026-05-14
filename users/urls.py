from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    RegisterUserView,
    VerifyOTPView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    ResendOTPView,
    SetupPlatformsView,
    GoogleLoginView
)

urlpatterns = [
    # Login & JWT
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify-email/', VerifyOTPView.as_view(), name='verify-email'),

    # Password Recovery
    path('password-reset-request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # Resend OTP
    path('resend-otp/', ResendOTPView.as_view(), name='resend-otp'),

    # ONBOARDING
    path('setup-platforms/', SetupPlatformsView.as_view(), name='setup-platforms'),

    # LOGIN WITH GOOGLE
path('google/', GoogleLoginView.as_view(), name='google_login'),
]                                                                               