import environ
from allauth.account.forms import default_token_generator
from allauth.account.models import EmailConfirmation, EmailConfirmationHMAC
from allauth.account.utils import user_pk_to_url_str
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.twitter.views import TwitterOAuthAdapter
from dj_rest_auth.jwt_auth import set_jwt_access_cookie, set_jwt_refresh_cookie
from dj_rest_auth.registration.views import SocialLoginView, VerifyEmailView
from dj_rest_auth.social_serializers import TwitterLoginSerializer
from dj_rest_auth.views import PasswordResetView
from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User

env = environ.Env()

frontend_url = settings.FRONTEND_URL

# Create your views here.


class CustomVerifyEmailView(VerifyEmailView):
    def get(self, request, key):
        try:
            emailconfirmation = EmailConfirmation.objects.filter(key=key).first()

            if emailconfirmation:
                # Confirm the email
                emailconfirmation.confirm(request)
                user = emailconfirmation.email_address.user

                resp = HttpResponseRedirect(f"{frontend_url}")
                refresh = RefreshToken.for_user(user)
                access = str(refresh.access_token)
                set_jwt_access_cookie(resp, access)
                set_jwt_refresh_cookie(resp, str(refresh))
                return resp

            else:
                # Try HMAC confirmation (for emails sent without storing in DB)
                emailconfirmation = EmailConfirmationHMAC.from_key(key)
                if emailconfirmation:
                    emailconfirmation.confirm(request)
                    user = emailconfirmation.email_address.user

                    resp = HttpResponseRedirect(f"{frontend_url}")
                    refresh = RefreshToken.for_user(user)
                    access = str(refresh.access_token)
                    set_jwt_access_cookie(resp, access)
                    set_jwt_refresh_cookie(resp, str(refresh))
                    return resp
                else:
                    # Invalid or expired key
                    return Response(
                        {"key": [("Verification key has expired")]},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        except Exception:
            # Handle any errors
            return Response(
                {"key": [("Verification key has expired")]},
                status=status.HTTP_400_BAD_REQUEST,
            )


@api_view(["POST"])
def google_auth(request):
    token = request.data.get("token")
    if not token:
        return Response(
            {"error": "Missing 'token'."}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        id_info = id_token.verify_oauth2_token(
            token, google_requests.Request(), settings.GOOGLE_OAUTH_CLIENT_ID
        )

        email = id_info["email"]

        user, created = User.objects.get_or_create(email=email)

        if created:
            user.set_unusable_password()
            user.username = email.split("@")[0]
            user.registration_method = "google"
            user.save()

        else:
            if user.registration_method != "google":
                return Response(
                    {"error": "User needs to sign in through email", "status": False},
                    status=status.HTTP_403_FORBIDDEN,
                )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                "status": True,
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"error": f"Invalid Token: {e}"}, status=status.HTTP_502_BAD_GATEWAY
        )


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


class TwitterLogin(SocialLoginView):
    adapter_class = TwitterOAuthAdapter
    serializer_class = TwitterLoginSerializer


class CustomPasswordResetView(PasswordResetView):
    def post(self, request, *args, **kwargs):
        # Create a form instance with the POST data
        form = PasswordResetForm(request.data)

        if form.is_valid():
            # Get current site
            current_site = get_current_site(request)

            # Process each user individually to get uid for each
            for user in form.get_users(form.cleaned_data["email"]):
                # Generate token and uid (using allauth's base36 encoding)
                token = default_token_generator.make_token(user)
                uid = user_pk_to_url_str(user)

                # Build the reset URL with uid and token
                reset_url = f"{frontend_url}/password-reset/confirm/{uid}/{token}/"

                # Create email context
                context = {
                    "email": user.email,
                    "domain": current_site.domain,
                    "site_name": current_site.name,
                    "uid": uid,
                    "token": token,
                    "protocol": "https" if request.is_secure() else "http",
                    "user": user,
                    "reset_url": reset_url,
                }

                # Render email subject and body
                subject = render_to_string(
                    "account/password_reset_subject.txt", context
                )
                subject = "".join(subject.splitlines())
                body = render_to_string("account/password_reset_email.html", context)

                # Send email
                send_mail(
                    subject,
                    body,
                    getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@localhost"),
                    [user.email],
                    html_message=None,
                )

            return Response(
                {"detail": "Password reset e-mail has been sent."},
                status=status.HTTP_200_OK,
            )

        # If form is invalid, return errors
        return Response(
            {"email": ["Enter a valid email address."]},
            status=status.HTTP_400_BAD_REQUEST,
        )
