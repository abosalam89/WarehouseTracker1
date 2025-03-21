#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Item controller for ASSI Warehouse Management System
"""

from database.db_setup import session
from models.item import Item, ItemStock
from models.warehouse import Warehouse
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

class ItemController:
    """Controller for item operations"""
    
    def get_all_items(self, active_only=True):
        """Get all items, optionally filtering for active ones only"""
        query = session.query(Item)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.all()
    
    def get_item_by_id(self, item_id):
        """Get an item by its ID"""
        return session.query(Item).filter_by(id=item_id).first()
    
    def create_item(self, name, main_unit, sub_unit, conversion_rate, 
                    purchase_price, selling_price, description=None):
        """Create a new item"""
        try:
            item = Item(
                name=name,
                description=description,
                main_unit=main_unit,
                sub_unit=sub_unit,
                conversion_rate=float(conversion_rate),
                purchase_price=float(purchase_price),
                selling_price=float(selling_price)
            )
            
            session.add(item)
            session.commit()
            return True, item
        except SQLAlchemyError as e:
            session.rollback()
            return False, f"Database error: {str(e)}"
        except Exception as e:
            return False, f"Error creating item: {str(e)}"
    
    def update_item(self, item_id, name=None, description=None, main_unit=None, 
                    sub_unit=None, conversion_rate=None, purchase_price=None, 
                    selling_price=None, is_active=None):
        """Update an existing item"""
        item = self.get_item_by_id(item_id)
        
        if not item:
            return False, "Item not found"
        
        try:
            if name is not None:
                item.name = name
            if description is not None:
                item.description = description
            if main_unit is not None:
                item.main_unit = main_unit
            if sub_unit is not None:
                item.sub_unit = sub_unit
            if conversion_rate is not None:
                item.conversion_rate = float(conversion_rate)
            if purchase_price is not None:
                item.purchase_price = float(purchase_price)
            if selling_price is not None:
                item.selling_price = float(selling_price)
            if is_active is not None:
                item.is_active = is_active
            
            item.updated_at = datetime.utcnow()
            session.commit()
            return True, item
        except SQLAlchemyError as e:
            session.rollback()
            return False, f"Database error: {str(e)}"
        except Exception as e:
            return False, f"Error updating item: {str(e)}"
    
    def get_item_stock(self, item_id, warehouse_id=None):
        """Get stock information for an item, optionally filtered by warehouse"""
        query = session.query(ItemStock).filter_by(item_id=item_id)
        
        if warehouse_id:
            return query.filter_by(warehouse_id=warehouse_id).first()
        
        return query.all()
    
    def update_stock(self, item_id, warehouse_id, quantity_change, is_absolute=False):
        """Update stock for an item in a warehouse
        
        Args:
            item_id: ID of the item
            warehouse_id: ID of the warehouse
            quantity_change: Quantity to add (positive) or remove (negative),
                           or absolute quantity if is_absolute=True
            is_absolute: If True, sets the stock to the exact quantity_change value
        """
        item = self.get_item_by_id(item_id)
        warehouse = session.query(Warehouse).filter_by(id=warehouse_id).first()
        
        if not item:
            return False, "Item not found"
        
        if not warehouse:
            return False, "Warehouse not found"
        
        try:
            stock = session.query(ItemStock).filter_by(
                item_id=item_id, warehouse_id=warehouse_id
            ).first()
            
            if not stock:
                # Create new stock entry if it doesn't exist
                stock = ItemStock(
                    item_id=item_id,
                    warehouse_id=warehouse_id,
                    quantity=0
                )
                session.add(stock)
            
            # Update quantity
            if is_absolute:
                stock.quantity = float(quantity_change)
            else:
                stock.quantity += float(quantity_change)
                
                # Prevent negative stock unless specifically allowed
                if stock.quantity < 0:
                    return False, "Insufficient stock quantity"
            
            stock.updated_at = datetime.utcnow()
            session.commit()
            return True, stock
        except SQLAlchemyError as e:
            session.rollback()
            return False, f"Database error: {str(e)}"
        except Exception as e:
            return False, f"Error updating stock: {str(e)}"
    
    def transfer_stock(self, item_id, from_warehouse_id, to_warehouse_id, quantity):
        """Transfer stock of an item from one warehouse to another"""
        item = self.get_item_by_id(item_id)
        from_warehouse = session.query(Warehouse).filter_by(id=from_warehouse_id).first()
        to_warehouse = session.query(Warehouse).filter_by(id=to_warehouse_id).first()
        
        if not item:
            return False, "Item not found"
        
        if not from_warehouse:
            return False, "Source warehouse not found"
        
        if not to_warehouse:
            return False, "Destination warehouse not found"
        
        from_stock = self.get_item_stock(item_id, from_warehouse_id)
        
        if not from_stock or from_stock.quantity < quantity:
            return False, "Insufficient stock in source warehouse"
        
        try:
            # Remove from source warehouse
            remove_result, _ = self.update_stock(
                item_id=item_id,
                warehouse_id=from_warehouse_id,
                quantity_change=-quantity
            )
            
            if not remove_result:
                return False, "Failed to remove stock from source warehouse"
            
            # Add to destination warehouse
            add_result, _ = self.update_stock(
                item_id=item_id,
                warehouse_id=to_warehouse_id,
                quantity_change=quantity
            )
            
            if not add_result:
                # Rollback if adding fails
                self.update_stock(
                    item_id=item_id,
                    warehouse_id=from_warehouse_id,
                    quantity_change=quantity
                )
                return False, "Failed to add stock to destination warehouse"
            
            return True, {
                'item': item.name,
                'from_warehouse': from_warehouse.name,
                'to_warehouse': to_warehouse.name,
                'quantity': quantity
            }
        except Exception as e:
            return False, f"Error transferring stock: {str(e)}"
    
    def get_low_stock_items(self, threshold=10):
        """Get items with low stock (below threshold)"""
        low_stock_items = []
        
        for item in self.get_all_items():
            total_stock = item.get_total_stock()
            if total_stock < threshold:
                low_stock_items.append({
                    'item': item,
                    'total_stock': total_stock
                })
        
        return low_stock_items
