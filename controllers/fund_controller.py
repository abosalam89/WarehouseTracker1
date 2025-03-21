#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fund controller for ASSI Warehouse Management System
"""

from database.db_setup import session
from models.fund import Fund, FundTransaction
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

class FundController:
    """Controller for fund operations"""
    
    def get_all_funds(self, active_only=True):
        """Get all funds, optionally filtering for active ones only"""
        query = session.query(Fund)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.all()
    
    def get_fund_by_id(self, fund_id):
        """Get a fund by its ID"""
        return session.query(Fund).filter_by(id=fund_id).first()
    
    def create_fund(self, name, currency='USD', exchange_rate=1.0, initial_balance=0.0):
        """Create a new fund"""
        try:
            fund = Fund(
                name=name,
                currency=currency,
                exchange_rate=float(exchange_rate),
                balance=float(initial_balance)
            )
            
            session.add(fund)
            session.commit()
            
            # If there's an initial balance, create a transaction
            if initial_balance > 0:
                self.add_transaction(
                    fund_id=fund.id,
                    amount=initial_balance,
                    transaction_type='deposit',
                    description='Initial balance'
                )
            
            return True, fund
        except SQLAlchemyError as e:
            session.rollback()
            return False, f"Database error: {str(e)}"
        except Exception as e:
            return False, f"Error creating fund: {str(e)}"
    
    def update_fund(self, fund_id, name=None, currency=None, exchange_rate=None, is_active=None):
        """Update an existing fund"""
        fund = self.get_fund_by_id(fund_id)
        
        if not fund:
            return False, "Fund not found"
        
        try:
            if name is not None:
                fund.name = name
            if currency is not None:
                fund.currency = currency
            if exchange_rate is not None:
                fund.exchange_rate = float(exchange_rate)
            if is_active is not None:
                fund.is_active = is_active
            
            fund.updated_at = datetime.utcnow()
            session.commit()
            return True, fund
        except SQLAlchemyError as e:
            session.rollback()
            return False, f"Database error: {str(e)}"
        except Exception as e:
            return False, f"Error updating fund: {str(e)}"
    
    def add_transaction(self, fund_id, amount, transaction_type, description=None, reference_id=None, reference_type=None):
        """Add a transaction to a fund and update the balance"""
        fund = self.get_fund_by_id(fund_id)
        
        if not fund:
            return False, "Fund not found"
        
        try:
            amount = float(amount)
            
            # Create transaction
            transaction = FundTransaction(
                fund_id=fund_id,
                amount=amount,
                transaction_type=transaction_type,
                description=description,
                reference_id=reference_id,
                reference_type=reference_type
            )
            
            session.add(transaction)
            
            # Update fund balance
            if transaction_type == 'deposit':
                fund.balance += amount
            elif transaction_type == 'withdrawal':
                fund.balance -= amount
            # For transfers, the balance is adjusted in separate operations
            
            fund.updated_at = datetime.utcnow()
            session.commit()
            return True, transaction
        except SQLAlchemyError as e:
            session.rollback()
            return False, f"Database error: {str(e)}"
        except Exception as e:
            return False, f"Error adding transaction: {str(e)}"
    
    def transfer_between_funds(self, from_fund_id, to_fund_id, amount, description=None):
        """Transfer money between two funds with proper exchange rate conversion"""
        from_fund = self.get_fund_by_id(from_fund_id)
        to_fund = self.get_fund_by_id(to_fund_id)
        
        if not from_fund:
            return False, "Source fund not found"
        
        if not to_fund:
            return False, "Destination fund not found"
        
        try:
            amount = float(amount)
            
            if from_fund.balance < amount:
                return False, "Insufficient balance in source fund"
            
            # Create withdrawal transaction
            withdrawal_result, withdrawal = self.add_transaction(
                fund_id=from_fund_id,
                amount=amount,
                transaction_type='withdrawal',
                description=f"Transfer to {to_fund.name}: {description}" if description else f"Transfer to {to_fund.name}"
            )
            
            if not withdrawal_result:
                return False, withdrawal  # withdrawal contains the error message
            
            # Calculate converted amount if currencies differ
            if from_fund.currency != to_fund.currency:
                # Convert to a common currency (USD) then to target currency
                usd_value = amount / from_fund.exchange_rate
                converted_amount = usd_value * to_fund.exchange_rate
            else:
                converted_amount = amount
            
            # Create deposit transaction
            deposit_result, deposit = self.add_transaction(
                fund_id=to_fund_id,
                amount=converted_amount,
                transaction_type='deposit',
                description=f"Transfer from {from_fund.name}: {description}" if description else f"Transfer from {from_fund.name}"
            )
            
            if not deposit_result:
                # Rollback the withdrawal if deposit fails
                self.add_transaction(
                    fund_id=from_fund_id,
                    amount=amount,
                    transaction_type='deposit',
                    description=f"Rollback of failed transfer to {to_fund.name}"
                )
                return False, deposit  # deposit contains the error message
            
            return True, {
                'from_fund': from_fund.name,
                'to_fund': to_fund.name,
                'amount': amount,
                'converted_amount': converted_amount
            }
        except SQLAlchemyError as e:
            session.rollback()
            return False, f"Database error: {str(e)}"
        except Exception as e:
            return False, f"Error transferring between funds: {str(e)}"
    
    def get_fund_transactions(self, fund_id, start_date=None, end_date=None, limit=100):
        """Get transactions for a specific fund with optional date filtering"""
        query = session.query(FundTransaction).filter_by(fund_id=fund_id)
        
        if start_date:
            query = query.filter(FundTransaction.created_at >= start_date)
        
        if end_date:
            query = query.filter(FundTransaction.created_at <= end_date)
        
        return query.order_by(FundTransaction.created_at.desc()).limit(limit).all()
