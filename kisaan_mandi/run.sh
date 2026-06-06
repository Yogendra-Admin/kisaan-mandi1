#!/bin/bash
echo "🌿 Starting Kisaan Mandi Server..."
cd "$(dirname "$0")"
python manage.py runserver 0.0.0.0:8000
