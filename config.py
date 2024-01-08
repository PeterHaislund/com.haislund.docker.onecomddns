import json
import os.path
import os  
from constants import CONFIG_FILE

class Config:
    def load_config(self):
        self.validate_config()
        
        with open(CONFIG_FILE, 'r') as openfile:
            config = json.load(openfile)
    
        return config    
    
    def validate_config(self):
        if not os.path.isfile(CONFIG_FILE):
            # Generate default config if config file doesn't exist
            config = {
                "update_interval": 3600,
                "log_size": 5000,
                "onecom": {
                    "user": "username",
                    "password": "password"
                },
                "records": [
                    {
                        "domain": "haislund.com",
                        "subdomains": [
                          {
                            "name": "home"
                          }
                        ]
                    }
                ]
            }
              
            with open(CONFIG_FILE, 'a') as outfile:
              json.dump(config, outfile, indent=4)
