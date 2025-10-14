import re

import pytest
from allauth.account.forms import default_token_generator
from allauth.account.utils import user_pk_to_url_str
from django.core import mail
from django.urls import reverse
from rest_framework import status

from users.models import User


@pytest.mark.django_db
class TestUserRegistration:
    """Test user registration endpoints"""

    def test_user_registration_success(self, client):
        """Test successful user registration"""
        url = reverse("rest_register")
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "TestPass123!",
            "password2": "TestPass123!",
        }
        response = client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username="newuser").exists()

        # Check that email was sent
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to[0] == "newuser@example.com"


@pytest.mark.django_db
class TestUserLogin:
    """Test user login/logout endpoints"""

    def test_login_success(self, client, user):
        """Test successful login"""
        user.set_password("TestPass123!")
        user.save()

        url = reverse("rest_login")
        data = {
            "username": user.username,
            "password": "TestPass123!",
        }
        response = client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data or "access_token" in response.data
        assert "refresh" in response.data or "refresh_token" in response.data

    def test_logout(self, client, user):
        """Test user logout with JWT authentication"""
        user.set_password("TestPass123!")
        user.save()

        # First login
        url = reverse("rest_login")
        data = {
            "username": user.username,
            "password": "TestPass123!",
        }
        login_response = client.post(url, data)
        assert login_response.status_code == status.HTTP_200_OK

        access_token = login_response.data.get("access")
        refresh_token = login_response.data.get("refresh")

        if access_token:
            client.cookies["jwt-auth"] = access_token
        if refresh_token:
            client.cookies["jwt-refresh-token"] = refresh_token

        # Then logout
        logout_url = reverse("rest_logout")
        response = client.post(logout_url)

        assert response.status_code in [
            status.HTTP_200_OK,
        ]


@pytest.mark.django_db
class TestPasswordReset:
    """Test password reset flow"""

    def test_password_reset_request_success(self, client, user, email_address):
        """Test password reset email is sent successfully"""
        url = reverse("rest_password_reset")
        data = {"email": user.email}
        response = client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to[0] == user.email

    def test_password_reset_email_contains_token(self, client, user, email_address):
        """Test that password reset email contains uid and token"""
        url = reverse("rest_password_reset")
        data = {"email": user.email}
        response = client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert len(mail.outbox) == 1

        # Check email content contains uid and token
        email_body = mail.outbox[0].body
        uid = user_pk_to_url_str(user)
        assert uid in email_body

        # Extract token from email using regex
        # The email format is: /api/v1/auth/password/reset/confirm/<uid>/<token>/
        token_pattern = r"/api/v1/auth/password/reset/confirm/[^/]+/([^/]+)/"
        match = re.search(token_pattern, email_body)
        assert match is not None
        token = match.group(1)
        assert len(token) > 0

    def test_password_reset_confirm_success(self, client, user, email_address):
        """Test successful password reset confirmation"""
        # Generate valid uid and token
        uid = user_pk_to_url_str(user)
        token = default_token_generator.make_token(user)

        url = reverse("rest_password_reset_confirm")
        data = {
            "uid": uid,
            "token": token,
            "new_password1": "NewTestPass123!",
            "new_password2": "NewTestPass123!",
        }
        response = client.post(url, data)

        assert response.status_code == status.HTTP_200_OK

        # Verify password was changed
        user.refresh_from_db()
        assert user.check_password("NewTestPass123!")

    def test_password_reset_complete_flow(self, client, user, email_address):
        """Test complete password reset flow from request to confirmation"""
        old_password = "OldTestPass123!"
        user.set_password(old_password)
        user.save()

        # Step 1: Request password reset
        reset_url = reverse("rest_password_reset")
        reset_data = {"email": user.email}
        response = client.post(reset_url, reset_data)
        assert response.status_code == status.HTTP_200_OK

        # Step 2: Extract uid and token from email
        assert len(mail.outbox) == 1
        email_body = mail.outbox[0].body

        # Extract uid and token
        # The email format is: /api/v1/auth/password/reset/confirm/<uid>/<token>/
        uid_pattern = r"/api/v1/auth/password/reset/confirm/([^/]+)/([^/]+)/"
        match = re.search(uid_pattern, email_body)
        assert match is not None
        uid = match.group(1)
        token = match.group(2)

        # Step 3: Confirm password reset
        confirm_url = reverse("rest_password_reset_confirm")
        new_password = "NewTestPass123!"
        confirm_data = {
            "uid": uid,
            "token": token,
            "new_password1": new_password,
            "new_password2": new_password,
        }
        response = client.post(confirm_url, confirm_data)
        assert response.status_code == status.HTTP_200_OK

        # Step 4: Verify new password works
        user.refresh_from_db()
        assert user.check_password(new_password)
        assert not user.check_password(old_password)

        # Step 5: Verify can login with new password
        login_url = reverse("rest_login")
        login_data = {
            "username": user.username,
            "password": new_password,
        }
        response = client.post(login_url, login_data)
        assert response.status_code == status.HTTP_200_OK


class TestEmailVerification:
    """Test email verification endpoints"""

    def test_email_verification_success(self, client, user):
        """Test email verification success"""
        request_data = {"email": user.email}
        url = reverse("account_confirm_email")
        response = client.post(url, request_data)
        assert response.status_code == status.HTTP_200_OK
        assert mail.outbox[0].to[0] == user.email
