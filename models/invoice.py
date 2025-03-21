#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Invoice model for ASSI Warehouse Management System
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.db_setup import Base
from datetime import datetime

class Invoice(Base):
    """Invoice model for purchase and sales"""
    
    __tablename__ = 'invoices'
    
    id = Column(Integer, primary_key=True)
    invoice_number = Column(String, unique=True)
    type = Column(String, nullable=False)  # purchase, sale
    entity_id = Column(Integer, ForeignKey('suppliers_customers.id'), nullable=False)
    total_amount = Column(Float, nullable=False)
    currency = Column(String, default='USD')
    exchange_rate = Column(Float, default=1.0)
    additional_costs = Column(Float, default=0.0)  # Additional costs
    tax = Column(Float, default=0.0)  # Tax
    invoice_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime)  # For deferred payment
    status = Column(String, default='pending')  # pending, paid, partially_paid
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    entity = relationship("SupplierCustomer", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice")
    
    def calculate_paid_amount(self):
        """Calculate the total amount paid on this invoice"""
        return sum(payment.amount for payment in self.payments)
    
    def calculate_remaining_amount(self):
        """Calculate the remaining unpaid amount"""
        return self.total_amount - self.calculate_paid_amount()
        
    def __repr__(self):
        return f"<Invoice(number='{self.invoice_number}', type='{self.type}', total={self.total_amount}, status='{self.status}')>"


class InvoiceItem(Base):
    """Invoice item model for items within an invoice"""
    
    __tablename__ = 'invoice_items'
    
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey('invoices.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False)  # main_unit or sub_unit
    price_per_unit = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'))
    
    # Relationships
    invoice = relationship("Invoice", back_populates="items")
    item = relationship("Item", back_populates="invoice_items")
    
    def __repr__(self):
        return f"<InvoiceItem(invoice_id={self.invoice_id}, item_id={self.item_id}, quantity={self.quantity}, total_price={self.total_price})>"
