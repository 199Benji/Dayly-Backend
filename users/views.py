import random
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import generics, status
from rest_framework.response import Response
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from rest_framework.permissions import AllowAny

from .serializers import UserRegistrationSerializer
from .models import User

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

            # Attempt to send emails
            # try:
            #     # Email for the User
            #     send_mail(
            #         subject="Welcome to Dayly - Verify your Email",
            #         message=f"Hi {user.username},\n\nYour verification code is: {otp_code}\n\nStay consistent!",
            #         from_email=settings.EMAIL_HOST_USER,
            #         recipient_list=[user.email]
            #     )
                
            #     # Email for the Admin 
            #     send_mail(
            #         subject="New Creator Joined Dayly! ",
            #         message=f"Victory! A new creator has signed up.\n\nUsername: {user.username}\nEmail: {user.email}\nProfession: {user.profession}",
            #         from_email=settings.EMAIL_HOST_USER,
            #         recipient_list=['benjaminmiracle719@gmail.com'] # my notification inbox
            #     )
            # except Exception as e:
            #     raise e


            # Email Drafting with HTML
            try:

                # Creator email + Styling 
                user_subject = "Action Required: Verify your Dayly Account"
                
                # This is the HTML version (Aligned and Styled)
                html_content = f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; border: 1px solid #eee; padding: 20px;">
                    <h2 style="color: #4A90E2; text-align: center;">Welcome to Dayly!</h2>
                    <p>Hi <strong>{user.username}</strong>,</p>
                    <p>Thank you for joining our community of creators. To get started and stay consistent, please use the verification code below:</p>
                    <div style="background: #f9f9f9; padding: 20px; text-align: center; font-size: 24px; font-weight: bold; letter-spacing: 5px; color: #333; border-radius: 8px; margin: 20px 0;">
                        {otp_code}
                    </div>
                    <p style="font-size: 12px; color: #777; text-align: center;">This code is valid for a limited time. If you didn't request this, please ignore this email.</p>
                    <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
                    <p style="text-align: center; font-style: italic; color: #999;">"Consistency is the playground of excellence."</p>
                </div>
                """
                text_content = strip_tags(html_content) # Fallback for old email apps

                msg = EmailMultiAlternatives(user_subject, text_content, settings.EMAIL_HOST_USER, [user.email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()

                #THE ADMIN NOTIFICATION + STYLING
                admin_subject = f"🚀 New Member: {user.username}"
                admin_msg = f"New Creator Alert!\n\nName: {user.username}\nEmail: {user.email}\nProfession: {user.profession}"
                send_mail(admin_subject, admin_msg, settings.EMAIL_HOST_USER, ['benjaminmiracle719@gmail.com'])

            except Exception as e:
                print(f"SMTP Error: {e}")

            return Response({
                "message": "Registration successful! Verification code sent to email.",
                "user": {"username": user.username, "email": user.email}
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#  OTP VERIFICATION VIEW 
class VerifyOTPView(generics.GenericAPIView):
    """
    Checks the 6-digit code sent to the user's email.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        
        try:
            user = User.objects.get(email=email)
            
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