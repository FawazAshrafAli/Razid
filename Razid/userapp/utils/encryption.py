from cryptography.fernet import Fernet

key = b'Yk3Y9mto-hpOCSeqeZLPS8ukt0pS_91vkkUATYHG__U='  # Ensure this key is securely stored and retrieved
cipher_suite = Fernet(key)

def encrypt_data(data):
    try:
        return cipher_suite.encrypt(data.encode()).decode()
    except Exception as e:
        print("Encryption Error:", e)  # Debugging statement
        return None

def decrypt_data(data):
    try:
        return cipher_suite.decrypt(data.encode()).decode()
    except Exception as e:
        print("Decryption Error:", e)  # Debugging statement
        return None


