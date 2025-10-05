import environ
from allauth.account.models import EmailConfirmation, EmailConfirmationHMAC
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.twitter.views import TwitterOAuthAdapter
from dj_rest_auth.registration.views import SocialLoginView, VerifyEmailView
from dj_rest_auth.social_serializers import TwitterLoginSerializer
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.response import Response

env = environ.Env()

# Create your views here.


class CustomVerifyEmailView(VerifyEmailView):
    def get(self, request, key):
        try:
            # Try to get confirmation object
            emailconfirmation = EmailConfirmation.objects.filter(key=key).first()

            if emailconfirmation:
                # Confirm the email
                emailconfirmation.confirm(request)
                # Redirect to frontend success page
                return redirect("home")
            else:
                # Try HMAC confirmation (for emails sent without storing in DB)
                emailconfirmation = EmailConfirmationHMAC.from_key(key)
                if emailconfirmation:
                    emailconfirmation.confirm(request)
                    return redirect("home")
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
