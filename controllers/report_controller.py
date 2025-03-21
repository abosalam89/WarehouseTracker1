#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Report controller for ASSI Warehouse Management System
"""

from database.db_setup import session
from models.report import Report
from models.invoice import Invoice, InvoiceItem
from models.supplier_customer import SupplierCustomer, Payment
from models.fund import Fund, FundTransaction
from models.item import Item, ItemStock
from models.expense import Expense, ExpenseCategory

from sqlalchemy import func, desc, extract
import json
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from io import BytesIO
import base64

# Configure matplotlib to use a non-GUI backend
matplotlib.use('Agg')

class ReportController:
    """Controller for generating reports"""
    
    def save_report(self, name, report_type, parameters, created_by=None, is_favorite=False):
        """Save a report configuration for future use"""
        try:
            # Convert parameters to JSON if they're not already a string
            if not isinstance(parameters, str):
                parameters = json.dumps(parameters)
            
            report = Report(
                name=name,
                type=report_type,
                parameters=parameters,
                created_by=created_by,
                is_favorite=is_favorite
            )
            
            session.add(report)
            session.commit()
            return True, report
        except Exception as e:
            session.rollback()
            return False, f"Error saving report: {str(e)}"
    
    def get_saved_reports(self, report_type=None, created_by=None):
        """Get saved report configurations"""
        query = session.query(Report)
        
        if report_type:
            query = query.filter_by(type=report_type)
        
        if created_by:
            query = query.filter_by(created_by=created_by)
        
        return query.order_by(Report.created_at.desc()).all()
    
    def get_favorite_reports(self, created_by=None):
        """Get favorite report configurations"""
        query = session.query(Report).filter_by(is_favorite=True)
        
        if created_by:
            query = query.filter_by(created_by=created_by)
        
        return query.all()
    
    def generate_sales_report(self, start_date=None, end_date=None, customer_id=None, include_chart=True):
        """Generate a sales report with optional filtering"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        # Query sales invoices
        query = session.query(Invoice).filter_by(type='sale')
        query = query.filter(Invoice.invoice_date >= start_date)
        query = query.filter(Invoice.invoice_date <= end_date)
        
        if customer_id:
            query = query.filter_by(entity_id=customer_id)
        
        invoices = query.order_by(Invoice.invoice_date).all()
        
        # Calculate total sales
        total_sales = sum(invoice.total_amount for invoice in invoices)
        paid_amount = sum(invoice.calculate_paid_amount() for invoice in invoices)
        outstanding_amount = total_sales - paid_amount
        
        # Get customer information if specified
        customer_name = "All Customers"
        if customer_id:
            customer = session.query(SupplierCustomer).filter_by(id=customer_id).first()
            if customer:
                customer_name = customer.name
        
        # Create sales by date data for chart
        date_sales = {}
        for invoice in invoices:
            date_str = invoice.invoice_date.strftime('%Y-%m-%d')
            if date_str not in date_sales:
                date_sales[date_str] = 0
            date_sales[date_str] += invoice.total_amount
        
        # Prepare chart if requested
        chart_base64 = None
        if include_chart and date_sales:
            plt.figure(figsize=(10, 6))
            dates = list(date_sales.keys())
            sales = list(date_sales.values())
            plt.bar(dates, sales)
            plt.xlabel('Date')
            plt.ylabel('Sales Amount')
            plt.title(f'Sales for {customer_name} ({start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")})')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Convert plot to base64 string
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            chart_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            plt.close()
        
        # Prepare data for DataFrame
        data = []
        for invoice in invoices:
            data.append({
                'Invoice Number': invoice.invoice_number,
                'Date': invoice.invoice_date,
                'Customer': invoice.entity.name,
                'Total Amount': invoice.total_amount,
                'Paid Amount': invoice.calculate_paid_amount(),
                'Outstanding': invoice.calculate_remaining_amount(),
                'Status': invoice.status
            })
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Summary statistics
        summary = {
            'Start Date': start_date,
            'End Date': end_date,
            'Customer': customer_name,
            'Total Invoices': len(invoices),
            'Total Sales': total_sales,
            'Paid Amount': paid_amount,
            'Outstanding Amount': outstanding_amount,
            'Chart': chart_base64
        }
        
        return {
            'summary': summary,
            'data': df,
            'raw_invoices': invoices
        }
    
    def generate_inventory_report(self, warehouse_id=None):
        """Generate an inventory report, optionally for a specific warehouse"""
        if warehouse_id:
            # Query for specific warehouse
            stocks = session.query(ItemStock).filter_by(warehouse_id=warehouse_id).all()
            warehouse_name = stocks[0].warehouse.name if stocks else "Unknown Warehouse"
        else:
            # Group by item and sum quantities across all warehouses
            stocks = session.query(
                Item.id,
                Item.name,
                Item.main_unit,
                Item.purchase_price,
                Item.selling_price,
                func.sum(ItemStock.quantity).label('total_quantity')
            ).join(
                ItemStock, Item.id == ItemStock.item_id
            ).group_by(
                Item.id
            ).all()
            warehouse_name = "All Warehouses"
        
        # Calculate inventory value
        total_value = 0
        if warehouse_id:
            for stock in stocks:
                total_value += stock.quantity * stock.item.purchase_price
        else:
            for item_id, name, unit, purchase_price, selling_price, quantity in stocks:
                total_value += quantity * purchase_price
        
        # Prepare data for DataFrame
        data = []
        if warehouse_id:
            for stock in stocks:
                data.append({
                    'Item ID': stock.item.id,
                    'Item Name': stock.item.name,
                    'Unit': stock.item.main_unit,
                    'Quantity': stock.quantity,
                    'Purchase Price': stock.item.purchase_price,
                    'Selling Price': stock.item.selling_price,
                    'Value': stock.quantity * stock.item.purchase_price
                })
        else:
            for item_id, name, unit, purchase_price, selling_price, quantity in stocks:
                data.append({
                    'Item ID': item_id,
                    'Item Name': name,
                    'Unit': unit,
                    'Quantity': quantity,
                    'Purchase Price': purchase_price,
                    'Selling Price': selling_price,
                    'Value': quantity * purchase_price
                })
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Summary statistics
        summary = {
            'Warehouse': warehouse_name,
            'Total Items': len(data),
            'Total Inventory Value': total_value,
            'Report Date': datetime.now()
        }
        
        return {
            'summary': summary,
            'data': df
        }
    
    def generate_financial_report(self, start_date=None, end_date=None, include_chart=True):
        """Generate a financial report for a specific period"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        # Get funds
        funds = session.query(Fund).all()
        
        # Get income (sales invoices)
        sales = session.query(
            func.sum(Invoice.total_amount).label('total_sales')
        ).filter(
            Invoice.type == 'sale',
            Invoice.invoice_date >= start_date,
            Invoice.invoice_date <= end_date
        ).scalar() or 0
        
        # Get expenses
        expenses = session.query(
            func.sum(Expense.amount).label('total_expenses')
        ).filter(
            Expense.expense_date >= start_date,
            Expense.expense_date <= end_date
        ).scalar() or 0
        
        # Get purchases
        purchases = session.query(
            func.sum(Invoice.total_amount).label('total_purchases')
        ).filter(
            Invoice.type == 'purchase',
            Invoice.invoice_date >= start_date,
            Invoice.invoice_date <= end_date
        ).scalar() or 0
        
        # Calculate profit
        profit = sales - expenses - purchases
        
        # Get top expense categories
        top_expenses = session.query(
            ExpenseCategory.name,
            func.sum(Expense.amount).label('total_amount')
        ).join(
            Expense, ExpenseCategory.id == Expense.category_id
        ).filter(
            Expense.expense_date >= start_date,
            Expense.expense_date <= end_date
        ).group_by(
            ExpenseCategory.name
        ).order_by(
            desc('total_amount')
        ).limit(5).all()
        
        # Prepare chart if requested
        chart_base64 = None
        if include_chart:
            plt.figure(figsize=(12, 6))
            
            # Financial Summary Pie Chart
            plt.subplot(1, 2, 1)
            labels = ['Sales', 'Expenses', 'Purchases']
            values = [sales, expenses, purchases]
            colors = ['#4CAF50', '#F44336', '#2196F3']
            plt.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            plt.axis('equal')
            plt.title('Financial Summary')
            
            # Top Expense Categories Bar Chart
            if top_expenses:
                plt.subplot(1, 2, 2)
                category_names = [category for category, _ in top_expenses]
                category_values = [amount for _, amount in top_expenses]
                plt.bar(category_names, category_values)
                plt.xlabel('Category')
                plt.ylabel('Amount')
                plt.title('Top Expense Categories')
                plt.xticks(rotation=45)
            
            plt.tight_layout()
            
            # Convert plot to base64 string
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            chart_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            plt.close()
        
        # Prepare fund data
        fund_data = []
        for fund in funds:
            fund_data.append({
                'Fund Name': fund.name,
                'Currency': fund.currency,
                'Balance': fund.balance,
                'Exchange Rate': fund.exchange_rate,
                'USD Equivalent': fund.balance / fund.exchange_rate if fund.exchange_rate > 0 else 0
            })
        
        # Create DataFrame for funds
        funds_df = pd.DataFrame(fund_data)
        
        # Get expense details
        expense_query = session.query(
            Expense.id,
            Expense.amount,
            Expense.currency,
            Expense.expense_date,
            Expense.description,
            ExpenseCategory.name.label('category_name')
        ).join(
            ExpenseCategory, Expense.category_id == ExpenseCategory.id
        ).filter(
            Expense.expense_date >= start_date,
            Expense.expense_date <= end_date
        ).order_by(
            Expense.expense_date
        )
        
        expense_data = []
        for expense in expense_query:
            expense_data.append({
                'Date': expense.expense_date,
                'Category': expense.category_name,
                'Amount': expense.amount,
                'Currency': expense.currency,
                'Description': expense.description
            })
        
        # Create DataFrame for expenses
        expenses_df = pd.DataFrame(expense_data)
        
        # Summary statistics
        summary = {
            'Start Date': start_date,
            'End Date': end_date,
            'Total Sales': sales,
            'Total Expenses': expenses,
            'Total Purchases': purchases,
            'Profit': profit,
            'Chart': chart_base64
        }
        
        return {
            'summary': summary,
            'funds': funds_df,
            'expenses': expenses_df
        }
    
    def generate_receivables_payables_report(self):
        """Generate a report of receivables (customer debts) and payables (supplier debts)"""
        # Get customers with outstanding balances
        customers = session.query(SupplierCustomer).filter(
            SupplierCustomer.type.in_(['customer', 'both']),
            SupplierCustomer.balance > 0
        ).order_by(
            desc(SupplierCustomer.balance)
        ).all()
        
        # Get suppliers with outstanding balances (we owe them)
        suppliers = session.query(SupplierCustomer).filter(
            SupplierCustomer.type.in_(['supplier', 'both']),
            SupplierCustomer.balance < 0
        ).order_by(
            SupplierCustomer.balance
        ).all()
        
        # Calculate totals
        total_receivables = sum(customer.balance for customer in customers)
        total_payables = sum(abs(supplier.balance) for supplier in suppliers)
        
        # Prepare customer data
        customer_data = []
        for customer in customers:
            customer_data.append({
                'Customer ID': customer.id,
                'Customer Name': customer.name,
                'Balance': customer.balance,
                'Currency': customer.currency,
                'Phone': customer.phone,
                'Email': customer.email
            })
        
        # Prepare supplier data
        supplier_data = []
        for supplier in suppliers:
            supplier_data.append({
                'Supplier ID': supplier.id,
                'Supplier Name': supplier.name,
                'Balance': abs(supplier.balance),  # Convert to positive for display
                'Currency': supplier.currency,
                'Phone': supplier.phone,
                'Email': supplier.email
            })
        
        # Create DataFrames
        customers_df = pd.DataFrame(customer_data)
        suppliers_df = pd.DataFrame(supplier_data)
        
        # Summary statistics
        summary = {
            'Total Receivables': total_receivables,
            'Total Payables': total_payables,
            'Net Position': total_receivables - total_payables,
            'Total Customers with Debt': len(customers),
            'Total Suppliers to Pay': len(suppliers),
            'Report Date': datetime.now()
        }
        
        return {
            'summary': summary,
            'receivables': customers_df,
            'payables': suppliers_df
        }
    
    def export_to_excel(self, report_data, filename=None):
        """Export report data to Excel"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"report_{timestamp}.xlsx"
        
        with pd.ExcelWriter(filename) as writer:
            # Write summary sheet
            if 'summary' in report_data:
                summary_df = pd.DataFrame([report_data['summary']])
                # Remove chart data if present to avoid Excel file corruption
                if 'Chart' in summary_df.columns:
                    summary_df = summary_df.drop(columns=['Chart'])
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Write data sheets
            for key, value in report_data.items():
                if key == 'summary' or not isinstance(value, pd.DataFrame):
                    continue
                value.to_excel(writer, sheet_name=key.capitalize(), index=False)
        
        return filename
