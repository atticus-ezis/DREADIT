import logging

from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings

logger = logging.getLogger(__name__)

# creates url for email confirmation


class CustomDefaultAccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        key = emailconfirmation.key
        logger.info(f"🔑 Email verification key: {key}")
        front_end_path = settings.VERIFY_EMAIL_URL + key

        email_confirmation_url = settings.FRONTEND_URL + front_end_path

        return email_confirmation_url
