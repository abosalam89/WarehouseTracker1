#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASSI Warehouse Management System - Web Interface
Flask-based web interface for the Warehouse Management System
"""

import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sys

# Setup path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import database session
from database.db_setup import session as db_session
from models.user import User
from models.fund import Fund
from models.item import Item
from models.warehouse import Warehouse
from models.invoice import Invoice 
from models.supplier_customer import SupplierCustomer, Payment

# Import controllers
from controllers.auth import AuthController
from controllers.fund_controller import FundController
from controllers.item_controller import ItemController
from controllers.warehouse_controller import WarehouseController
from controllers.invoice_controller import InvoiceController
from controllers.supplier_customer_controller import SupplierCustomerController
from controllers.expense_controller import ExpenseController
from controllers.report_controller import ReportController

# Initialize Flask application
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'assi_wms_secret_key')

# Initialize controllers
auth_controller = AuthController()
fund_controller = FundController()
item_controller = ItemController()
warehouse_controller = WarehouseController()
invoice_controller = InvoiceController()
supplier_customer_controller = SupplierCustomerController()
expense_controller = ExpenseController()
report_controller = ReportController()

# Login required decorator
def login_required(view):
    def wrapped_view(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return view(*args, **kwargs)
    wrapped_view.__name__ = view.__name__
    return wrapped_view

# Routes
@app.route('/')
def index():
    """Home page route"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login route"""
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = auth_controller.authenticate(username, password)
        
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            flash('Login successful', 'success')
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid username or password'
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    """Logout route"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard route"""
    # Get summary data for dashboard
    total_items = len(item_controller.get_all_items())
    total_warehouses = len(warehouse_controller.get_all_warehouses())
    funds = fund_controller.get_all_funds()
    
    # Calculate total fund balances
    total_usd = sum(fund.balance / fund.exchange_rate for fund in funds if fund.currency != 'USD')
    total_usd += sum(fund.balance for fund in funds if fund.currency == 'USD')
    
    # Get recent transactions
    recent_transactions = []
    for fund in funds:
        transactions = fund_controller.get_fund_transactions(fund.id, limit=5)
        for transaction in transactions:
            recent_transactions.append({
                'fund': fund.name,
                'amount': transaction.amount,
                'currency': fund.currency,
                'type': transaction.transaction_type,
                'date': transaction.created_at,
                'description': transaction.description
            })
    
    # Sort transactions by date
    recent_transactions.sort(key=lambda x: x['date'], reverse=True)
    recent_transactions = recent_transactions[:10]  # Get top 10
    
    return render_template('dashboard.html', 
                          total_items=total_items,
                          total_warehouses=total_warehouses,
                          total_usd=total_usd,
                          funds=funds,
                          recent_transactions=recent_transactions)

# Fund Management Routes
@app.route('/funds')
@login_required
def list_funds():
    """List all funds"""
    funds = fund_controller.get_all_funds(active_only=False)
    return render_template('funds/list.html', funds=funds)

@app.route('/funds/add', methods=['GET', 'POST'])
@login_required
def add_fund():
    """Add a new fund"""
    if request.method == 'POST':
        name = request.form['name']
        currency = request.form['currency']
        exchange_rate = request.form['exchange_rate']
        initial_balance = request.form.get('initial_balance', 0)
        
        success, result = fund_controller.create_fund(
            name=name,
            currency=currency,
            exchange_rate=exchange_rate,
            initial_balance=initial_balance
        )
        
        if success:
            flash('Fund added successfully', 'success')
            return redirect(url_for('list_funds'))
        else:
            flash(f'Error adding fund: {result}', 'danger')
    
    return render_template('funds/add.html')

@app.route('/funds/<int:fund_id>')
@login_required
def view_fund(fund_id):
    """View fund details"""
    fund = fund_controller.get_fund_by_id(fund_id)
    if not fund:
        flash('Fund not found', 'danger')
        return redirect(url_for('list_funds'))
    
    transactions = fund_controller.get_fund_transactions(fund_id)
    return render_template('funds/view.html', fund=fund, transactions=transactions)

# Item Management Routes
@app.route('/items')
@login_required
def list_items():
    """List all items"""
    items = item_controller.get_all_items(active_only=False)
    return render_template('items/list.html', items=items)

@app.route('/items/add', methods=['GET', 'POST'])
@login_required
def add_item():
    """Add a new item"""
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')
        main_unit = request.form['main_unit']
        sub_unit = request.form['sub_unit']
        conversion_rate = request.form['conversion_rate']
        purchase_price = request.form['purchase_price']
        selling_price = request.form['selling_price']
        
        success, result = item_controller.create_item(
            name=name,
            main_unit=main_unit,
            sub_unit=sub_unit,
            conversion_rate=conversion_rate,
            purchase_price=purchase_price,
            selling_price=selling_price,
            description=description
        )
        
        if success:
            flash('Item added successfully', 'success')
            return redirect(url_for('list_items'))
        else:
            flash(f'Error adding item: {result}', 'danger')
    
    return render_template('items/add.html')

