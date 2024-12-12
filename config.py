import secrets
secret_key = secrets.token_hex(16)
class Config:
    SECRET_KEY = secret_key
