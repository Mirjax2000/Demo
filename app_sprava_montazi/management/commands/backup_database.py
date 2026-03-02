"""
Management command pro zálohu databáze.

Vytvoří timestampovanou kopii SQLite databáze (nebo pg_dump pro PostgreSQL).
Odstraní staré zálohy podle retention policy.

Použití:
    python manage.py backup_database
    python manage.py backup_database --keep 14
    python manage.py backup_database --output /path/to/backups/
"""

import os
import shutil
import glob
from datetime import datetime, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Vytvoří zálohu databáze a odstraní staré zálohy."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            type=str,
            default=os.path.join(settings.BASE_DIR, "backups"),
            help="Výstupní adresář pro zálohy (default: ./backups/)",
        )
        parser.add_argument(
            "--keep",
            type=int,
            default=7,
            help="Počet dní, po které se zálohy uchovávají (default: 7)",
        )

    def handle(self, *args, **options):
        output_dir = options["output"]
        keep_days = options["keep"]

        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        db_config = settings.DATABASES["default"]
        engine = db_config["ENGINE"]

        if "sqlite3" in engine:
            self._backup_sqlite(db_config, output_dir, timestamp)
        elif "postgresql" in engine:
            self._backup_postgres(db_config, output_dir, timestamp)
        else:
            self.stderr.write(
                self.style.ERROR(f"Nepodporovaný DB engine: {engine}")
            )
            return

        # Vyčistit staré zálohy
        self._cleanup_old_backups(output_dir, keep_days)

    def _backup_sqlite(self, db_config, output_dir, timestamp):
        """Záloha SQLite — prostá kopie souboru."""
        db_path = db_config["NAME"]
        if not os.path.exists(db_path):
            self.stderr.write(self.style.ERROR(f"DB soubor neexistuje: {db_path}"))
            return

        backup_name = f"db_backup_{timestamp}.sqlite3"
        backup_path = os.path.join(output_dir, backup_name)

        shutil.copy2(db_path, backup_path)
        size_mb = os.path.getsize(backup_path) / (1024 * 1024)

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ SQLite záloha vytvořena: {backup_path} ({size_mb:.1f} MB)"
            )
        )

    def _backup_postgres(self, db_config, output_dir, timestamp):
        """Záloha PostgreSQL — pg_dump."""
        backup_name = f"db_backup_{timestamp}.sql"
        backup_path = os.path.join(output_dir, backup_name)

        env = os.environ.copy()
        env["PGPASSWORD"] = db_config.get("PASSWORD", "")

        cmd = (
            f'pg_dump -h {db_config.get("HOST", "localhost")} '
            f'-p {db_config.get("PORT", "5432")} '
            f'-U {db_config.get("USER", "postgres")} '
            f'-d {db_config["NAME"]} '
            f'-f "{backup_path}"'
        )

        ret = os.system(cmd)
        if ret == 0:
            size_mb = os.path.getsize(backup_path) / (1024 * 1024)
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ PostgreSQL záloha vytvořena: {backup_path} ({size_mb:.1f} MB)"
                )
            )
        else:
            self.stderr.write(
                self.style.ERROR(f"pg_dump selhal s kódem {ret}")
            )

    def _cleanup_old_backups(self, output_dir, keep_days):
        """Smaže zálohy starší než keep_days."""
        cutoff = datetime.now() - timedelta(days=keep_days)
        patterns = [
            os.path.join(output_dir, "db_backup_*.sqlite3"),
            os.path.join(output_dir, "db_backup_*.sql"),
        ]

        removed = 0
        for pattern in patterns:
            for path in glob.glob(pattern):
                mtime = datetime.fromtimestamp(os.path.getmtime(path))
                if mtime < cutoff:
                    os.remove(path)
                    removed += 1
                    self.stdout.write(f"  🗑️ Smazána stará záloha: {os.path.basename(path)}")

        if removed:
            self.stdout.write(
                self.style.WARNING(f"Odstraněno {removed} starých záloh (starší než {keep_days} dní).")
            )
        else:
            self.stdout.write("Žádné staré zálohy k odstranění.")
