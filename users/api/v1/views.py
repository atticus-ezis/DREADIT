import environ
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.twitter.views import TwitterOAuthAdapter
from dj_rest_auth.registration.views import SocialLoginView, VerifyEmailView
from dj_rest_auth.social_serializers import TwitterLoginSerializer

env = environ.Env()

# Create your views here.


class CustomVerifyEmailView(VerifyEmailView):
    pass


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
