from django.contrib.auth.models import User

from scoap3.users.permissions import assign_permissions

class CustomUserManager:
    def create_user(self, username, email, password, role=None, **extra_fields):
        user = User.objects.create_user(username, email, password, **extra_fields)
        if role:
            self.assign_the_group(role, user)
        return user

    def assign_the_group(self, role, user):
        if role[0] == 1:
            assign_permissions()["admin_group"].user_set.add(user)
        elif role[0] == 2:
            assign_permissions()["curator_group"].user_set.add(user)
        else:
            assign_permissions()["user_group"].user_set.add(user)
