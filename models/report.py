#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Report model for ASSI Warehouse Management System
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from database.db_setup import Base
from datetime import datetime

class Report(Base):
    """Report model for saving generated reports"""
    
    __tablename__ = 'reports'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # financial, inventory, sales, purchases, etc.
    parameters = Column(Text)  # JSON encoded parameters
    created_by = Column(Integer)
    is_favorite = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Report(name='{self.name}', type='{self.type}', created_at={self.created_at})>"
