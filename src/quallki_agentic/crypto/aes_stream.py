from __future__ import annotations

import base64
from dataclasses import dataclass


@dataclass
class AESStreamCipher:
    """Placeholder implementation until cryptography-backed AES-GCM is integrated."""

    def encrypt(self, plaintext: str) -> str:
        return base64.b64encode(plaintext.encode("utf-8")).decode("ascii")

    def decrypt(self, ciphertext: str) -> str:
        return base64.b64decode(ciphertext.encode("ascii")).decode("utf-8")
