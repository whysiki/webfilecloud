import os
from pathlib import Path


def get_file_extension(filepath):
    try:
        # 使用 pathlib.Path 来获取文件路径对象
        path_obj = Path(filepath)

        # 使用 os.path.splitext 来分割文件名和后缀
        _, extension = os.path.splitext(path_obj.name)

        # 如果无法获取后缀，则返回 'binary'
        if not extension:
            return "binary"

        # 去除后缀中的点号，例如从 '.txt' 变为 'txt'
        return extension.lstrip(".")

    except Exception as e:
        print(f"获取文件后缀时出错: {e}")
        return "binary"


# 测试示例
file_path1 = "/path/to/file.txt"
file_path2 = "/path/to/unknown_file"

print(f"文件 {file_path1} 的后缀是: {get_file_extension(file_path1)}")
print(f"文件 {file_path2} 的后缀是: {get_file_extension(file_path2)}")
