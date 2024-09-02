import os
import subprocess
import psutil
import sys

def find_handle_exe_path():
    possible_paths = [
        "C:\\Sysinternals\\handle.exe",
        "C:\\Program Files\\Sysinternals\\handle.exe",
        "C:\\Program Files (x86)\\Sysinternals\\handle.exe"
    ]
    for path in possible_paths:
        if os.path.isfile(path):
            return path
    return None

def get_process_id(file_path):
    handle_exe = find_handle_exe_path()
    if not handle_exe:
        print("handle.exe not found. Please download Sysinternals Suite and extract it to a known directory.")
        sys.exit(1)

    result = subprocess.run([handle_exe, file_path], capture_output=True, text=True)
    output = result.stdout
    lines = output.splitlines()
    
    for line in lines:
        if file_path in line:
            parts = line.split()
            for part in parts:
                if part.isdigit():
                    return int(part)
    return None

def kill_process(pid):
    process = psutil.Process(pid)
    process.terminate()
    process.wait()

def delete_file(file_path):
    os.remove(file_path)

def forcey_delete_path(file_path):
    pid = get_process_id(file_path)
    if pid:
        print(f"Process ID {pid} is using the file.")
        kill_process(pid)
        print(f"Process {pid} terminated.")
        delete_file(file_path)
        print(f"File {file_path} deleted.")
    else:
        print(f"No process is using the file {file_path}.")
        delete_file(file_path)
        print(f"File {file_path} deleted.")

# if __name__ == "__main__":
    # if len(sys.argv) != 2:
        # print("Usage: python script.py <file_path>")
        # sys.exit(1)

    # file_path = sys.argv[1]
    # if not os.path.isfile(file_path):
        # print(f"File {file_path} does not exist.")
        # sys.exit(1)

    # main(file_path)
