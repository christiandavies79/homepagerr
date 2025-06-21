#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Run the initialization logic first.
# We explicitly tell python to run the main() function from the main.py script.
echo "--- Running initialization script ---"
python -c 'from main import main; main()'
echo "--- Initialization complete ---"

# Now that initialization is guaranteed to be done, start Gunicorn.
# The --access-logfile - and --error-logfile - flags will direct logs to the Docker console.
echo "--- Starting Gunicorn ---"
exec gunicorn --bind 0.0.0.0:8000 --access-logfile - --error-logfile - main:app
