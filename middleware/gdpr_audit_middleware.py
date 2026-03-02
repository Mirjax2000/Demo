"""
GDPR Audit Log Middleware.

Loguje přístupy k endpoints obsahujícím osobní údaje zákazníků.
Loguje: uživatel, IP, endpoint, metoda, timestamp.
"""

import logging
import re
from django.utils import timezone

logger = logging.getLogger("gdpr_audit")

# Endpointy s osobními údaji — regex vzory
SENSITIVE_PATTERNS = [
    re.compile(r"^/api/v1/clients/"),
    re.compile(r"^/api/v1/call-logs/"),
    re.compile(r"^/api/v1/orders/\d+/$"),  # detail obsahuje client data
]


class GDPRAuditMiddleware:
    """Middleware pro logování přístupů k osobním údajům (GDPR čl. 30)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Pouze logovat autentizované requesty na citlivé endpointy
        if hasattr(request, "user") and request.user.is_authenticated:
            path = request.path
            if any(p.match(path) for p in SENSITIVE_PATTERNS):
                self._log_access(request, response)

        return response

    @staticmethod
    def _log_access(request, response):
        user = request.user
        ip = GDPRAuditMiddleware._get_client_ip(request)
        logger.info(
            "GDPR_ACCESS | user=%s | ip=%s | method=%s | path=%s | status=%s | time=%s",
            user.username,
            ip,
            request.method,
            request.path,
            response.status_code,
            timezone.now().isoformat(),
        )

    @staticmethod
    def _get_client_ip(request):
        """Získá IP adresu klienta (podpora proxy)."""
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded:
            return x_forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")
