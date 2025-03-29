import os
import json
import logging
from cryptography.fernet import Fernet
import ctypes

CONFIG_FILE = 'config.json'
KEY_FILE = 'key.key'
LOG_FILE = 'setup.log'

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def generate_key():
    """Generate and save a key for encryption."""
    key = Fernet.generate_key()
    with open(KEY_FILE, 'wb') as key_file:
        key_file.write(key)
    logging.info("Encryption key generated and saved.")

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

def save_config(data, key):
    """Save encrypted configuration data to the config file."""
    encrypted_data = encrypt_config(data, key)
    with open(CONFIG_FILE, 'wb') as config_file:
        config_file.write(encrypted_data)
    logging.info("Configuration saved successfully.")

def open_console():
    """Open a console window for user input."""
    if not ctypes.windll.kernel32.AllocConsole():
        logging.error("Failed to open console window.")
        print("Failed to open console window.")
    else:
        os.system("cls")  # Clear the console

def prompt_user_for_config():
    """Prompt the user to enter configuration details."""
    open_console()
    print("Please enter the following configuration details:")

    # Ask if local sync or SFTP sync is needed
    local_sync = input("Enable local sync? (true/false): ").strip().lower() == 'true'
    sftp_sync = input("Enable SFTP sync? (true/false): ").strip().lower() == 'true'

    config = {
        "local_sync": local_sync,
        "sftp_sync": sftp_sync
    }

    # Prompt for source folder if any sync is enabled
    if local_sync or sftp_sync:
        config["source_folder"] = input("Source folder: ").strip()

    # Prompt for local sync configuration if enabled
    if local_sync:
        config["local_backup_folder"] = input("Local backup folder: ").strip()

    # Prompt for SFTP sync configuration if enabled
    if sftp_sync:
        config["remote_backup_directory"] = input("Remote backup directory: ").strip()
        config["remote_host"] = input("Remote host: ").strip()
        config["remote_port"] = int(input("Remote port (default 22): ").strip() or 22)
        config["remote_username"] = input("Remote username: ").strip()
        config["remote_password"] = input("Remote password: ").strip()

    # Add scheduling configuration
    print("Configure scheduling:")
    config["schedule_interval"] = input("Enter schedule interval (daily/weekly/custom): ").strip().lower()
    if config["schedule_interval"] == "custom":
        config["custom_interval_minutes"] = int(input("Enter custom interval in minutes: ").strip())

    return config

def main():
    key = load_key()

    # Prompt the user for configuration
    print("Welcome to the RemoteBackup Configuration Setup.")
    config = prompt_user_for_config()

    # Save the configuration
    save_config(config, key)
    print("Configuration saved and encrypted successfully.")
    logging.info("Configuration setup completed.")

if __name__ == "__main__":
    main()