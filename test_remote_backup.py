import os
import unittest
from unittest.mock import patch, MagicMock
from utils import generate_key, load_key, save_config, load_config, validate_config, add_to_startup
from RemoteBackup import run_backup, schedule_backup

class TestUtils(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        generate_key()  # Generate the key
        self.key = load_key()  # Load the key
        self.config = {
            "source_folder": "test_source",
            "local_sync": True,
            "sftp_sync": False,
            "local_backup_folder": "test_backup",
            "schedule_interval": "daily",
        }

    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists("config.json"):
            os.remove("config.json")
        if os.path.exists("key.key"):
            os.remove("key.key")

    def test_generate_and_load_key(self):
        """Test key generation and loading."""
        key = load_key()
        self.assertIsNotNone(key)
        self.assertEqual(len(key), 44)  # Fernet keys are 44 bytes long

    def test_save_and_load_config(self):
        """Test saving and loading configuration."""
        save_config(self.config, self.key)
        loaded_config = load_config(self.key)
        self.assertEqual(self.config, loaded_config)

    def test_validate_config(self):
        """Test configuration validation."""
        self.assertTrue(validate_config(self.config))
        invalid_config = {"source_folder": ""}
        self.assertFalse(validate_config(invalid_config))

    @patch("win32com.client.Dispatch")
    def test_add_to_startup(self, mock_dispatch):
        """Test adding the program to startup."""
        mock_shell = MagicMock()
        mock_dispatch.return_value = mock_shell
        add_to_startup()
        mock_shell.CreateShortcut.assert_called_once()

class TestRemoteBackup(unittest.TestCase):
    @patch("RemoteBackup.run_backup")
    def test_schedule_backup_daily(self, mock_run_backup):
        """Test daily backup scheduling."""
        config = {"schedule_interval": "daily"}
        result = schedule_backup(config)
        self.assertTrue(result)

    @patch("RemoteBackup.run_backup")
    def test_schedule_backup_invalid(self, mock_run_backup):
        """Test invalid backup scheduling."""
        config = {"schedule_interval": "invalid"}
        result = schedule_backup(config)
        self.assertFalse(result)

    @patch("RemoteBackup.local_sync_directories")
    @patch("RemoteBackup.sftp_sync_directories")
    def test_run_backup(self, mock_sftp_sync, mock_local_sync):
        """Test running the backup."""
        config = {
            "local_sync": True,
            "sftp_sync": True,
            "source_folder": "test_source",
            "local_backup_folder": "test_backup",
            "remote_backup_directory": "test_remote",
            "remote_host": "localhost",
            "remote_port": 22,
            "remote_username": "user",
            "remote_password": "pass",
        }
        run_backup(config)
        mock_local_sync.assert_called_once_with("test_source", "test_backup")
        mock_sftp_sync.assert_called_once_with(
            "test_source", "test_remote", "localhost", 22, "user", "pass"
        )

if __name__ == "__main__":
    unittest.main()
