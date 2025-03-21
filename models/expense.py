#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Expense model for ASSI Warehouse Management System
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.db_setup import Base
from datetime import datetime

class ExpenseCategory(Base):
    """Expense category model for categorizing expenses"""
    
    __tablename__ = 'expense_categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    expenses = relationship("Expense", back_populates="category")
    
    def __repr__(self):
        return f"<ExpenseCategory(name='{self.name}')>"


class Expense(Base):
    """Expense model for tracking costs"""
    
    __tablename__ = 'expenses'
    
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('expense_categories.id'), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default='USD')
    exchange_rate = Column(Float, default=1.0)
    expense_date = Column(DateTime, default=datetime.utcnow)
    description = Column(Text)
    fund_id = Column(Integer, ForeignKey('funds.id'))
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    category = relationship("ExpenseCategory", back_populates="expenses")
    
    def __repr__(self):
        return f"<Expense(category_id={self.category_id}, amount={self.amount}, date={self.expense_date})>"
