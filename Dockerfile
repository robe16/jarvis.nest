FROM resin/rpi-raspbian:latest
MAINTAINER robe16

# Port number to listen on
ARG portApplication
ENV portA ${portApplication}

# Update
RUN apt-get update && apt-get install -y python python-pip

WORKDIR /jarvis/nest

# Bundle app source
COPY src /jarvis/nest

# Copy app dependencies
COPY requirements.txt requirements.txt

# Install app dependencies
RUN pip install -r requirements.txt

# Run application
CMD python run.py ${portA}