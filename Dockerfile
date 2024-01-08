####################################################################################
#### Build final image
####################################################################################
FROM python:3.7-alpine

#### Copy files
RUN mkdir app
RUN mkdir data

COPY /app.py /app/app.py
COPY /config.py /app/config.py
COPY /constants.py /app/constants.py
COPY /logger.py /app/logger.py

#### Install dependencies
RUN pip3 install requests

#### Set app.py as image main process
CMD [ "python3", "/app/app.py"]
