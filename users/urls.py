from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
# Note: VerifyOTPView comes from YOUR views, not simplejwt
from .views import RegisterUserView, VerifyOTPView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify-email/', VerifyOTPView.as_view(), name='verify-email'),
]