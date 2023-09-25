# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory to /server
WORKDIR /server

# Copy the current directory contents into the container at /server
COPY PythonServer /server

RUN apt update && apt install -y nano 

RUN pip install --upgrade pip

RUN pip install --upgrade google-api-python-client

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

WORKDIR /storage/Palatial_V01_UE51/

# Run app.py when the container launches
CMD ["python", "/server/BuildServer.py"]
