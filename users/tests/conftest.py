import pytest
from allauth.account.models import EmailAddress
from rest_framework.test import APIClient

from users.models import User


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create(email="initial@example.com", username="testuser")


@pytest.fixture
def email_address(user):
    return EmailAddress.objects.create(
        user=user, email=user.email, primary=True, verified=True
    )
