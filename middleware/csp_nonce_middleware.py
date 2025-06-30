"""nonce generator pro povoleni js v html"""

import secrets


class CSPNonceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        nonce = secrets.token_urlsafe(16)
        request.csp_nonce = nonce

        response = self.get_response(request)

        csp_policy = (
            "default-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "object-src 'none'; "
            "frame-ancestors 'none'; "
            f"script-src 'nonce-{nonce}' 'self';"
        )
        response["Content-Security-Policy"] = csp_policy

        return response
