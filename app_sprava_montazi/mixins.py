"""Mixiny"""

from typing import Any
from django.views.generic.base import ContextMixin
from .utils import call_errors_adviced


class ErrorContextMixin(ContextMixin):
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        is_errors, count = call_errors_adviced()
        context["errors"] = {
            "has_error": is_errors,
            "count": count,
        }
        return context

    def get_error_context(self):
        is_errors, count = call_errors_adviced()
        return {
            "errors": {
                "has_error": is_errors,
                "count": count,
            }
        }
