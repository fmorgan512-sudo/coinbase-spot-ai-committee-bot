import time
import jwt  # PyJWT
from cryptography.hazmat.primitives import serialization
from .config import settings


def _load_private_key():
      if not settings.coinbase_api_private_key_pem.strip():
                return None
            key = settings.coinbase_api_private_key_pem.encode("utf-8")
    return serialization.load_pem_private_key(key, password=None)


def build_jwt(method: str, path: str, host: str = "api.coinbase.com", ttl_seconds: int = 60) -> str:
      """
          Coinbase CDP style: sign JWT with your API key secret/private key, then use:
                  Authorization: Bearer <JWT>
                      """
    key = _load_private_key()
    if key is None:
              raise RuntimeError("Missing COINBASE_API_PRIVATE_KEY_PEM")

    now = int(time.time())
    payload = {
              "sub": settings.coinbase_api_key_name,
              "iss": "coinbase-cloud",
              "nbf": now,
              "exp": now + ttl_seconds,
              "uri": f"{method.upper()} {host}{path}",
    }
    token = jwt.encode(payload, key, algorithm="ES256", headers={"kid": settings.coinbase_api_key_name})
    return token
