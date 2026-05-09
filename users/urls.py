from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    RegisterUserView, 
    VerifyOTPView,
    PasswordResetRequestView, 
    PasswordResetConfirmView
    )

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify-email/', VerifyOTPView.as_view(), name='verify-email'),

    path('password-reset-request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
]