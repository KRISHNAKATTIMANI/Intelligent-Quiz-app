import re
from email_validator import validate_email, EmailNotValidError


def validate_username(username: str) -> tuple[bool, str]:
    """
    Validate username format
    Returns: (is_valid, error_message)
    """
    if not username:
        return False, "Username is required"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if len(username) > 50:
        return False, "Username must be less than 50 characters"
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens"
    
    return True, ""


def validate_email_format(email: str) -> tuple[bool, str]:
    """
    Validate email format
    Returns: (is_valid, error_message)
    """
    try:
        validate_email(email, check_deliverability=False)
        return True, ""
    except EmailNotValidError as e:
        return False, str(e)


def validate_registration_data(data: dict) -> tuple[bool, str]:
    """
    Validate complete registration data
    Returns: (is_valid, error_message)
    """
    required_fields = ['username', 'email', 'password', 'full_name']
    
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"{field} is required"
    
    # Validate username
    is_valid, error = validate_username(data['username'])
    if not is_valid:
        return False, error
    
    # Validate email
    is_valid, error = validate_email_format(data['email'])
    if not is_valid:
        return False, error
    
    return True, ""
