import bcrypt


def check_password(password: str, password_hash: str):
    """check password encryption and decryption

    Args:
        password (str): _description_
        password_hash (str): _description_

    Returns:
        _type_: encrypted password
    """
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def hash_password(password: str):
    """password encryption

    Args:
        password (str): _description_

    Returns:
        _type_: encrypted password
    """
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
