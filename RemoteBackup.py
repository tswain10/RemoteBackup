import paramiko
import os
import shutil
import time
import stat

def zip_folder(source_folder, output_zip): 
    shutil.make_archive(output_zip, 'zip', source_folder) 
    print(f"Folder zipped to: {output_zip}.zip")

def backup_folder_to_remote(zip_file, remote_dir, host, port, username, password): 
    ssh = paramiko.SSHClient() 
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
    ssh.connect(host, port, username, password) 
    sftp = ssh.open_sftp() 
    remote_file = os.path.join(remote_dir, os.path.basename(zip_file)) 
    sftp.put(f"{zip_file}.zip", remote_file) 
    print(f"Backup successful: {zip_file}.zip to {remote_file}") 
    sftp.close()
    ssh.close()

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

def get_file_modification_time(file_path):
    return os.path.getmtime(file_path)

def incremental_backup_local(source_dir, dest_dir):
    # Create destination directory if it doesn't exist
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    # Record the current time
    current_time = time.time()

    # Walk through the source directory
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            # Construct full file path
            src_file = os.path.join(root, file)
            # Construct destination file path
            dest_file = os.path.join(dest_dir, os.path.relpath(src_file, source_dir))

            # Create destination directory if it doesn't exist
            dest_file_dir = os.path.dirname(dest_file)
            if not os.path.exists(dest_file_dir):
                os.makedirs(dest_file_dir)

            # Check if the file has been modified since the last backup
            if not os.path.exists(dest_file) or get_file_modification_time(src_file) > get_file_modification_time(dest_file):
                shutil.copy2(src_file, dest_file)
                print(f"Copied: {src_file} to {dest_file}")

def connect_to_sftp(host, port, username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port, username, password)
    return ssh.open_sftp()

def incremental_backup_to_remote(source_dir, remote_dir, host, port, username, password):
    sftp = connect_to_sftp(host, port, username, password)

    # Walk through the source directory
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            src_file = os.path.join(root, file)
            relative_path = os.path.relpath(src_file, source_dir)
            dest_file = os.path.join(remote_dir, relative_path).replace('\\', '/')

            try:
                remote_file_info = sftp.stat(dest_file)
                remote_mtime = remote_file_info.st_mtime
            except IOError:
                remote_mtime = 0

            local_mtime = get_file_modification_time(src_file)

            if local_mtime > remote_mtime:
                remote_dir_path = os.path.dirname(dest_file)
                try:
                    sftp.chdir(remote_dir_path)
                except IOError:
                    # Create remote directory if it doesn't exist
                    sftp.makedirs(remote_dir_path)

                sftp.put(src_file, dest_file)
                print(f"Copied: {src_file} to {dest_file}")

    sftp.close()



source_folder = 'C:\\data\\backups\\foldername'
output_zip = 'E:\\data\\zipfoldername'
remote_directory = 'E:\\data\\backups\\foldername'
files_to_backup = ['file1.txt', 'file2.txt']
remote_host = 'remote.host'
remote_port = 22
remote_username = 'username'
remote_password = 'password'

#zip_folder(source_folder, output_zip) 
#backup_folder_to_remote(output_zip, remote_directory, remote_host, remote_port, remote_username, remote_password)
#backup_files_to_remote(source_directory, remote_directory, files_to_backup, remote_host, remote_port, remote_username, remote_password)
#incremental_backup_local(source_folder, remote_directory)
incremental_backup_to_remote(source_folder, remote_directory, remote_host, remote_port, remote_username, remote_password)