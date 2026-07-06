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

    def add_item(
        self,
        session_data: dict,
        title: str,
        url: str,
        username: str,
        password: str,
        notes: str,
        category: str = "Other",
    ) -> int:
        user_id = session_data["user_id"]
        mp = session_data["master_password"]
        salt = session_data["salt"]

        encrypted_pw = self.crypto.encrypt(mp, salt, password)
        return self.vault_repo.add_item(
            user_id, title, url, username, encrypted_pw, notes, category
        )

    def update_item(
        self,
        item_id: int,
        session_data: dict,
        title: str,
        url: str,
        username: str,
        password: str,
        notes: str,
        category: str = "Other",
    ) -> bool:
        logger.info(
            f"VaultService: Updating item {item_id} for user {session_data.get('username')}"
        )
        user_id = session_data["user_id"]
        mp = session_data["master_password"]
        salt = session_data["salt"]

        encrypted_pw = self.crypto.encrypt(mp, salt, password)
        return self.vault_repo.update_item(
            item_id, user_id, title, url, username, encrypted_pw, notes, category
        )

    def delete_item(self, item_id: int, session_data: dict) -> bool:
        user_id = session_data["user_id"]
        try:
            success = self.vault_repo.delete_item(item_id, user_id)
            if success:
                logger.info(f"VaultService: Delete successful for item {item_id}")
            return success
        except Exception as e:
            logger.error(f"VaultService: Error deleting item {item_id}: {e}")
            return False

    def get_all_items(self, session_data: dict) -> list:
        user_id = session_data["user_id"]
        mp = session_data["master_password"]
        salt = session_data["salt"]

        items = self.vault_repo.get_items_by_user_id(user_id)
        for item in items:
            if item.get("encrypted_password"):
                try:
                    item["password"] = self.crypto.decrypt(
                        mp, salt, item["encrypted_password"]
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to decrypt password for item {item['id']}: {e}"
                    )
                    item["password"] = "ERROR_DECRYPTING"
        return items

    def search_items(self, session_data: dict, query: str) -> list:
        logger.info(
            f"VaultService: Searching for '{query}' by user {session_data.get('username')}"
        )
        user_id = session_data["user_id"]
        mp = session_data["master_password"]
        salt = session_data["salt"]

        items = self.vault_repo.search_items(user_id, query)
        for item in items:
            if item.get("encrypted_password"):
                try:
                    item["password"] = self.crypto.decrypt(
                        mp, salt, item["encrypted_password"]
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to decrypt password for item {item['id']}: {e}"
                    )
                    item["password"] = "ERROR_DECRYPTING"
        return items

    def get_vault_health(self, session_data: dict) -> dict:
        """Analyzes all items and returns health metrics."""
        items = self.get_all_items(session_data)

        total = len(items)
        weak_count = 0
        strong_count = 0
        fav_count = 0

        for item in items:
            pw = item.get("password", "")

            _, _, score = self.pw_gen.calculate_strength(pw)
            if score < 0.5:
                weak_count += 1
            elif score >= 0.7:
                strong_count += 1

            if item.get("is_favorite") == 1:
                fav_count += 1

        return {
            "total": total,
            "favorites": fav_count,
            "weak": weak_count,
            "strong": strong_count,
        }

    def toggle_favorite(self, item_id: int, session_data: dict) -> bool:
        user_id = session_data["user_id"]
        try:
            return self.vault_repo.toggle_favorite(item_id, user_id)
        except Exception as e:
            logger.error(
                f"VaultService: Error toggling favorite for item {item_id}: {e}"
            )
            return False

    def get_favorites(self, session_data: dict) -> list:
        user_id = session_data["user_id"]
        mp = session_data["master_password"]
        salt = session_data["salt"]

        items = self.vault_repo.get_favorites(user_id)
        for item in items:
            if item.get("encrypted_password"):
                try:
                    item["password"] = self.crypto.decrypt(
                        mp, salt, item["encrypted_password"]
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to decrypt password for item {item['id']}: {e}"
                    )
                    item["password"] = "ERROR_DECRYPTING"
        return items
