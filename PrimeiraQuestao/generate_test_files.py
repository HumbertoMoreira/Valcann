import os
import time
from datetime import datetime, timedelta


directory = "/mnt/efs-simulada/backupsFrom"
os.makedirs(directory, exist_ok=True)


def create_test_files(directory, days_range):
    current_time = time.time()
    for days in range(1, days_range + 1):
        file_path = os.path.join(directory, f"file_{days}_days_old.txt")
        with open(file_path, "w") as f:
            f.write(f"This file is {days} days old.\n")


        file_time = current_time - (days * 24 * 60 * 60)
        os.utime(file_path, (file_time, file_time))
        print(f"Created: {file_path} with date {datetime.fromtimestamp(file_time)}")


create_test_files(directory, 5)
