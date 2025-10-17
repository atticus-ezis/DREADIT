import pytest
from allauth.account.models import EmailAddress
from rest_framework.test import APIClient

from users.models import User


@pytest.fixture(autouse=True)
def email_backend_setup(settings):
    """Use locmem email backend for testing"""
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def auth_client(user):
    """Returns an authenticated APIClient for the given user."""
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def user():
    return User.objects.create(email="initial@example.com", username="testuser")


@pytest.fixture
def email_address(user):
    """Create a verified EmailAddress for the user"""
    return EmailAddress.objects.create(
        user=user, email=user.email, verified=True, primary=True
    )
