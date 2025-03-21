#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Reports view for ASSI Warehouse Management System
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import gettext
from datetime import datetime, timedelta
import os
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import io
import base64
from PIL import Image, ImageTk

from controllers.report_controller import ReportController
from controllers.supplier_customer_controller import SupplierCustomerController
from controllers.warehouse_controller import WarehouseController
from controllers.fund_controller import FundController
from utils.notifications import show_notification
from utils.export import export_to_excel

# Configure matplotlib to use a non-GUI backend for report generation
matplotlib.use('Agg')

class ReportsView:
    """Reports view class"""
    
    def __init__(self, root, back_to_main_menu):
        """Initialize the reports view
        
        Args:
            root: The root window
            back_to_main_menu: Callback function to return to main menu
        """
        self.root = root
        self.back_to_main_menu = back_to_main_menu
        self.report_controller = ReportController()
        self.sc_controller = SupplierCustomerController()
        self.warehouse_controller = WarehouseController()
        self.fund_controller = FundController()
        
        # Setup translation
        self._ = gettext.gettext
        
        # Set window title
        self.root.title(self._("ASSI WMS - Reports"))
        
        # Create main frame
        self.frame = ttk.Frame(self.root)
        self.frame.pack(expand=True, fill="both")
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_sales_report_tab()
        self.create_inventory_report_tab()
        self.create_financial_report_tab()
        self.create_receivables_payables_tab()
        
        # Add back button
        back_button = ttk.Button(
            self.frame,
            text=self._("Back to Main Menu"),
            command=self.back_to_main_menu,
            bootstyle=SECONDARY,
            width=20
        )
        back_button.pack(pady=10)
    
    def create_dashboard_tab(self):
        """Create the dashboard overview tab"""
        tab = ttk.Frame(self.notebook, padding=10)
        
        # Create a welcome header
        header_frame = ttk.Frame(tab)
        header_frame.pack(fill="x", pady=(0, 20))
        
        welcome_label = ttk.Label(
            header_frame,
            text=self._("Reports Dashboard"),
            font=("TkDefaultFont", 18, "bold")
        )
        welcome_label.pack(anchor="w")
        
        date_label = ttk.Label(
            header_frame,
            text=datetime.now().strftime("%Y-%m-%d"),
            font=("TkDefaultFont", 12)
        )
        date_label.pack(anchor="w", pady=5)
        
        # Create a two-column layout
        columns_frame = ttk.Frame(tab)
        columns_frame.pack(fill="both", expand=True)
        
        # Left column for key metrics
        left_frame = ttk.Frame(columns_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Create key metrics frame
        metrics_frame = ttk.LabelFrame(left_frame, text=self._("Key Metrics"), padding=10)
        metrics_frame.pack(fill="both", expand=True)
        
        # Fetch key metrics (in a background thread in a real app)
        try:
            # Get receivables/payables summary
            rp_report = self.report_controller.generate_receivables_payables_report()
            total_receivables = rp_report['summary']['Total Receivables']
            total_payables = rp_report['summary']['Total Payables']
            net_position = rp_report['summary']['Net Position']
            
            # Get inventory value
            inventory_report = self.report_controller.generate_inventory_report()
            inventory_value = inventory_report['summary']['Total Inventory Value']
            
            # Get financial data for last 30 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            financial_report = self.report_controller.generate_financial_report(
                start_date=start_date,
                end_date=end_date,
                include_chart=False
            )
            monthly_sales = financial_report['summary']['Total Sales']
            monthly_expenses = financial_report['summary']['Total Expenses']
            monthly_profit = financial_report['summary']['Profit']
            
            # Create metrics layout - 2x3 grid
            metrics_frame.columnconfigure(0, weight=1)
            metrics_frame.columnconfigure(1, weight=1)
            
            # Row 1: Sales & Receivables
            self.create_metric_widget(
                metrics_frame, 0, 0,
                self._("Monthly Sales"),
                f"{monthly_sales:.2f}",
                "USD",
                "💰"
            )
            
            self.create_metric_widget(
                metrics_frame, 0, 1,
                self._("Receivables"),
                f"{total_receivables:.2f}",
                "USD",
                "📈"
            )
            
            # Row 2: Expenses & Payables
            self.create_metric_widget(
                metrics_frame, 1, 0,
                self._("Monthly Expenses"),
                f"{monthly_expenses:.2f}",
                "USD",
                "💸"
            )
            
            self.create_metric_widget(
                metrics_frame, 1, 1,
                self._("Payables"),
                f"{total_payables:.2f}",
                "USD",
                "📉"
            )
            
            # Row 3: Profit & Inventory
            self.create_metric_widget(
                metrics_frame, 2, 0,
                self._("Monthly Profit"),
                f"{monthly_profit:.2f}",
                "USD",
                "✅" if monthly_profit >= 0 else "❌",
                SUCCESS if monthly_profit >= 0 else DANGER
            )
            
            self.create_metric_widget(
                metrics_frame, 2, 1,
                self._("Inventory Value"),
                f"{inventory_value:.2f}",
                "USD",
                "📦"
            )
            
        except Exception as e:
            # Show error if metrics can't be loaded
            error_label = ttk.Label(
                metrics_frame,
                text=self._("Error loading metrics: {0}").format(str(e)),
                bootstyle=DANGER
            )
            error_label.pack(pady=20)
        
        # Right column for quick access and charts
        right_frame = ttk.Frame(columns_frame)
        right_frame.pack(side="right", fill="both", expand=True)
        
        # Quick access to reports
        quick_access_frame = ttk.LabelFrame(right_frame, text=self._("Quick Access"), padding=10)
        quick_access_frame.pack(fill="x", pady=(0, 10))
        
        reports = [
            {"name": self._("Sales Report"), "tab_index": 1, "icon": "💰"},
            {"name": self._("Inventory Report"), "tab_index": 2, "icon": "📦"},
            {"name": self._("Financial Report"), "tab_index": 3, "icon": "💹"},
            {"name": self._("Receivables & Payables"), "tab_index": 4, "icon": "💳"}
        ]
        
        # Create a button for each report
        for i, report in enumerate(reports):
            button = ttk.Button(
                quick_access_frame,
                text=f"{report['icon']} {report['name']}",
                command=lambda idx=report['tab_index']: self.notebook.select(idx),
                bootstyle=INFO
            )
            button.pack(fill="x", pady=5)
        
        # Mini chart showing sales trend
        chart_frame = ttk.LabelFrame(right_frame, text=self._("Sales Trend (Last 30 Days)"), padding=10)
        chart_frame.pack(fill="both", expand=True)
        
        try:
            # Get sales data
            sales_report = self.report_controller.generate_sales_report(
                start_date=start_date,
                end_date=end_date,
                include_chart=True
            )
            
            if sales_report['summary']['Chart']:
                # Decode the base64 chart image
                chart_data = base64.b64decode(sales_report['summary']['Chart'])
                chart_image = Image.open(io.BytesIO(chart_data))
                
                # Create PhotoImage and label
                photo = ImageTk.PhotoImage(chart_image)
                chart_label = ttk.Label(chart_frame, image=photo)
                chart_label.image = photo  # Keep a reference to prevent garbage collection
                chart_label.pack(fill="both", expand=True)
            else:
                # Create a simple matplotlib figure if no chart exists
                figure = plt.Figure(figsize=(5, 4), dpi=100)
                ax = figure.add_subplot(111)
                
                # Create a dummy plot if no data is available
                ax.plot([1, 2, 3, 4, 5], [0, 0, 0, 0, 0], marker='o')
                ax.set_title(self._("No Sales Data Available"))
                ax.set_xlabel(self._("Date"))
                ax.set_ylabel(self._("Sales"))
                
                # Embed the figure in the tkinter window
                canvas = FigureCanvasTkAgg(figure, chart_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="both", expand=True)
        except Exception as e:
            error_label = ttk.Label(
                chart_frame,
                text=self._("Error loading chart: {0}").format(str(e)),
                bootstyle=DANGER
            )
            error_label.pack(pady=20)
        
        # Add tab to notebook
        self.notebook.add(tab, text=self._("Dashboard"))
    
    def create_metric_widget(self, parent, row, col, title, value, unit, icon, bootstyle=None):
        """Create a metric display widget
        
        Args:
            parent: Parent widget
            row: Grid row
            col: Grid column
            title: Metric title
            value: Metric value
            unit: Unit of measurement
            icon: Icon to display
            bootstyle: Optional bootstyle for value
        """
        frame = ttk.Frame(parent, padding=10)
        frame.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
        
        # Add a border
        border_frame = ttk.Frame(frame, bootstyle=SECONDARY)
        border_frame.pack(fill="both", expand=True, padx=1, pady=1)
        
        inner_frame = ttk.Frame(border_frame, padding=10)
        inner_frame.pack(fill="both", expand=True)
        
        # Icon and title in one row
        header_frame = ttk.Frame(inner_frame)
        header_frame.pack(fill="x")
        
        icon_label = ttk.Label(
            header_frame,
            text=icon,
            font=("TkDefaultFont", 16)
        )
        icon_label.pack(side="left")
        
        title_label = ttk.Label(
            header_frame,
            text=title,
            font=("TkDefaultFont", 10)
        )
        title_label.pack(side="left", padx=5)
        
        # Value with optional bootstyle
        value_label = ttk.Label(
            inner_frame,
            text=value,
            font=("TkDefaultFont", 14, "bold"),
            bootstyle=bootstyle
        )
        value_label.pack(pady=5)
        
        # Unit
        unit_label = ttk.Label(
            inner_frame,
            text=unit,
            font=("TkDefaultFont", 9)
        )
        unit_label.pack()
    
    def create_sales_report_tab(self):
        """Create the sales report tab"""
        tab = ttk.Frame(self.notebook, padding=10)
        
        # Create filters section
        filters_frame = ttk.LabelFrame(tab, text=self._("Report Filters"), padding=10)
        filters_frame.pack(fill="x", pady=(0, 10))
        
        # Date filters
        date_frame = ttk.Frame(filters_frame)
        date_frame.pack(fill="x", pady=5)
        
        ttk.Label(date_frame, text=self._("Date Range:")).pack(side="left", padx=(0, 5))
        
        # Predefined date ranges
        self.sales_date_range_var = ttk.StringVar(value="last30days")
        ttk.Radiobutton(
            date_frame,
            text=self._("Last 30 Days"),
            variable=self.sales_date_range_var,
            value="last30days"
        ).pack(side="left", padx=5)
        
        ttk.Radiobutton(
            date_frame,
            text=self._("This Month"),
            variable=self.sales_date_range_var,
            value="thismonth"
        ).pack(side="left", padx=5)
        
        ttk.Radiobutton(
            date_frame,
            text=self._("Last Month"),
            variable=self.sales_date_range_var,
            value="lastmonth"
        ).pack(side="left", padx=5)
        
        ttk.Radiobutton(
            date_frame,
            text=self._("Custom"),
            variable=self.sales_date_range_var,
            value="custom"
        ).pack(side="left", padx=5)
        
        # Custom date range
        custom_date_frame = ttk.Frame(filters_frame)
        custom_date_frame.pack(fill="x", pady=5)
        
        ttk.Label(custom_date_frame, text=self._("From:")).pack(side="left", padx=(0, 5))
        self.sales_date_from_var = ttk.StringVar()
        date_from = ttk.DateEntry(
            custom_date_frame,
            dateformat="%Y-%m-%d",
            firstweekday=0,
            width=12,
            textvariable=self.sales_date_from_var
        )
        date_from.pack(side="left", padx=5)
        
        ttk.Label(custom_date_frame, text=self._("To:")).pack(side="left", padx=(10, 5))
        self.sales_date_to_var = ttk.StringVar()
        date_to = ttk.DateEntry(
            custom_date_frame,
            dateformat="%Y-%m-%d",
            firstweekday=0,
            width=12,
            textvariable=self.sales_date_to_var
        )
        date_to.pack(side="left", padx=5)
        
        # Customer filter
        customer_frame = ttk.Frame(filters_frame)
        customer_frame.pack(fill="x", pady=5)
        
        ttk.Label(customer_frame, text=self._("Customer:")).pack(side="left", padx=(0, 5))
        
        # Get customers for combobox
        customers = self.sc_controller.get_customers()
        customer_choices = [("all", self._("All Customers"))]
        customer_choices.extend([(str(c.id), c.name) for c in customers])
        
        self.sales_customer_var = ttk.StringVar(value="all")
        customer_combo = ttk.Combobox(
            customer_frame,
            textvariable=self.sales_customer_var,
            values=[c[1] for c in customer_choices],
            width=30
        )
        customer_combo.pack(side="left", padx=5)
        customer_combo.current(0)
        
        # Generate and Export buttons
        button_frame = ttk.Frame(filters_frame)
        button_frame.pack(fill="x", pady=5)
        
        ttk.Button(
            button_frame,
            text=self._("Generate Report"),
            command=self.generate_sales_report,
            bootstyle=SUCCESS,
            width=15
        ).pack(side="left", padx=5)
        
        self.sales_export_button = ttk.Button(
            button_frame,
            text=self._("Export to Excel"),
            command=lambda: self.export_report("sales"),
            bootstyle=INFO,
            width=15
        )
        self.sales_export_button.pack(side="left", padx=5)
        self.sales_export_button.config(state="disabled")  # Disabled until report is generated
        
        # Create summary section
        self.sales_summary_frame = ttk.LabelFrame(tab, text=self._("Summary"), padding=10)
        self.sales_summary_frame.pack(fill="x", pady=10)
        
        # Will be populated when report is generated
        
        # Create a frame for the chart
        self.sales_chart_frame = ttk.LabelFrame(tab, text=self._("Sales Chart"), padding=10)
        self.sales_chart_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Will be populated when report is generated
        
        # Create a frame for the details table
        self.sales_details_frame = ttk.LabelFrame(tab, text=self._("Details"), padding=10)
        self.sales_details_frame.pack(fill="both", expand=True)
        
        # Will be populated when report is generated
        
        # Initialize report data variable
        self.sales_report_data = None
        
        # Set default dates
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        self.sales_date_from_var.set(start_date.strftime("%Y-%m-%d"))
        self.sales_date_to_var.set(end_date.strftime("%Y-%m-%d"))
        
        # Add tab to notebook
        self.notebook.add(tab, text=self._("Sales Report"))
    
    def generate_sales_report(self):
        """Generate the sales report based on filters"""
        try:
            # Get date range based on selection
            date_range = self.sales_date_range_var.get()
            end_date = datetime.now()
            
            if date_range == "last30days":
                start_date = end_date - timedelta(days=30)
            elif date_range == "thismonth":
                start_date = datetime(end_date.year, end_date.month, 1)
            elif date_range == "lastmonth":
                if end_date.month == 1:
                    start_date = datetime(end_date.year - 1, 12, 1)
                    end_date = datetime(end_date.year, 1, 1) - timedelta(days=1)
                else:
                    start_date = datetime(end_date.year, end_date.month - 1, 1)
                    end_date = datetime(end_date.year, end_date.month, 1) - timedelta(days=1)
            else:  # custom
                try:
                    start_date = datetime.strptime(self.sales_date_from_var.get(), "%Y-%m-%d")
                    end_date = datetime.strptime(self.sales_date_to_var.get(), "%Y-%m-%d")
                    # Set time to end of day for end_date
                    end_date = end_date.replace(hour=23, minute=59, second=59)
                except ValueError:
                    show_notification(
                        self._("Error"), 
                        self._("Please enter valid dates")
                    )
                    return
            
            # Get customer ID if not "all"
            customer_id = None
            if self.sales_customer_var.get() != "all":
                customers = self.sc_controller.get_customers()
                customer_name = self.sales_customer_var.get()
                for customer in customers:
                    if customer.name == customer_name:
                        customer_id = customer.id
                        break
            
            # Generate report
            self.sales_report_data = self.report_controller.generate_sales_report(
                start_date=start_date,
                end_date=end_date,
                customer_id=customer_id,
                include_chart=True
            )
            
            # Clear existing widgets
            for widget in self.sales_summary_frame.winfo_children():
                widget.destroy()
                
            for widget in self.sales_chart_frame.winfo_children():
                widget.destroy()
                
            for widget in self.sales_details_frame.winfo_children():
                widget.destroy()
            
            # Populate summary section
            summary = self.sales_report_data['summary']
            
            # Create a grid layout for summary
            summary_grid = ttk.Frame(self.sales_summary_frame)
            summary_grid.pack(fill="x")
            
            summary_grid.columnconfigure(0, weight=1)
            summary_grid.columnconfigure(1, weight=1)
            summary_grid.columnconfigure(2, weight=1)
            summary_grid.columnconfigure(3, weight=1)
            
            # Row 1
            ttk.Label(summary_grid, text=self._("Date Range:")).grid(row=0, column=0, sticky="w", pady=2)
            ttk.Label(
                summary_grid, 
                text=f"{summary['Start Date'].strftime('%Y-%m-%d')} - {summary['End Date'].strftime('%Y-%m-%d')}"
            ).grid(row=0, column=1, sticky="w", pady=2)
            
            ttk.Label(summary_grid, text=self._("Customer:")).grid(row=0, column=2, sticky="w", pady=2)
            ttk.Label(summary_grid, text=summary['Customer']).grid(row=0, column=3, sticky="w", pady=2)
            
            # Row 2
            ttk.Label(summary_grid, text=self._("Total Invoices:")).grid(row=1, column=0, sticky="w", pady=2)
            ttk.Label(summary_grid, text=str(summary['Total Invoices'])).grid(row=1, column=1, sticky="w", pady=2)
            
            ttk.Label(summary_grid, text=self._("Total Sales:"), font=("TkDefaultFont", 10, "bold")).grid(row=1, column=2, sticky="w", pady=2)
            ttk.Label(
                summary_grid, 
                text=f"{summary['Total Sales']:.2f} USD",
                font=("TkDefaultFont", 10, "bold")
            ).grid(row=1, column=3, sticky="w", pady=2)
            
            # Row 3
            ttk.Label(summary_grid, text=self._("Paid Amount:")).grid(row=2, column=0, sticky="w", pady=2)
            ttk.Label(
                summary_grid, 
                text=f"{summary['Paid Amount']:.2f} USD"
            ).grid(row=2, column=1, sticky="w", pady=2)
            
            ttk.Label(summary_grid, text=self._("Outstanding Amount:")).grid(row=2, column=2, sticky="w", pady=2)
            ttk.Label(
                summary_grid, 
                text=f"{summary['Outstanding Amount']:.2f} USD"
            ).grid(row=2, column=3, sticky="w", pady=2)
            
            # Display chart if available
            if summary['Chart']:
                try:
                    chart_data = base64.b64decode(summary['Chart'])
                    chart_image = Image.open(io.BytesIO(chart_data))
                    
                    photo = ImageTk.PhotoImage(chart_image)
                    chart_label = ttk.Label(self.sales_chart_frame, image=photo)
                    chart_label.image = photo  # Keep a reference
                    chart_label.pack(fill="both", expand=True)
                except Exception as e:
                    ttk.Label(
                        self.sales_chart_frame,
                        text=self._("Error displaying chart: {0}").format(str(e)),
                        bootstyle=DANGER
                    ).pack(pady=10)
            else:
                ttk.Label(
                    self.sales_chart_frame,
                    text=self._("No chart data available")
                ).pack(pady=10)
            
            # Create treeview for details
            columns = (
                "invoice_number", "date", "customer", "total", "paid", "outstanding", "status"
            )
            
            details_tree = ttk.Treeview(
                self.sales_details_frame,
                columns=columns,
                show="headings",
                bootstyle=INFO
            )
            
            # Define column headings
            details_tree.heading("invoice_number", text=self._("Invoice Number"))
            details_tree.heading("date", text=self._("Date"))
            details_tree.heading("customer", text=self._("Customer"))
            details_tree.heading("total", text=self._("Total Amount"))
            details_tree.heading("paid", text=self._("Paid Amount"))
            details_tree.heading("outstanding", text=self._("Outstanding"))
            details_tree.heading("status", text=self._("Status"))
            
            # Define column widths
            details_tree.column("invoice_number", width=120)
            details_tree.column("date", width=100, stretch=False)
            details_tree.column("customer", width=150)
            details_tree.column("total", width=100, stretch=False)
            details_tree.column("paid", width=100, stretch=False)
            details_tree.column("outstanding", width=100, stretch=False)
            details_tree.column("status", width=100, stretch=False)
            
            # Add scrollbar
            scrollbar = ttk.Scrollbar(self.sales_details_frame, orient="vertical", command=details_tree.yview)
            details_tree.configure(yscrollcommand=scrollbar.set)
            
            # Pack treeview and scrollbar
            details_tree.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Add data to treeview
            if 'data' in self.sales_report_data and not self.sales_report_data['data'].empty:
                for _, row in self.sales_report_data['data'].iterrows():
                    details_tree.insert(
                        "",
                        "end",
                        values=(
                            row['Invoice Number'],
                            row['Date'].strftime('%Y-%m-%d'),
                            row['Customer'],
                            f"{row['Total Amount']:.2f}",
                            f"{row['Paid Amount']:.2f}",
                            f"{row['Outstanding']:.2f}",
                            row['Status']
                        )
                    )
            
            # Enable export button
            self.sales_export_button.config(state="normal")
            
            # Show success notification
            show_notification(
                self._("Report Generated"),
                self._("Sales report generated successfully")
            )
        except Exception as e:
            show_notification(
                self._("Error"),
                self._("Error generating report: {0}").format(str(e))
            )
    
    def create_inventory_report_tab(self):
        """Create the inventory report tab"""
        tab = ttk.Frame(self.notebook, padding=10)
        
        # Create filters section
        filters_frame = ttk.LabelFrame(tab, text=self._("Report Filters"), padding=10)
        filters_frame.pack(fill="x", pady=(0, 10))
        
        # Warehouse filter
        warehouse_frame = ttk.Frame(filters_frame)
        warehouse_frame.pack(fill="x", pady=5)
        
        ttk.Label(warehouse_frame, text=self._("Warehouse:")).pack(side="left", padx=(0, 5))
        
        # Get warehouses for combobox
        warehouses = self.warehouse_controller.get_all_warehouses()
        warehouse_choices = [("all", self._("All Warehouses"))]
        warehouse_choices.extend([(str(w.id), w.name) for w in warehouses])
        
        self.inventory_warehouse_var = ttk.StringVar(value="all")
        warehouse_combo = ttk.Combobox(
            warehouse_frame,
            textvariable=self.inventory_warehouse_var,
            values=[w[1] for w in warehouse_choices],
            width=30
        )
        warehouse_combo.pack(side="left", padx=5)
        warehouse_combo.current(0)
        
        # Generate and Export buttons
        button_frame = ttk.Frame(filters_frame)
        button_frame.pack(fill="x", pady=5)
        
        ttk.Button(
            button_frame,
            text=self._("Generate Report"),
            command=self.generate_inventory_report,
            bootstyle=SUCCESS,
            width=15
        ).pack(side="left", padx=5)
        
        self.inventory_export_button = ttk.Button(
            button_frame,
            text=self._("Export to Excel"),
            command=lambda: self.export_report("inventory"),
            bootstyle=INFO,
            width=15
        )
        self.inventory_export_button.pack(side="left", padx=5)
        self.inventory_export_button.config(state="disabled")  # Disabled until report is generated
        
        # Create summary section
        self.inventory_summary_frame = ttk.LabelFrame(tab, text=self._("Summary"), padding=10)
        self.inventory_summary_frame.pack(fill="x", pady=10)
        
        # Will be populated when report is generated
        
        # Create a frame for the details table
        self.inventory_details_frame = ttk.LabelFrame(tab, text=self._("Inventory Details"), padding=10)
        self.inventory_details_frame.pack(fill="both", expand=True)
        
        # Will be populated when report is generated
        
        # Initialize report data variable
        self.inventory_report_data = None
        
        # Add tab to notebook
        self.notebook.add(tab, text=self._("Inventory Report"))
    
    def generate_inventory_report(self):
        """Generate the inventory report based on filters"""
        try:
            # Get warehouse ID if not "all"
            warehouse_id = None
            if self.inventory_warehouse_var.get() != "all":
                warehouses = self.warehouse_controller.get_all_warehouses()
                warehouse_name = self.inventory_warehouse_var.get()
                for warehouse in warehouses:
                    if warehouse.name == warehouse_name:
                        warehouse_id = warehouse.id
                        break
            
            # Generate report
            self.inventory_report_data = self.report_controller.generate_inventory_report(
                warehouse_id=warehouse_id
            )
            
            # Clear existing widgets
            for widget in self.inventory_summary_frame.winfo_children():
                widget.destroy()
                
            for widget in self.inventory_details_frame.winfo_children():
                widget.destroy()
            
            # Populate summary section
            summary = self.inventory_report_data['summary']
            
            # Create a grid layout for summary
            summary_grid = ttk.Frame(self.inventory_summary_frame)
            summary_grid.pack(fill="x")
            
            summary_grid.columnconfigure(0, weight=1)
            summary_grid.columnconfigure(1, weight=1)
            summary_grid.columnconfigure(2, weight=1)
            summary_grid.columnconfigure(3, weight=1)
            
            # Row 1
            ttk.Label(summary_grid, text=self._("Warehouse:")).grid(row=0, column=0, sticky="w", pady=2)
            ttk.Label(summary_grid, text=summary['Warehouse']).grid(row=0, column=1, sticky="w", pady=2)
            
            ttk.Label(summary_grid, text=self._("Report Date:")).grid(row=0, column=2, sticky="w", pady=2)
            ttk.Label(summary_grid, text=summary['Report Date'].strftime("%Y-%m-%d %H:%M")).grid(row=0, column=3, sticky="w", pady=2)
            
            # Row 2
            ttk.Label(summary_grid, text=self._("Total Items:")).grid(row=1, column=0, sticky="w", pady=2)
            ttk.Label(summary_grid, text=str(summary['Total Items'])).grid(row=1, column=1, sticky="w", pady=2)
            
            ttk.Label(summary_grid, text=self._("Total Inventory Value:"), font=("TkDefaultFont", 10, "bold")).grid(row=1, column=2, sticky="w", pady=2)
            ttk.Label(
                summary_grid, 
                text=f"{summary['Total Inventory Value']:.2f} USD",
                font=("TkDefaultFont", 10, "bold")
            ).grid(row=1, column=3, sticky="w", pady=2)
            
            # Create treeview for details
            columns = (
                "item_id", "item_name", "unit", "quantity", "purchase_price", "value"
            )
            
            details_tree = ttk.Treeview(
                self.inventory_details_frame,
                columns=columns,
                show="headings",
                bootstyle=INFO
            )
            
            # Define column headings
            details_tree.heading("item_id", text=self._("ID"))
            details_tree.heading("item_name", text=self._("Item Name"))
            details_tree.heading("unit", text=self._("Unit"))
            details_tree.heading("quantity", text=self._("Quantity"))
            details_tree.heading("purchase_price", text=self._("Purchase Price"))
            details_tree.heading("value", text=self._("Value"))
            
            # Define column widths
            details_tree.column("item_id", width=50, stretch=False)
            details_tree.column("item_name", width=200)
            details_tree.column("unit", width=80, stretch=False)
            details_tree.column("quantity", width=100, stretch=False)
            details_tree.column("purchase_price", width=120, stretch=False)
            details_tree.column("value", width=120, stretch=False)
            
            # Add scrollbar
            scrollbar = ttk.Scrollbar(self.inventory_details_frame, orient="vertical", command=details_tree.yview)
            details_tree.configure(yscrollcommand=scrollbar.set)
            
            # Pack treeview and scrollbar
            details_tree.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Add data to treeview
            if 'data' in self.inventory_report_data and not self.inventory_report_data['data'].empty:
                for _, row in self.inventory_report_data['data'].iterrows():
                    details_tree.insert(
                        "",
                        "end",
                        values=(
                            row['Item ID'],
                            row['Item Name'],
                            row['Unit'],
                            f"{row['Quantity']:.2f}",
                            f"{row['Purchase Price']:.2f}",
                            f"{row['Value']:.2f}"
                        )
                    )
            
            # Enable export button
            self.inventory_export_button.config(state="normal")
            
            # Show success notification
            show_notification(
                self._("Report Generated"),
                self._("Inventory report generated successfully")
            )
        except Exception as e:
            show_notification(
                self._("Error"),
                self._("Error generating report: {0}").format(str(e))
            )
    
    def create_financial_report_tab(self):
        """Create the financial report tab"""
        tab = ttk.Frame(self.notebook, padding=10)
        
        # Create filters section
        filters_frame = ttk.LabelFrame(tab, text=self._("Report Filters"), padding=10)
        filters_frame.pack(fill="x", pady=(0, 10))
        
        # Date filters
        date_frame = ttk.Frame(filters_frame)
        date_frame.pack(fill="x", pady=5)
        
        ttk.Label(date_frame, text=self._("Date Range:")).pack(side="left", padx=(0, 5))
        
        # Predefined date ranges
        self.financial_date_range_var = ttk.StringVar(value="thismonth")
        ttk.Radiobutton(
            date_frame,
            text=self._("This Month"),
            variable=self.financial_date_range_var,
            value="thismonth"
        ).pack(side="left", padx=5)
        
        ttk.Radiobutton(
            date_frame,
            text=self._("Last Month"),
            variable=self.financial_date_range_var,
            value="lastmonth"
        ).pack(side="left", padx=5)
        
        ttk.Radiobutton(
            date_frame,
            text=self._("This Quarter"),
            variable=self.financial_date_range_var,
            value="thisquarter"
        ).pack(side="left", padx=5)
        
        ttk.Radiobutton(
            date_frame,
            text=self._("This Year"),
            variable=self.financial_date_range_var,
            value="thisyear"
        ).pack(side="left", padx=5)
        
        ttk.Radiobutton(
            date_frame,
            text=self._("Custom"),
            variable=self.financial_date_range_var,
            value="custom"
        ).pack(side="left", padx=5)
        
        # Custom date range
        custom_date_frame = ttk.Frame(filters_frame)
        custom_date_frame.pack(fill="x", pady=5)
        
        ttk.Label(custom_date_frame, text=self._("From:")).pack(side="left", padx=(0, 5))
        self.financial_date_from_var = ttk.StringVar()
        date_from = ttk.DateEntry(
            custom_date_frame,
            dateformat="%Y-%m-%d",
            firstweekday=0,
            width=12,
            textvariable=self.financial_date_from_var
        )
        date_from.pack(side="left", padx=5)
        
        ttk.Label(custom_date_frame, text=self._("To:")).pack(side="left", padx=(10, 5))
        self.financial_date_to_var = ttk.StringVar()
        date_to = ttk.DateEntry(
            custom_date_frame,
            dateformat="%Y-%m-%d",
            firstweekday=0,
            width=12,
            textvariable=self.financial_date_to_var
        )
        date_to.pack(side="left", padx=5)
        
        # Generate and Export buttons
        button_frame = ttk.Frame(filters_frame)
        button_frame.pack(fill="x", pady=5)
        
        ttk.Button(
            button_frame,
            text=self._("Generate Report"),
            command=self.generate_financial_report,
            bootstyle=SUCCESS,
            width=15
        ).pack(side="left", padx=5)
        
        self.financial_export_button = ttk.Button(
            button_frame,
            text=self._("Export to Excel"),
            command=lambda: self.export_report("financial"),
            bootstyle=INFO,
            width=15
        )
        self.financial_export_button.pack(side="left", padx=5)
        self.financial_export_button.config(state="disabled")  # Disabled until report is generated
        
        # Create summary section
        self.financial_summary_frame = ttk.LabelFrame(tab, text=self._("Summary"), padding=10)
        self.financial_summary_frame.pack(fill="x", pady=10)
        
        # Will be populated when report is generated
        
        # Create a frame for the chart
        self.financial_chart_frame = ttk.LabelFrame(tab, text=self._("Financial Analysis"), padding=10)
        self.financial_chart_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Will be populated when report is generated
        
        # Create a notebook for funds and expenses details
        self.financial_details_notebook = ttk.Notebook(tab)
        self.financial_details_notebook.pack(fill="both", expand=True)
        
        # Create frames for each tab
        self.financial_funds_frame = ttk.Frame(self.financial_details_notebook, padding=10)
        self.financial_expenses_frame = ttk.Frame(self.financial_details_notebook, padding=10)
        
        # Add tabs to the notebook
        self.financial_details_notebook.add(self.financial_funds_frame, text=self._("Funds"))
        self.financial_details_notebook.add(self.financial_expenses_frame, text=self._("Expenses"))
        
        # Initialize report data variable
        self.financial_report_data = None
        
        # Set default dates
        end_date = datetime.now()
        start_date = datetime(end_date.year, end_date.month, 1)  # First day of current month
        self.financial_date_from_var.set(start_date.strftime("%Y-%m-%d"))
        self.financial_date_to_var.set(end_date.strftime("%Y-%m-%d"))
        
        # Add tab to notebook
        self.notebook.add(tab, text=self._("Financial Report"))
    
    def generate_financial_report(self):
        """Generate the financial report based on filters"""
        try:
            # Get date range based on selection
            date_range = self.financial_date_range_var.get()
            end_date = datetime.now()
            
            if date_range == "thismonth":
                start_date = datetime(end_date.year, end_date.month, 1)
            elif date_range == "lastmonth":
                if end_date.month == 1:
                    start_date = datetime(end_date.year - 1, 12, 1)
                    end_date = datetime(end_date.year, 1, 1) - timedelta(days=1)
                else:
                    start_date = datetime(end_date.year, end_date.month - 1, 1)
                    end_date = datetime(end_date.year, end_date.month, 1) - timedelta(days=1)
            elif date_range == "thisquarter":
                quarter = (end_date.month - 1) // 3 + 1
                start_date = datetime(end_date.year, (quarter - 1) * 3 + 1, 1)
            elif date_range == "thisyear":
                start_date = datetime(end_date.year, 1, 1)
            else:  # custom
                try:
                    start_date = datetime.strptime(self.financial_date_from_var.get(), "%Y-%m-%d")
                    end_date = datetime.strptime(self.financial_date_to_var.get(), "%Y-%m-%d")
                    # Set time to end of day for end_date
                    end_date = end_date.replace(hour=23, minute=59, second=59)
                except ValueError:
                    show_notification(
                        self._("Error"), 
                        self._("Please enter valid dates")
                    )
                    return
            
            # Generate report
            self.financial_report_data = self.report_controller.generate_financial_report(
                start_date=start_date,
                end_date=end_date,
                include_chart=True
            )
            
            # Clear existing widgets
            for widget in self.financial_summary_frame.winfo_children():
                widget.destroy()
                
            for widget in self.financial_chart_frame.winfo_children():
                widget.destroy()
                
            for widget in self.financial_funds_frame.winfo_children():
                widget.destroy()
                
            for widget in self.financial_expenses_frame.winfo_children():
                widget.destroy()
            
            # Populate summary section
            summary = self.financial_report_data['summary']
            
            # Create a grid layout for summary
            summary_grid = ttk.Frame(self.financial_summary_frame)
            summary_grid.pack(fill="x")
            
            summary_grid.columnconfigure(0, weight=1)
            summary_grid.columnconfigure(1, weight=1)
            summary_grid.columnconfigure(2, weight=1)
            summary_grid.columnconfigure(3, weight=1)
            
            # Row 1
            ttk.Label(summary_grid, text=self._("Date Range:")).grid(row=0, column=0, sticky="w", pady=2)
            ttk.Label(
                summary_grid, 
                text=f"{summary['Start Date'].strftime('%Y-%m-%d')} - {summary['End Date'].strftime('%Y-%m-%d')}"
            ).grid(row=0, column=1, sticky="w", pady=2)
            
            # Row 2
            ttk.Label(summary_grid, text=self._("Total Sales:")).grid(row=1, column=0, sticky="w", pady=2)
            ttk.Label(
                summary_grid, 
                text=f"{summary['Total Sales']:.2f} USD"
            ).grid(row=1, column=1, sticky="w", pady=2)
            
            ttk.Label(summary_grid, text=self._("Total Expenses:")).grid(row=1, column=2, sticky="w", pady=2)
            ttk.Label(
                summary_grid, 
                text=f"{summary['Total Expenses']:.2f} USD"
            ).grid(row=1, column=3, sticky="w", pady=2)
            
            # Row 3
            ttk.Label(summary_grid, text=self._("Total Purchases:")).grid(row=2, column=0, sticky="w", pady=2)
            ttk.Label(
                summary_grid, 
                text=f"{summary['Total Purchases']:.2f} USD"
            ).grid(row=2, column=1, sticky="w", pady=2)
            
            # Row 4
            ttk.Label(
                summary_grid, 
                text=self._("Profit:"),
                font=("TkDefaultFont", 10, "bold")
            ).grid(row=3, column=0, sticky="w", pady=2)
            
            profit_label = ttk.Label(
                summary_grid, 
                text=f"{summary['Profit']:.2f} USD",
                font=("TkDefaultFont", 10, "bold"),
                bootstyle=SUCCESS if summary['Profit'] >= 0 else DANGER
            )
            profit_label.grid(row=3, column=1, sticky="w", pady=2)
            
            # Display chart if available
            if summary['Chart']:
                try:
                    chart_data = base64.b64decode(summary['Chart'])
                    chart_image = Image.open(io.BytesIO(chart_data))
                    
                    photo = ImageTk.PhotoImage(chart_image)
                    chart_label = ttk.Label(self.financial_chart_frame, image=photo)
                    chart_label.image = photo  # Keep a reference
                    chart_label.pack(fill="both", expand=True)
                except Exception as e:
                    ttk.Label(
                        self.financial_chart_frame,
                        text=self._("Error displaying chart: {0}").format(str(e)),
                        bootstyle=DANGER
                    ).pack(pady=10)
            else:
                ttk.Label(
                    self.financial_chart_frame,
                    text=self._("No chart data available")
                ).pack(pady=10)
            
            # Populate Funds tab
            if 'funds' in self.financial_report_data and not self.financial_report_data['funds'].empty:
                # Create treeview for funds
                columns = (
                    "fund_name", "currency", "balance", "exchange_rate", "usd_equivalent"
                )
                
                funds_tree = ttk.Treeview(
                    self.financial_funds_frame,
                    columns=columns,
                    show="headings",
                    bootstyle=INFO
                )
                
                # Define column headings
                funds_tree.heading("fund_name", text=self._("Fund Name"))
                funds_tree.heading("currency", text=self._("Currency"))
                funds_tree.heading("balance", text=self._("Balance"))
                funds_tree.heading("exchange_rate", text=self._("Exchange Rate"))
                funds_tree.heading("usd_equivalent", text=self._("USD Equivalent"))
                
                # Define column widths
                funds_tree.column("fund_name", width=150)
                funds_tree.column("currency", width=80, stretch=False)
                funds_tree.column("balance", width=100, stretch=False)
                funds_tree.column("exchange_rate", width=100, stretch=False)
                funds_tree.column("usd_equivalent", width=120, stretch=False)
                
                # Add scrollbar
                funds_scrollbar = ttk.Scrollbar(self.financial_funds_frame, orient="vertical", command=funds_tree.yview)
                funds_tree.configure(yscrollcommand=funds_scrollbar.set)
                
                # Pack treeview and scrollbar
                funds_tree.pack(side="left", fill="both", expand=True)
                funds_scrollbar.pack(side="right", fill="y")
                
                # Add data to treeview
                for _, row in self.financial_report_data['funds'].iterrows():
                    funds_tree.insert(
                        "",
                        "end",
                        values=(
                            row['Fund Name'],
                            row['Currency'],
                            f"{row['Balance']:.2f}",
                            f"{row['Exchange Rate']:.2f}",
                            f"{row['USD Equivalent']:.2f}"
                        )
                    )
            else:
                ttk.Label(
                    self.financial_funds_frame,
                    text=self._("No fund data available")
                ).pack(pady=10)
            
            # Populate Expenses tab
            if 'expenses' in self.financial_report_data and not self.financial_report_data['expenses'].empty:
                # Create treeview for expenses
                columns = (
                    "date", "category", "amount", "currency", "description"
                )
                
                expenses_tree = ttk.Treeview(
                    self.financial_expenses_frame,
                    columns=columns,
                    show="headings",
                    bootstyle=INFO
                )
                
                # Define column headings
                expenses_tree.heading("date", text=self._("Date"))
                expenses_tree.heading("category", text=self._("Category"))
                expenses_tree.heading("amount", text=self._("Amount"))
                expenses_tree.heading("currency", text=self._("Currency"))
                expenses_tree.heading("description", text=self._("Description"))
                
                # Define column widths
                expenses_tree.column("date", width=100, stretch=False)
                expenses_tree.column("category", width=150)
                expenses_tree.column("amount", width=100, stretch=False)
                expenses_tree.column("currency", width=80, stretch=False)
                expenses_tree.column("description", width=250)
                
                # Add scrollbar
                expenses_scrollbar = ttk.Scrollbar(self.financial_expenses_frame, orient="vertical", command=expenses_tree.yview)
                expenses_tree.configure(yscrollcommand=expenses_scrollbar.set)
                
                # Pack treeview and scrollbar
                expenses_tree.pack(side="left", fill="both", expand=True)
                expenses_scrollbar.pack(side="right", fill="y")
                
                # Add data to treeview
                for _, row in self.financial_report_data['expenses'].iterrows():
                    expenses_tree.insert(
                        "",
                        "end",
                        values=(
                            row['Date'].strftime('%Y-%m-%d'),
                            row['Category'],
                            f"{row['Amount']:.2f}",
                            row['Currency'],
                            row['Description'] or ""
                        )
                    )
            else:
                ttk.Label(
                    self.financial_expenses_frame,
                    text=self._("No expense data available")
                ).pack(pady=10)
            
            # Enable export button
            self.financial_export_button.config(state="normal")
            
            # Show success notification
            show_notification(
                self._("Report Generated"),
                self._("Financial report generated successfully")
            )
        except Exception as e:
            show_notification(
                self._("Error"),
                self._("Error generating report: {0}").format(str(e))
            )
    
    def create_receivables_payables_tab(self):
        """Create the receivables and payables report tab"""
        tab = ttk.Frame(self.notebook, padding=10)
        
        # Create filters section
        filters_frame = ttk.LabelFrame(tab, text=self._("Report Filters"), padding=10)
        filters_frame.pack(fill="x", pady=(0, 10))
        
        # Minimum balance filter
        min_balance_frame = ttk.Frame(filters_frame)
        min_balance_frame.pack(fill="x", pady=5)
        
        ttk.Label(min_balance_frame, text=self._("Minimum Balance:")).pack(side="left", padx=(0, 5))
        self.rp_min_balance_var = ttk.DoubleVar(value=0.0)
        min_balance_entry = ttk.Entry(min_balance_frame, textvariable=self.rp_min_balance_var, width=15)
        min_balance_entry.pack(side="left", padx=5)
        
        ttk.Label(min_balance_frame, text="USD").pack(side="left")
        
        # Generate and Export buttons
        button_frame = ttk.Frame(filters_frame)
        button_frame.pack(fill="x", pady=5)
        
        ttk.Button(
            button_frame,
            text=self._("Generate Report"),
            command=self.generate_rp_report,
            bootstyle=SUCCESS,
            width=15
        ).pack(side="left", padx=5)
        
        self.rp_export_button = ttk.Button(
            button_frame,
            text=self._("Export to Excel"),
            command=lambda: self.export_report("receivables_payables"),
            bootstyle=INFO,
            width=15
        )
        self.rp_export_button.pack(side="left", padx=5)
        self.rp_export_button.config(state="disabled")  # Disabled until report is generated
        
        # Create summary section
        self.rp_summary_frame = ttk.LabelFrame(tab, text=self._("Summary"), padding=10)
        self.rp_summary_frame.pack(fill="x", pady=10)
        
        # Will be populated when report is generated
        
        # Create a notebook for receivables and payables details
        self.rp_details_notebook = ttk.Notebook(tab)
        self.rp_details_notebook.pack(fill="both", expand=True)
        
        # Create frames for each tab
        self.receivables_frame = ttk.Frame(self.rp_details_notebook, padding=10)
        self.payables_frame = ttk.Frame(self.rp_details_notebook, padding=10)
        
        # Add tabs to the notebook
        self.rp_details_notebook.add(self.receivables_frame, text=self._("Receivables (Customers)"))
        self.rp_details_notebook.add(self.payables_frame, text=self._("Payables (Suppliers)"))
        
        # Initialize report data variable
        self.rp_report_data = None
        
        # Add tab to notebook
        self.notebook.add(tab, text=self._("Receivables & Payables"))
    
    def generate_rp_report(self):
        """Generate the receivables and payables report"""
        try:
            # Get minimum balance
            min_balance = 0.0
            try:
                min_balance = float(self.rp_min_balance_var.get())
                if min_balance < 0:
                    min_balance = 0.0
            except (ValueError, tkinter.TclError):
                pass
            
            # Generate report
            self.rp_report_data = self.report_controller.generate_receivables_payables_report()
            
            # Clear existing widgets
            for widget in self.rp_summary_frame.winfo_children():
                widget.destroy()
                
            for widget in self.receivables_frame.winfo_children():
                widget.destroy()
                
            for widget in self.payables_frame.winfo_children():
                widget.destroy()
            
            # Populate summary section
            summary = self.rp_report_data['summary']
            
            # Create a grid layout for summary
            summary_grid = ttk.Frame(self.rp_summary_frame)
            summary_grid.pack(fill="x")
            
            summary_grid.columnconfigure(0, weight=1)
            summary_grid.columnconfigure(1, weight=1)
            summary_grid.columnconfigure(2, weight=1)
            summary_grid.columnconfigure(3, weight=1)
            
            # Row 1
            ttk.Label(summary_grid, text=self._("Total Receivables:")).grid(row=0, column=0, sticky="w", pady=2)
            ttk.Label(
                summary_grid, 
                text=f"{summary['Total Receivables']:.2f} USD",
                bootstyle=SUCCESS
            ).grid(row=0, column=1, sticky="w", pady=2)
            
            ttk.Label(summary_grid, text=self._("Total Payables:")).grid(row=0, column=2, sticky="w", pady=2)
            ttk.Label(
                summary_grid, 
                text=f"{summary['Total Payables']:.2f} USD",
                bootstyle=DANGER
            ).grid(row=0, column=3, sticky="w", pady=2)
            
            # Row 2
            ttk.Label(summary_grid, text=self._("Customers with Debt:")).grid(row=1, column=0, sticky="w", pady=2)
            ttk.Label(
                summary_grid, 
                text=str(summary['Total Customers with Debt'])
            ).grid(row=1, column=1, sticky="w", pady=2)
            
            ttk.Label(summary_grid, text=self._("Suppliers to Pay:")).grid(row=1, column=2, sticky="w", pady=2)
            ttk.Label(
                summary_grid, 
                text=str(summary['Total Suppliers to Pay'])
            ).grid(row=1, column=3, sticky="w", pady=2)
            
            # Row 3
            ttk.Label(
                summary_grid, 
                text=self._("Net Position:"),
                font=("TkDefaultFont", 10, "bold")
            ).grid(row=2, column=0, sticky="w", pady=2)
            
            net_position = summary['Net Position']
            net_position_label = ttk.Label(
                summary_grid, 
                text=f"{net_position:.2f} USD",
                font=("TkDefaultFont", 10, "bold"),
                bootstyle=SUCCESS if net_position >= 0 else DANGER
            )
            net_position_label.grid(row=2, column=1, sticky="w", pady=2)
            
            ttk.Label(summary_grid, text=self._("Report Date:")).grid(row=2, column=2, sticky="w", pady=2)
            ttk.Label(
                summary_grid, 
                text=summary['Report Date'].strftime("%Y-%m-%d %H:%M")
            ).grid(row=2, column=3, sticky="w", pady=2)
            
            # Populate Receivables tab
            if 'receivables' in self.rp_report_data and not self.rp_report_data['receivables'].empty:
                # Filter by minimum balance if set
                if min_balance > 0:
                    receivables_df = self.rp_report_data['receivables']
                    receivables_df = receivables_df[receivables_df['Balance'] >= min_balance]
                else:
                    receivables_df = self.rp_report_data['receivables']
                
                # Create treeview for receivables
                columns = (
                    "customer_id", "customer_name", "balance", "currency", "phone", "email"
                )
                
                receivables_tree = ttk.Treeview(
                    self.receivables_frame,
                    columns=columns,
                    show="headings",
                    bootstyle=INFO
                )
                
                # Define column headings
                receivables_tree.heading("customer_id", text=self._("ID"))
                receivables_tree.heading("customer_name", text=self._("Customer Name"))
                receivables_tree.heading("balance", text=self._("Balance"))
                receivables_tree.heading("currency", text=self._("Currency"))
                receivables_tree.heading("phone", text=self._("Phone"))
                receivables_tree.heading("email", text=self._("Email"))
                
                # Define column widths
                receivables_tree.column("customer_id", width=50, stretch=False)
                receivables_tree.column("customer_name", width=200)
                receivables_tree.column("balance", width=100, stretch=False)
                receivables_tree.column("currency", width=80, stretch=False)
                receivables_tree.column("phone", width=120)
                receivables_tree.column("email", width=150)
                
                # Add scrollbar
                rec_scrollbar = ttk.Scrollbar(self.receivables_frame, orient="vertical", command=receivables_tree.yview)
                receivables_tree.configure(yscrollcommand=rec_scrollbar.set)
                
                # Pack treeview and scrollbar
                receivables_tree.pack(side="left", fill="both", expand=True)
                rec_scrollbar.pack(side="right", fill="y")
                
                # Add data to treeview
                for _, row in receivables_df.iterrows():
                    receivables_tree.insert(
                        "",
                        "end",
                        values=(
                            row['Customer ID'],
                            row['Customer Name'],
                            f"{row['Balance']:.2f}",
                            row['Currency'],
                            row['Phone'] or "",
                            row['Email'] or ""
                        )
                    )
            else:
                ttk.Label(
                    self.receivables_frame,
                    text=self._("No receivables data available")
                ).pack(pady=10)
            
            # Populate Payables tab
            if 'payables' in self.rp_report_data and not self.rp_report_data['payables'].empty:
                # Filter by minimum balance if set
                if min_balance > 0:
                    payables_df = self.rp_report_data['payables']
                    payables_df = payables_df[payables_df['Balance'] >= min_balance]
                else:
                    payables_df = self.rp_report_data['payables']
                
                # Create treeview for payables
                columns = (
                    "supplier_id", "supplier_name", "balance", "currency", "phone", "email"
                )
                
                payables_tree = ttk.Treeview(
                    self.payables_frame,
                    columns=columns,
                    show="headings",
                    bootstyle=INFO
                )
                
                # Define column headings
                payables_tree.heading("supplier_id", text=self._("ID"))
                payables_tree.heading("supplier_name", text=self._("Supplier Name"))
                payables_tree.heading("balance", text=self._("Balance"))
                payables_tree.heading("currency", text=self._("Currency"))
                payables_tree.heading("phone", text=self._("Phone"))
                payables_tree.heading("email", text=self._("Email"))
                
                # Define column widths
                payables_tree.column("supplier_id", width=50, stretch=False)
                payables_tree.column("supplier_name", width=200)
                payables_tree.column("balance", width=100, stretch=False)
                payables_tree.column("currency", width=80, stretch=False)
                payables_tree.column("phone", width=120)
                payables_tree.column("email", width=150)
                
                # Add scrollbar
                pay_scrollbar = ttk.Scrollbar(self.payables_frame, orient="vertical", command=payables_tree.yview)
                payables_tree.configure(yscrollcommand=pay_scrollbar.set)
                
                # Pack treeview and scrollbar
                payables_tree.pack(side="left", fill="both", expand=True)
                pay_scrollbar.pack(side="right", fill="y")
                
                # Add data to treeview
                for _, row in payables_df.iterrows():
                    payables_tree.insert(
                        "",
                        "end",
                        values=(
                            row['Supplier ID'],
                            row['Supplier Name'],
                            f"{row['Balance']:.2f}",
                            row['Currency'],
                            row['Phone'] or "",
                            row['Email'] or ""
                        )
                    )
            else:
                ttk.Label(
                    self.payables_frame,
                    text=self._("No payables data available")
                ).pack(pady=10)
            
            # Enable export button
            self.rp_export_button.config(state="normal")
            
            # Show success notification
            show_notification(
                self._("Report Generated"),
                self._("Receivables & Payables report generated successfully")
            )
        except Exception as e:
            show_notification(
                self._("Error"),
                self._("Error generating report: {0}").format(str(e))
            )
    
    def export_report(self, report_type):
        """Export the selected report to Excel
        
        Args:
            report_type: Type of report to export ('sales', 'inventory', 'financial', 'receivables_payables')
        """
        try:
            # Check if report data exists
            if report_type == "sales" and self.sales_report_data:
                filename = f"sales_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                self.report_controller.export_to_excel(self.sales_report_data, filename)
                show_notification(
                    self._("Export Complete"),
                    self._("Report exported to {0}").format(filename)
                )
            elif report_type == "inventory" and self.inventory_report_data:
                filename = f"inventory_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                self.report_controller.export_to_excel(self.inventory_report_data, filename)
                show_notification(
                    self._("Export Complete"),
                    self._("Report exported to {0}").format(filename)
                )
            elif report_type == "financial" and self.financial_report_data:
                filename = f"financial_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                self.report_controller.export_to_excel(self.financial_report_data, filename)
                show_notification(
                    self._("Export Complete"),
                    self._("Report exported to {0}").format(filename)
                )
            elif report_type == "receivables_payables" and self.rp_report_data:
                filename = f"receivables_payables_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                self.report_controller.export_to_excel(self.rp_report_data, filename)
                show_notification(
                    self._("Export Complete"),
                    self._("Report exported to {0}").format(filename)
                )
            else:
                show_notification(
                    self._("Error"),
                    self._("No report data available to export")
                )
        except Exception as e:
            show_notification(
                self._("Error"),
                self._("Error exporting report: {0}").format(str(e))
            )
