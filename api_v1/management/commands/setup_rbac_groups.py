"""
Inicializace RBAC skupin (Django Groups).

Použití:
    python manage.py setup_rbac_groups
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


ROLES = ["Admin", "Manager", "Operator", "ReadOnly"]


class Command(BaseCommand):
    help = "Vytvoří výchozí RBAC skupiny: Admin, Manager, Operator, ReadOnly"

    def handle(self, *args, **options):
        for role in ROLES:
            group, created = Group.objects.get_or_create(name=role)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Skupina '{role}' vytvořena."))
            else:
                self.stdout.write(f"Skupina '{role}' již existuje.")

        self.stdout.write(self.style.SUCCESS("RBAC skupiny inicializovány."))
