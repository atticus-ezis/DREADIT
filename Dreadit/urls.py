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
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt.authentication import JWTAuthentication

from users.api.v1.views import (
    CustomPasswordResetView,
    CustomVerifyEmailView,
    FacebookLogin,
    GoogleLogin,
    TwitterLogin,
)

# password reset


def health(request):
    return HttpResponse("Health check: OK")


def home(request):
    return HttpResponse("home page")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health),
    path("home/", home, name="home"),
    # rest urls
    path(
        "api/v1/",
        include(
            (
                [
                    # Custom auth views - must come BEFORE dj_rest_auth.urls to override
                    path(
                        "auth/password/reset/",
                        CustomPasswordResetView.as_view(),
                        name="rest_password_reset",
                    ),
                    # path("auth/password/reset/confirm/<uidb64>/<token>/",
                    # PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
                    path(
                        "auth/account-confirm-email/<str:key>",
                        CustomVerifyEmailView.as_view(),
                        name="account_confirm_email",
                    ),
                    # Default dj_rest_auth URLs (these come after custom views)
                    path("auth/", include("dj_rest_auth.urls")),
                    path(
                        "auth/registration/", include("dj_rest_auth.registration.urls")
                    ),
                    # path(
                    #     "auth/registration/verify-email/",
                    #     VerifyEmailView.as_view(),
                    #     name="rest_verify_email",
                    # ),
                    # social logins
                    path(
                        "auth/google/",
                        GoogleLogin.as_view(),
                        name="google_login",
                    ),
                    path(
                        "auth/facebook/",
                        FacebookLogin.as_view(),
                        name="fb_login",
                    ),
                    path(
                        "auth/twitter/",
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

# swagger
api_info = openapi.Info(
    title="DREADIT API",
    default_version="v1",
    description="API documentation for DREADIT",
)
schema_view = get_schema_view(
    api_info,
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=(JWTAuthentication,),
)
urlpatterns += [
    path("api/docs/", schema_view.with_ui("swagger", cache_timeout=0), name="api_docs"),
]

admin.site.site_header = "DREADIT"
admin.site.site_title = "DREADIT Admin Portal"
admin.site.index_title = "DREADIT Admin"