# Warehouse Management Routes
@app.route('/warehouses')
@login_required
def list_warehouses():
    """List all warehouses"""
    warehouses = warehouse_controller.get_all_warehouses(active_only=False)
    return render_template('warehouses/list.html', warehouses=warehouses)

@app.route('/warehouses/add', methods=['GET', 'POST'])
@login_required
def add_warehouse():
    """Add a new warehouse"""
    if request.method == 'POST':
        name = request.form['name']
        location = request.form.get('location', '')
        description = request.form.get('description', '')
        
        success, result = warehouse_controller.create_warehouse(
            name=name,
            location=location,
            description=description
        )
        
        if success:
            flash('Warehouse added successfully', 'success')
            return redirect(url_for('list_warehouses'))
        else:
            flash(f'Error adding warehouse: {result}', 'danger')
    
    return render_template('warehouses/add.html')

@app.route('/warehouses/<int:warehouse_id>')
@login_required
def view_warehouse(warehouse_id):
    """View warehouse details"""
    warehouse = warehouse_controller.get_warehouse_by_id(warehouse_id)
    if not warehouse:
        flash('Warehouse not found', 'danger')
        return redirect(url_for('list_warehouses'))
    
    # Get inventory information
    inventory = warehouse_controller.get_warehouse_stock(warehouse_id)
    inventory_count = len(inventory)
    inventory_value = warehouse_controller.get_warehouse_inventory_value(warehouse_id)
    
    # Get low stock items
    low_stock_items = []
    for stock in inventory:
        if stock.quantity < 10:  # Assuming 10 is the threshold for low stock
            item_info = {
                'name': stock.item.name,
                'quantity': stock.quantity,
                'main_unit': stock.item.main_unit
            }
            low_stock_items.append(item_info)
    
    return render_template('warehouses/view.html', 
                           warehouse=warehouse,
                           inventory_count=inventory_count,
                           inventory_value=inventory_value,
                           low_stock_items=low_stock_items)

@app.route('/warehouses/<int:warehouse_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_warehouse(warehouse_id):
    """Edit a warehouse"""
    warehouse = warehouse_controller.get_warehouse_by_id(warehouse_id)
    if not warehouse:
        flash('Warehouse not found', 'danger')
        return redirect(url_for('list_warehouses'))
    
    if request.method == 'POST':
        name = request.form['name']
        location = request.form.get('location', '')
        description = request.form.get('description', '')
        is_active = 'is_active' in request.form
        
        success, result = warehouse_controller.update_warehouse(
            warehouse_id=warehouse_id,
            name=name,
            location=location,
            description=description,
            is_active=is_active
        )
        
        if success:
            flash('Warehouse updated successfully', 'success')
            return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))
        else:
            flash(f'Error updating warehouse: {result}', 'danger')
    
    return render_template('warehouses/edit.html', warehouse=warehouse)

@app.route('/warehouses/<int:warehouse_id>/deactivate', methods=['POST'])
@login_required
def deactivate_warehouse(warehouse_id):
    """Deactivate a warehouse"""
    success, result = warehouse_controller.update_warehouse(
        warehouse_id=warehouse_id,
        is_active=False
    )
    
    if success:
        flash('Warehouse deactivated successfully', 'success')
    else:
        flash(f'Error deactivating warehouse: {result}', 'danger')
    
    return redirect(url_for('list_warehouses'))

@app.route('/warehouses/<int:warehouse_id>/inventory')
@login_required
def warehouse_inventory(warehouse_id):
    """View warehouse inventory"""
    warehouse = warehouse_controller.get_warehouse_by_id(warehouse_id)
    if not warehouse:
        flash('Warehouse not found', 'danger')
        return redirect(url_for('list_warehouses'))
    
    inventory = warehouse_controller.get_warehouse_stock(warehouse_id)
    return render_template('warehouses/inventory.html', 
                          warehouse=warehouse, 
                          inventory=inventory)

# Define more routes for other functionality...

# API endpoints for AJAX operations
@app.route('/api/funds')
def api_funds():
    """API endpoint to get all funds"""
    funds = fund_controller.get_all_funds()
    return jsonify([{
        'id': fund.id,
        'name': fund.name,
        'balance': fund.balance,
        'currency': fund.currency,
        'exchange_rate': fund.exchange_rate
    } for fund in funds])

@app.route('/api/items')
def api_items():
    """API endpoint to get all items"""
    items = item_controller.get_all_items()
    return jsonify([{
        'id': item.id,
        'name': item.name,
        'main_unit': item.main_unit,
        'sub_unit': item.sub_unit,
        'conversion_rate': item.conversion_rate,
        'purchase_price': item.purchase_price,
        'selling_price': item.selling_price,
        'stock': item.get_total_stock()
    } for item in items])

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500

# Language switching route
@app.route('/set_language/<lang_code>', methods=['POST'])
def set_language(lang_code):
    """Set the application language"""
    from utils.language import switch_language
    switch_language(lang_code)
    return jsonify({'success': True})

# Create static folders for uploads and exports
# Create necessary folders
os.makedirs(os.path.join('static', 'exports'), exist_ok=True)
os.makedirs(os.path.join('static', 'uploads'), exist_ok=True)

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)