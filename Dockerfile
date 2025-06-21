# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies that might be needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main application file into the container
COPY main.py .

# Define the volume that will hold your data and static files.
# This allows you to manage your config, data, and frontend files outside the container.
VOLUME /app/config

# Run the initialization function and then start Gunicorn when the container launches.
# Gunicorn is a robust production WSGI server.
# The 'CMD' command will execute the python script which will initialize and then Gunicorn will take over.
# We're using an entrypoint script to ensure initialization runs first.
CMD ["sh", "-c", "python main.py && gunicorn --bind 0.0.0.0:8000 main:app"]
