#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASSI Warehouse Management System
Main Entry Point
"""

import os
import sys
from datetime import datetime

# Setup path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Initialize database
from database.db_setup import init_db, create_admin_if_not_exists

# Initialize database before importing the app
init_db()
create_admin_if_not_exists()

from web_app import app

if __name__ == '__main__':
    # Print startup message
    print(f"ASSI Warehouse Management System starting at {datetime.now()}")
    print(f"Running on http://0.0.0.0:5000/")
    
    # Run the Flask web application
    app.run(host='0.0.0.0', port=5000, debug=True)