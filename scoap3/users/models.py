from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, PositiveSmallIntegerField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from scoap3.users.permissions import assign_permissions

class User(AbstractUser):
    """
    Default custom user model for SCOAP3.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """
    ADMIN = 1
    CURATOR = 2
    USER = 3

    ROLE_CHOICES = (
          (ADMIN, 'Administrator'),
          (CURATOR, 'Curator'),
          (USER, 'User')
      )
    role = PositiveSmallIntegerField(choices=ROLE_CHOICES, blank=True, null=True)
    #: First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore
    last_name = None  # type: ignore

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})

    def assign_the_group(self):
        if self.role[0] == 1:
            assign_permissions()["admin_group"].user_set.add(self)
        elif self.role[0] == 2:
            assign_permissions()["curator_group"].user_set.add(self)
        else:
            assign_permissions()["user_group"].user_set.add(self)
