#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supplier and Customer controller for ASSI Warehouse Management System
"""

from database.db_setup import session
from models.supplier_customer import SupplierCustomer, Payment
from models.fund import Fund
from controllers.fund_controller import FundController
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

class SupplierCustomerController:
    """Controller for supplier and customer operations"""
    
    def __init__(self):
        self.fund_controller = FundController()
    
    def get_all_entities(self, entity_type=None):
        """Get all suppliers and customers, optionally filtered by type"""
        query = session.query(SupplierCustomer)
        
        if entity_type:
            if entity_type == 'both':
                # Include those marked as 'both' or the specific type
                query = query.filter(SupplierCustomer.type.in_([entity_type, 'both']))
            else:
                query = query.filter(SupplierCustomer.type.in_([entity_type, 'both']))
        
        return query.order_by(SupplierCustomer.name).all()
    
    def get_suppliers(self):
        """Get all suppliers (including entities marked as 'both')"""
        return self.get_all_entities(entity_type='supplier')
    
    def get_customers(self):
        """Get all customers (including entities marked as 'both')"""
        return self.get_all_entities(entity_type='customer')
    
    def get_entity_by_id(self, entity_id):
        """Get a supplier or customer by ID"""
        return session.query(SupplierCustomer).filter_by(id=entity_id).first()
    
    def create_entity(self, name, entity_type, phone=None, email=None, address=None, 
                      currency='USD', exchange_rate=1.0, notes=None):
        """Create a new supplier or customer
        
        Args:
            name: Name of entity
            entity_type: 'supplier', 'customer', or 'both'
            phone: Phone number
            email: Email address
            address: Physical address
            currency: Currency code
            exchange_rate: Exchange rate to USD
            notes: Additional notes
        """
        if entity_type not in ['supplier', 'customer', 'both']:
            return False, "Invalid entity type. Must be 'supplier', 'customer', or 'both'"
        
        try:
            entity = SupplierCustomer(
                name=name,
                type=entity_type,
                phone=phone,
                email=email,
                address=address,
                currency=currency,
                exchange_rate=float(exchange_rate),
                notes=notes
            )
            
            session.add(entity)
            session.commit()
            return True, entity
        except SQLAlchemyError as e:
            session.rollback()
            return False, f"Database error: {str(e)}"
        except Exception as e:
            return False, f"Error creating entity: {str(e)}"
    
    def update_entity(self, entity_id, name=None, entity_type=None, phone=None, 
                      email=None, address=None, currency=None, exchange_rate=None, notes=None):
        """Update an existing supplier or customer"""
        entity = self.get_entity_by_id(entity_id)
        
        if not entity:
            return False, "Entity not found"
        
        try:
            if name is not None:
                entity.name = name
            if entity_type is not None:
                if entity_type not in ['supplier', 'customer', 'both']:
                    return False, "Invalid entity type. Must be 'supplier', 'customer', or 'both'"
                entity.type = entity_type
            if phone is not None:
                entity.phone = phone
            if email is not None:
                entity.email = email
            if address is not None:
                entity.address = address
            if currency is not None:
                entity.currency = currency
            if exchange_rate is not None:
                entity.exchange_rate = float(exchange_rate)
            if notes is not None:
                entity.notes = notes
            
            entity.updated_at = datetime.utcnow()
            session.commit()
            return True, entity
        except SQLAlchemyError as e:
            session.rollback()
            return False, f"Database error: {str(e)}"
        except Exception as e:
            return False, f"Error updating entity: {str(e)}"
    
    def add_payment(self, entity_id, amount, payment_method='cash', fund_id=None, 
                    payment_date=None, notes=None, invoice_id=None):
        """Add a direct payment to/from a supplier or customer (not linked to an invoice)
        
        Args:
            entity_id: ID of supplier or customer
            amount: Payment amount (positive for receiving, negative for paying)
            payment_method: Method of payment
            fund_id: ID of fund for financial tracking
            payment_date: Date of payment (defaults to now)
            notes: Additional notes
            invoice_id: Optional invoice ID if this payment is for a specific invoice
        """
        entity = self.get_entity_by_id(entity_id)
        
        if not entity:
            return False, "Entity not found"
        
        if fund_id:
            fund = session.query(Fund).filter_by(id=fund_id).first()
            if not fund:
                return False, "Fund not found"
        
        try:
            # Determine payment direction
            is_payment_to_entity = amount < 0
            abs_amount = abs(amount)
            
            # Create payment record
            payment = Payment(
                entity_id=entity_id,
                amount=abs_amount,  # Always store as positive
                currency=entity.currency,
                exchange_rate=entity.exchange_rate,
                payment_date=payment_date or datetime.utcnow(),
                payment_method=payment_method,
                fund_id=fund_id,
                notes=notes,
                invoice_id=invoice_id
            )
            
            session.add(payment)
            
            # Update entity balance
            if is_payment_to_entity:
                # We're paying them, so decrease what they owe us or increase what we owe them
                entity.balance -= abs_amount
            else:
                # They're paying us, so increase what they owe us or decrease what we owe them
                entity.balance += abs_amount
            
            # Update fund if specified
            if fund_id:
                transaction_type = 'withdrawal' if is_payment_to_entity else 'deposit'
                description = f"{'Payment to' if is_payment_to_entity else 'Payment from'} {entity.name}"
                if notes:
                    description += f": {notes}"
                
                result, message = self.fund_controller.add_transaction(
                    fund_id=fund_id,
                    amount=abs_amount,
                    transaction_type=transaction_type,
                    description=description,
                    reference_id=payment.id,
                    reference_type='direct_payment'
                )
                
                if not result:
                    session.rollback()
                    return False, f"Failed to update fund: {message}"
            
            session.commit()
            return True, payment
        except SQLAlchemyError as e:
            session.rollback()
            return False, f"Database error: {str(e)}"
        except Exception as e:
            return False, f"Error adding payment: {str(e)}"
    
    def get_entity_payments(self, entity_id, start_date=None, end_date=None):
        """Get all payments for a specific entity with optional date filtering"""
        query = session.query(Payment).filter_by(entity_id=entity_id)
        
        if start_date:
            query = query.filter(Payment.payment_date >= start_date)
        
        if end_date:
            query = query.filter(Payment.payment_date <= end_date)
        
        return query.order_by(Payment.payment_date.desc()).all()
    
    def get_outstanding_balances(self, entity_type=None, min_balance=0):
        """Get entities with outstanding balances
        
        Args:
            entity_type: 'supplier', 'customer', or None for both
            min_balance: Minimum absolute balance to include
        
        Returns:
            List of entities with their outstanding balances
        """
        query = session.query(SupplierCustomer).filter(
            abs(SupplierCustomer.balance) >= min_balance
        )
        
        if entity_type:
            if entity_type == 'supplier':
                query = query.filter(SupplierCustomer.type.in_(['supplier', 'both']))
            elif entity_type == 'customer':
                query = query.filter(SupplierCustomer.type.in_(['customer', 'both']))
        
        return query.order_by(SupplierCustomer.balance.desc()).all()
