"""nonce generator pro povoleni js v html"""
import secrets


class CSPNonceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Vygenerujeme náhodný nonce (řetězec)
        nonce = secrets.token_urlsafe(16)
        request.csp_nonce = nonce  # uložíme nonce do requestu

        response = self.get_response(request)

        # Přidáme CSP hlavičku s nonce
        csp_policy = f"script-src 'nonce-{nonce}' 'self';"
        response["Content-Security-Policy"] = csp_policy

        return response
