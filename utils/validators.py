from utils.consts import (PASSWORD_ERROR_MSGS,
                    SYMBOLS_CONST, EMAIL_ERROR_DEFAULT)


def validate_password(password: str) -> dict:
    errors: list = list()

    includes_upper = any(char.isupper() for char in password)
    if len(password) < 6:
        errors.append(PASSWORD_ERROR_MSGS["min_passw_len"])
    if not includes_upper:
        errors.append(PASSWORD_ERROR_MSGS["upper_case"])

    includes_symbol = any(char in SYMBOLS_CONST for char in password)

    if not includes_symbol:
        errors.append(PASSWORD_ERROR_MSGS["symbols"])

    if errors:
        return {
            'success': False,
            "errors": errors
        }
    return {
        'success': True,
        'error': None
    }

def validate_email(email: str) -> dict:
    if "@" not in email:
        return {
            "success": False,
            "errors": [EMAIL_ERROR_DEFAULT]
        }
    domain = email.split("@")[1]
    if "." not in domain:
        return {
            "success": False,
            "errors": [EMAIL_ERROR_DEFAULT]
        }
    return {
        "success": True,
        "errors": None
    }