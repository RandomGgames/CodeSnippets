import os

files = os.listdir()

with open("files.txt", "a", encoding="UTF-8") as textfile:
    for file in files:
        textfile.write(file + "\n")
