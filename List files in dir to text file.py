import logging
import os
import sys
logger = logging.getLogger()

files_list = os.listdir()

with open("files_list.txt", "a", encoding="UTF-8") as textfile:
    for file in files_list:
        textfile.write(file + "\n")
