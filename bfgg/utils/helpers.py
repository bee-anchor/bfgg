import os
import shutil


def create_or_empty_folder(folder):
    if not os.path.exists(folder):
        os.mkdir(folder)
    else:
        for i in os.listdir(folder):
            if os.path.isfile(os.path.join(folder, i)):
                os.remove(os.path.join(folder, i))
            elif os.path.isdir(os.path.join(folder, i)):
                shutil.rmtree(os.path.join(folder, i))


def ip_to_log_filename(ip: str):
    return ip.replace('.', '_') + '.log'
