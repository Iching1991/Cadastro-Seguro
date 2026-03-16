import os
import base64
import json

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# ─────────────────────────────────────────────
# KEY LOADING
# ─────────────────────────────────────────────
def load_key() -> bytes:

    key_hex = os.getenv("DATA_ENCRYPTION_KEY")

    if not key_hex:
        # fallback apenas para ambiente de desenvolvimento
        key_hex = "a" * 64

    key = bytes.fromhex(key_hex)

    if len(key) not in (16, 24, 32):
        raise ValueError(
            "DATA_ENCRYPTION_KEY deve ter 32 bytes (64 hex)."
        )

    return key


KEY = load_key()

aes = AESGCM(KEY)


# ─────────────────────────────────────────────
# ENCRYPT
# ─────────────────────────────────────────────
def encrypt_data(data: dict) -> dict:

    nonce = os.urandom(12)

    plaintext = json.dumps(data).encode()

    ciphertext = aes.encrypt(
        nonce,
        plaintext,
        None
    )

    return {
        "cipher": base64.b64encode(ciphertext).decode(),
        "nonce": base64.b64encode(nonce).decode()
    }


# ─────────────────────────────────────────────
# DECRYPT
# ─────────────────────────────────────────────
def decrypt_data(payload: dict) -> dict:

    if "cipher" not in payload or "nonce" not in payload:
        raise ValueError("Payload inválido.")

    ciphertext = base64.b64decode(payload["cipher"])

    nonce = base64.b64decode(payload["nonce"])

    plaintext = aes.decrypt(
        nonce,
        ciphertext,
        None
    )

    return json.loads(plaintext.decode())
