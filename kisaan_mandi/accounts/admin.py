from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'state', 'district', 'is_verified', 'date_joined']
    list_filter = ['role', 'is_verified', 'state']
    fieldsets = UserAdmin.fieldsets + (
        ('Kisaan Mandi', {'fields': ('role', 'phone', 'address', 'state', 'district', 'profile_pic', 'is_verified')}),
    )
