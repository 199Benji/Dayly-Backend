from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    # This controls what columns you see in the list view
    list_display = ('username', 'email', 'profession', 'is_verified', 'is_staff', 'date_joined')
    
    # This adds a "Filter" sidebar on the right
    list_filter = ('is_verified', 'is_staff', 'profession')
    
    # This allows you to search users by name or email
    search_fields = ('username', 'email')
    
    # This makes the profession and verification status editable directly in the list
    list_editable = ('is_verified', 'profession')

admin.site.register(User, CustomUserAdmin)