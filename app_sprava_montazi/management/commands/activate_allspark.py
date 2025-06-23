"""custom command activate_allspark"""

import os
from typing import TypedDict
from rich.console import Console
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from dotenv import load_dotenv

# --- načtení .env
load_dotenv(override=True, verbose=True)
cons = Console()
User = get_user_model()


# --- typ uživatele
class SysUser(TypedDict):
    username: str
    password: str
    is_superuser: bool
    is_staff: bool
    message: str


class Command(BaseCommand):
    help = "Provede základní nastavení aplikace: migrace a vytvoření uživatelů."

    def handle(self, *args, **kwargs) -> None:
        cons.rule("[bold yellow]⚡ Aktivace AllSpark zahájena...[/bold yellow]")
        self.run_migrations()
        self.create_users()
        cons.rule("[bold green]✅ Aktivace dokončena – systém je připraven.[/bold green]")

    def run_migrations(self) -> None:
        try:
            cons.log("[blue]🔧 Spouštím makemigrations...[/blue]")
            call_command("makemigrations", interactive=False)
            cons.log("[green]✅ Makemigrations dokončeno – AllSpark začal formovat struktury světa.[/green]")
        except Exception as e:
            cons.log(f"[red]❌ Makemigrations selhalo: {e}[/red]")
            return

        try:
            cons.log("[blue]🔧 Spouštím migrate...[/blue]")
            call_command("migrate", interactive=False)
            cons.log("[green]✅ Migrace dokončeny – tabulky naplněny životem z AllSpark.[/green]")
        except Exception as e:
            cons.log(f"[red]❌ Migrace selhala: {e}[/red]")

    def create_users(self) -> None:
        users: list[SysUser] = [
            {
                "username": os.getenv("SYSTEM_USER", ""),
                "password": os.getenv("SYSTEM_USER_PASS", ""),
                "is_superuser": False,
                "is_staff": False,
                "message": "AllSpark napojen – systém je naplněn životní funkcionalitou!",
            },
            {
                "username": os.getenv("SYSTEM_SUPER_USER", ""),
                "password": os.getenv("SYSTEM_SUPER_USER_PASS", ""),
                "is_superuser": True,
                "is_staff": True,
                "message": "Optimus Prime je napojený na AllSpark a připraven vládnout admin panelu!",
            },
            {
                "username": os.getenv("SYSTEM_BOT", ""),
                "password": os.getenv("SYSTEM_BOT_PASS", ""),
                "is_superuser": False,
                "is_staff": False,
                "message": "Bumblebee připojený k AllSpark – tichý, ale smrtící!",
            },
        ]

        for user in users:
            username = user["username"]
            password = user["password"]

            if not username or not password:
                cons.log("[red]⚠️ Uživatel nemá vyplněné jméno nebo heslo – přeskočeno.[/red]")
                continue

            if not User.objects.filter(username=username).exists():
                User.objects.create_user(
                    username=username,
                    password=password,
                    is_staff=user["is_staff"],
                    is_superuser=user["is_superuser"],
                )
                cons.log(f"[green]✅ Uživatel '{username}' byl úspěšně vytvořen.[/green]")
                cons.log(f"[cyan]{user['message']}[/cyan]")
            else:
                cons.log(f"[yellow]⚠️ Uživatel '{username}' již existuje – přeskočeno.[/yellow]")
