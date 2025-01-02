# Use an official Python runtime as a parent image
FROM python:3.11.8

# Set the working directory in the container to /app
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt /app/

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Make port 8900 available to the world outside this container
EXPOSE 8900

# Run the command to start uvicorn
CMD ["python", "main.py"]