#!/bin/bash

# Create necessary directories if they don't exist
mkdir -p app/static/css
mkdir -p app/static/js
mkdir -p app/static/img
mkdir -p app/templates/auth
mkdir -p app/templates/compliance
mkdir -p app/templates/dashboard
mkdir -p app/templates/email
mkdir -p app/templates/errors
mkdir -p app/templates/main
mkdir -p app/templates/settings
mkdir -p app/templates/threats
mkdir -p app/templates/vulnerabilities

# Create empty __init__.py files in directories that need them
touch app/models/__init__.py
touch app/controllers/__init__.py
touch app/utils/__init__.py

# Install dependencies
pip install -r requirements.txt

# Initialize the database
export FLASK_APP=run.py
flask init-db

# Run the application
python run.py

