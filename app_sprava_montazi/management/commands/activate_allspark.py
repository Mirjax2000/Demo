"""custom command activate_allspark"""

import os
from typing import TypedDict
from rich.console import Console
from dotenv import load_dotenv

from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.management import call_command
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

load_dotenv(override=True, verbose=True)

cons = Console()
User = get_user_model()


class SysUser(TypedDict):
    username: str
    password: str
    is_superuser: bool
    is_staff: bool
    message: str


class Command(BaseCommand):
    help = "Provede základní nastavení aplikace: migrace, vytvoření uživatelů a tokenů."

    def handle(self, *args, **kwargs) -> None:
        cons.log("\n")
        cons.rule("[bold yellow]⚡ Aktivace AllSpark zahájena[/bold yellow]")
        cons.log("\n")
        self.run_migrations()
        self.create_users()
        self.collect_static()
        self.run_distrib_hubs()
        # self.settings_fill_database()
        cons.log("\n")
        cons.rule(
            "[bold yellow]⚡ Aktivace dokončena. Systém je připraven.[/bold yellow]"
        )
        self.final_message()

    def run_migrations(self) -> None:
        try:
            cons.log("🔧 Spouštím makemigrations...", style="blue")
            call_command("makemigrations", interactive=False)
            cons.log(
                "✅ Makemigrations dokončeno. AllSpark začal formovat struktury databaze.\n",
                style="green",
            )
        except Exception as e:
            cons.log(f"❌ Makemigrations selhalo: {e}", style="red")
            return

        try:
            cons.log("🔧 Spouštím migrate...", style="blue")
            call_command("migrate", interactive=False)
            cons.log(
                "✅ Migrace dokončeny. Tabulky naplněny životem z AllSpark.\n",
                style="green",
            )
        except Exception as e:
            cons.log(f"[red]❌ Migrace selhala: {e}[/red]")

    def run_distrib_hubs(self) -> None:
        try:
            cons.log("📦 Spouštím distrib huby instalaci...", style="blue")
            call_command("distrib_hub")
            cons.log(
                "✅ Všechny distrib huby jsou pripraveny na naklad.",
                style="green",
            )
        except Exception as e:
            cons.log(f"❌ Distrib hub instalace selhala: {e}", style="red")

    def create_users(self) -> None:
        users: list[SysUser] = [
            {
                "username": os.getenv("SYSTEM_USER", ""),
                "password": os.getenv("SYSTEM_USER_PASS", ""),
                "is_superuser": False,
                "is_staff": False,
                "message": "AllSpark zažehnut. Systém je naplněn funkcionalitou!",
            },
            {
                "username": os.getenv("SYSTEM_SUPER_USER", ""),
                "password": os.getenv("SYSTEM_SUPER_USER_PASS", ""),
                "is_superuser": True,
                "is_staff": True,
                "message": "Optimus Prime připojený na AllSpark a připraven vládnout admin panelu!",
            },
            {
                "username": os.getenv("SYSTEM_BOT", ""),
                "password": os.getenv("SYSTEM_BOT_PASS", ""),
                "is_superuser": False,
                "is_staff": False,
                "message": "Bumblebee připojený k AllSpark. Tichý, ale výkonný.",
            },
        ]

        for user in users:
            username = user["username"]
            password = user["password"]

            if not username or not password:
                cons.log(
                    "⚠️ Uživatel nemá vyplněné jméno nebo heslo.přeskočeno.", style="red"
                )
                continue

            if User.objects.filter(username=username).exists():
                cons.log(
                    f"⚠️ Uživatel '{username}' již existuje. přeskočeno.", style="yellow"
                )
                continue

            user_obj = User.objects.create_user(
                username=username,
                password=password,
                is_staff=user["is_staff"],
                is_superuser=user["is_superuser"],
            )
            cons.log(f"✅ Uživatel '{username}' byl úspěšně vytvořen.", style="green")
            cons.log(f"{user['message']}", style="cyan")

            token, _ = Token.objects.get_or_create(user=user_obj)
            cons.log(
                f"🔑 Token pro '{username}': ...{token.key[2:8]}...\n", style="magenta"
            )

    def collect_static(self) -> None:
        if settings.DEBUG:
            cons.log("🛑 DEBUG je zapnutý collectstatic se přeskočí.", style="yellow")
            return

        try:
            cons.log("📦 Spouštím collectstatic...", style="blue")
            call_command("collectstatic", interactive=False, verbosity=0)
            cons.log(
                "✅ Všechny jednotky AllSpark byly přesunuty do základny STATIC_ROOT.",
                style="green",
            )
            cons.log(
                "🌀 Statické komponenty se transformovaly a jsou připraveny na nasazení!",
                style="cyan",
            )
        except Exception as e:
            cons.log(f"❌ Collectstatic selhal: {e}", style="red")

    def settings_fill_database(self) -> None:
        try:
            cons.log("📦 Spouštím nastavovani aplikace...", style="blue")
            call_command("settings_fill_db", "app_settings.json", verbosity=0)
            cons.log("✅ App Settings databaze zaplnena.", style="green")

        except Exception as e:
            cons.log(f"❌ Nastaveni AppSettings databaze selhalo: {e}", style="red")

    def print_host(self) -> str:
        hosts = os.getenv("ALLOWED_HOSTS", "localhost")
        host = hosts.split(",")[0].strip()
        return host

    def system_bot_token(self) -> str:
        system_bot = os.getenv("SYSTEM_BOT")
        if not system_bot:
            msg = "⚠️ Nebyl nastaven SYSTEM_BOT v .env, nelze vypsat token system_bota."
            if settings.DEBUG:
                cons.log(f"{msg}", style="red")
            return msg

        try:
            user = User.objects.get(username=system_bot)
            token = Token.objects.get(user=user)
            return token.key

        except User.DoesNotExist:
            msg = f"Chyba: Uživatele '{system_bot}' nelze najít."
            if settings.DEBUG:
                cons.log(f"[red]{msg}[/red]")
            return msg

        except Token.DoesNotExist:
            msg = f"Chyba: Token pro uživatele '{system_bot}' neexistuje."
            if settings.DEBUG:
                cons.log(f"[red]{msg}[/red]")
            return msg

    def final_message(self):
        cons.log("\n\n")
        cons.rule("🔧 nastavení autobota u uživatele", style="blue")
        cons.log(
            f"\nToto nastav u autobota u dispečerta.\nTokken:[magenta bold]{self.system_bot_token()}[/magenta bold]\n"
        )
        cons.log(
            f'API_URL_GET = "http://{self.print_host()}/api/incomplete-customers/"'
        )
        cons.log(
            f'API_URL_UPDATE = "http://{self.print_host()}/api/update-customers/"\n'
        )
        cons.log(
            "\nDalším krokem je vytvoření uživatelských účtů pro dispečerty!\n",
            style="blue",
        )
        cons.rule("", style="blue")
