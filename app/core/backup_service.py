import os
import shutil
import sqlite3
from app.utils.logger import logger
import config


class BackupService:
    def __init__(self):
        pass

    def export_database(self, destination_path: str) -> bool:
        """Exports the raw SQLite database."""
        try:
            logger.info("Backup started")
            if not os.path.exists(config.DB_PATH):
                logger.error("Database file not found.")
                return False

            shutil.copy2(config.DB_PATH, destination_path)
            logger.info(f"Backup completed: copied to {destination_path}")
            return True
        except Exception as e:
            logger.error(f"Error during backup: {e}")
            return False

    def import_database(self, source_path: str) -> bool:
        """Imports an SQLite database and validates it."""
        try:
            logger.info("Restore started")
            if not os.path.exists(source_path):
                logger.error("Source file not found.")
                return False

            # Validate SQLite database
            try:
                conn = sqlite3.connect(source_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                conn.close()

                required_tables = {"users", "vault_items"}
                if not required_tables.issubset(set(tables)):
                    logger.error("Restore failed: Invalid LockMate database format.")
                    return False
            except Exception as e:
                logger.error(f"Restore failed: Not a valid SQLite database. {e}")
                return False

            shutil.copy2(source_path, config.DB_PATH)
            logger.info("Restore completed")
            return True
        except Exception as e:
            logger.error(f"Error during restore: {e}")
            return False
