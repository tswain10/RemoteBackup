import paramiko
import os

def backup_files_to_remote(source_dir, remote_dir, file_list, host, port, username, password):
    # Create an SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port, username, password)

    # Create an SFTP client
    sftp = ssh.open_sftp()

    # Copy files to the remote destination
    for file_name in file_list:
        src_file = os.path.join(source_dir, file_name)
        dest_file = os.path.join(remote_dir, file_name)
        if os.path.exists(src_file):
            sftp.put(src_file, dest_file)
            print(f"Copied: {src_file} to {dest_file}")
        else:
            print(f"File not found: {src_file}")

    # Close the SFTP and SSH clients
    sftp.close()
    ssh.close()

# Example usage
source_directory = '/path/to/source/directory'
remote_directory = '/path/to/remote/directory'
files_to_backup = ['file1.txt', 'file2.txt', 'file3.txt']
remote_host = 'your.remote.server'
remote_port = 22
remote_username = 'your_username'
remote_password = 'your_password'

backup_files_to_remote(source_directory, remote_directory, files_to_backup, remote_host, remote_port, remote_username, remote_password)
