#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Item model for ASSI Warehouse Management System
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.db_setup import Base
from datetime import datetime

class Item(Base):
    """Item model for inventory management"""
    
    __tablename__ = 'items'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    main_unit = Column(String, nullable=False)  # Main unit (e.g., bag)
    sub_unit = Column(String, nullable=False)   # Sub unit (e.g., kg)
    conversion_rate = Column(Float, nullable=False)  # Relation (1 bag = 50 kg)
    purchase_price = Column(Float, nullable=False)  # Purchase price
    selling_price = Column(Float, nullable=False)   # Selling price
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    stocks = relationship("ItemStock", back_populates="item", cascade="all, delete-orphan")
    invoice_items = relationship("InvoiceItem", back_populates="item")
    
    def get_total_stock(self):
        """Calculate total stock across all warehouses"""
        return sum(stock.quantity for stock in self.stocks)
    
    def __repr__(self):
        return f"<Item(name='{self.name}', purchase_price={self.purchase_price}, selling_price={self.selling_price})>"


class ItemStock(Base):
    """Item stock model to track inventory in specific warehouses"""
    
    __tablename__ = 'item_stocks'
    
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'), nullable=False)
    quantity = Column(Float, default=0.0)  # In main unit
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    item = relationship("Item", back_populates="stocks")
    warehouse = relationship("Warehouse", back_populates="stocks")
    
    def __repr__(self):
        return f"<ItemStock(item_id={self.item_id}, warehouse_id={self.warehouse_id}, quantity={self.quantity})>"
