#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Warehouse model for ASSI Warehouse Management System
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.db_setup import Base
from datetime import datetime

class Warehouse(Base):
    """Warehouse model for storing location information"""
    
    __tablename__ = 'warehouses'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    location = Column(String)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    stocks = relationship("ItemStock", back_populates="warehouse", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Warehouse(name='{self.name}', location='{self.location}')>"
