"""custom command activate_allspark"""

import os
from typing import TypedDict
from rich.console import Console
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from dotenv import load_dotenv

# ---
load_dotenv(override=True, verbose=True)
cons: Console = Console()
User = get_user_model()


class SysUser(TypedDict):
    username: str
    password: str
    is_superuser: bool
    is_staff: bool
    message: str


class Command(BaseCommand):
    help = "provede zakladni nastaveni aplikace"

    def handle(self, *args, **kwargs) -> None:
        env_super_user = os.getenv("SYSTEM_SUPER_USER", "")
        env_super_user_pass = os.getenv("SYSTEM_SUPER_USER_PASS", "")
        env_system = os.getenv("SYSTEM_USER", "")
        env_system_pass = os.getenv("SYSTEM_USER_PASS", "")
        env_autobot = os.getenv("SYSTEM_BOT", "")
        env_autobot_pass = os.getenv("SYSTEM_BOT_PASS", "")

        users: list[SysUser] = [
            {
                "username": env_system,
                "password": env_system_pass,
                "is_superuser": False,
                "is_staff": False,
                "message": "AllSpark napojen, system je naplnen zivotni funkcionalitou!",
            },
            {
                "username": env_super_user,
                "password": env_super_user_pass,
                "is_superuser": True,
                "is_staff": True,
                "message": "Optimus Prime je napojený na AllSpark a připraven vládnout admin panelu!",
            },
            {
                "username": env_autobot,
                "password": env_autobot_pass,
                "is_superuser": False,
                "is_staff": False,
                "message": "Bumblebee připojený k AllSpark  tichý, ale smrtící!",
            },
        ]

        for user in users:
            username = user["username"]
            password = user["password"]

            if not username or not password:
                cons.log(
                    "[red]Uživatel nemá vyplněné uživatelské jméno nebo heslo, přeskočeno.[/red]"
                )
                continue

            if not User.objects.filter(username=username).exists():
                User.objects.create_user(
                    username=username,
                    password=password,
                    is_staff=user["is_staff"],
                    is_superuser=user["is_superuser"],
                )
                cons.log(f"[green]Uživatel '{username}' byl úspěšně vytvořen.[/green]")
                cons.log(f"{user['message']}")
            else:
                cons.log(f"[yellow]Uživatel '{username}' již existuje.[/yellow]")
