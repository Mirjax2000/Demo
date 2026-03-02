"""
Cookie-based JWT Authentication.

Čte access token z httpOnly cookie místo Authorization headeru.
Fallback na klasický Bearer header pro zpětnou kompatibilitu (API klienti, bot).
"""

from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    """Pokusí se načíst JWT z httpOnly cookie, fallback na Bearer header."""

    def authenticate(self, request):
        # 1) Zkus cookie
        cookie_name = getattr(settings, "JWT_COOKIE_NAME", "ams_access")
        raw_token = request.COOKIES.get(cookie_name)
        if raw_token:
            validated = self.get_validated_token(raw_token)
            return self.get_user(validated), validated

        # 2) Fallback na klasický Authorization: Bearer <token>
        return super().authenticate(request)
