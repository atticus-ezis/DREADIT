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

from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from oauth2_provider.urls import path as oauth2_urls


def health(request):
    return HttpResponse("Health check: OK")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health),
    # auth
    path("accounts/", include("allauth.urls")),
    path("api/v1/oauth2/", include(oauth2_urls, namespace="oauth2_provider")),
    # rest urls
    path(
        "api/v1/",
        include(
            (
                [
                    path("auth/", include("dj_rest_auth.urls")),
                ]
            )
        ),
    ),
]
