#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
User model for ASSI Warehouse Management System
"""

import hashlib
from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from database.db_setup import Base

class User(Base):
    """User model for authentication and authorization"""
    
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  # Stored as SHA256 hash
    full_name = Column(String)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    def set_password(self, password):
        """Hash and set the user's password"""
        # Simple SHA256 hash - in a real-world scenario, use a proper password hashing library
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        self.password = password_hash
        
    def check_password(self, password):
        """Check if the provided password matches the stored hash"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return self.password == password_hash
        
    def record_login(self):
        """Record the current time as the last login time"""
        self.last_login = datetime.utcnow()
        
    def __repr__(self):
        return f"<User {self.username}>"