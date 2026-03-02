"""
RBAC permission classes pro API v1.

Role (Django Groups):
  Admin    – plný přístup (CRUD + mazání + admin akce)
  Manager  – CRUD bez mazání
  Operator – vytvoření + editace (ne mazání, ne admin akce)
  ReadOnly – pouze GET

Superuser má vždy plný přístup.
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS

# Hierarchie rolí (vyšší číslo = vyšší oprávnění)
ROLE_HIERARCHY = {
    "ReadOnly": 0,
    "Operator": 1,
    "Manager": 2,
    "Admin": 3,
}


def get_user_role(user) -> str:
    """Vrátí nejvyšší roli uživatele (název skupiny)."""
    if user.is_superuser:
        return "Admin"
    groups = set(user.groups.values_list("name", flat=True))
    best = "ReadOnly"
    best_level = -1
    for name, level in ROLE_HIERARCHY.items():
        if name in groups and level > best_level:
            best = name
            best_level = level
    return best


def has_minimum_role(user, minimum_role: str) -> bool:
    """Ověří, zda uživatel má alespoň danou roli."""
    if user.is_superuser:
        return True
    user_role = get_user_role(user)
    return ROLE_HIERARCHY.get(user_role, 0) >= ROLE_HIERARCHY.get(minimum_role, 0)


class IsAdminRole(BasePermission):
    """Přístup pouze pro Admin roli (nebo superuser)."""

    def has_permission(self, request, view) -> bool:  # type: ignore[override]
        return request.user and request.user.is_authenticated and has_minimum_role(
            request.user, "Admin"
        )


class IsManagerOrAbove(BasePermission):
    """Manager+ může CRUD (bez destroy — to řeší view), ReadOnly a Operator mají jen safe."""

    def has_permission(self, request, view) -> bool:  # type: ignore[override]
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return has_minimum_role(request.user, "Manager")


class IsOperatorOrAbove(BasePermission):
    """Operator+ může vytvářet a editovat. ReadOnly jen čte."""

    def has_permission(self, request, view) -> bool:  # type: ignore[override]
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return has_minimum_role(request.user, "Operator")


class RBACPermission(BasePermission):
    """
    Univerzální RBAC permission pro ViewSety.

    Logika:
      - list, retrieve: všichni přihlášení
      - create, update, partial_update: Operator+
      - destroy: Manager+
      - custom actions (hide, generate-pdf, send-mail...): Operator+
    """

    def has_permission(self, request, view) -> bool:  # type: ignore[override]
        if not request.user or not request.user.is_authenticated:
            return False

        # Safe methods — všichni přihlášení
        if request.method in SAFE_METHODS:
            return True

        action = getattr(view, "action", None)

        # Destroy (DELETE) vyžaduje Manager+
        if action == "destroy" or request.method == "DELETE":
            return has_minimum_role(request.user, "Manager")

        # Ostatní write operace (create, update, custom actions) — Operator+
        return has_minimum_role(request.user, "Operator")
