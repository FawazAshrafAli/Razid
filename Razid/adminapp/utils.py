from cryptography.fernet import Fernet
from django.conf import settings

# Use the key from settings
cipher_suite = Fernet(settings.ENCRYPTION_KEY)

def encrypt(data):
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt(token):
    return cipher_suite.decrypt(token.encode()).decode()
