import bcrypt

class SecurityUtils:
    @staticmethod
    def hash_password(password: str) -> str:
        """Genera un hash bcrypt con salt automático."""
        return bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(rounds=12)
        ).decode("utf-8")


    @staticmethod
    def verify_password(plain: str, stored: str) -> bool:
        if stored.startswith("$2b$"):
            return bcrypt.checkpw(
                plain.encode("utf-8"),
                stored.encode("utf-8")
            )
        # Fallback temporal: texto plano (usuarios legados sin migrar)
        return plain == stored
