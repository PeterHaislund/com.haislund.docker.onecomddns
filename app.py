import time  
import math
import traceback  
from logger import logger
from config import Config

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
    
           #do stuff

        except Exception as inst:
            logger.log(traceback.TracebackException.from_exception(inst).format())
                
        time.sleep(int(config["update_interval"]))

    client.loop_stop()  
    
except Exception as inst:
    logger.log(traceback.TracebackException.from_exception(inst).format())
