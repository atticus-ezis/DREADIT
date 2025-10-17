from allauth.account.models import EmailAddress
from dj_rest_auth.serializers import UserDetailsSerializer
from rest_framework import serializers

from users.models import User


class CustomUserDetailsSerializer(UserDetailsSerializer):
    """
    Custom user serializer that includes bio field and handles email verification
    when email is changed.
    """

    bio = serializers.CharField(max_length=500, required=False, allow_blank=True)
    registration_method = serializers.CharField(read_only=True)
    is_verified = serializers.SerializerMethodField()

    class Meta(UserDetailsSerializer.Meta):
        model = User
        fields = (
            "pk",
            "username",
            "email",
            "bio",
            "registration_method",
            "date_joined",
            "last_login",
            "is_verified",
        )
        read_only_fields = (
            "registration_method",
            "date_joined",
            "last_login",
            "is_verified",
        )

    def get_is_verified(self, obj):
        try:
            email_address = EmailAddress.objects.get(user=obj, primary=True)
            return email_address.verified
        except EmailAddress.DoesNotExist:
            return False
