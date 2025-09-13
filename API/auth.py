from datetime import timedelta

# ---
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token

# ---
from django.utils import timezone
from django.conf import settings


class ExpiringTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        try:
            token = Token.objects.select_related("user").get(key=key)

        except Token.DoesNotExist:
            raise AuthenticationFailed("Token expired.")

        if not token.user.is_active:
            raise AuthenticationFailed("User inactive or deleted.")

        expiration_time = timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES)
        if token.created + expiration_time < timezone.now():
            token.delete()
            raise AuthenticationFailed("Token expired.")

        return (token.user, token)
