#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Invoice controller for ASSI Warehouse Management System
"""

from database.db_setup import session
from models.invoice import Invoice, InvoiceItem
from models.supplier_customer import SupplierCustomer, Payment
from models.item import Item
from models.fund import Fund
from controllers.item_controller import ItemController
from controllers.fund_controller import FundController
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import uuid

class InvoiceController:
    """Controller for invoice operations"""
    
    def __init__(self):
        self.item_controller = ItemController()
        self.fund_controller = FundController()
    
    def get_all_invoices(self, invoice_type=None, status=None, start_date=None, end_date=None, limit=100):
        """Get all invoices with optional filtering"""
        query = session.query(Invoice)
        
        if invoice_type:
            query = query.filter_by(type=invoice_type)
        
        if status:
            query = query.filter_by(status=status)
        
        if start_date:
            query = query.filter(Invoice.invoice_date >= start_date)
        
        if end_date:
            query = query.filter(Invoice.invoice_date <= end_date)
        
        return query.order_by(Invoice.invoice_date.desc()).limit(limit).all()
    
    def get_invoice_by_id(self, invoice_id):
        """Get an invoice by its ID"""
        return session.query(Invoice).filter_by(id=invoice_id).first()
    
    def create_invoice(self, invoice_type, entity_id, items_data, warehouse_id, 
                       invoice_date=None, due_date=None, currency='USD', 
                       exchange_rate=1.0, additional_costs=0.0, tax=0.0, notes=None):
        """Create a new invoice
        
        Args:
            invoice_type: 'purchase' or 'sale'
            entity_id: ID of supplier or customer
            items_data: List of dicts with keys: item_id, quantity, unit, price_per_unit
            warehouse_id: ID of warehouse for stock updates
            invoice_date: Date of invoice (defaults to now)
            due_date: Due date for payment (for deferred payment)
            currency: Currency code
            exchange_rate: Exchange rate to USD
            additional_costs: Additional costs
            tax: Tax amount
            notes: Additional notes
        """
        entity = session.query(SupplierCustomer).filter_by(id=entity_id).first()
        
        if not entity:
            return False, "Supplier/Customer not found"
        
        # Validate entity type matches invoice type
        if invoice_type == 'purchase' and entity.type not in ['supplier', 'both']:
            return False, "Entity is not a supplier"
        elif invoice_type == 'sale' and entity.type not in ['customer', 'both']:
            return False, "Entity is not a customer"
        
        # Generate unique invoice number
        invoice_number = f"{invoice_type[:1].upper()}-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        try:
            # Create invoice
            invoice = Invoice(
                invoice_number=invoice_number,
                type=invoice_type,
                entity_id=entity_id,
                total_amount=0,  # Will be calculated below
                currency=currency,
                exchange_rate=float(exchange_rate),
                additional_costs=float(additional_costs),
                tax=float(tax),
                invoice_date=invoice_date or datetime.utcnow(),
                due_date=due_date,
                notes=notes,
                status='pending'
            )
            
            session.add(invoice)
            session.flush()  # Get invoice ID without committing
            
            # Process items and update total
            total_amount = 0
            for item_data in items_data:
                item_id = item_data['item_id']
                quantity = float(item_data['quantity'])
                unit = item_data['unit']
                price_per_unit = float(item_data['price_per_unit'])
                
                item = self.item_controller.get_item_by_id(item_id)
                if not item:
                    session.rollback()
                    return False, f"Item with ID {item_id} not found"
                
                # Calculate total price for this item
                total_price = quantity * price_per_unit
                total_amount += total_price
                
                # Create invoice item
                invoice_item = InvoiceItem(
                    invoice_id=invoice.id,
                    item_id=item_id,
                    quantity=quantity,
                    unit=unit,
                    price_per_unit=price_per_unit,
                    total_price=total_price,
                    warehouse_id=warehouse_id
                )
                
                session.add(invoice_item)
                
                # Update stock based on invoice type
                quantity_main_unit = quantity
                if unit == item.sub_unit:
                    # Convert to main unit if needed
                    quantity_main_unit = quantity / item.conversion_rate
                
                if invoice_type == 'purchase':
                    # Increase stock for purchases
                    self.item_controller.update_stock(
                        item_id=item_id,
                        warehouse_id=warehouse_id,
                        quantity_change=quantity_main_unit
                    )
                else:  # 'sale'
                    # Decrease stock for sales
                    self.item_controller.update_stock(
                        item_id=item_id,
                        warehouse_id=warehouse_id,
                        quantity_change=-quantity_main_unit
                    )
            
            # Update invoice total (including additional costs and tax)
            invoice.total_amount = total_amount + additional_costs + tax
            
            # Update entity balance
            if invoice_type == 'purchase':
                # Increase supplier balance (we owe them money)
                entity.balance += invoice.total_amount
            else:  # 'sale'
                # Increase customer balance (they owe us money)
                entity.balance += invoice.total_amount
            
            session.commit()
            return True, invoice
        except SQLAlchemyError as e:
            session.rollback()
            return False, f"Database error: {str(e)}"
        except Exception as e:
            session.rollback()
            return False, f"Error creating invoice: {str(e)}"
    
    def record_payment(self, invoice_id, amount, payment_date=None, 
                       payment_method='cash', fund_id=None, notes=None):
        """Record a payment for an invoice
        
        Args:
            invoice_id: ID of the invoice
            amount: Payment amount
            payment_date: Date of payment (defaults to now)
            payment_method: Method of payment
            fund_id: ID of fund for financial tracking
            notes: Additional notes
        """
        invoice = self.get_invoice_by_id(invoice_id)
        
        if not invoice:
            return False, "Invoice not found"
        
        if fund_id:
            fund = session.query(Fund).filter_by(id=fund_id).first()
            if not fund:
                return False, "Fund not found"
        
        # Calculate remaining amount
        remaining_amount = invoice.calculate_remaining_amount()
        
        if amount > remaining_amount:
            return False, f"Payment amount exceeds remaining balance ({remaining_amount})"
        
        try:
            # Create payment
            payment = Payment(
                entity_id=invoice.entity_id,
                amount=float(amount),
                currency=invoice.currency,
                exchange_rate=invoice.exchange_rate,
                payment_date=payment_date or datetime.utcnow(),
                payment_method=payment_method,
                fund_id=fund_id,
                notes=notes,
                invoice_id=invoice_id
            )
            
            session.add(payment)
            
            # Update entity balance
            entity = session.query(SupplierCustomer).filter_by(id=invoice.entity_id).first()
            
            if invoice.type == 'purchase':
                # Decrease supplier balance (we paid them)
                entity.balance -= amount
            else:  # 'sale'
                # Decrease customer balance (they paid us)
                entity.balance -= amount
            
            # Update invoice status
            new_paid_amount = invoice.calculate_paid_amount() + amount
            if new_paid_amount >= invoice.total_amount:
                invoice.status = 'paid'
            else:
                invoice.status = 'partially_paid'
            
            # Update fund if specified
            if fund_id:
                transaction_type = 'withdrawal' if invoice.type == 'purchase' else 'deposit'
                reference_type = 'invoice_payment'
                description = f"{'Payment to supplier' if invoice.type == 'purchase' else 'Payment from customer'} for invoice #{invoice.invoice_number}"
                
                self.fund_controller.add_transaction(
                    fund_id=fund_id,
                    amount=amount,
                    transaction_type=transaction_type,
                    description=description,
                    reference_id=payment.id,
                    reference_type=reference_type
                )
            
            session.commit()
            return True, payment
        except SQLAlchemyError as e:
            session.rollback()
            return False, f"Database error: {str(e)}"
        except Exception as e:
            session.rollback()
            return False, f"Error recording payment: {str(e)}"
    
    def get_invoice_items(self, invoice_id):
        """Get all items for a specific invoice"""
        return session.query(InvoiceItem).filter_by(invoice_id=invoice_id).all()
    
    def get_invoice_payments(self, invoice_id):
        """Get all payments for a specific invoice"""
        return session.query(Payment).filter_by(invoice_id=invoice_id).all()
    
    def cancel_invoice(self, invoice_id):
        """Cancel an invoice and reverse its effects on stock and balances"""
        invoice = self.get_invoice_by_id(invoice_id)
        
        if not invoice:
            return False, "Invoice not found"
        
        if invoice.status == 'cancelled':
            return False, "Invoice is already cancelled"
        
        try:
            # Get all items in the invoice
            invoice_items = self.get_invoice_items(invoice_id)
            
            # Reverse stock changes
            for invoice_item in invoice_items:
                item = self.item_controller.get_item_by_id(invoice_item.item_id)
                
                # Convert to main unit if needed
                quantity_main_unit = invoice_item.quantity
                if invoice_item.unit == item.sub_unit:
                    quantity_main_unit = invoice_item.quantity / item.conversion_rate
                
                # Reverse the stock change
                if invoice.type == 'purchase':
                    # Decrease stock (reverse of purchase)
                    self.item_controller.update_stock(
                        item_id=invoice_item.item_id,
                        warehouse_id=invoice_item.warehouse_id,
                        quantity_change=-quantity_main_unit
                    )
                else:  # 'sale'
                    # Increase stock (reverse of sale)
                    self.item_controller.update_stock(
                        item_id=invoice_item.item_id,
                        warehouse_id=invoice_item.warehouse_id,
                        quantity_change=quantity_main_unit
                    )
            
            # Update entity balance
            entity = session.query(SupplierCustomer).filter_by(id=invoice.entity_id).first()
            
            # Adjust for payments already made
            paid_amount = invoice.calculate_paid_amount()
            remaining_amount = invoice.total_amount - paid_amount
            
            if invoice.type == 'purchase':
                # Decrease supplier balance (we no longer owe them)
                entity.balance -= remaining_amount
            else:  # 'sale'
                # Decrease customer balance (they no longer owe us)
                entity.balance -= remaining_amount
            
            # Mark invoice as cancelled
            invoice.status = 'cancelled'
            
            session.commit()
            return True, "Invoice cancelled successfully"
        except SQLAlchemyError as e:
            session.rollback()
            return False, f"Database error: {str(e)}"
        except Exception as e:
            session.rollback()
            return False, f"Error cancelling invoice: {str(e)}"
