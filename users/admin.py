from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    # list_display defines the columns you see in the main table
    list_display = ['username', 'email', 'profession', 'date_joined', 'is_staff']
    
    # This adds custom fields to the user editing page
    fieldsets = UserAdmin.fieldsets + (
        ('Creator Details', {'fields': ('profession', 'bio', 'profile_completed')}),
    )
    
    # This makes the joined date appear in the "Creator Details" section as well
    readonly_fields = ('date_joined', 'last_login')

admin.site.register(User, CustomUserAdmin)