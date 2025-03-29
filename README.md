# RemoteBackup

The RemoteBackup script is a Python-based backup utility that allows users to synchronize files and directories either locally or to a remote server via SFTP. It supports encryption for configuration files, scheduling for automated backups, and logging for monitoring backup operations. The script is designed to run in the background and can prompt the user for configuration if necessary.

---

## Features

- **Local Backup**: Synchronize files and directories to a local destination.
- **Remote Backup via SFTP**: Synchronize files and directories to a remote server using SFTP.
- **Encrypted Configuration**: Securely store configuration details (e.g., credentials) using encryption.
- **Automated Scheduling**: Schedule backups to run daily, weekly, or at custom intervals.
- **Logging**: Log all backup operations, errors, and statistics to a log file (`backup.log`).
- **Background Execution**: Run silently in the background, with the ability to prompt the user for configuration when needed.
- **Separate Configuration Setup**: Use the `SetupConfig.py` script to configure the backup settings independently.

---

## How It Works

### 1. Configuration

The configuration setup has been moved to a separate script (`SetupConfig.py`). This script prompts the user for configuration details, encrypts the configuration, and saves it to an encrypted file (`config.json`). The main backup script (`RemoteBackup.py`) loads and validates the configuration before performing backups.

#### Configuration Details:

- **Local Sync**:
  - `source_folder`: The folder to back up.
  - `local_backup_folder`: The destination folder for local backups.
- **SFTP Sync**:
  - `source_folder`: The folder to back up.
  - `remote_backup_directory`: The destination directory on the remote server.
  - `remote_host`: The hostname or IP address of the remote server.
  - `remote_port`: The port for the SFTP connection (default: 22).
  - `remote_username`: The username for the SFTP connection.
  - `remote_password`: The password for the SFTP connection.
- **Scheduling**:
  - `schedule_interval`: The interval for backups (`daily`, `weekly`, or `custom`).
  - `custom_interval_minutes`: The interval in minutes for custom scheduling.

### 2. Encryption

The script uses the `cryptography` library to encrypt and decrypt the configuration file. A key file (`key.key`) is generated and used for encryption. The `SetupConfig.py` script handles the encryption and saving of the configuration.

### 3. Backup Operations

The script supports two types of backups:
- **Local Sync**: Copies files from the source folder to a local destination folder.
- **SFTP Sync**: Uploads files from the source folder to a remote server using SFTP.

### 4. Scheduling

The script uses the `schedule` library to automate backups. Users can configure backups to run daily, weekly, or at custom intervals.

### 5. Logging

All operations, including errors and statistics, are logged to `backup.log`. This allows users to monitor the script's activity and troubleshoot issues.

### 6. Background Execution

The script can run silently in the background. If configuration is required, it opens a temporary console window to prompt the user for input.

---

## Usage

### Prerequisites

1. **Python**: Install Python 3.6 or later.
2. **Dependencies**: Install the required Python libraries:
   ```bash
   pip install paramiko cryptography schedule
   ```

### Configuration Setup

1. Run the `SetupConfig.py` script to configure the backup settings:
   ```bash
   python SetupConfig.py
   ```
2. Enter the required details when prompted:
   - Enable local sync or SFTP sync.
   - Provide the source folder, destination folder, and remote server details (if applicable).
   - Configure the backup schedule (daily, weekly, or custom intervals).

3. The configuration will be saved to an encrypted file (`config.json`), and the encryption key will be stored in `key.key`.

### Running the Backup Script

1. Run the `RemoteBackup.py` script to perform backups:
   ```bash
   python RemoteBackup.py
   ```
2. The script will load the saved configuration and perform backups based on the schedule.

### Build as Executables (Optional)

You can use PyInstaller to create standalone executables for both scripts:

- For `SetupConfig.py`:
  ```bash
  pyinstaller --onefile SetupConfig.py
  ```
- For `RemoteBackup.py`:
  ```bash
  pyinstaller --noconsole --onefile RemoteBackup.py
  ```

---

## Configuration Details

### Prompted Configuration

When running `SetupConfig.py`, the script prompts the user for the following details:

1. **Enable Local Sync**: Whether to enable local backups.
2. **Enable SFTP Sync**: Whether to enable remote backups via SFTP.
3. **Source Folder**: The folder to back up.
4. **Local Backup Folder**: The destination folder for local backups (if local sync is enabled).
5. **Remote Backup Details** (if SFTP sync is enabled):
   - Remote backup directory
   - Remote host
   - Remote port
   - Remote username
   - Remote password
6. **Scheduling**:
   - Interval (`daily`, `weekly`, or `custom`).
   - Custom interval in minutes (if `custom` is selected).

### Configuration File

The configuration is saved in an encrypted file (`config.json`). The encryption key is stored in `key.key`.

---

## Logging

The script logs all operations to `backup.log`. Example log entries:

```plaintext
2025-03-21 10:00:00 - INFO - Configuration loaded successfully.
2025-03-21 10:00:01 - INFO - Backup scheduled to run daily at 00:00.
2025-03-21 10:30:00 - INFO - Starting local directory sync...
2025-03-21 10:30:01 - INFO - Copied: C:\Users\TreyS\Documents\file1.txt to C:\Users\TreyS\Backup\file1.txt
2025-03-21 10:30:02 - INFO - SFTP Sync Completed: 1 files copied, 0 files skipped, 0 files failed.
```

---

## Error Handling

- **Missing Configuration**: Prompts the user to provide configuration details.
- **Invalid Scheduling**: Logs an error and prompts the user to reconfigure.
- **File/Directory Errors**: Logs errors for missing files or directories.

---

## Functions

### Key Functions in `SetupConfig.py`

1. **`generate_key()`**:
   - Generates an encryption key and saves it to `key.key`.

2. **`load_key()`**:
   - Loads the encryption key from `key.key`.

3. **`encrypt_config(data, key)`**:
   - Encrypts the configuration data.

4. **`save_config(data, key)`**:
   - Saves the encrypted configuration to `config.json`.

5. **`prompt_user_for_config()`**:
   - Prompts the user to enter configuration details.

6. **`open_console()`**:
   - Opens a temporary console window for user input.

### Key Functions in `RemoteBackup.py`

1. **`load_key()`**:
   - Loads the encryption key from `key.key`.

2. **`decrypt_config(encrypted_data, key)`**:
   - Decrypts the configuration data.

3. **`load_config(key)`**:
   - Loads and decrypts the configuration from `config.json`.

4. **`schedule_backup(config)`**:
   - Schedules backups based on the configuration.

5. **`graceful_exit(signum, frame)`**:
   - Handles graceful shutdown of the scheduler.

6. **`main()`**:
   - The main entry point of the script.

---

## Example Workflow

1. Run the configuration setup:
   ```bash
   python SetupConfig.py
   ```
   - Enter the required details when prompted.

2. Run the backup script:
   ```bash
   python RemoteBackup.py
   ```

3. Build executables (optional):
   - For `SetupConfig.py`:
     ```bash
     pyinstaller --onefile SetupConfig.py
     ```
   - For `RemoteBackup.py`:
     ```bash
     pyinstaller --noconsole --onefile RemoteBackup.py
     ```

---

## Notes

- **Security**: Ensure the `key.key` file is stored securely, as it is required to decrypt the configuration.
- **Testing**: Test the script thoroughly before deploying it in a production environment.
- **Task Scheduler**: Use the Windows Task Scheduler or a similar tool to run the script automatically on system boot.