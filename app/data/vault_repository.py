from app.data.connection import get_db_connection
from app.utils.logger import logger

class VaultRepository:
    """Handles data access for Vault items."""
    
    def add_item(self, user_id: int, title: str, url: str, username: str, encrypted_password: str, notes: str) -> int:
        """Inserts a new vault item for a user and returns its ID."""
        sql = """
            INSERT INTO vault_items (user_id, title, url, username, encrypted_password, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (user_id, title, url, username, encrypted_password, notes))
                conn.commit()
                logger.info(f"Vault item '{title}' added for user_id={user_id}.")
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to add vault item for user_id={user_id}: {e}")
            raise

    def get_items_by_user_id(self, user_id: int) -> list:
        """Retrieves all vault items belonging to a specific user."""
        sql = "SELECT * FROM vault_items WHERE user_id = ?"
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (user_id,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching vault items for user_id={user_id}: {e}")
            raise
            
    def delete_item(self, item_id: int, user_id: int) -> bool:
        """Deletes a specific vault item ensuring it belongs to the user."""
        sql = "DELETE FROM vault_items WHERE id = ? AND user_id = ?"
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (item_id, user_id))
                conn.commit()
                if cursor.rowcount > 0:
                    logger.info(f"Deleted vault item {item_id}.")
                    return True
                return False
        except Exception as e:
            logger.error(f"Failed to delete vault item {item_id}: {e}")
            raise

    def update_item(self, item_id: int, user_id: int, title: str, url: str, username: str, encrypted_password: str, notes: str) -> bool:
        """Updates an existing vault item."""
        sql = """
            UPDATE vault_items 
            SET title = ?, url = ?, username = ?, encrypted_password = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND user_id = ?
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (title, url, username, encrypted_password, notes, item_id, user_id))
                conn.commit()
                if cursor.rowcount > 0:
                    logger.info(f"Updated vault item {item_id}.")
                    return True
                return False
        except Exception as e:
            logger.error(f"Failed to update vault item {item_id}: {e}")
            raise

    def search_items(self, user_id: int, query: str) -> list:
        """Searches vault items by title or username."""
        sql = "SELECT * FROM vault_items WHERE user_id = ? AND (title LIKE ? OR username LIKE ?)"
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                like_query = f"%{query}%"
                cursor.execute(sql, (user_id, like_query, like_query))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error searching vault items for user_id={user_id}: {e}")
            raise

