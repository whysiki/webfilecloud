import os

def get_new_path(path: str):
    name, extension = path.split(".")[-2],path.split(".")[-1] if len(path.split(".")) > 1 else [path, '']
    def get_path_r(pathr: str, intn: int = 1):
        if os.path.exists(pathr):
            return get_path_r(f"{name}({intn}).{extension}" if extension else f"{name}({intn})", intn + 1)
        else:
            return pathr
    return get_path_r(path)

# print(get_new_path(r"D:\xraytest\filecloud\fastapi_backend\test\test_1.py"))
            
            