#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
User model for ASSI Warehouse Management System
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from database.db_setup import Base
import hashlib
from datetime import datetime

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
        self.password = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password):
        """Check if the provided password matches the stored hash"""
        return self.password == hashlib.sha256(password.encode()).hexdigest()
    
    def record_login(self):
        """Record the current time as the last login time"""
        self.last_login = datetime.utcnow()
    
    def __repr__(self):
        return f"<User(username='{self.username}', is_admin={self.is_admin})>"
