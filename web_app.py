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

# Invoice Management Routes
@app.route('/invoices')
@login_required
def list_invoices():
    """List all invoices"""
    invoices = invoice_controller.get_all_invoices()
    entities = supplier_customer_controller.get_all_entities()
    funds = fund_controller.get_all_funds()
    return render_template('invoices/list.html', 
                          invoices=invoices,
                          entities=entities,
                          funds=funds)

@app.route('/invoices/new-purchase', methods=['GET', 'POST'])
@login_required
def new_purchase_invoice():
    """Create a new purchase invoice"""
    if request.method == 'POST':
        # Extract data from form
        supplier_id = request.form['supplier_id']
        warehouse_id = request.form['warehouse_id']
        invoice_date = request.form['invoice_date']
        due_date = request.form.get('due_date', None)
        currency = request.form['currency']
        exchange_rate = request.form['exchange_rate']
        additional_costs = request.form.get('additional_costs', 0)
        tax = request.form.get('tax', 0)
        notes = request.form.get('notes', '')
        
        # Get items data from form arrays
        item_ids = request.form.getlist('item_ids[]')
        item_quantities = request.form.getlist('item_quantities[]')
        item_units = request.form.getlist('item_units[]')
        item_prices = request.form.getlist('item_prices[]')
        
        # Prepare items data for controller
        items_data = []
        for i in range(len(item_ids)):
            items_data.append({
                'item_id': item_ids[i],
                'quantity': item_quantities[i],
                'unit': item_units[i],
                'price_per_unit': item_prices[i]
            })
        
        # Create the invoice
        success, result = invoice_controller.create_invoice(
            invoice_type='purchase',
            entity_id=supplier_id,
            items_data=items_data,
            warehouse_id=warehouse_id,
            invoice_date=invoice_date,
            due_date=due_date,
            currency=currency,
            exchange_rate=exchange_rate,
            additional_costs=additional_costs,
            tax=tax,
            notes=notes
        )
        
        if success:
            # Record initial payment if requested
            if 'record_payment' in request.form:
                payment_amount = request.form['payment_amount']
                payment_method = request.form['payment_method']
                fund_id = request.form['fund_id']
                
                invoice_controller.record_payment(
                    invoice_id=result.id,
                    amount=payment_amount,
                    payment_date=invoice_date,
                    payment_method=payment_method,
                    fund_id=fund_id,
                    notes=f"Initial payment for invoice #{result.invoice_number}"
                )
            
            flash('Purchase invoice created successfully', 'success')
            return redirect(url_for('view_invoice', invoice_id=result.id))
        else:
            flash(f'Error creating invoice: {result}', 'danger')
    
    # GET request - display form
    suppliers = supplier_customer_controller.get_suppliers()
    warehouses = warehouse_controller.get_all_warehouses()
    items = item_controller.get_all_items()
    funds = fund_controller.get_all_funds()
    
    return render_template('invoices/new_purchase.html',
                          suppliers=suppliers,
                          warehouses=warehouses,
                          items=items,
                          funds=funds)

@app.route('/invoices/new-sale', methods=['GET', 'POST'])
@login_required
def new_sales_invoice():
    """Create a new sales invoice"""
    if request.method == 'POST':
        # Extract data from form
        customer_id = request.form['customer_id']
        warehouse_id = request.form['warehouse_id']
        invoice_date = request.form['invoice_date']
        due_date = request.form.get('due_date', None)
        currency = request.form['currency']
        exchange_rate = request.form['exchange_rate']
        additional_costs = request.form.get('additional_costs', 0)
        tax = request.form.get('tax', 0)
        notes = request.form.get('notes', '')
        
        # Get items data from form arrays
        item_ids = request.form.getlist('item_ids[]')
        item_quantities = request.form.getlist('item_quantities[]')
        item_units = request.form.getlist('item_units[]')
        item_prices = request.form.getlist('item_prices[]')
        
        # Prepare items data for controller
        items_data = []
        for i in range(len(item_ids)):
            items_data.append({
                'item_id': item_ids[i],
                'quantity': item_quantities[i],
                'unit': item_units[i],
                'price_per_unit': item_prices[i]
            })
        
        # Create the invoice
        success, result = invoice_controller.create_invoice(
            invoice_type='sale',
            entity_id=customer_id,
            items_data=items_data,
            warehouse_id=warehouse_id,
            invoice_date=invoice_date,
            due_date=due_date,
            currency=currency,
            exchange_rate=exchange_rate,
            additional_costs=additional_costs,
            tax=tax,
            notes=notes
        )
        
        if success:
            # Record initial payment if requested
            if 'record_payment' in request.form:
                payment_amount = request.form['payment_amount']
                payment_method = request.form['payment_method']
                fund_id = request.form['fund_id']
                
                invoice_controller.record_payment(
                    invoice_id=result.id,
                    amount=payment_amount,
                    payment_date=invoice_date,
                    payment_method=payment_method,
                    fund_id=fund_id,
                    notes=f"Initial payment for invoice #{result.invoice_number}"
                )
            
            flash('Sales invoice created successfully', 'success')
            return redirect(url_for('view_invoice', invoice_id=result.id))
        else:
            flash(f'Error creating invoice: {result}', 'danger')
    
    # GET request - display form
    customers = supplier_customer_controller.get_customers()
    warehouses = warehouse_controller.get_all_warehouses()
    items = item_controller.get_all_items()
    funds = fund_controller.get_all_funds()
    
    return render_template('invoices/new_sale.html',
                          customers=customers,
                          warehouses=warehouses,
                          items=items,
                          funds=funds)

