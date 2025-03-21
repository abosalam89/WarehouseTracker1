#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supplier and Customer models for ASSI Warehouse Management System
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.db_setup import Base
from datetime import datetime
import enum

class EntityType(enum.Enum):
    """Entity type enumeration"""
    SUPPLIER = "supplier"
    CUSTOMER = "customer"
    BOTH = "both"

class SupplierCustomer(Base):
    """Supplier and Customer model for tracking business partners"""
    
    __tablename__ = 'suppliers_customers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # supplier, customer, both
    phone = Column(String)
    email = Column(String)
    address = Column(Text)
    balance = Column(Float, default=0.0)  # Outstanding balance
    currency = Column(String, default='USD')
    exchange_rate = Column(Float, default=1.0)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    invoices = relationship("Invoice", back_populates="entity")
    payments = relationship("Payment", back_populates="entity")
    
    def __repr__(self):
        return f"<SupplierCustomer(name='{self.name}', type='{self.type}', balance={self.balance})>"


class Payment(Base):
    """Payment model for tracking payments to suppliers or from customers"""
    
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True)
    entity_id = Column(Integer, ForeignKey('suppliers_customers.id'), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default='USD')
    exchange_rate = Column(Float, default=1.0)
    payment_date = Column(DateTime, default=datetime.utcnow)
    payment_method = Column(String)  # cash, bank transfer, etc.
    fund_id = Column(Integer, ForeignKey('funds.id'))
    notes = Column(Text)
    invoice_id = Column(Integer, ForeignKey('invoices.id'))  # Optional link to invoice
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    entity = relationship("SupplierCustomer", back_populates="payments")
    invoice = relationship("Invoice", back_populates="payments")
    
    def __repr__(self):
        return f"<Payment(entity_id={self.entity_id}, amount={self.amount}, payment_date={self.payment_date})>"
