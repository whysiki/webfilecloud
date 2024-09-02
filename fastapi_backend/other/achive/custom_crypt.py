# encoding: utf-8

from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os


# 生成密钥
def generate_key(
    username: str, userpassword: str, salt: bytes = None
) -> tuple[bytes, bytes]:
    combined = username + userpassword
    if salt is None:
        salt = os.urandom(16)  # 生成随机盐值
    kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1, backend=default_backend())
    key = kdf.derive(combined.encode())
    return key, salt


# 加密数据
def encrypt_data(data: bytes, key: bytes) -> bytes:
    iv = os.urandom(16)  # 生成随机初始化向量
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = iv + encryptor.update(data) + encryptor.finalize()
    return encrypted_data


# 解密数据
def decrypt_data(encrypted_data: bytes, key: bytes) -> bytes:
    iv = encrypted_data[:16]  # 从加密数据中提取初始化向量
    encrypted_data = encrypted_data[16:]
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
    return decrypted_data


# 获取加密的二进制数据
def get_encrypted_data(username, userpassword, original_bytes_data: bytes) -> bytes:
    key, salt = generate_key(username, userpassword)
    encrypted_data = encrypt_data(original_bytes_data, key)
    return salt + encrypted_data


# 获取解密的二进制数据
def get_decrypted_data(username, userpassword, encrypted_bytes_data: bytes) -> bytes:
    salt = encrypted_bytes_data[:16]
    encrypted_data = encrypted_bytes_data[16:]
    key, _ = generate_key(username, userpassword, salt)
    decrypted_data = decrypt_data(encrypted_data, key)
    return decrypted_data


if __name__ == "__main__":
    pass
    # import os
    # import uuid
    # from tqdm import tqdm

    # def test_custom_crypt():

    #     username = "admin"
    #     userpassword = "123456"

    #     key, salt = generate_key(username, userpassword)

    #     file_path = "./test/example.txt"
    #     original_content: str = "Hello, World!" * 1000
    #     with open(file_path, "wb") as file:
    #         data_bytes = (
    #             original_content.encode()
    #             if not isinstance(original_content, bytes)
    #             else original_content
    #         )
    #         encrypt_data_bytes = encrypt_data(data_bytes, key)
    #         # 在文件中保存盐值和加密后的数据
    #         file.write(salt + encrypt_data_bytes)

    #     with open(file_path, "rb") as file:
    #         # 从文件中读取盐值和加密后的数据
    #         file_content = file.read()
    #         salt = file_content[:16]
    #         encrypt_data_bytes = file_content[16:]
    #         key, _ = generate_key(username, userpassword, salt)
    #         decrypt_data_bytes = decrypt_data(encrypt_data_bytes, key)
    #         decrypt_original_content = decrypt_data_bytes.decode()
    #         # print(original_content)
    #         assert decrypt_original_content == original_content
    #         print("Decrypted content is the same as the original content.")
    #         print(decrypt_original_content)

    #     for i in tqdm(range(10)):
    #         username = "admin"
    #         userpassword = "123456"
    #         original_content: str = "-".join([str(uuid.uuid4()) for _ in range(1000)])
    #         original_content_bytes = original_content.encode()
    #         encrypted_databytes = get_encrypted_data(
    #             username, userpassword, original_content_bytes
    #         )
    #         decrypted_databytes = get_decrypted_data(
    #             username, userpassword, encrypted_databytes
    #         )

    #         assert decrypted_databytes == original_content_bytes

    # test_custom_crypt()
    # print("All tests passed.")
