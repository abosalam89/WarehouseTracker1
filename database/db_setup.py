#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Database setup and session management for ASSI Warehouse Management System
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import hashlib

# Create the base class for declarative models
Base = declarative_base()

# Create engine and session
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assi_wms.db')
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)

# Create session factory
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
session = Session()

def init_db():
    """Initialize the database, creating all tables"""
    import models.user
    import models.fund
    import models.item
    import models.invoice
    import models.warehouse
    import models.expense
    import models.supplier_customer
    import models.report
    
    # Create all tables
    Base.metadata.create_all(engine)
    
def create_admin_if_not_exists():
    """Create default admin user if it doesn't exist"""
    from models.user import User
    
    # Check if admin user exists
    admin = session.query(User).filter_by(username='admin').first()
    
    if not admin:
        # Create admin user with default password 'admin'
        admin = User(username='admin', is_admin=True)
        admin.set_password('admin')
        session.add(admin)
        session.commit()
        print("Default admin user created with password 'admin'")
        print("Please change this password after first login.")
