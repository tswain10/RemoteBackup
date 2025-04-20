import os
import tkinter as tk
from tkinter import messagebox
from utils import generate_key, load_key, save_config  # Import shared utility functions
import win32com.client  # Requires `pywin32` package

CONFIG_FILE = 'config.json'

def add_to_startup():
    """Add the script to Windows Startup."""
    startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
    exe_path = sys.executable  # Path to the .exe file
    shortcut_path = os.path.join(startup_folder, 'RemoteBackup.lnk')

    if not os.path.exists(shortcut_path):  # Avoid duplicate shortcuts
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(shortcut_path)
        shortcut.TargetPath = exe_path
        shortcut.WorkingDirectory = os.path.dirname(exe_path)
        shortcut.IconLocation = exe_path
        shortcut.Save()
        print("Shortcut added to Windows Startup.")
    else:
        print("Shortcut already exists in Windows Startup.")

def prompt_user_for_config_gui():
    """Prompt the user to create a configuration file using a GUI."""
    def save_and_exit():
        config = {
            "local_sync": local_sync_var.get(),
            "sftp_sync": sftp_sync_var.get(),
            "source_folder": source_folder_var.get(),
            "local_backup_folder": local_backup_folder_var.get(),
            "remote_backup_directory": remote_backup_directory_var.get(),
            "remote_host": remote_host_var.get(),
            "remote_port": int(remote_port_var.get() or 22),
            "remote_username": remote_username_var.get(),
            "remote_password": remote_password_var.get(),
            "schedule_interval": schedule_interval_var.get(),
            "custom_interval_minutes": int(custom_interval_var.get() or 0)
        }
        key = load_key()
        save_config(config, key)
        add_to_startup()  # Add to startup after saving the configuration
        messagebox.showinfo("Configuration Saved", "Configuration has been saved successfully.")
        root.destroy()

    root = tk.Tk()
    root.title("RemoteBackup Configuration")
    root.geometry("400x600")
    root.resizable(False, False)

    # Local Sync
    local_sync_var = tk.BooleanVar(value=False)
    tk.Checkbutton(root, text="Enable Local Sync", variable=local_sync_var).pack(anchor="w", padx=10, pady=5)

    # SFTP Sync
    sftp_sync_var = tk.BooleanVar(value=False)
    tk.Checkbutton(root, text="Enable SFTP Sync", variable=sftp_sync_var).pack(anchor="w", padx=10, pady=5)

    # Source Folder
    tk.Label(root, text="Source Folder:").pack(anchor="w", padx=10, pady=2)
    source_folder_var = tk.StringVar()
    tk.Entry(root, textvariable=source_folder_var, width=50).pack(anchor="w", padx=10, pady=2)

    # Local Backup Folder
    tk.Label(root, text="Local Backup Folder:").pack(anchor="w", padx=10, pady=2)
    local_backup_folder_var = tk.StringVar()
    tk.Entry(root, textvariable=local_backup_folder_var, width=50).pack(anchor="w", padx=10, pady=2)

    # Remote Backup Directory
    tk.Label(root, text="Remote Backup Directory:").pack(anchor="w", padx=10, pady=2)
    remote_backup_directory_var = tk.StringVar()
    tk.Entry(root, textvariable=remote_backup_directory_var, width=50).pack(anchor="w", padx=10, pady=2)

    # Remote Host
    tk.Label(root, text="Remote Host:").pack(anchor="w", padx=10, pady=2)
    remote_host_var = tk.StringVar()
    tk.Entry(root, textvariable=remote_host_var, width=50).pack(anchor="w", padx=10, pady=2)

    # Remote Port
    tk.Label(root, text="Remote Port (default 22):").pack(anchor="w", padx=10, pady=2)
    remote_port_var = tk.StringVar()
    tk.Entry(root, textvariable=remote_port_var, width=50).pack(anchor="w", padx=10, pady=2)

    # Remote Username
    tk.Label(root, text="Remote Username:").pack(anchor="w", padx=10, pady=2)
    remote_username_var = tk.StringVar()
    tk.Entry(root, textvariable=remote_username_var, width=50).pack(anchor="w", padx=10, pady=2)

    # Remote Password
    tk.Label(root, text="Remote Password:").pack(anchor="w", padx=10, pady=2)
    remote_password_var = tk.StringVar()
    tk.Entry(root, textvariable=remote_password_var, width=50, show="*").pack(anchor="w", padx=10, pady=2)

    # Schedule Interval
    tk.Label(root, text="Schedule Interval (daily/weekly/custom):").pack(anchor="w", padx=10, pady=2)
    schedule_interval_var = tk.StringVar()
    tk.Entry(root, textvariable=schedule_interval_var, width=50).pack(anchor="w", padx=10, pady=2)

    # Custom Interval Minutes
    tk.Label(root, text="Custom Interval Minutes (if custom):").pack(anchor="w", padx=10, pady=2)
    custom_interval_var = tk.StringVar()
    tk.Entry(root, textvariable=custom_interval_var, width=50).pack(anchor="w", padx=10, pady=2)

    # Save Button
    tk.Button(root, text="Save Configuration", command=save_and_exit).pack(anchor="center", pady=20)

    root.mainloop()

if __name__ == "__main__":
    prompt_user_for_config_gui()
