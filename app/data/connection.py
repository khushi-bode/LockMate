import sqlite3
import config
from app.utils.logger import logger

def get_db_connection() -> sqlite3.Connection:
    """Returns a connected SQLite database instance configured with row factory."""
    # Ensure data directory exists
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        conn = sqlite3.connect(config.DB_PATH)
        conn.row_factory = sqlite3.Row
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Failed to connect to database at {config.DB_PATH}: {e}")
        raise

def run_script(script_path: str):
    """Executes a SQL script file against the database."""
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
            
        with get_db_connection() as conn:
            conn.executescript(sql_script)
            logger.info(f"Successfully executed SQL script: {script_path}")
    except Exception as e:
        logger.error(f"Failed to execute SQL script {script_path}: {e}")
        raise

def initialize_database():
    """Ensures database schema is created on startup."""
    schema_path = config.BASE_DIR / "app" / "data" / "migrations" / "001_initial_schema.sql"
    if schema_path.exists():
        run_script(str(schema_path))
    else:
        logger.error(f"Migration script not found at {schema_path}")
