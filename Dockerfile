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

# Run Gunicorn to serve the app.
# Because the initialization logic in main.py is now at the top level,
# it will run automatically when Gunicorn imports the `app` object.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "main:app"]
