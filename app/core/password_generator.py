import secrets
import string
import customtkinter as ctk
from app.utils.logger import logger

class PasswordGeneratorService:
    """Generates cryptographically secure random passwords."""
    
    LOWERCASE = string.ascii_lowercase
    UPPERCASE = string.ascii_uppercase
    DIGITS = string.digits
    SYMBOLS = string.punctuation

    def generate(self, length: int, use_upper: bool, use_digits: bool, use_symbols: bool) -> str:
        """
        Generates a random password with the specified character options.
        Guarantees at least one character from each enabled set.
        """
        pool = self.LOWERCASE  # Always includes lowercase
        required = [secrets.choice(self.LOWERCASE)]
        
        if use_upper:
            pool += self.UPPERCASE
            required.append(secrets.choice(self.UPPERCASE))
        if use_digits:
            pool += self.DIGITS
            required.append(secrets.choice(self.DIGITS))
        if use_symbols:
            pool += self.SYMBOLS
            required.append(secrets.choice(self.SYMBOLS))
            
        # Fill remaining characters from the full pool
        remaining_length = length - len(required)
        remaining = [secrets.choice(pool) for _ in range(remaining_length)]
        
        # Combine required + remaining and shuffle
        password_chars = required + remaining
        secrets.SystemRandom().shuffle(password_chars)
        
        return ''.join(password_chars)

    def calculate_strength(self, password: str) -> tuple[str, str, float]:
        """
        Calculates the strength of a given password.
        Returns (label, color, score_0_to_1).
        """
        if not password:
            return "None", "gray", 0.0
            
        score = 0
        length = len(password)
        
        # Length score (up to 40 points)
        if length >= 20:
            score += 40
        elif length >= 16:
            score += 30
        elif length >= 12:
            score += 20
        elif length >= 8:
            score += 10
            
        # Variety score (up to 60 points)
        if any(c in string.ascii_lowercase for c in password):
            score += 10
        if any(c in string.ascii_uppercase for c in password):
            score += 15
        if any(c in string.digits for c in password):
            score += 15
        if any(c in string.punctuation for c in password):
            score += 20
            
        # Normalize
        normalized = min(score / 100, 1.0)
        
        if normalized >= 0.8:
            return "Strong", "#00b894", normalized
        elif normalized >= 0.5:
            return "Medium", "#fdcb6e", normalized
        else:
            return "Weak", "#d63031", normalized
