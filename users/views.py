import random
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.utils.html import strip_tags
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

# Google Social Auth Imports
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

from .serializers import UserRegistrationSerializer
from .models import User, UserPlatform

# --- 1. REGISTRATION VIEW ---
class RegisterUserView(generics.CreateAPIView):
    """
    Handles creating a new user, generating an OTP, 
    and sending verification emails.
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Save the user to the database
            user = serializer.save()

            # Generate a random 6-digit OTP
            otp_code = str(random.randint(100000, 999999))
            user.otp = otp_code
            user.otp_created_at = timezone.now()
            user.save()

            # Email Drafting with HTML
            try:
                # Creator email + Styling (Greets by display_name if available)
                user_subject = "Action Required: Verify your Dayly Account"
                greeting_name = user.display_name if user.display_name else user.username
                
                # This is the HTML version (Aligned and Styled)
                html_content = f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; border: 1px solid #eee; padding: 20px;">
                    <h2 style="color: #4A90E2; text-align: center;">Welcome to Dayly!</h2>
                    <p>Hi <strong>{greeting_name}</strong>,</p>
                    <p>Thank you for joining our community of creators. To get started and stay consistent, please use the verification code below:</p>
                    <div style="background: #f9f9f9; padding: 20px; text-align: center; font-size: 24px; font-weight: bold; letter-spacing: 5px; color: #333; border-radius: 8px; margin: 20px 0;">
                        {otp_code}
                    </div>
                    <p style="font-size: 12px; color: #777; text-align: center;">This code is valid for 2 minutes. If you didn't request this, please ignore this email.</p>
                    <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
                    <p style="text-align: center; font-style: italic; color: #999;">"Consistency is the playground of excellence."</p>
                </div>
                """
                text_content = strip_tags(html_content) # Fallback for old email apps

                msg = EmailMultiAlternatives(user_subject, text_content, settings.EMAIL_HOST_USER, [user.email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()

                # THE ADMIN NOTIFICATION + STYLING
                admin_subject = f"New Member: {user.username}"
                admin_msg = f"New Creator Alert!\n\nName: {user.username}\nEmail: {user.email}\nProfession: {user.profession}"
                send_mail(admin_subject, admin_msg, settings.EMAIL_HOST_USER, ['benjaminmiracle719@gmail.com'])

            except Exception as e:
                print(f"SMTP Error: {e}")

            return Response({
                "message": "Registration successful! Verification code sent to email.",
                "user": {"username": user.username, "email": user.email}
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- 2. OTP VERIFICATION VIEW ---
class VerifyOTPView(generics.GenericAPIView):
    """
    Checks the 6-digit code sent to the user's email.
    Includes a 2-minute expiration check.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        
        try:
            user = User.objects.get(email=email)

            # Check if user is already verified
            if user.is_verified:
                return Response({"message": "Email is already verified. Please log in."}, status=status.HTTP_200_OK)
            
            # Check if the code has expired (2-minute window)
            if user.otp_created_at < timezone.now() - timedelta(minutes=2):
                return Response({"error": "OTP has expired. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)

            # check if the code matches
            if user.otp == otp:
                user.is_verified = True
                user.otp = None  # Clear OTP after use 
                user.save()
                return Response({"message": "Email verified successfully! You can now log in."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid OTP. Please check your email again."}, status=status.HTTP_400_BAD_REQUEST)
                
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)


# --- 3. RESEND OTP VIEW ---
class ResendOTPView(generics.GenericAPIView):
    """
    Generates and sends a fresh OTP if the user didn't get the first one.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            
            # Prevent spamming if account is already verified
            if user.is_verified:
                return Response({"message": "Account already verified. Please log in."}, status=status.HTTP_400_BAD_REQUEST)

            # Generate new OTP and reset the timer
            new_otp = str(random.randint(100000, 999999))
            user.otp = new_otp
            user.otp_created_at = timezone.now()
            user.save()

            # Email Drafting (Reusing the registration style)
            try:
                subject = "New Verification Code: Dayly"
                greeting_name = user.display_name if user.display_name else user.username
                html_content = f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; border: 1px solid #eee; padding: 20px;">
                    <h2 style="color: #4A90E2; text-align: center;">New Verification Code</h2>
                    <p>Hi <strong>{greeting_name}</strong>,</p>
                    <p>Here is your fresh verification code. Remember, it is only valid for 2 minutes:</p>
                    <div style="background: #f9f9f9; padding: 20px; text-align: center; font-size: 24px; font-weight: bold; letter-spacing: 5px; color: #333; border-radius: 8px; margin: 20px 0;">
                        {new_otp}
                    </div>
                    <p style="text-align: center; font-style: italic; color: #999;">"Progress is built one habit at a time."</p>
                </div>
                """
                msg = EmailMultiAlternatives(subject, strip_tags(html_content), settings.EMAIL_HOST_USER, [user.email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()

                return Response({"message": "A fresh verification code has been sent to your email."}, status=status.HTTP_200_OK)
            except Exception as e:
                print(f"Resend OTP Error: {e}")
                return Response({"error": "Failed to send email. Please try again."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except User.DoesNotExist:
            return Response({"error": "No user found with this email."}, status=status.HTTP_404_NOT_FOUND)


# --- 4. PASSWORD RESET REQUEST VIEW ---
class PasswordResetRequestView(generics.GenericAPIView):
    """
    Sends a 6-digit OTP to the user's email for password recovery.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            
            # Generate Reset OTP (Valid for 10 minutes)
            reset_otp = str(random.randint(100000, 999999))
            user.otp = reset_otp
            user.otp_created_at = timezone.now()
            user.save()

            # Email Drafting with HTML
            try:
                subject = "Reset Your Dayly Password"
                greeting_name = user.display_name if user.display_name else user.username
                
                # HTML Version for Password Reset
                html_content = f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; border: 1px solid #eee; padding: 20px;">
                    <h2 style="color: #E67E22; text-align: center;">Password Reset Request</h2>
                    <p>Hi <strong>{greeting_name}</strong>,</p>
                    <p>We received a request to reset your password for your Dayly account. Use the code below to proceed:</p>
                    <div style="background: #fff3e0; padding: 20px; text-align: center; font-size: 24px; font-weight: bold; color: #e65100; border-radius: 8px; margin: 20px 0; border: 1px solid #ffe0b2;">
                        {reset_otp}
                    </div>
                    <p style="font-size: 12px; color: #777; text-align: center;">This code expires in 10 minutes. If you didn't request this, please secure your account immediately.</p>
                </div>
                """
                msg = EmailMultiAlternatives(subject, strip_tags(html_content), settings.EMAIL_HOST_USER, [user.email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()

                return Response({"message": "Password reset code sent to email."}, status=status.HTTP_200_OK)
            except Exception as e:
                print(f"Password Reset Email Error: {e}")
                return Response({"error": "Failed to send reset email."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except User.DoesNotExist:
            # Security Note: Returning 200 even if user doesn't exist prevents email enumeration
            return Response({"message": "If this email is registered, you will receive a code."}, status=status.HTTP_200_OK)


# --- 5. PASSWORD RESET CONFIRM VIEW ---
class PasswordResetConfirmView(generics.GenericAPIView):
    """
    Verifies the Reset OTP and updates the user's password.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')

        # Check if passwords match
        if new_password != confirm_password:
            return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)

            # Check OTP and Expiration (10-minute window for reset)
            if user.otp == otp and user.otp_created_at > timezone.now() - timedelta(minutes=10):
                # .set_password handles the hashing automatically
                user.set_password(new_password) 
                user.otp = None 
                user.save()
                return Response({"message": "Password reset successful. You can now log in with your new password."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid or expired reset code."}, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)


# --- 6. PLATFORM SETUP VIEW ---
class SetupPlatformsView(generics.GenericAPIView):
    """
    Handles the dashboard popup where users submit their social platforms.
    Updates profile_completed to True once submitted.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        platforms_data = request.data.get('platforms', [])

        if not platforms_data:
            return Response({"error": "Please add at least one platform to proceed."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            for platform in platforms_data:
                UserPlatform.objects.create(
                    user=user,
                    platform_name=platform.get('name'),
                    handle=platform.get('handle'),
                    link=platform.get('link', '')
                )

            user.profile_completed = True
            user.save()

            return Response({
                "message": "Profile setup complete!",
                "profile_completed": user.profile_completed
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": "An error occurred while saving your platforms."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# --- 7. GOOGLE LOGIN VIEW ---
class GoogleLoginView(SocialLoginView):
    """
    Receives an access_token or code from Google 
    and returns Dayly JWT tokens.
    """
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://localhost:5173" # React Frontend URL
    client_class = OAuth2Client 