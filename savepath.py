import os

save_path = '/mnt/HDD4'
check_exists_path = []  # ['/mnt/HDD2', '/mnt/HDD3', '/mnt/HDD4']


def check_exists(*names):
    if not check_exists_path:
        return False
    for p in check_exists_path:
        check_path = os.path.join(p, *names)
        if os.path.exists(check_path):
            return True
    return False
