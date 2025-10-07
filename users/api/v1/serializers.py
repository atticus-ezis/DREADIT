# users/serializers.py
from dj_rest_auth.serializers import PasswordResetSerializer
from django.conf import settings


class CustomPasswordResetSerializer(PasswordResetSerializer):
    def get_email_options(self):
        """Override to use custom email template and context"""
        return {
            "email_template_name": "account/password_reset_email.html",
            "extra_email_context": {
                "frontend_url": settings.FRONTEND_URL,
            },
        }

    def save(self):
        request = self.context.get("request")
        # Use Django's built-in password reset instead of allauth's
        opts = {
            "use_https": request.is_secure(),
            "from_email": getattr(settings, "DEFAULT_FROM_EMAIL"),
            "request": request,
            "email_template_name": "account/password_reset_email.html",
            "subject_template_name": "account/password_reset_subject.txt",
            "extra_email_context": {
                "frontend_url": settings.FRONTEND_URL,
            },
        }
        self.reset_form.save(**opts)
