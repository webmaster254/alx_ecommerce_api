#!/bin/bash
# Simulate Render build process
echo "Testing build process..."
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py check
python manage.py test --keepdb
echo "Build test completed!"