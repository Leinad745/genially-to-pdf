import os


def create_directory(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)


def remove_directory_recursively(path: str) -> None:
    if not os.path.exists(path):
        return
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            remove_directory_recursively(file_path)
    os.rmdir(path)
