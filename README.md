# com.haislund.docker.onecomddns

Docker image that update DNS values at One.com to the current detected IP address.

Logic for updating one.com entries are taken from https://github.com/lgc-4/one.com-ddns-python-script

## Logging
Logs are written to /data/status.log so mapping the /data directory to the Docker host might be a good idea.

## Configuration
Configuration is done in a config file.

The easiest way to get started is to create the container and change the default config file afterwards.

### Config file
The config file is located in /data/config.json, so mapping the /data directory to the Docker host is highly recommended to avoid loosing any changes to the default config.
By using the config file it is possible to update multiple DNS entries.

A small example of a config:
```
{
    "publish_interval": "3600",
    "log_size": "1000",
    "onecom": {
        "user": "email",
        "password": "password"
    },
    "records": [
        {
            "domain": "mydomain.com",
            "subdomains": [
                {
                    "name": "subname"
                }
            ]
        }
    ]
}
```

### Configuration variables

#### publish_interval
Seconds between checks whether the current IP has changed

#### log_size
Lines to keep in the log file

#### onecom / user
Username (mail) used to log into one.com

#### onecom / password
Password used to log into one.com

#### records
List of domains to update

#### records / domain
Name of a domain to update

#### records / subdomain
Sub-domain to update

## Running container
Example of creating/running the container:

```
docker image pull peterhaislund/onecom_ddns
docker create -e TZ=Europe/Copenhagen -v /volume1/docker/onecom_ddns:/data --name onecom_ddns peterhaislund/onecom_ddns
```

It is recommended to map the /data directory in the container to the Docker host.
