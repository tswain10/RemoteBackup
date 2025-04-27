import logging
import os
import schedule
import time
import json
import paramiko
import shutil
from cryptography.fernet import Fernet
import signal
import sys
import win32com.client  # Requires `pywin32` package
import subprocess
import tkinter as tk
from tkinter import simpledialog, messagebox
from setup import prompt_user_for_config_gui  # Import setup functions
from utils import generate_key, load_key, save_config, load_config, validate_config, add_to_startup  # Import shared utility functions

CONFIG_FILE = 'config.json'
LOG_FILE = 'backup.log'
BUSINESS_HOURS = (8, 18)  # 8 AM to 6 PM

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def encrypt_config(data, key):
    """Encrypt configuration data."""
    fernet = Fernet(key)
    return fernet.encrypt(json.dumps(data).encode())

def decrypt_config(encrypted_data, key):
    """Decrypt configuration data."""
    fernet = Fernet(key)
    return json.loads(fernet.decrypt(encrypted_data).decode())

def prompt_user_for_config():
    """Prompt the user to enter configuration details."""
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

def sftp_sync_directories(source_dir, remote_dir, host, port, username, password):
    def connect_to_sftp(host, port, username, password):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, username, password)
        return ssh.open_sftp()

    def create_remote_dir(sftp, remote_dir_path):
        """Recursively create directories on the remote server."""
        dirs = remote_dir_path.replace('\\', '/').split('/')
        path = ''
        for dir in dirs:
            if dir:
                path += f'/{dir}'
                try:
                    sftp.stat(path)
                except IOError:
                    sftp.mkdir(path)
                    logging.info(f"Created remote directory: {path}")

    def get_file_modification_time(file_path):
        return os.path.getmtime(file_path)

    try:
        logging.info("Connecting to SFTP...")
        sftp = connect_to_sftp(host, port, username, password)
        logging.info("Connected to SFTP.")

        # Set the initial remote directory
        try:
            sftp.chdir(remote_dir)
            logging.info(f"Changed to remote directory: {remote_dir}")
        except IOError:
            logging.info(f"Remote directory {remote_dir} does not exist. Creating it.")
            create_remote_dir(sftp, remote_dir)
            sftp.chdir(remote_dir)
            logging.info(f"Changed to remote directory: {remote_dir}")

        files_copied = 0
        files_skipped = 0
        files_failed = 0

        # Walk through the source directory
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                src_file = os.path.join(root, file)
                relative_path = os.path.relpath(src_file, source_dir)
                dest_file = os.path.join(remote_dir, relative_path).replace('\\', '/')

                if not os.path.exists(src_file):
                    logging.error(f"Source file does not exist: {src_file}")
                    continue

                try:
                    remote_file_info = sftp.stat(dest_file)
                    remote_mtime = remote_file_info.st_mtime
                except IOError:
                    remote_mtime = 0

                local_mtime = get_file_modification_time(src_file)
                if local_mtime > remote_mtime:
                    remote_dir_path = os.path.dirname(dest_file).replace('\\', '/')
                    try:
                        sftp.chdir(remote_dir_path)
                    except IOError:
                        create_remote_dir(sftp, remote_dir_path)
                        sftp.chdir(remote_dir_path)
                    try:
                        sftp.put(src_file, dest_file)
                        logging.info(f"Copied: {src_file} to {dest_file}")
                        files_copied += 1
                    except Exception as e:
                        logging.error(f"Failed to copy {src_file} to {dest_file}: {e}")
                        files_failed += 1
                else:
                    logging.info(f"Skipped (up-to-date): {src_file}")
                    files_skipped += 1

        logging.info(f"SFTP Sync Completed: {files_copied} files copied, {files_skipped} files skipped, {files_failed} files failed.")
        sftp.close()
    except Exception as e:
        logging.error(f"An error occurred during SFTP sync: {e}")

def local_sync_directories(source_dir, dest_dir):
    def create_local_dir(path):
        """Recursively create directories on the local system."""
        if not os.path.exists(path):
            os.makedirs(path)
            logging.info(f"Created local directory: {path}")

    def get_file_modification_time(file_path):
        return os.path.getmtime(file_path)

    try:
        logging.info("Starting local directory sync...")

        # Ensure the destination directory exists
        create_local_dir(dest_dir)

        files_copied = 0
        files_skipped = 0
        files_failed = 0

        # Walk through the source directory
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                src_file = os.path.join(root, file)
                relative_path = os.path.relpath(src_file, source_dir)
                dest_file = os.path.join(dest_dir, relative_path)

                if not os.path.exists(src_file):
                    logging.error(f"Source file does not exist: {src_file}")
                    continue

                try:
                    remote_mtime = os.path.getmtime(dest_file)
                except FileNotFoundError:
                    remote_mtime = 0

                local_mtime = get_file_modification_time(src_file)
                if local_mtime > remote_mtime:
                    dest_dir_path = os.path.dirname(dest_file)
                    create_local_dir(dest_dir_path)
                    try:
                        shutil.copy2(src_file, dest_file)
                        logging.info(f"Copied: {src_file} to {dest_file}")
                        files_copied += 1
                    except Exception as e:
                        logging.error(f"Failed to copy {src_file} to {dest_file}: {e}")
                        files_failed += 1
                else:
                    logging.info(f"Skipped (up-to-date): {src_file}")
                    files_skipped += 1

        logging.info(f"Local Sync Completed: {files_copied} files copied, {files_skipped} files skipped, {files_failed} files failed.")
    except Exception as e:
        logging.error(f"An error occurred during local sync: {e}")

