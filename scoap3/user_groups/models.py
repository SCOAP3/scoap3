from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import models

User = get_user_model()


class UserGroups(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.group.name}"
