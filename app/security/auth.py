import bcrypt
from app.data.user_repository import UserRepository
from app.utils.logger import logger


class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()

    def hash_password(self, password: str) -> tuple[str, str]:
        """Hashes a password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        # Store salt alongside hash or just return hash (bcrypt includes salt in hash)
        return hashed.decode("utf-8"), salt.decode("utf-8")

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verifies a plain password against a hashed password."""
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

    def register_user(self, username: str, password: str) -> tuple[bool, str]:
        """Registers a new user. Returns (success, message)."""
        if not username or not password:
            return False, "Username and password are required."

        try:
            existing_user = self.user_repo.get_user_by_username(username)
            if existing_user:
                return False, "Username already exists."

            hashed_pw, salt = self.hash_password(password)
            self.user_repo.create_user(username, hashed_pw, salt)
            logger.info(f"User '{username}' registered successfully.")
            return True, "Registration successful."
        except Exception as e:
            logger.error(f"Error during registration: {e}")
            return False, "An error occurred during registration."

    def login_user(self, username: str, password: str) -> tuple[bool, str, dict]:
        """Validates login credentials. Returns (success, message, session_data)."""
        if not username or not password:
            return False, "Username and password are required.", None

        try:
            user = self.user_repo.get_user_by_username(username)
            if not user:
                return False, "Invalid username or password.", None

            if self.verify_password(password, user["password_hash"]):
                logger.info(f"User '{username}' logged in successfully.")
                session_data = {
                    "user_id": user["id"],
                    "username": user["username"],
                    "master_password": password,
                    "salt": user["salt"],
                }
                return True, "Login successful!", session_data
            else:
                logger.warning(f"Failed login attempt for user '{username}'.")
                return False, "Invalid username or password.", None
        except Exception as e:
            logger.error(f"Error during login validation: {e}")
            return False, "An error occurred during login.", None