def validate_config(config, required_fields):
    """Validate the configuration and check for missing fields."""
    missing_fields = [desc for field, desc in required_fields.items() if not config.get(field)]
    if missing_fields:
        print("Error: Missing the following required fields:")
        for field in missing_fields:
            print(f"- {field}")
        return False
    return True

def print_config(config):
    """Print the configuration, masking sensitive fields."""
    print("Saved Configuration:")
    for key, value in config.items():
        if key == "remote_password":  # Mask sensitive information
            print(f"{key}: {'*' * len(value)}")
        else:
            print(f"{key}: {value}")

def get_required_fields(local_sync, sftp_sync):
    """Get the required fields based on the sync type."""
    if local_sync and sftp_sync:
        return {
            "source_folder": "Source folder",
            "local_backup_folder": "Local backup folder",
            "remote_backup_directory": "Remote backup directory",
            "remote_host": "Remote host",
            "remote_port": "Remote port",
            "remote_username": "Remote username",
            "remote_password": "Remote password",
        }
    elif local_sync:
        return {
            "source_folder": "Source folder",
            "local_backup_folder": "Local backup folder",
        }
    elif sftp_sync:
        return {
            "source_folder": "Source folder",
            "remote_backup_directory": "Remote backup directory",
            "remote_host": "Remote host",
            "remote_port": "Remote port",
            "remote_username": "Remote username",
            "remote_password": "Remote password",
        }
    return {}

def run_backup(config):
    """Run the backup based on the configuration."""
    try:
        logging.info("Starting backup...")
        local_sync = config.get('local_sync', False)
        sftp_sync = config.get('sftp_sync', False)

        source_folder = config.get('source_folder')
        remote_directory = config.get('remote_backup_directory')
        remote_host = config.get('remote_host')
        remote_port = config.get('remote_port')
        remote_username = config.get('remote_username')
        remote_password = config.get('remote_password')
        destination_folder = config.get('local_backup_folder')

        # Perform sync operations
        if sftp_sync:
            sftp_sync_directories(source_folder, remote_directory, remote_host, remote_port, remote_username, remote_password)

        if local_sync:
            local_sync_directories(source_folder, destination_folder)
        logging.info("Backup completed successfully.")
    except Exception as e:
        logging.error(f"An error occurred during the backup: {e}")

def schedule_backup(config):
    """Schedule the backup outside of business hours."""
    interval = config.get("schedule_interval", "daily")
    custom_minutes = config.get("custom_interval_minutes", None)

    if interval == "daily":
        schedule.every().day.at("19:00").do(run_backup, config)  # 7 PM
        logging.info("Backup scheduled daily at 7 PM.")
    elif interval == "weekly":
        schedule.every().week.at("19:00").do(run_backup, config)  # 7 PM
        logging.info("Backup scheduled weekly at 7 PM.")
    elif interval == "custom" and custom_minutes:
        schedule.every(custom_minutes).minutes.do(run_backup, config)
        logging.info(f"Backup scheduled every {custom_minutes} minutes.")
    else:
        logging.error("Invalid scheduling configuration. Please reconfigure.")
        return False
    return True

def graceful_exit(signum, frame):
    logging.info("Scheduler is shutting down.")
    print("Scheduler is shutting down.")
    exit(0)

signal.signal(signal.SIGINT, graceful_exit)
signal.signal(signal.SIGTERM, graceful_exit)

def run_in_background():
    """Restart the program in the background."""
    if not hasattr(sys, 'frozen'):  # Skip if already running as an .exe
        return
    subprocess.Popen([sys.executable], creationflags=subprocess.DETACHED_PROCESS)
    sys.exit()

def main():
        # Check if configuration exists
    if not os.path.exists(CONFIG_FILE):
        print("Configuration file not found. Launching setup...")
        prompt_user_for_config_gui()  # Launch setup GUI for configuration
        #return

    # Run in the background
    run_in_background()

    # Load configuration and start the scheduler
    key = load_key()
    config = load_config(key)
    if not config:
        logging.error("Failed to load configuration.")
        return

    # Validate configuration
    required_fields = get_required_fields(config.get('local_sync', False), config.get('sftp_sync', False))
    if not validate_config(config, required_fields):
        print("Please reconfigure the application.")
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