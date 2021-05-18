import os
import shutil


def create_or_empty_results_folder(folder: str, group: str):
    full_path = os.path.join(folder, group)
    if not os.path.exists(folder):
        os.mkdir(folder)
    if not os.path.exists(full_path):
        os.mkdir(full_path)
    else:
        shutil.rmtree(full_path)
        os.mkdir(full_path)


def ip_to_log_filename(ip: str):
    return ip.replace(".", "_") + ".log"
