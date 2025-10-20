import traceback

from allauth.account.models import EmailConfirmation, EmailConfirmationHMAC
from allauth.account.utils import url_str_to_user_pk
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.twitter.views import TwitterOAuthAdapter
from dj_rest_auth.jwt_auth import set_jwt_cookies
from dj_rest_auth.registration.views import SocialLoginView, VerifyEmailView
from dj_rest_auth.social_serializers import TwitterLoginSerializer
from dj_rest_auth.views import PasswordResetConfirmView
from django.conf import settings
from django.contrib.auth import get_user_model
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User


# can replace with APIView?
class CustomVerifyEmailView(VerifyEmailView):
    def post(self, request):
        key = request.data.get("key")
        print(f"Key: {key}")
        if not key:
            raise ValidationError({"key": [("Missing verification key.")]})

        try:
            emailconfirmation = EmailConfirmation.objects.filter(
                key=key
            ).first() or EmailConfirmationHMAC.from_key(key)
            if not emailconfirmation:
                raise ValidationError({"key": [("Invalid verification key.")]})

            emailconfirmation.confirm(request)

            user = emailconfirmation.email_address.user

            refresh = RefreshToken.for_user(user)
            access = refresh.access_token

            resp = Response(
                {
                    "detail": "Email confirmed successfully",
                    "access": str(access),
                    "refresh": str(refresh),
                },
                status=status.HTTP_200_OK,
            )
            set_jwt_cookies(resp, str(access), str(refresh))
            return resp

        except Exception as e:
            print(f"Error: {e}")
            print(traceback.format_exc())
            return Response(
                {"key": [f"Error: {str(e)}"]},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """
    Custom password reset confirm view that automatically logs the user in
    after successful password reset by returning JWT tokens and setting cookies.
    """

    def post(self, request, *args, **kwargs):

        try:
            response = super().post(request, *args, **kwargs)

            if response.status_code == status.HTTP_200_OK:
                User = get_user_model()
                uid = request.data.get("uid")

                # Decode uid using allauth's base36 decoder
                user_pk = url_str_to_user_pk(uid)
                user = User.objects.get(pk=user_pk)

                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                access = refresh.access_token

                # Add tokens to response data
                response.data["access"] = str(access)
                response.data["refresh"] = str(refresh)

                # Set JWT cookies
                set_jwt_cookies(response, str(access), str(refresh))

            return response

        except Exception as e:
            print(f"Error in CustomPasswordResetConfirmView: {e}")
            print(traceback.format_exc())
            return Response(
                {"detail": [f"Error: {str(e)}"]},
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
        resp = Response(
            {
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                "status": True,
            },
            status=status.HTTP_200_OK,
        )
        set_jwt_cookies(resp, str(refresh.access_token), str(refresh))
        return resp
    except Exception as e:
        return Response(
            {"error": f"Invalid Token: {e}"}, status=status.HTTP_502_BAD_GATEWAY
        )


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


class TwitterLogin(SocialLoginView):
    adapter_class = TwitterOAuthAdapter
    serializer_class = TwitterLoginSerializer
