# encoding: utf-8

from rich.prompt import Prompt
from rich.console import Console
from dotenv import load_dotenv
import os
import uuid
import getpass
import re


# THis file is used to generate the .env file for the project
# It will ask the user for the configuration values and write them to the .env file

console = Console()


def get_valid_password(number_of_characters: int = 8):
    while True:
        password = getpass.getpass(
            "Enter the root password (must be at least 8 characters long)  (default random uuid4): "
        )
        if not password:
            return str(uuid.uuid4())
        if len(password) >= number_of_characters:
            return password
        else:
            console.print(
                "Password must be at least 8 characters long. Please try again.",
                style="yellow",
            )


def generate_env_file():

    console.print("Let's generate the .env configuration file.")

    upload_path = Prompt.ask(
        "Enter the upload path (default: uploads): ", default="uploads"
    )
    secret_key = Prompt.ask(
        "Enter the secret key (default random uuid4): ", default=str(uuid.uuid4())
    )
    algorithm = Prompt.ask("Enter the algorithm (default: HS256): ", default="HS256")
    expire_minutes = Prompt.ask(
        "Enter the access token expire minutes (default: 30): ", default="30"
    )
    root_user = Prompt.ask(
        "Enter the root user (default: whysiki): ", default="whysiki"
    )

    root_password = get_valid_password()

    database_url = Prompt.ask(
        "Enter the database URL (default: sqlite:///./fileserver.db): ",
        default="sqlite:///./fileserver.db",
    )

    env_content = f"""
UPLOAD_PATH={upload_path}
SECRET_KEY={secret_key}
ALGORITHM={algorithm}
ACCESS_TOKEN_EXPIRE_MINUTES={expire_minutes}
ROOT_USER={root_user}
ROOT_PASSWORD={root_password}
DATABASE_URL={database_url}
""".strip()
    with open(".env", "w") as file:
        file.write(env_content)

    console.print("Configuration generation successful", style="green")


def test_generate_env_file():
    # 读取 .env 文件
    load_dotenv()
    # 读取配置
    upload_path = os.getenv("UPLOAD_PATH")
    secret_key = os.getenv("SECRET_KEY")
    algorithm = os.getenv("ALGORITHM")
    expire_minutes = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    root_user = os.getenv("ROOT_USER")
    root_password = os.getenv("ROOT_PASSWORD")
    database_url = os.getenv("DATABASE_URL")

    if not (
        upload_path
        and secret_key
        and algorithm
        and expire_minutes
        and root_user
        and root_password
        and database_url
    ):
        console.print("Configuration generation failed", style="red")

    else:

        print("Configuration test successful")
        console.print(".env file has been generated.", style="green")
        # print("Configuration generation successful")
        # 打印配置
        print("UPLOAD_PATH:", upload_path)
        print("SECRET_KEY:", secret_key)
        print("ALGORITHM:", algorithm)
        print("ACCESS_TOKEN_EXPIRE_MINUTES:", expire_minutes)
        print("ROOT_USER:", root_user)
        print("ROOT_PASSWORD:", root_password)
        print("DATABASE_URL:", database_url)


def main():
    generate_env_file()
    test_generate_env_file()


def write_database_url_in_alembic_ini():
    try:
        # 读取 .env 文件
        load_dotenv()
        tag = Prompt.ask(
            "Do you want to write the database url in alembic.ini? (y/n): ", default="y"
        )
        if tag.lower() == "y":
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                console.print("Configuration generation failed", style="red")
                return
            if not database_url:
                console.print("Configuration generation failed", style="red")
            else:
                with open("alembic.ini", "r") as file:
                    alembic_ini_content = file.read()
                # Create a regex pattern
                pattern = re.compile(
                    r"^sqlalchemy\.url = .*$", flags=re.IGNORECASE | re.MULTILINE
                )

                replace_content = f"sqlalchemy.url = {database_url}"

                # Use the sub method of the pattern to replace the line
                alembic_ini_content = pattern.sub(replace_content, alembic_ini_content)

                if not replace_content in alembic_ini_content:

                    console.print(
                        "Error writing database url in alembic.ini", style="yellow"
                    )

                    return

                # re.IGNORECASE：忽略大小写。
                # re.MULTILINE：多行模式。
                with open("alembic.ini", "w") as file:
                    file.write(alembic_ini_content)

            console.print("Database url has been written in alembic.ini", style="green")
    except Exception as e:
        console.print("Error writing database url in alembic.ini", style="yellow")
        console.print(str(e), style="yellow")


if __name__ == "__main__":
    main()
    write_database_url_in_alembic_ini()
