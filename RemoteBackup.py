import logging
import os
import schedule
import time
from cryptography.fernet import Fernet
import signal

CONFIG_FILE = 'config.json'
KEY_FILE = 'key.key'
LOG_FILE = 'backup.log'

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def load_key():
    """Load the encryption key from the key file."""
    with open(KEY_FILE, 'rb') as key_file:
        return key_file.read()

def decrypt_config(encrypted_data, key):
    """Decrypt configuration data."""
    fernet = Fernet(key)
    return json.loads(fernet.decrypt(encrypted_data).decode())

def load_config(key):
    """Load and decrypt configuration data from the config file."""
    if not os.path.exists(CONFIG_FILE):
        logging.error("Configuration file not found. Please run SetupConfig.py to create it.")
        raise FileNotFoundError("Configuration file not found. Please run SetupConfig.py to create it.")
    with open(CONFIG_FILE, 'rb') as config_file:
        encrypted_data = config_file.read()
    logging.info("Configuration loaded successfully.")
    return decrypt_config(encrypted_data, key)

def graceful_exit(signum, frame):
    logging.info("Scheduler is shutting down.")
    print("Scheduler is shutting down.")
    exit(0)

signal.signal(signal.SIGINT, graceful_exit)
signal.signal(signal.SIGTERM, graceful_exit)

def main():
    key = load_key()

    # Load existing configuration
    try:
        config = load_config(key)
    except FileNotFoundError as e:
        print(e)
        return

    # Schedule the backup
    if not schedule_backup(config):
        return

    # Run the scheduler in the background
    print("Scheduler is running in the background. Press Ctrl+C to exit.")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()