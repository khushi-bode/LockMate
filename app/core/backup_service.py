import json
import os
from app.security.encryption import CryptoService
from app.core.vault_service import VaultService
from app.utils.logger import logger

class BackupService:
    def __init__(self):
        self.crypto = CryptoService()
        self.vault_service = VaultService()

    def export_vault(self, session_data: dict, backup_pw: str, file_path: str) -> bool:
        """Exports the user's vault to an encrypted JSON file."""
        try:
            items = self.vault_service.get_all_items(session_data)
            
            # Prepare payload (we export the raw decrypted items)
            payload = []
            for item in items:
                payload.append({
                    'title': item['title'],
                    'url': item.get('url', ''),
                    'username': item.get('username', ''),
                    'password': item.get('password', ''),
                    'notes': item.get('notes', '')
                })
                
            json_data = json.dumps(payload)
            
            # Generate a new salt for this backup file
            salt = os.urandom(16).hex()
            
            # Encrypt the json data
            encrypted_data = self.crypto.encrypt(backup_pw, salt, json_data)
            
            # Wrap in backup format
            backup = {
                'version': '1.0',
                'salt': salt,
                'data': encrypted_data
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(backup, f)
                
            logger.info(f"Vault exported successfully to {file_path}.")
            return True
        except Exception as e:
            logger.error(f"Error exporting vault: {e}")
            return False
            
    def import_vault(self, session_data: dict, backup_pw: str, file_path: str) -> bool:
        """Imports vault items from an encrypted backup file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                backup = json.load(f)
                
            if 'salt' not in backup or 'data' not in backup:
                logger.error("Invalid backup file format.")
                return False
                
            # Decrypt the payload
            try:
                decrypted_json = self.crypto.decrypt(backup_pw, backup['salt'], backup['data'])
            except Exception as e:
                logger.error(f"Failed to decrypt backup. Incorrect password? {e}")
                return False
                
            items = json.loads(decrypted_json)
            
            # Import items
            for item in items:
                self.vault_service.add_item(
                    session_data,
                    title=item.get('title', 'Imported Item'),
                    url=item.get('url', ''),
                    username=item.get('username', ''),
                    password=item.get('password', ''),
                    notes=item.get('notes', '')
                )
                
            logger.info(f"Successfully imported {len(items)} items from {file_path}.")
            return True
        except Exception as e:
            logger.error(f"Error importing vault: {e}")
            return False
