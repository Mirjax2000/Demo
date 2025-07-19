"""Mixiny"""

from typing import Any
from django.views.generic.base import ContextMixin
from .utils import call_errors


class ErrorContextMixin(ContextMixin):
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        is_errors, count = call_errors()
        context["errors"] = {
            "has_error": is_errors,
            "count": count,
        }
        return context
