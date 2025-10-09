import environ
from allauth.account.forms import default_token_generator
from allauth.account.models import EmailConfirmation, EmailConfirmationHMAC
from allauth.account.utils import user_pk_to_url_str
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.twitter.views import TwitterOAuthAdapter
from dj_rest_auth.registration.views import SocialLoginView, VerifyEmailView
from dj_rest_auth.social_serializers import TwitterLoginSerializer
from dj_rest_auth.views import PasswordResetView
from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

env = environ.Env()

frontend_url = settings.FRONTEND_URL

# Create your views here.


def _set_jwt_cookies(resp, user):
    refresh = RefreshToken.for_user(user)
    access = refresh.access_token

    # Pull names from REST_AUTH
    access_name = settings.REST_AUTH.get("JWT_AUTH_COOKIE", "jwt-auth")
    refresh_name = settings.REST_AUTH.get(
        "JWT_AUTH_REFRESH_COOKIE", "jwt-refresh-token"
    )

    # Cookie security knobs (use your env)
    secure = getattr(settings, "SESSION_COOKIE_SECURE", True)
    samesite = settings.REST_AUTH.get("JWT_AUTH_SAMESITE", "Lax")
    domain = getattr(settings, "SESSION_COOKIE_DOMAIN", None)

    # Access cookie
    resp.set_cookie(
        access_name,
        str(access),
        max_age=5 * 60,  # match your SIMPLE_JWT ACCESS_TOKEN_LIFETIME
        httponly=settings.REST_AUTH.get("JWT_AUTH_HTTPONLY", True),
        secure=secure,
        samesite=samesite,
        domain=domain,
        path="/",
    )
    # Refresh cookie
    resp.set_cookie(
        refresh_name,
        str(refresh),
        max_age=14 * 24 * 60 * 60,  # match your SIMPLE_JWT REFRESH_TOKEN_LIFETIME
        httponly=settings.REST_AUTH.get("JWT_AUTH_HTTPONLY", True),
        secure=secure,
        samesite=samesite,
        domain=domain,
        path="/",
    )


class CustomVerifyEmailView(VerifyEmailView):
    def get(self, request, key):
        try:
            emailconfirmation = EmailConfirmation.objects.filter(key=key).first()

            if emailconfirmation:
                # Confirm the email
                emailconfirmation.confirm(request)
                user = emailconfirmation.email_address.user

                resp = HttpResponseRedirect(f"{frontend_url}/profile")
                _set_jwt_cookies(resp, user)
                return resp

            else:
                # Try HMAC confirmation (for emails sent without storing in DB)
                emailconfirmation = EmailConfirmationHMAC.from_key(key)
                if emailconfirmation:
                    emailconfirmation.confirm(request)
                    user = emailconfirmation.email_address.user

                    resp = HttpResponseRedirect(f"{frontend_url}/profile")
                    _set_jwt_cookies(resp, user)
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


# Social Logins
class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = env.str("GOOGLE_CALLBACK_URL")
    client_class = OAuth2Client


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


class TwitterLogin(SocialLoginView):
    adapter_class = TwitterOAuthAdapter
    serializer_class = TwitterLoginSerializer


# class CustomPasswordResetConfirmView(PasswordResetConfirmView):
#     """
#     Custom password reset confirm view that handles allauth password reset URLs
#     and redirects to frontend after successful reset
#     """

#     template_name = "account/password_reset_confirm.html"
#     success_url = "/"

#     def form_valid(self, form):
#         # Call parent form_valid to reset the password
#         super().form_valid(form)

#         # Redirect to frontend with success message
#         return HttpResponseRedirect(f"{frontend_url}/login?reset=success")


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
