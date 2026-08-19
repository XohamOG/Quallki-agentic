from __future__ import annotations

from quallki_agentic.crypto.aes_stream import AESStreamCipher


class MessageCrypto:
    def __init__(self) -> None:
        self._cipher = AESStreamCipher()

    def seal(self, payload: str) -> str:
        return self._cipher.encrypt(payload)

    def open(self, payload: str) -> str:
        return self._cipher.decrypt(payload)
