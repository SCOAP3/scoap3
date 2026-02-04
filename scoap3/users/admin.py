from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import TokenProxy

from scoap3.users.forms import UserAdminChangeForm, UserAdminCreationForm

User = get_user_model()


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = ["username", "name", "is_superuser"]
    search_fields = ["name"]


class TokenAdmin(admin.ModelAdmin):
    list_display = ("key", "user", "created")

    def get_queryset(self, request):
        """Limit tokens to those of the logged-in user unless they are a superuser."""
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(user=request.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Restrict the 'user' dropdown in the admin
        form to display only the logged-in user.
        """
        if db_field.name == "user":
            if not request.user.is_superuser:
                kwargs["queryset"] = User.objects.filter(id=request.user.id)
            else:
                kwargs["queryset"] = User.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_fields(self, request, obj=None):
        """
        Customize fields displayed in the form.
        Hide the 'key' field from the form.
        """
        fields = super().get_fields(request, obj)
        if not request.user.is_superuser:
            # Exclude the 'key' field for non-superusers
            return [field for field in fields if field != "key"]
        return fields

    def save_model(self, request, obj, form, change):
        """
        Automatically create a token for the user if it does not already exist.
        """
        if not TokenProxy.objects.filter(user=obj.user).exists():
            TokenProxy.objects.create(user=obj.user)


admin.site.unregister(TokenProxy)
admin.site.register(TokenProxy, TokenAdmin)
