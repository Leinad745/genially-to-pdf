import os
from app.config import PRESENTATION_DIRECTORY, SLIDES_DIRECTORY, TIME_BEFORE_CLEANUP
import time


def cleanup_files() -> None:
    if os.path.exists(PRESENTATION_DIRECTORY):
        for filename in os.listdir(PRESENTATION_DIRECTORY):
            file_path = os.path.join(PRESENTATION_DIRECTORY, filename)
            if os.path.isfile(file_path):
                file_age = time.time() - os.path.getctime(file_path)
                if file_age > TIME_BEFORE_CLEANUP:
                    os.remove(file_path)

    if os.path.exists(SLIDES_DIRECTORY):
        for slides_directory in os.listdir(SLIDES_DIRECTORY):
            dir_path = os.path.join(SLIDES_DIRECTORY, slides_directory)
            if os.path.isdir(dir_path):
                dir_age = time.time() - os.path.getctime(dir_path)
                if dir_age > TIME_BEFORE_CLEANUP:
                    for filename in os.listdir(dir_path):
                        file_path = os.path.join(dir_path, filename)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    os.rmdir(dir_path)
