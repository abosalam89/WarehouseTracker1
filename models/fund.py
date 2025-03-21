#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fund model for ASSI Warehouse Management System
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.db_setup import Base
from datetime import datetime

class Fund(Base):
    """Fund model for financial management"""
    
    __tablename__ = 'funds'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    balance = Column(Float, default=0.0)
    currency = Column(String, default='USD')  # Currency (USD/SYP)
    exchange_rate = Column(Float, default=1.0)  # Manual exchange rate
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Fund transactions relationship
    transactions = relationship("FundTransaction", back_populates="fund", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Fund(name='{self.name}', balance={self.balance}, currency='{self.currency}')>"


class FundTransaction(Base):
    """Fund transaction model to track all financial movements"""
    
    __tablename__ = 'fund_transactions'
    
    id = Column(Integer, primary_key=True)
    fund_id = Column(Integer, ForeignKey('funds.id'), nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String, nullable=False)  # deposit, withdrawal, transfer
    description = Column(String)
    reference_id = Column(Integer)  # ID of related entity (invoice, expense, etc.)
    reference_type = Column(String)  # Type of related entity (invoice, expense, etc.)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with fund
    fund = relationship("Fund", back_populates="transactions")
    
    def __repr__(self):
        return f"<FundTransaction(fund_id={self.fund_id}, amount={self.amount}, type='{self.transaction_type}')>"
