"""Custom command distrib_hub"""

from pathlib import Path
import json
from rich.console import Console

from django.core.management.base import BaseCommand, CommandParser
from django.conf import settings

# --- models
from app_sprava_montazi.models import AppSetting

# ---
cons: Console = Console()


class Command(BaseCommand):
    help = "zaplni Appsettings databazi"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("file", type=str, help="cesta k json souboru")

    def handle(self, *args, **kwargs) -> None:
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        file_path = base_dir / "configs" / "app" / kwargs["file"]

        if not file_path.exists():
            cons.log(f"[bold red]❌ Soubor '{file_path}' neexistuje.[/bold red]")
            return

        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            cons.log(f"[bold red]❌ Chyba v JSON: {e}[/bold red]")
            return

        # for name, content in data.items():
        #     obj, created = AppSetting.objects.update_or_create(
        #         name=name,
        #         defaults={"data": content},
        #     )
        #     if created:
        #         cons.log(f"[green]✅ Vytvořeno:[/green] {name}")
        #     else:
        #         cons.log(f"[yellow]✏️ Aktualizováno:[/yellow] {name}")

        cons.log("[bold green]🎉 Hotovo.[/bold green]")
