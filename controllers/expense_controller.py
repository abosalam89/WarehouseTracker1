#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Expense controller for ASSI Warehouse Management System
"""

from database.db_setup import session
from models.expense import Expense, ExpenseCategory
from models.fund import Fund
from controllers.fund_controller import FundController
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

class ExpenseController:
    """Controller for expense operations"""
    
    def __init__(self):
        self.fund_controller = FundController()
    
    def get_all_expenses(self, start_date=None, end_date=None, category_id=None, limit=100):
        """Get all expenses with optional filtering"""
        query = session.query(Expense)
        
        if start_date:
            query = query.filter(Expense.expense_date >= start_date)
        
        if end_date:
            query = query.filter(Expense.expense_date <= end_date)
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        return query.order_by(Expense.expense_date.desc()).limit(limit).all()
    
    def get_expense_by_id(self, expense_id):
        """Get an expense by its ID"""
        return session.query(Expense).filter_by(id=expense_id).first()
    
    def create_expense(self, category_id, amount, expense_date=None, currency='USD', 
                       exchange_rate=1.0, description=None, fund_id=None, created_by=None):
        """Create a new expense
        
        Args:
            category_id: ID of expense category
            amount: Expense amount
            expense_date: Date of expense (defaults to now)
            currency: Currency code
            exchange_rate: Exchange rate to USD
            description: Description of expense
            fund_id: ID of fund for financial tracking
            created_by: ID of user creating the expense
        """
        category = session.query(ExpenseCategory).filter_by(id=category_id).first()
        
        if not category:
            return False, "Expense category not found"
        
        if fund_id:
            fund = session.query(Fund).filter_by(id=fund_id).first()
            if not fund:
                return False, "Fund not found"
        
        try:
            # Create expense
            expense = Expense(
                category_id=category_id,
                amount=float(amount),
                currency=currency,
                exchange_rate=float(exchange_rate),
                expense_date=expense_date or datetime.utcnow(),
                description=description,
                fund_id=fund_id,
                created_by=created_by
            )
            
            session.add(expense)
            
            # Update fund if specified
            if fund_id:
                result, message = self.fund_controller.add_transaction(
                    fund_id=fund_id,
                    amount=amount,
                    transaction_type='withdrawal',
                    description=f"Expense: {category.name} - {description or ''}",
                    reference_id=expense.id,
                    reference_type='expense'
                )
                
                if not result:
                    session.rollback()
                    return False, f"Failed to update fund: {message}"
            
            session.commit()
            return True, expense
        except SQLAlchemyError as e:
            session.rollback()
            return False, f"Database error: {str(e)}"
        except Exception as e:
            return False, f"Error creating expense: {str(e)}"
    
    def get_all_categories(self):
        """Get all expense categories"""
        return session.query(ExpenseCategory).all()
    
    def get_category_by_id(self, category_id):
        """Get a category by its ID"""
        return session.query(ExpenseCategory).filter_by(id=category_id).first()
    
    def create_category(self, name, description=None):
        """Create a new expense category"""
        try:
            category = ExpenseCategory(
                name=name,
                description=description
            )
            
            session.add(category)
            session.commit()
            return True, category
        except SQLAlchemyError as e:
            session.rollback()
            return False, f"Database error: {str(e)}"
        except Exception as e:
            return False, f"Error creating category: {str(e)}"
    
    def update_category(self, category_id, name=None, description=None):
        """Update an existing expense category"""
        category = self.get_category_by_id(category_id)
        
        if not category:
            return False, "Category not found"
        
        try:
            if name is not None:
                category.name = name
            if description is not None:
                category.description = description
            
            session.commit()
            return True, category
        except SQLAlchemyError as e:
            session.rollback()
            return False, f"Database error: {str(e)}"
        except Exception as e:
            return False, f"Error updating category: {str(e)}"
