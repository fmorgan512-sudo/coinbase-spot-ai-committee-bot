"""
Secure key storage module using Fernet symmetric encryption.
Keys are encrypted at rest using a password-derived key.
"""
from __future__ import annotations
import os
import json
import base64
import hashlib
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

KEY_FILE = Path("/data/keys.enc")
SALT_FILE = Path("/data/keys.salt")


def _derive_key(password: str, salt: bytes) -> bytes:
      """Derive a Fernet key from password using PBKDF2."""
      kdf = PBKDF2HMAC(
          algorithm=hashes.SHA256(),
          length=32,
          salt=salt,
          iterations=480000,
      )
      return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def _get_or_create_salt() -> bytes:
      """Get existing salt or create new one."""
      if SALT_FILE.exists():
                return SALT_FILE.read_bytes()
            salt = os.urandom(16)
    SALT_FILE.parent.mkdir(parents=True, exist_ok=True)
    SALT_FILE.write_bytes(salt)
    return salt


def save_keys(password: str, keys: dict) -> bool:
      """Encrypt and save keys to disk."""
    try:
              salt = _get_or_create_salt()
              fernet_key = _derive_key(password, salt)
              fernet = Fernet(fernet_key)
              encrypted = fernet.encrypt(json.dumps(keys).encode())
              KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
              KEY_FILE.write_bytes(encrypted)
              return True
except Exception as e:
        print(f"Error saving keys: {e}")
        return False


def load_keys(password: str) -> dict | None:
      """Load and decrypt keys from disk."""
    if not KEY_FILE.exists():
              return None
          try:
                    salt = _get_or_create_salt()
                    fernet_key = _derive_key(password, salt)
                    fernet = Fernet(fernet_key)
                    encrypted = KEY_FILE.read_bytes()
                    decrypted = fernet.decrypt(encrypted)
                    return json.loads(decrypted.decode())
except InvalidToken:
        return None  # Wrong password
except Exception as e:
        print(f"Error loading keys: {e}")
        return None


def keys_exist() -> bool:
      """Check if encrypted keys file exists."""
    return KEY_FILE.exists()


def delete_keys() -> bool:
      """Delete stored keys."""
    try:
              if KEY_FILE.exists():
                            KEY_FILE.unlink()
                        if SALT_FILE.exists():
                                      SALT_FILE.unlink()
                                  return True
except Exception:
        return False
