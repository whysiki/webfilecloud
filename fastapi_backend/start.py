# encoding: utf-8

import os
import sys
import subprocess
import time
import socket

while True:
    start_port = input("Enter the start port (default: 8000): ") or "8000"
    if start_port.isdigit() and 1024 <= int(start_port) <= 65535:
        break
    print("Invalid port number. Please enter a number between 1024 and 65535.")


def install_dependencies():

    print("Installing dependencies...")

    subprocess.run(
        [
            "pip3",
            "config",
            "set",
            "global.index-url",
            "https://pypi.tuna.tsinghua.edu.cn/simple",
        ],
        check=True,
    )

    subprocess.run(["pip3", "install", "--upgrade", "pip"], check=True)

    pakages = [
        "python-dotenv",
        "uvicorn",
        "fastapi",
        "argon2-cffi",
        "pyjwt",
        "loguru",
        "sqlalchemy",
        "rich",
        "python-multipart",
        "gunicorn",
        "cryptography",
        "aiofiles",
        "python-multipart",
        "requests",
        # "hypercorn",
        # "psycopg2",
        "alembic",
        "numpy",
    ]

    for pakage in pakages:
        subprocess.run(["pip3", "install", pakage], check=True)

    if os.name != "nt":

        subprocess.run(
            [
                "apt",
                "install",
                "-y",
                "python3-psycopg2",
            ],
            check=True,
        )
        # subprocess.run(["pip3", "install", "psycopg2"], check=True)

    else:
        subprocess.run(["pip3", "install", "psycopg2"], check=True)

    subprocess.run(["pip3", "freeze", ">", "requirements.txt"], check=True)


def generate_env_file():

    # Generate .env file
    subprocess.run([sys.executable, "env.py"], check=True)

    if not os.path.exists(".env"):
        print("Failed to generate .env file.")
        sys.exit(1)

    # Append start port to .env file
    with open(".env", "a") as f:
        f.write(f"\nSTART_PORT={start_port}")


def start_server():

    generate_env_file()

    print("Starting server...")

    if os.name != "nt":
        subprocess.run(["sudo", "killall", "gunicorn"], check=True)
        subprocess.run(
            [
                "gunicorn",
                "-w",
                "4",
                "-k",
                "uvicorn.workers.UvicornWorker",
                "-b",
                f"0.0.0.0:{start_port}",
                "-D",
                "main:app",
            ],
            check=True,
        )
    else:
        # hypercorn main:app --workers 4 --bind 0.0.0.0:8000 --reload
        # subprocess.run(
        #     [
        #         "hypercorn",
        #         "main:app",
        #         "--workers",
        #         "4",
        #         "--bind",
        #         f"0.0.0.0:{start_port}",
        #         "--reload",
        #     ],
        #     check=True,
        # )
        subprocess.run(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "main:app",
                "--workers",
                "4",
                "--host",
                "0.0.0.0",
                "--port",
                f"{start_port}",
                "--reload",
            ],
            check=True,
        )


def wait_for_port(port, host="localhost", timeout=600):  # type: ignore
    start_time = time.perf_counter()
    while True:
        try:
            with socket.create_connection((host, port), timeout=timeout):  # type: ignore
                break
        except (OSError, ConnectionRefusedError):
            time.sleep(0.01)
            if time.perf_counter() - start_time >= timeout:
                raise TimeoutError(
                    f"Waited too long for the port {port} on host {host} to start accepting connections."
                )


def check_server_status():
    # Wait for the server to start
    wait_for_port(int(start_port))
    print("Checking server status...")
    for _ in range(4):
        time.sleep(1)
        print(".", end="", flush=True)
    response = os.system(f"curl http://localhost:{start_port}")
    if response == 0:
        print("Server is running.")
    else:
        print("Server failed to start.")
        sys.exit(1)


def get_existing_venv():
    possible_venvs = ["venv", ".venv", "myenv", "myvenv"]
    for venv in possible_venvs:
        if os.path.exists(os.path.join(venv, "pyvenv.cfg")):
            print(f"Found existing virtual environment: {venv}")
            return venv
    return None


def activate_venv(venv_root):  # type: ignore

    if not os.path.exists(venv_root):  # type: ignore
        print(f"Virtual environment {venv_root} does not exist.")
        sys.exit(1)

    activate_script = (
        f". {venv_root}/bin/activate"
        if os.name != "nt"
        else f"{venv_root}\\Scripts\\activate"
    )
    activate_command = f"{activate_script}{'.bat' if os.name == 'nt' else ''}"

    if os.name != "nt":
        subprocess.run(
            activate_command,
            shell=True,
            check=True,
        )
    else:
        subprocess.run(
            activate_command,
            shell=True,
            check=True,
        )

    print(f"Activated virtual environment: {venv_root}")


def run_test():
    if os.path.exists("test_file.py"):
        to_run_tests = input("Run test_file.py? (y/n) default(y): ") or "y"
        if to_run_tests.lower() == "y":
            print("Running tests...")
            try:
                subprocess.run([sys.executable, "test_file.py"], check=True)
                print("Tests passed.")
            except subprocess.CalledProcessError:
                print("Tests failed.")
                sys.exit(1)


def main():
    # venv_root = get_existing_venv()

    if os.name != "nt":
        subprocess.run(["apt", "update"], check=True)
        subprocess.run(
            [
                "apt",
                "install",
                "-y",
                "python3",
                "python3-pip",
                "python3.10-venv",
                "curl",
                # "python3-psycopg2",
            ],
            check=True,
        )
        # sudo apt install python3-psycopg2
        # subprocess.run([""])

    # if not venv_root:
    # venv_root = "myenv"
    # print("Creating virtual environment...")
    # subprocess.run([sys.executable, "-m", "venv", venv_root], check=True)

    # activate_venv(venv_root)
    install_dependencies()
    start_server()
    check_server_status()

    print("Server started successfully.")


if __name__ == "__main__":
    main()
