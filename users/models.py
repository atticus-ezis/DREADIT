from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class RegistrationMethod(models.TextChoices):
        LOCAL = "local"
        GOOGLE = "google"
        FACEBOOK = "facebook"
        TWITTER = "twitter"

    bio = models.TextField(blank=True)
    registration_method = models.CharField(
        max_length=20,
        choices=RegistrationMethod.choices,
        default=RegistrationMethod.LOCAL,
    )

    def __str__(self):
        return self.username
