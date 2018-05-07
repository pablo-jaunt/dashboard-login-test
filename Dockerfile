############################################################
# Dockerfile to build Python WSGI Application Containers
############################################################
 
# The docker creators have built an image with Alpine OS and Python already
# installed.  We will base our container on this existing container image.
FROM python:3
 
# Set the Dockerfile Author / Maintainer
MAINTAINER pablo@jauntvr.com
 
# Install Python which is required for our app
RUN apt-get install -y python
 
# Set the default directory where CMD (specified below) will
# execute.  This also defines "./" as used below
WORKDIR /usr/src/app
 
# Copy requirements.txt file to /usr/src/app and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
 
# Copy the application folder inside the container
ADD . .
 
# Expose the port that the server will be listening on
EXPOSE 8080
 
# Set the default command to execute when the container is launched.
# i.e. using CherryPy to serve the application
CMD python server.py