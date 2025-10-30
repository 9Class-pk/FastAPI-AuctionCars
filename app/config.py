import os
from dotenv import load_dotenv


load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_LIFETIME = 30
REFRESH_TOKEN_LIFETIME = 3
ENCRYPT_KEY = os.getenv('ENCRYPT_KEY')


class Settings:
    GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
    GITHUB_KEY = os.getenv('GITHUB_KEY')
    GITHUB_LOGIN_CALLBACK = os.getenv('GITHUB_LOGIN_CALLBACK')

    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_KEY = os.getenv('GOOGLE_KEY')
    GOOGLE_LOGIN_CALLBACK = os.getenv('GOOGLE_LOGIN_CALLBACK')


settings = Settings()


GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')