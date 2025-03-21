#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Warehouse controller for ASSI Warehouse Management System
"""

from database.db_setup import session
from models.warehouse import Warehouse
from models.item import ItemStock
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

class WarehouseController:
    """Controller for warehouse operations"""
    
    def get_all_warehouses(self, active_only=True):
        """Get all warehouses, optionally filtering for active ones only"""
        query = session.query(Warehouse)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.all()
    
    def get_warehouse_by_id(self, warehouse_id):
        """Get a warehouse by its ID"""
        return session.query(Warehouse).filter_by(id=warehouse_id).first()
    
    def create_warehouse(self, name, location=None, description=None):
        """Create a new warehouse"""
        try:
            warehouse = Warehouse(
                name=name,
                location=location,
                description=description
            )
            
            session.add(warehouse)
            session.commit()
            return True, warehouse
        except SQLAlchemyError as e:
            session.rollback()
            return False, f"Database error: {str(e)}"
        except Exception as e:
            return False, f"Error creating warehouse: {str(e)}"
    
    def update_warehouse(self, warehouse_id, name=None, location=None, description=None, is_active=None):
        """Update an existing warehouse"""
        warehouse = self.get_warehouse_by_id(warehouse_id)
        
        if not warehouse:
            return False, "Warehouse not found"
        
        try:
            if name is not None:
                warehouse.name = name
            if location is not None:
                warehouse.location = location
            if description is not None:
                warehouse.description = description
            if is_active is not None:
                warehouse.is_active = is_active
            
            warehouse.updated_at = datetime.utcnow()
            session.commit()
            return True, warehouse
        except SQLAlchemyError as e:
            session.rollback()
            return False, f"Database error: {str(e)}"
        except Exception as e:
            return False, f"Error updating warehouse: {str(e)}"
    
    def get_warehouse_stock(self, warehouse_id):
        """Get all items and their quantities in a specific warehouse"""
        return session.query(ItemStock).filter_by(warehouse_id=warehouse_id).all()
    
    def get_warehouse_inventory_value(self, warehouse_id):
        """Calculate the total value of inventory in a warehouse"""
        total_value = 0
        stocks = self.get_warehouse_stock(warehouse_id)
        
        for stock in stocks:
            item = stock.item
            total_value += stock.quantity * item.purchase_price
            
        return total_value
