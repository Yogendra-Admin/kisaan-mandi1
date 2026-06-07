#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python kisaan_mandi/manage.py collectstatic --noinput

# Run database migrations
python kisaan_mandi/manage.py migrate
