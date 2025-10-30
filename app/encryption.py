from cryptography.fernet import Fernet
from app.config import ENCRYPT_KEY  # возьмём из .env

cipher = Fernet(ENCRYPT_KEY.encode() if isinstance(ENCRYPT_KEY, str) else ENCRYPT_KEY)

def encrypt_data(data: str) -> str:
    #Шифрует строку
    return cipher.encrypt(data.encode()).decode()

def decrypt_data(token: str) -> str:
    #Расшифровывает строку
    return cipher.decrypt(token.encode()).decode()
