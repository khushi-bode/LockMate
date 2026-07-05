from app.data.connection import get_db_connection
from app.utils.logger import logger

class UserRepository:
    """Handles data access for User entities."""
    
    def create_user(self, username: str, password_hash: str, salt: str) -> int:
        """Inserts a new user into the database and returns the new ID."""
        sql = """
            INSERT INTO users (username, password_hash, salt)
            VALUES (?, ?, ?)
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (username, password_hash, salt))
                conn.commit()
                logger.info(f"User '{username}' created successfully.")
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to create user '{username}': {e}")
            raise

    def get_user_by_username(self, username: str) -> dict:
        """Retrieves a user by username, returning a dictionary or None."""
        sql = "SELECT * FROM users WHERE username = ?"
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (username,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error fetching user by username '{username}': {e}")
            raise

    def get_user_settings(self, user_id: int) -> dict:
        """Retrieves user settings or returns default."""
        sql = "SELECT auto_lock_minutes FROM user_settings WHERE user_id = ?"
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (user_id,))
                row = cursor.fetchone()
                if row:
                    return dict(row)
                else:
                    return {'auto_lock_minutes': 5}
        except Exception as e:
            logger.error(f"Error fetching settings for user {user_id}: {e}")
            return {'auto_lock_minutes': 5}

    def update_user_settings(self, user_id: int, auto_lock_minutes: int) -> bool:
        """Updates user settings, inserting if not exists."""
        sql = """
            INSERT OR REPLACE INTO user_settings (user_id, auto_lock_minutes)
            VALUES (?, ?)
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (user_id, auto_lock_minutes))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to update settings for user {user_id}: {e}")
            return False
