import os
import json
from cryptography.fernet import Fernet

CONFIG_FILE = 'config.json'
KEY_FILE = 'key.key'

def generate_key():
    """Generate and save a key for encryption."""
    key = Fernet.generate_key()
    with open(KEY_FILE, 'wb') as key_file:
        key_file.write(key)

def load_key():
    """Load the encryption key from the key file."""
    if not os.path.exists(KEY_FILE):
        generate_key()
    with open(KEY_FILE, 'rb') as key_file:
        return key_file.read()

def encrypt_config(data, key):
    """Encrypt configuration data."""
    fernet = Fernet(key)
    return fernet.encrypt(json.dumps(data).encode())

def decrypt_config(encrypted_data, key):
    """Decrypt configuration data."""
    fernet = Fernet(key)
    return json.loads(fernet.decrypt(encrypted_data).decode())

def save_config(data, key):
    """Save encrypted configuration data to the config file."""
    encrypted_data = encrypt_config(data, key)
    with open(CONFIG_FILE, 'wb') as config_file:
        config_file.write(encrypted_data)
    print("Configuration saved successfully.")

def load_config(key):
    """Load and decrypt configuration data from the config file."""
    if not os.path.exists(CONFIG_FILE):
        return None
    with open(CONFIG_FILE, 'rb') as config_file:
        encrypted_data = config_file.read()
    return decrypt_config(encrypted_data, key)
