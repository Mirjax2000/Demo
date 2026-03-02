"""
Šifrování osobních údajů zákazníků — GDPR compliance.

Používá Fernet symmetric encryption (AES-128-CBC + HMAC-SHA256)
z knihovny `cryptography`.

Šifrovaná pole modelu Client:
  - phone  (telefon)
  - email  (e-mail)
  - street (ulice)

Nastavení v .env:
  FIELD_ENCRYPTION_KEY="<vygenerovaný klíč>"

Generování klíče:
  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
"""

import base64
import hashlib
import logging

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.validators import validate_email
from django.db import models

logger = logging.getLogger(__name__)

# ── Fernet helpers ──────────────────────────────────────────────────

_fernet_instance: Fernet | None = None


def _get_fernet_key() -> bytes:
    """
    Odvodí platný 32-byte Fernet klíč z FIELD_ENCRYPTION_KEY.
    Fernet požaduje URL-safe base64-encoded 32-byte klíč.
    Používáme SHA-256 derivaci, takže v .env může být libovolný string.
    """
    raw_key = getattr(settings, "FIELD_ENCRYPTION_KEY", None)
    if not raw_key:
        raise ImproperlyConfigured(
            "FIELD_ENCRYPTION_KEY musí být nastaveno v settings.py (přes .env).\n"
            'Vygenerovat: python -c "from cryptography.fernet import Fernet; '
            'print(Fernet.generate_key().decode())"'
        )
    # Odvodíme 32 bajtů přes SHA-256, pak base64-encode pro Fernet
    derived = hashlib.sha256(raw_key.encode()).digest()
    return base64.urlsafe_b64encode(derived)


def get_fernet() -> Fernet:
    """Vrátí Fernet instanci (singleton pro celý proces)."""
    global _fernet_instance
    if _fernet_instance is None:
        _fernet_instance = Fernet(_get_fernet_key())
    return _fernet_instance


def encrypt_str(plaintext: str) -> str:
    """Zašifruje plaintext string → base64 Fernet token."""
    if not plaintext:
        return plaintext
    f = get_fernet()
    return f.encrypt(plaintext.encode("utf-8")).decode("ascii")


def decrypt_str(ciphertext: str) -> str:
    """Dešifruje Fernet token → plaintext string."""
    if not ciphertext:
        return ciphertext
    f = get_fernet()
    try:
        return f.decrypt(ciphertext.encode("ascii")).decode("utf-8")
    except (InvalidToken, Exception):
        # Fallback: data mohou být ještě v plaintextu (během migrace)
        logger.warning("Fernet decryption failed — returning value as-is.")
        return ciphertext


def is_encrypted(value: str) -> bool:
    """Heuristicky zjistí, zda je hodnota Fernet token."""
    if not value or len(value) < 50:
        return False
    try:
        decoded = base64.urlsafe_b64decode(value + "==")
        return len(decoded) >= 57 and decoded[0] == 0x80
    except Exception:
        return False


# ── Custom encrypted Django model fields ────────────────────────────


class EncryptedTextField(models.TextField):
    """
    TextField s transparentním Fernet šifrováním.

    Data jsou zašifrována před uložením do DB (get_prep_value)
    a dešifrována při čtení (from_db_value).

    V databázi je uložen base64-encoded Fernet token (~120+ znaků).
    Python kód vždy vidí plaintext.
    """

    description = "Šifrované textové pole (Fernet AES-128-CBC + HMAC)"

    def get_prep_value(self, value):
        """Zašifruj před uložením do databáze."""
        value = super().get_prep_value(value)
        if value is None or value == "":
            return value
        str_value = str(value)
        # Ochrana proti dvojitému šifrování
        if is_encrypted(str_value):
            return str_value
        return encrypt_str(str_value)

    def from_db_value(self, value, expression, connection):
        """Dešifruj po načtení z databáze."""
        if value is None or value == "":
            return value
        return decrypt_str(value)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        return name, "app_sprava_montazi.encryption.EncryptedTextField", args, kwargs


class EncryptedCharField(EncryptedTextField):
    """
    Encrypted verze CharField.
    V DB je uloženo jako TEXT (kvůli délce ciphertextu),
    ale validuje max_length na Python straně.
    """

    description = "Šifrované znakové pole"

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        return name, "app_sprava_montazi.encryption.EncryptedCharField", args, kwargs


class EncryptedEmailField(EncryptedTextField):
    """
    Encrypted verze EmailField.
    Zachovává email validaci na Python straně.
    """

    description = "Šifrované emailové pole"
    default_validators = [validate_email]

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        # Odstraníme validators z kwargs — jsou na úrovni třídy
        kwargs.pop("validators", None)
        return name, "app_sprava_montazi.encryption.EncryptedEmailField", args, kwargs

    def formfield(self, **kwargs):
        """Pro Django admin/forms vrátíme EmailField formulářové pole."""
        from django.forms import EmailField as EmailFormField

        defaults = {"form_class": EmailFormField}
        defaults.update(kwargs)
        return super().formfield(**defaults)
