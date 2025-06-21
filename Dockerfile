# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies that might be needed
# (Keeping this as it is good practice, though not strictly needed for this app)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code and the new startup script
COPY main.py .
COPY start.sh .

# Make the startup script executable
RUN chmod +x ./start.sh

# Define the volume that will hold your data and static files.
VOLUME /app/config

# Run the startup script.
# This will run the initialization and then start Gunicorn.
CMD ["./start.sh"]
