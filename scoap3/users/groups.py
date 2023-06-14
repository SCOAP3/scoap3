from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from scoap3.users.permissions import assign_permissions

User = get_user_model()

@admin.register(User)
class UserGroup():
    groups = assign_permissions()
    admin.site.register(groups['admin_group'])
    admin.site.register(groups['curator_group'])
    admin.site.register(groups['user_group'])

