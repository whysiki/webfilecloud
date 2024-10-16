import os
from rich import print
from pathlib import Path
from typing import Optional, Tuple, Any


def list_dir(path):
    return os.listdir(path)


# def path_glob(path, pattern):
# Path(path).glob(pattern)
def get_files_in_sys_dir_one_layer(
    path: str,
    extension: Optional[str] = None,
    *args: Tuple[Any],
    **kwargs: dict[str, Any],
):
    """
    path is a system directory

    if extension is None, return all files in the directory, just as os.listdir.only contain basename. with extension.

    if extension is not None, return all files with the extension in the directory.will contain relative file path.contain dir/filebasename. with extension.

    so why I write this function? 🥲

    """
    assert os.path.exists(path), f"Path not found: {path}"

    assert os.path.isdir(path), f"Path is not a directory: {path}"

    if extension:
        pathp = Path(path)
        ts_files = list(pathp.glob(f"*.{extension}"))
        ts_files2 = [
            Path(pathp, file.name).as_posix() for file in ts_files if file.is_file()
        ]
        assert len(ts_files) == len(
            ts_files2
        ), f"Error in get_files_in_sys_dir_one_layer: {ts_files} -> {ts_files2}"
        return ts_files2
    else:
        return os.listdir(path)


def test_list_dir():
    testdir = os.path.dirname(os.path.abspath(__file__))

    # print(list_dir(testdir))
    # print([i.as_posix() for i in list(Path(testdir).glob("*.py"))])
    print(get_files_in_sys_dir_one_layer(testdir))  # basebasename. with extension
    print(get_files_in_sys_dir_one_layer(testdir, "py"))  # full path. with extension


# test_list_dir()
if __name__ == "__main__":
    test_list_dir()
