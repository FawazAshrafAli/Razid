from cryptography.fernet import Fernet

# Generate a key and instantiate a Fernet instance
# Note: In a real application, store the key securely and don't regenerate it every time
key = Fernet.generate_key()
cipher_suite = Fernet(key)
print(key.decode())

def encrypt(text):
    return cipher_suite.encrypt(text.encode()).decode()

def decrypt(encrypted_text):
    return cipher_suite.decrypt(encrypted_text.encode()).decode()