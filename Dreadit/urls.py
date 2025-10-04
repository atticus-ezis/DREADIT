"""
URL configuration for dreadit project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from django.views.generic import TemplateView

from users.api.v1.views import (
    CustomVerifyEmailView,
    FacebookLogin,
    GoogleLogin,
    TwitterLogin,
)


def health(request):
    return HttpResponse("Health check: OK")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health),
    # auth
    path("accounts/", include("allauth.urls")),
    # TODO create template
    path(
        "accounts/confirm-email/<str:key>/",
        TemplateView.as_view(template_name="account/email_confirm.html"),
        name="account_confirm_email",
    ),
    # rest urls
    path(
        "api/v1/",
        include(
            (
                [
                    path("auth/", include("dj_rest_auth.urls")),
                    path(
                        "auth/registration/", include("dj_rest_auth.registration.urls")
                    ),
                    path(
                        "auth/registration/verify-email/",
                        CustomVerifyEmailView.as_view(),
                        name="rest_verify_email",
                    ),
                    # social logins
                    path(
                        "auth/social/google/",
                        GoogleLogin.as_view(),
                        name="google_login",
                    ),
                    path(
                        "auth/social/facebook/",
                        FacebookLogin.as_view(),
                        name="facebook_login",
                    ),
                    path(
                        "auth/social/twitter/",
                        TwitterLogin.as_view(),
                        name="twitter_login",
                    ),
                ]
            )
        ),
    ),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
