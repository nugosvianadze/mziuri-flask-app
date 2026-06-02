from typing import Optional, Any

from werkzeug.security import generate_password_hash


class AuthService:

    def validate_signup_form(self, first_name: Optional[str], last_name: Optional[str],
                             password: str, email: str, age: int) -> dict[str, Any]:
        errors: list = []
        hashed_password = None

        if email:
            if "@" not in email or "." not in email:
                errors.append("Incorrect email format")
        if age:
            try:
                age = int(age)
                if age < 16 or age > 120:
                    errors.append("Incorrect age format")
            except Exception as e:
                errors.append("Incorrect age format")

        if password:
            if len(password) < 6 or len(password) > 64:
                errors.append("Password length should be in range 6-64")
            else:
                hashed_password = self.hash_password(password)
                if not hashed_password.get("success"):
                    errors.append(hashed_password.get("message"))
        if errors:
            return {
                "errors": errors
            }

        return {
            "success": True,
            "hashed_password": hashed_password
        }

    @staticmethod
    def hash_password(password: str) -> dict:
        try:
            hashed_password = generate_password_hash(password=password)
        except Exception as e:
            print(e)
            return {
                "success": False,
                "message": str(e)
            }
        return {
            "success": True,
            "hash_password": hashed_password
        }