@app.route('/invoices/<int:invoice_id>')
@login_required
def view_invoice(invoice_id):
    """View invoice details"""
    invoice = invoice_controller.get_invoice_by_id(invoice_id)
    if not invoice:
        flash('Invoice not found', 'danger')
        return redirect(url_for('list_invoices'))
    
    funds = fund_controller.get_all_funds()
    return render_template('invoices/view.html', invoice=invoice, funds=funds)

@app.route('/invoices/<int:invoice_id>/payment', methods=['POST'])
@login_required
def record_payment(invoice_id):
    """Record a payment for an invoice"""
    amount = request.form['amount']
    payment_date = request.form['payment_date']
    payment_method = request.form['payment_method']
    fund_id = request.form['fund_id']
    notes = request.form.get('notes', '')
    
    success, result = invoice_controller.record_payment(
        invoice_id=invoice_id,
        amount=amount,
        payment_date=payment_date,
        payment_method=payment_method,
        fund_id=fund_id,
        notes=notes
    )
    
    if success:
        flash('Payment recorded successfully', 'success')
    else:
        flash(f'Error recording payment: {result}', 'danger')
    
    return redirect(url_for('view_invoice', invoice_id=invoice_id))

@app.route('/invoices/<int:invoice_id>/cancel', methods=['POST'])
@login_required
def cancel_invoice(invoice_id):
    """Cancel an invoice"""
    success, result = invoice_controller.cancel_invoice(invoice_id)
    
    if success:
        flash('Invoice cancelled successfully', 'success')
    else:
        flash(f'Error cancelling invoice: {result}', 'danger')
    
    return redirect(url_for('view_invoice', invoice_id=invoice_id))

# API endpoint for stock data
@app.route('/api/stock')
@login_required
def api_stock():
    """API endpoint to get stock data for a warehouse"""
    warehouse_id = request.args.get('warehouse_id')
    if not warehouse_id:
        return jsonify({'error': 'Warehouse ID is required'}), 400
    
    stock_data = {}
    stock_items = warehouse_controller.get_warehouse_stock(warehouse_id)
    
    for stock in stock_items:
        stock_data[stock.item_id] = {
            'quantity': stock.quantity,
            'item_name': stock.item.name,
            'main_unit': stock.item.main_unit
        }
    
    return jsonify(stock_data)

