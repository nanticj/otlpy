from base64 import b64decode

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


def aes_cbc_base64_dec(key: str, iv: str, cipher_text: str) -> str:
    cipher = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv.encode("utf-8"))
    return bytes.decode(
        unpad(cipher.decrypt(b64decode(cipher_text)), AES.block_size)
    )
