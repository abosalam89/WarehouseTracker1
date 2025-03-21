#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Database setup and session management for ASSI Warehouse Management System
"""

import os
import hashlib

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

# Create database connection
db_url = os.environ.get('DATABASE_URL')
engine = create_engine(db_url, echo=False)

# Create session factory
session_factory = sessionmaker(bind=engine)
session = scoped_session(session_factory)

# Create base class for models
Base = declarative_base()
Base.query = session.query_property()

def init_db():
    """Initialize the database, creating all tables"""
    # Import all models to ensure they're registered
    import models.user
    import models.warehouse
    import models.item
    import models.supplier_customer
    import models.invoice
    import models.fund
    import models.expense
    import models.report
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create default admin user if not exists
    create_admin_if_not_exists()
    
def create_admin_if_not_exists():
    """Create default admin user if it doesn't exist"""
    from models.user import User
    
    # Check if admin exists
    admin = session.query(User).filter_by(username='admin').first()
    
    if not admin:
        # Create admin user with default password
        admin = User(
            username='admin',
            full_name='Administrator',
            is_admin=True
        )
        
        # Set default password (admin)
        admin.set_password('admin')
        
        # Add to database
        session.add(admin)
        session.commit()