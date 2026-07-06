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
        with open(script_path, "r", encoding="utf-8") as f:
            sql_script = f.read()

        with get_db_connection() as conn:
            conn.executescript(sql_script)
            logger.info(f"Successfully executed SQL script: {script_path}")
    except Exception as e:
        logger.error(f"Failed to execute SQL script {script_path}: {e}")
        raise


def initialize_database():
    """Ensures database schema and all migrations are applied on startup."""
    migrations_dir = config.BASE_DIR / "app" / "data" / "migrations"

    try:
        with get_db_connection() as conn:
            # Create table to track applied migrations
            conn.execute("""
                CREATE TABLE IF NOT EXISTS applied_migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT UNIQUE NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Legacy support: if users table exists, assume 001_initial_schema.sql was applied
            cursor = conn.execute(
                "SELECT count(name) FROM sqlite_master WHERE type='table' AND name='users'"
            )
            if cursor.fetchone()[0] == 1:
                conn.execute(
                    "INSERT OR IGNORE INTO applied_migrations (filename) VALUES ('001_initial_schema.sql')"
                )

            conn.commit()
    except Exception as e:
        logger.error(f"Failed to set up migrations tracking: {e}")
        return

    if not migrations_dir.exists():
        logger.error(f"Migrations directory not found at {migrations_dir}")
        return

    # Sort migration files to apply them in order
    migration_files = sorted(
        [f for f in migrations_dir.iterdir() if f.suffix == ".sql"]
    )

    for migration_file in migration_files:
        try:
            with get_db_connection() as conn:
                cursor = conn.execute(
                    "SELECT 1 FROM applied_migrations WHERE filename = ?",
                    (migration_file.name,),
                )
                if cursor.fetchone():
                    continue  # Migration already applied

            # Execute the migration script
            run_script(str(migration_file))

            # Record successful application
            with get_db_connection() as conn:
                conn.execute(
                    "INSERT INTO applied_migrations (filename) VALUES (?)",
                    (migration_file.name,),
                )
                conn.commit()

            logger.info(f"Successfully applied migration: {migration_file.name}")
        except Exception as e:
            logger.error(
                f"Critical error applying migration {migration_file.name}: {e}"
            )
            break  # Stop applying further migrations if one fails
