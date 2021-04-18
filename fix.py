#!/usr/bin/python3

import requests
import os
import sys
import signal
from cryptography.fernet import Fernet


if __name__ == '__main__':
    with open("key.key", "rb") as keyFile:
        for file in os.listdir(os.path.expanduser('/home/test/')):
            if file.endswith(".txt"):
                filePath = os.path.join("/home/test/", file)
                f = Fernet(keyFile.read())
                with open(filePath, "rb") as fileContents:
                    data = fileContents.read()
                    decryptedData = f.decrypt(data)
                with open(filePath, "wb") as fileContents:
                    fileContents.write(decryptedData)