# API endpoint for stock adjustment
@app.route('/api/stock/adjust', methods=['POST'])
@login_required
def api_adjust_stock():
    """API endpoint to adjust stock"""
    item_id = request.form['item_id']
    warehouse_id = request.form['warehouse_id']
    quantity = float(request.form['quantity'])
    adjustment_type = request.form['adjustment_type']
    
    try:
        if adjustment_type == 'absolute':
            success, result = item_controller.update_stock(
                item_id=item_id,
                warehouse_id=warehouse_id,
                quantity_change=quantity,
                is_absolute=True
            )
        elif adjustment_type == 'increase':
            success, result = item_controller.update_stock(
                item_id=item_id,
                warehouse_id=warehouse_id,
                quantity_change=quantity
            )
        elif adjustment_type == 'decrease':
            success, result = item_controller.update_stock(
                item_id=item_id,
                warehouse_id=warehouse_id,
                quantity_change=-quantity
            )
        else:
            return jsonify({'success': False, 'message': 'Invalid adjustment type'})
        
        return jsonify({'success': success, 'message': str(result) if not success else 'Stock updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# Reports Routes
@app.route('/reports')
@login_required
def reports_dashboard():
    """Reports dashboard"""
    # Get metrics for dashboard
    now = datetime.now()
    thirty_days_ago = now - timedelta(days=30)
    
    # Sales and purchases data for the chart
    chart_data = report_controller.generate_sales_purchases_chart(start_date=thirty_days_ago, end_date=now)
    
    # Top selling items
    top_items = report_controller.get_top_selling_items(start_date=thirty_days_ago, end_date=now, limit=5)
    
    # Get financial summary
    financial = report_controller.get_financial_summary(start_date=thirty_days_ago, end_date=now)
    
    # Get inventory status
    inventory = report_controller.get_inventory_status()
    
    # Get receivables and payables
    receivables_payables = report_controller.get_receivables_payables_summary()
    
    # Main metrics
    metrics = {
        'total_sales': financial['total_revenue'],
        'total_purchases': financial['cost_of_goods'],
        'inventory_value': inventory['total_value'],
        'net_profit': financial['net_profit']
    }
    
    return render_template('reports/dashboard.html',
                          metrics=metrics,
                          chart_data=chart_data,
                          top_items=top_items,
                          financial=financial,
                          inventory=inventory,
                          receivables_payables=receivables_payables)

@app.route('/reports/sales')
@login_required
def sales_report():
    """Sales report"""
    # Get filter parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    customer_id = request.args.get('customer_id')
    status = request.args.get('status')
    
    # Generate report data
    report_data = report_controller.generate_sales_report(
        start_date=start_date,
        end_date=end_date,
        customer_id=customer_id,
        status=status
    )
    
    # Get customers for filters
    customers = supplier_customer_controller.get_customers()
    
    # Build filters object for template
    filters = {
        'start_date': start_date,
        'end_date': end_date,
        'customer_id': customer_id,
        'status': status
    }
    
    return render_template('reports/sales.html',
                          summary=report_data['summary'],
                          invoices=report_data['invoices'],
                          top_customers=report_data['top_customers'],
                          top_products=report_data['top_products'],
                          sales_by_month=report_data['sales_by_month'],
                          chart_data=report_data['chart_data'],
                          customers=customers,
                          filters=filters)

@app.route('/reports/inventory')
@login_required
def inventory_report():
    """Inventory report"""
    # Get filter parameters
    warehouse_id = request.args.get('warehouse_id')
    stock_status = request.args.get('stock_status')
    sort_by = request.args.get('sort_by', 'name')
    
    # Generate report data
    report_data = report_controller.generate_inventory_report(
        warehouse_id=warehouse_id,
        stock_status=stock_status,
        sort_by=sort_by
    )
    
    # Get warehouses for filters
    warehouses = warehouse_controller.get_all_warehouses()
    
    # Build filters object for template
    filters = {
        'warehouse_id': warehouse_id,
        'stock_status': stock_status,
        'sort_by': sort_by
    }
    
    return render_template('reports/inventory.html',
                          summary=report_data['summary'],
                          inventory_items=report_data['items'],
                          value_distribution=report_data['value_distribution'],
                          warehouse_summary=report_data['warehouse_summary'],
                          charts=report_data['charts'],
                          warehouses=warehouses,
                          filters=filters)

@app.route('/reports/financial')
@login_required
def financial_report():
    """Financial report"""
    # Get filter parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    currency = request.args.get('currency', 'USD')
    fund_id = request.args.get('fund_id')
    
    # Generate report data
    report_data = report_controller.generate_financial_report(
        start_date=start_date,
        end_date=end_date,
        currency=currency,
        fund_id=fund_id
    )
    
    # Get funds for filters
    funds = fund_controller.get_all_funds()
    
    # Build filters object for template
    filters = {
        'start_date': start_date,
        'end_date': end_date,
        'currency': currency,
        'fund_id': fund_id
    }
    
    return render_template('reports/financial.html',
                          summary=report_data['summary'],
                          income_statement=report_data['income_statement'],
                          fund_balances=report_data['fund_balances'],
                          total_fund_balance=report_data['total_fund_balance'],
                          expense_categories=report_data['expense_categories'],
                          monthly_trend=report_data['monthly_trend'],
                          funds=funds,
                          filters=filters)

@app.route('/reports/receivables-payables')
@login_required
def receivables_payables_report():
    """Receivables and payables report"""
    # Generate report data
    report_data = report_controller.generate_receivables_payables_report()
    
    return render_template('reports/receivables_payables.html',
                          report_data=report_data)

# Export routes
@app.route('/reports/sales/export')
@login_required
def export_sales_report():
    """Export sales report to Excel"""
    # Get filter parameters from request
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    customer_id = request.args.get('customer_id')
    status = request.args.get('status')
    
    # Generate report data
    report_data = report_controller.generate_sales_report(
        start_date=start_date,
        end_date=end_date,
        customer_id=customer_id,
        status=status
    )
    
    # Export to Excel
    file_path = report_controller.export_to_excel(report_data, 'sales_report')
    
    # Return file for download
    return send_file(file_path, as_attachment=True)

@app.route('/reports/inventory/export')
@login_required
def export_inventory_report():
    """Export inventory report to Excel"""
    # Get filter parameters
    warehouse_id = request.args.get('warehouse_id')
    stock_status = request.args.get('stock_status')
    sort_by = request.args.get('sort_by', 'name')
    
    # Generate report data
    report_data = report_controller.generate_inventory_report(
        warehouse_id=warehouse_id,
        stock_status=stock_status,
        sort_by=sort_by
    )
    
    # Export to Excel
    file_path = report_controller.export_to_excel(report_data, 'inventory_report')
    
    # Return file for download
    return send_file(file_path, as_attachment=True)

@app.route('/reports/financial/export')
@login_required
def export_financial_report():
    """Export financial report to Excel"""
    # Get filter parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    currency = request.args.get('currency', 'USD')
    fund_id = request.args.get('fund_id')
    
    # Generate report data
    report_data = report_controller.generate_financial_report(
        start_date=start_date,
        end_date=end_date,
        currency=currency,
        fund_id=fund_id
    )
    
    # Export to Excel
    file_path = report_controller.export_to_excel(report_data, 'financial_report')
    
    # Return file for download
    return send_file(file_path, as_attachment=True)

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