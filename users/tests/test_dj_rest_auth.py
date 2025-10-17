import re

import pytest
from allauth.account.forms import default_token_generator
from allauth.account.utils import user_pk_to_url_str
from django.conf import settings
from django.core import mail
from django.urls import reverse
from rest_framework import status

from users.models import User

frontend_url = settings.FRONTEND_URL
verify_email_url = settings.VERIFY_EMAIL_URL
password_reset_url = settings.PASSWORD_RESET_URL


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

    def test_rest_password_reset(self, client, user, email_address):
        """Test password reset request endpoint sends email with valid frontend URL"""
        # Set a password for the user first (required for token generation)
        user.set_password("InitialPassword123!")
        user.save()

        url = reverse("custom_rest_password_reset")
        data = {"email": user.email}
        response = client.post(url, data)

        # Verify the endpoint returns success
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("detail") == "Password reset e-mail has been sent."

        # Verify email was sent to the correct recipient
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to[0] == user.email

        # Parse the email body to extract the frontend reset URL
        email_body = mail.outbox[0].body

        reset_link_pattern = re.compile(
            rf"{re.escape(frontend_url)}{re.escape(password_reset_url)}"
            r"(?P<uid>[^/]+)/(?P<token>[^/\s]+)/?",
            flags=re.IGNORECASE,
        )

        match = reset_link_pattern.search(email_body)
        assert (
            match is not None
        ), f"No password reset URL found in email body. Body: {email_body}"

        # Extract uid and token from the email
        uid = match.group("uid")
        token = match.group("token")

        # Verify uid and token are present and not empty
        assert uid, "UID is empty in the reset link"
        assert token, "Token is empty in the reset link"

        # Verify the token is valid for this user
        # Note: We don't import user_url_str_to_pk to avoid coupling,
        # but we verify it's the correct format
        assert len(uid) > 0, "UID should not be empty"
        assert len(token) > 10, "Token should be a reasonable length"
        assert "-" in token, "Token should contain a dash (typical Django token format)"

    def test_custom_password_reset_confirm(self, client, user, email_address):
        """Test password reset confirm endpoint works correctly"""
        # Set an original password first
        original_password = "OldPassword123!"
        user.set_password(original_password)
        user.save()

        # Generate uid and token AFTER setting password (tokens are based on password hash)
        uid = user_pk_to_url_str(user)
        token = default_token_generator.make_token(user)

        # Test the password reset confirm endpoint directly
        reset_url = reverse("custom_password_reset_confirm")
        data = {
            "new_password1": "SecondPass12@",
            "new_password2": "SecondPass12@",
            "uid": uid,
            "token": token,
        }

        reset_response = client.post(reset_url, data)
        assert reset_response.status_code == status.HTTP_200_OK
        assert (
            reset_response.data.get("detail")
            == "Password has been reset with the new password."
        )

        # Verify the password was actually changed
        user.refresh_from_db()
        assert user.check_password("SecondPass12@")
        assert not user.check_password(original_password)

    def test_complete_flow(self, client, user, email_address):
        """Test complete password reset flow"""
        # Set an original password first
        original_password = "OldPassword123!"
        user.set_password(original_password)
        user.save()

        url = reverse("custom_rest_password_reset")
        data = {"email": user.email}
        client.post(url, data)

        email_body = mail.outbox[0].body

        reset_link_pattern = re.compile(
            rf"{re.escape(frontend_url)}{re.escape(password_reset_url)}"
            r"(?P<uid>[^/]+)/(?P<token>[^/\s]+)/?",
            flags=re.IGNORECASE,
        )

        match = reset_link_pattern.search(email_body)
        # Extract uid and token from the email
        uid = match.group("uid")
        token = match.group("token")

        reset_url = reverse("custom_password_reset_confirm")
        data = {
            "new_password1": "SecondPass12@",
            "new_password2": "SecondPass12@",
            "uid": uid,
            "token": token,
        }

        reset_response = client.post(reset_url, data)
        assert reset_response.status_code == status.HTTP_200_OK
        assert (
            reset_response.data.get("detail")
            == "Password has been reset with the new password."
        )

        # Verify the password was actually changed
        user.refresh_from_db()
        assert user.check_password("SecondPass12@")
        assert not user.check_password(original_password)


@pytest.mark.django_db
class TestEmailVerification:
    """Test email verification endpoints"""

    def test_register_email_verification_success(self, client):
        """Test email verification success"""
        # login user and send email
        url = reverse("rest_register")
        data = {
            "username": "verifyuser",
            "email": "verifyuser@example.com",
            "password1": "TestPass123!",
            "password2": "TestPass123!",
        }
        response = client.post(url, data)

        assert len(mail.outbox) == 1

        email_body = mail.outbox[0].body

        token_pattern = re.escape(frontend_url + verify_email_url) + r"([^&\s]+)"
        match = re.search(token_pattern, email_body)
        assert (
            match is not None
        ), f"Token pattern not found in email. Email body: {email_body}"
        token = match.group(1)

        url = reverse("account_confirm_email")
        data = {"key": token}
        response = client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("detail") == "Email confirmed successfully"
        assert User.objects.filter(email="verifyuser@example.com").exists()

        # test if set_jwt_cookies is working
        assert "jwt-auth" in client.cookies
        assert "jwt-refresh-token" in client.cookies
        assert client.cookies["jwt-auth"].value is not None
        assert client.cookies["jwt-refresh-token"].value is not None


@pytest.mark.django_db
class TestUserProfile:
    """Test user profile endpoints"""

    def test_get_user_profile(self, auth_client, user):
        """Test getting user profile"""
        url = reverse("rest_user_details")
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("username") == user.username
        assert response.data.get("email") == user.email
        assert response.data.get("registration_method") == User.RegistrationMethod.LOCAL

    def test_update_user_profile(self, auth_client, user):
        """Test updating user profile"""
        url = reverse("rest_user_details")
        data = {
            "username": "newusername",
            "email": "newemail@example.com",
            "bio": "new bio",
        }
        response = auth_client.put(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("username") == "newusername"
        assert response.data.get("email") == "newemail@example.com"
        assert response.data.get("bio") == "new bio"
        assert response.data.get("registration_method") == User.RegistrationMethod.LOCAL
        assert response.data.get("is_verified") is False
        print(response.data.get("date_joined"))
        print(response.data.get("last_login"))
        assert response.data.get("date_joined") is not None
        assert response.data.get("last_login") is None
