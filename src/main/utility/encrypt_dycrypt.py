import base64
import sys
import os
from src.main.utility.logging_config import *
from Cryptodome.Cipher import AES
from Cryptodome.Protocol.KDF import PBKDF2
from Cryptodome.Util.Padding import pad, unpad
import configparser

config_file_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'conf.ini')

conf = configparser.ConfigParser()
conf.read(config_file_path)  # Ensure correct file path


class AESCipher:
    def __init__(self, key=None, salt=None):
        # Use provided key and salt or fallback to config values
        self.key = key if key else conf.get('Encryption', 'key')
        self.salt = salt.encode('utf-8') if salt else conf.get('Encryption', 'salt').encode('utf-8')

        if not (self.key and self.salt):
            logger.error("Missing key or salt in configuration.")
            sys.exit(1)

        self.bs = AES.block_size
        self.aes_key = self._generate_key()

    def _generate_key(self):
        """Generate a 32-byte private key using PBKDF2."""
        try:
            kdf = PBKDF2(self.key, self.salt, 64, count=100000)
            return kdf[:32]  # AES-256 key
        except Exception as e:
            logger.error("Error generating private key: %s", e)
            sys.exit(1)

    def encrypt(self, raw_text):
        """Encrypts a given text using AES CBC mode with a randomly generated IV."""
        try:
            raw = pad(raw_text.encode(), self.bs)
            iv = os.urandom(self.bs)  # Generate a random IV
            cipher = AES.new(self.aes_key, AES.MODE_CBC, iv)
            encrypted_data = cipher.encrypt(raw)
            return base64.b64encode(iv + encrypted_data).decode('utf-8')  # Prepend IV
        except Exception as e:
            logger.error("Encryption error: %s", e)
            return None

    def decrypt(self, enc_text):
        """Decrypts an AES CBC encrypted text where IV is extracted from the ciphertext."""
        try:
            enc_data = base64.b64decode(enc_text)
            iv = enc_data[:self.bs]  # Extract IV from the first block
            cipher = AES.new(self.aes_key, AES.MODE_CBC, iv)
            decrypted_data = cipher.decrypt(enc_data[self.bs:])
            return unpad(decrypted_data, self.bs).decode('utf-8')
        except Exception as e:
            logger.error("Decryption error: %s", e)
            return None


