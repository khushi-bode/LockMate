import datetime
from collections import Counter
from app.data.vault_repository import VaultRepository
from app.security.encryption import CryptoService
from app.core.password_generator import PasswordGeneratorService
from app.utils.logger import logger

class VaultService:
    """Business logic layer for managing vault items with transparent encryption."""
    
    def __init__(self):
        self.vault_repo = VaultRepository()
        self.crypto = CryptoService()
        self.pw_gen = PasswordGeneratorService()
        
    def add_item(self, session_data: dict, title: str, url: str, username: str, password: str, notes: str) -> int:
        user_id = session_data['user_id']
        mp = session_data['master_password']
        salt = session_data['salt']
        
        encrypted_pw = self.crypto.encrypt(mp, salt, password)
        return self.vault_repo.add_item(user_id, title, url, username, encrypted_pw, notes)
        
    def update_item(self, item_id: int, session_data: dict, title: str, url: str, username: str, password: str, notes: str) -> bool:
        user_id = session_data['user_id']
        mp = session_data['master_password']
        salt = session_data['salt']
        
        encrypted_pw = self.crypto.encrypt(mp, salt, password)
        return self.vault_repo.update_item(item_id, user_id, title, url, username, encrypted_pw, notes)

    def delete_item(self, item_id: int, session_data: dict) -> bool:
        user_id = session_data['user_id']
        return self.vault_repo.delete_item(item_id, user_id)
        
    def get_all_items(self, session_data: dict) -> list:
        user_id = session_data['user_id']
        mp = session_data['master_password']
        salt = session_data['salt']
        
        items = self.vault_repo.get_items_by_user_id(user_id)
        for item in items:
            if item.get('encrypted_password'):
                try:
                    item['password'] = self.crypto.decrypt(mp, salt, item['encrypted_password'])
                except Exception as e:
                    logger.error(f"Failed to decrypt password for item {item['id']}: {e}")
                    item['password'] = "ERROR_DECRYPTING"
        return items

    def search_items(self, session_data: dict, query: str) -> list:
        user_id = session_data['user_id']
        mp = session_data['master_password']
        salt = session_data['salt']
        
        items = self.vault_repo.search_items(user_id, query)
        for item in items:
            if item.get('encrypted_password'):
                try:
                    item['password'] = self.crypto.decrypt(mp, salt, item['encrypted_password'])
                except Exception as e:
                    logger.error(f"Failed to decrypt password for item {item['id']}: {e}")
                    item['password'] = "ERROR_DECRYPTING"
        return items

    def get_vault_health(self, session_data: dict) -> dict:
        """Analyzes all items and returns health metrics."""
        items = self.get_all_items(session_data)
        
        total = len(items)
        weak_count = 0
        passwords = []
        old_count = 0
        
        now = datetime.datetime.utcnow() # SQLite CURRENT_TIMESTAMP is UTC
        
        for item in items:
            pw = item.get('password', '')
            passwords.append(pw)
            
            # Strength
            _, _, score = self.pw_gen.calculate_strength(pw)
            if score < 0.5:
                weak_count += 1
                
            # Age
            updated_str = item.get('updated_at')
            if not updated_str:
                updated_str = item.get('created_at')
                
            if updated_str:
                try:
                    # SQLite default CURRENT_TIMESTAMP format is 'YYYY-MM-DD HH:MM:SS'
                    updated = datetime.datetime.strptime(updated_str, '%Y-%m-%d %H:%M:%S')
                    if (now - updated).days > 90:
                        old_count += 1
                except Exception as e:
                    logger.warning(f"Could not parse date {updated_str}: {e}")
                    
        pw_counts = Counter(passwords)
        reused_count = sum(1 for pw, count in pw_counts.items() if count > 1 and pw)
        
        return {
            'total': total,
            'weak': weak_count,
            'reused': reused_count,
            'old': old_count
        }
