from rest_framework import serializers
from .models import User

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        style={'input_type': 'password'},
        min_length=8
    )
    confirm_password = serializers.CharField(
        write_only=True, 
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'username', 'display_name', 'email', 'password', 
            'confirm_password', 'profession', 'bio', 'profile_picture'
        ]

    def validate(self, attrs):
        # Password Matching
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        
        # 2. Email Uniqueness Check
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "A user with this email already exists."})
            
        return attrs

    def create(self, validated_data):
        # Remove the extra password field before saving
        validated_data.pop('confirm_password')
        
        # .create_user handles the password hashing automatically
        return User.objects.create_user(**validated_data)