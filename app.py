import time  
import math
import traceback  
import requests
import json
import sys
import os.path
from logger import logger
from config import Config
from constants import IP_FILE

##########################
### FUNCTIONS
##########################   

def findBetween(haystack, needle1, needle2):
    index1 = haystack.find(needle1) + len(needle1)
    index2 = haystack.find(needle2, index1 + 1)
    return haystack[index1 : index2]


# will create a requests session and log you into your one.com account in that session
def loginSession(USERNAME,  PASSWORD, TARGET_DOMAIN=''):
    logger.log("Logging in...")

    # create requests session
    session = requests.session()

    # get admin panel to be redirected to login page
    redirectmeurl = "https://www.one.com/admin/"
    try:
        r = session.get(redirectmeurl)
    except requests.ConnectionError:
        raise SystemExit("Connection to one.com failed.")

    # find url to post login credentials to from form action attribute
    substrstart = '<form id="kc-form-login" class="Login-form login autofill" onsubmit="login.disabled = true; return true;" action="'
    substrend = '"'
    posturl = findBetween(r.text, substrstart, substrend).replace('&amp;','&')

    # post login data
    logindata = {'username': USERNAME, 'password': PASSWORD, 'credentialId' : ''}
    response = session.post(posturl, data=logindata)
    if response.text.find("Invalid username or password.") != -1:
        logger.log("!!! - Invalid credentials. Exiting")
        exit(1)

    logger.log("Login successful.")

    # For accounts with multiple domains it seems to still be needed to select which target domain to operate on.
    if TARGET_DOMAIN:
        logger.log("Setting active domain to: {}".format(TARGET_DOMAIN))
        selectAdminDomain(session, TARGET_DOMAIN)

    return session


def selectAdminDomain(session, DOMAIN):
    request_str = "https://www.one.com/admin/select-admin-domain.do?domain={}".format(DOMAIN)
    session.get(request_str)


# gets all DNS records on your domain.
def getCustomRecords(session, DOMAIN):
    logger.log("Getting Records")
    getres = session.get("https://www.one.com/admin/api/domains/" + DOMAIN + "/dns/custom_records").text
    if len(getres) == 0:
        logger.log("!!! - No records found. Exiting")
        exit()
    return json.loads(getres)["result"]["data"]


# finds the record id of a record from it's subdomain
def findIdBySubdomain(records, subdomain):
    logger.log("searching domain '" + subdomain + "'")
    for obj in records:
        if obj["attributes"]["prefix"] == subdomain:
            logger.log("Found Domain '" + subdomain + "': " + obj["id"])
            return obj["id"]
    return ""


# changes the IP Address of a TYPE A record. Default TTL=3800
def changeIP(session, ID, DOMAIN, SUBDOMAIN, IP, TTL=3600):
    logger.log("Changing IP on subdomain '" + SUBDOMAIN + "' - ID '" + ID + "' TO NEW IP '" + IP + "'")

    tosend = {"type":"dns_service_records","id":ID,"attributes":{"type":"A","prefix":SUBDOMAIN,"content":IP,"ttl":TTL}}

    dnsurl="https://www.one.com/admin/api/domains/" + DOMAIN + "/dns/custom_records/" + ID

    sendheaders={'Content-Type': 'application/json'}

    session.patch(dnsurl, data=json.dumps(tosend), headers=sendheaders)

    logger.log("Sent Change IP Request")

##########################
### APP CODE
##########################   

logger

try:
    logger = logger()

    config_loader = Config()
    config = config_loader.load_config()

    onecom_config = config["onecom"]
    
    onecom_user = onecom_config["user"]
    onecom_password = onecom_config["password"]
   
    while True:
        try: 
            logger.log("Updating dns")
    
            ip_changed = True

            current_ip = requests.get("https://api.ipify.org/").text

            logger.log(f"Detected IP: {current_ip}")
            
            # try to read file
            if (os.path.isfile(IP_FILE)):
                with open(IP_FILE,"r+") as f:
                    if (current_ip == f.read()):
                        # abort if ip in file is same as current
                        logger.log("IP Address hasn't changed. Aborting")
                        ip_changed = False

            if (ip_changed):
                logger.log("IP Address has changed.")

                for record in config["records"]:
                    domain = record["domain"]

                    # Create login session
                    s = loginSession(onecom_user, onecom_password, domain)

                    # get dns records
                    records = getCustomRecords(s, domain)
                    #logger.log(records)

                    for subdomain in record["subdomains"]:
                        subdomain_name = subdomain["name"]

                        #change ip address
                        recordid = findIdBySubdomain(records, subdomain_name)

                        if recordid == "":
                            logger.log("!!! - Record '" + subdomain_name + "' could not be found.")
                            continue

                        changeIP(s, recordid, domain, subdomain_name, current_ip, 600)
                        logger.log(f"IP Address for {subdomain_name}.{domain} changed to {current_ip}.")
                        
                # write current ip to file
                with open(IP_FILE,"w") as f:
                    f.write(current_ip)
                    
        except Exception as inst:
            logger.log(traceback.TracebackException.from_exception(inst).format())
                
        time.sleep(int(config["update_interval"]))

    client.loop_stop()  
    
except Exception as inst:
    logger.log(traceback.TracebackException.from_exception(inst).format())
