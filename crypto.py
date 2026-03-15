import os
import base64
import json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

KEY = bytes.fromhex(
    os.getenv(
        "DATA_ENCRYPTION_KEY",
        "a"*64  # dev fallback
    )
)

# =====================================================

def encrypt_data(data: dict):

    aes = AESGCM(KEY)

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

# =====================================================

def decrypt_data(payload: dict):

    aes = AESGCM(KEY)

    ciphertext = base64.b64decode(payload["cipher"])
    nonce = base64.b64decode(payload["nonce"])

    plaintext = aes.decrypt(
        nonce,
        ciphertext,
        None
    )

    return json.loads(plaintext.decode())
