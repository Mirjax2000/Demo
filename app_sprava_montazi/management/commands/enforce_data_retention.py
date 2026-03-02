"""
GDPR Data Retention — Automatická anonymizace starých zákaznických dat.

Spouštět denně přes cron:
  python manage.py enforce_data_retention

Volby:
  --dry-run     Pouze zobrazí co by se anonymizovalo (nic nesmaže)
  --policy NAME Použije konkrétní politiku (jinak výchozí = 5 let)
  --force       Anonymizovat i zákazníky bez consent_given=False

Logika:
  1. Načte aktivní DataRetentionPolicy
  2. Pro každého zákazníka spočítá datum poslední zakázky
  3. Pokud od poslední zakázky uplynula doba retention_days → anonymizovat
  4. Zákazníci bez zakázek → pokud data_retention_until uplynulo → anonymizovat
"""

import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Max

from app_sprava_montazi.models import Client, DataRetentionPolicy

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "GDPR: Anonymizace osobních údajů zákazníků po uplynutí doby uchovávání"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Pouze zobrazit zákazníky k anonymizaci, nic neměnit",
        )
        parser.add_argument(
            "--policy",
            type=str,
            default=None,
            help="Název konkrétní DataRetentionPolicy",
        )
        parser.add_argument(
            "--retention-days",
            type=int,
            default=None,
            help="Přepsat dobu uchovávání (dní). Ignoruje policy.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        policy_name = options["policy"]
        override_days = options["retention_days"]

        # --- Zjisti dobu uchovávání ---
        retention_days = self._get_retention_days(policy_name, override_days)
        cutoff_date = timezone.now().date() - timedelta(days=retention_days)

        self.stdout.write(
            f"GDPR Data Retention: {retention_days} dní | "
            f"cutoff: {cutoff_date} | "
            f"{'DRY RUN' if dry_run else 'LIVE'}"
        )

        # --- Najdi zákazníky k anonymizaci ---
        candidates = self._find_candidates(cutoff_date)

        if not candidates:
            self.stdout.write(self.style.SUCCESS("Žádní zákazníci k anonymizaci."))
            return

        self.stdout.write(f"Nalezeno {len(candidates)} zákazníků k anonymizaci:")

        for client in candidates:
            last_order = client.last_order_date
            reason = self._get_reason(client, cutoff_date, last_order)

            if dry_run:
                self.stdout.write(
                    f"  [DRY] {client.name} (ID={client.pk}) — {reason}"
                )
            else:
                self.stdout.write(
                    f"  [ANON] {client.name} (ID={client.pk}) — {reason}"
                )
                client.anonymize()
                logger.info(
                    "GDPR anonymizace: Client ID=%d, důvod=%s",
                    client.pk,
                    reason,
                )

        total = len(candidates)
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f"DRY RUN: {total} zákazníků by bylo anonymizováno.")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Anonymizováno {total} zákazníků.")
            )

    def _get_retention_days(self, policy_name, override_days):
        """Zjistí dobu uchovávání z policy, override, nebo default."""
        if override_days is not None:
            return override_days

        if policy_name:
            try:
                policy = DataRetentionPolicy.objects.get(
                    name=policy_name, is_active=True
                )
                return policy.retention_days
            except DataRetentionPolicy.DoesNotExist:
                self.stderr.write(
                    self.style.ERROR(
                        f"Politika '{policy_name}' neexistuje nebo není aktivní."
                    )
                )
                raise SystemExit(1)

        # Výchozí: vezmi první aktivní politiku s auto_anonymize=True
        policy = (
            DataRetentionPolicy.objects.filter(is_active=True, auto_anonymize=True)
            .order_by("retention_days")
            .first()
        )
        if policy:
            return policy.retention_days

        # Fallback: 5 let (1825 dní)
        self.stdout.write(
            self.style.WARNING(
                "Žádná aktivní politika s auto_anonymize=True. Používám default 5 let."
            )
        )
        return 1825

    def _find_candidates(self, cutoff_date):
        """Najde zákazníky jejichž data mají být anonymizována."""
        # Zákazníci, kteří ještě nejsou anonymizovaní
        eligible = Client.objects.filter(is_anonymized=False)

        candidates = []
        for client in eligible.annotate(
            last_order_date=Max("order__evidence_termin")
        ):
            should_anonymize = False

            # 1. Explicitní data_retention_until
            if (
                client.data_retention_until
                and client.data_retention_until <= cutoff_date
            ):
                should_anonymize = True

            # 2. Žádná zakázka + starý záznam
            elif client.last_order_date is None:
                # Zákazník bez zakázek — ponechat jen pokud je čerstvý
                # (nemáme created field, tak kontrolujeme retention_until)
                if client.data_retention_until and client.data_retention_until <= timezone.now().date():
                    should_anonymize = True

            # 3. Poslední zakázka starší než cutoff
            elif client.last_order_date <= cutoff_date:
                should_anonymize = True

            if should_anonymize:
                candidates.append(client)

        return candidates

    @staticmethod
    def _get_reason(client, cutoff_date, last_order_date):
        """Vrátí čitelný důvod anonymizace."""
        if client.data_retention_until and client.data_retention_until <= cutoff_date:
            return f"data_retention_until={client.data_retention_until}"
        if last_order_date is None:
            return "žádné zakázky + retention uplynul"
        return f"poslední zakázka: {last_order_date}"
