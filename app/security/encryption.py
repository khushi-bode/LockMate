import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from app.utils.logger import logger

class CryptoService:
    """Handles encryption and decryption of vault data using Fernet and PBKDF2."""
    
    # 600,000 is the recommended iteration count for PBKDF2 HMAC SHA256 as of 2023.
    # It provides strong resistance against brute-force attacks.
    ITERATIONS = 600_000

    def _derive_key(self, master_password: str, salt: str) -> bytes:
        """
        Derives a strong cryptographic key from a master password and salt.
        Returns a url-safe base64-encoded 32-byte key required by Fernet.
        """
        try:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt.encode('utf-8'),
                iterations=self.ITERATIONS,
            )
            key = base64.urlsafe_b64encode(kdf.derive(master_password.encode('utf-8')))
            return key
        except Exception as e:
            logger.error(f"Failed to derive key: {e}")
            raise

    def encrypt(self, master_password: str, salt: str, plaintext: str) -> str:
        """
        Encrypts plaintext data using a derived key.
        Returns the url-safe base64-encoded encrypted string.
        """
        if not plaintext:
            return ""
            
        try:
            key = self._derive_key(master_password, salt)
            fernet = Fernet(key)
            encrypted_data = fernet.encrypt(plaintext.encode('utf-8'))
            return encrypted_data.decode('utf-8')
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise

    def decrypt(self, master_password: str, salt: str, ciphertext: str) -> str:
        """
        Decrypts ciphertext back to plaintext using the derived key.
        Returns the original plaintext string.
        """
        if not ciphertext:
            return ""
            
        try:
            key = self._derive_key(master_password, salt)
            fernet = Fernet(key)
            decrypted_data = fernet.decrypt(ciphertext.encode('utf-8'))
            return decrypted_data.decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
