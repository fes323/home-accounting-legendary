from users.models.user import User
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _


class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'total_balance')
    search_fields = ('username', 'email', 'first_name', 'last_name')

    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'total_balance')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )

    ordering = ('username',)

    actions = ['send_password_reset_email']

    def send_password_reset_email(self, request, queryset):
        for user in queryset:
            user.send_password_reset_email()

        self.message_user(request, _("Password reset email sent to selected users."))

    send_password_reset_email.short_description = _("Send password reset email to selected users")

admin.site.register(User, UserAdmin)