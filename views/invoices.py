#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Invoices management view for ASSI Warehouse Management System
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import gettext
from datetime import datetime, timedelta
from controllers.invoice_controller import InvoiceController
from controllers.item_controller import ItemController
from controllers.warehouse_controller import WarehouseController
from controllers.supplier_customer_controller import SupplierCustomerController
from controllers.fund_controller import FundController
from utils.notifications import show_notification

class InvoicesView:
    """Invoices management view class"""
    
    def __init__(self, root, back_to_main_menu):
        """Initialize the invoices view
        
        Args:
            root: The root window
            back_to_main_menu: Callback function to return to main menu
        """
        self.root = root
        self.back_to_main_menu = back_to_main_menu
        self.invoice_controller = InvoiceController()
        self.item_controller = ItemController()
        self.warehouse_controller = WarehouseController()
        self.supplier_customer_controller = SupplierCustomerController()
        self.fund_controller = FundController()
        
        # Setup translation
        self._ = gettext.gettext
        
        # Set window title
        self.root.title(self._("ASSI WMS - Invoices Management"))
        
        # Create main frame
        self.frame = ttk.Frame(self.root)
        self.frame.pack(expand=True, fill="both")
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Create tabs
        self.create_invoices_list_tab()
        self.create_new_purchase_invoice_tab()
        self.create_new_sales_invoice_tab()
        self.create_payments_tab()
        
        # Add back button
        back_button = ttk.Button(
            self.frame,
            text=self._("Back to Main Menu"),
            command=self.back_to_main_menu,
            bootstyle=SECONDARY,
            width=20
        )
        back_button.pack(pady=10)
    
    def create_invoices_list_tab(self):
        """Create the invoices list tab"""
        tab = ttk.Frame(self.notebook, padding=10)
        
        # Create filters section
        filters_frame = ttk.LabelFrame(tab, text=self._("Filters"), padding=10)
        filters_frame.pack(fill="x", pady=(0, 10))
        
        # Type filter
        filter_row1 = ttk.Frame(filters_frame)
        filter_row1.pack(fill="x", pady=5)
        
        ttk.Label(filter_row1, text=self._("Type:"), width=10).pack(side="left")
        self.type_filter_var = ttk.StringVar(value="all")
        
        ttk.Radiobutton(
            filter_row1,
            text=self._("All"),
            variable=self.type_filter_var,
            value="all"
        ).pack(side="left", padx=5)
        
        ttk.Radiobutton(
            filter_row1,
            text=self._("Purchase"),
            variable=self.type_filter_var,
            value="purchase"
        ).pack(side="left", padx=5)
        
        ttk.Radiobutton(
            filter_row1,
            text=self._("Sale"),
            variable=self.type_filter_var,
            value="sale"
        ).pack(side="left", padx=5)
        
        # Status filter
        ttk.Label(filter_row1, text=self._("Status:"), width=10).pack(side="left", padx=(20, 0))
        self.status_filter_var = ttk.StringVar(value="all")
        
        ttk.Radiobutton(
            filter_row1,
            text=self._("All"),
            variable=self.status_filter_var,
            value="all"
        ).pack(side="left", padx=5)
        
        ttk.Radiobutton(
            filter_row1,
            text=self._("Pending"),
            variable=self.status_filter_var,
            value="pending"
        ).pack(side="left", padx=5)
        
        ttk.Radiobutton(
            filter_row1,
            text=self._("Partially Paid"),
            variable=self.status_filter_var,
            value="partially_paid"
        ).pack(side="left", padx=5)
        
        ttk.Radiobutton(
            filter_row1,
            text=self._("Paid"),
            variable=self.status_filter_var,
            value="paid"
        ).pack(side="left", padx=5)
        
        # Date filters
        filter_row2 = ttk.Frame(filters_frame)
        filter_row2.pack(fill="x", pady=5)
        
        ttk.Label(filter_row2, text=self._("Date From:"), width=10).pack(side="left")
        self.date_from_var = ttk.StringVar()
        date_from = ttk.DateEntry(
            filter_row2,
            dateformat="%Y-%m-%d",
            firstweekday=0,
            width=12,
            textvariable=self.date_from_var
        )
        date_from.pack(side="left", padx=5)
        
        ttk.Label(filter_row2, text=self._("To:"), width=3).pack(side="left")
        self.date_to_var = ttk.StringVar()
        date_to = ttk.DateEntry(
            filter_row2,
            dateformat="%Y-%m-%d",
            firstweekday=0,
            width=12,
            textvariable=self.date_to_var
        )
        date_to.pack(side="left", padx=5)
        
        # Buttons
        filter_button = ttk.Button(
            filter_row2,
            text=self._("Apply Filters"),
            command=self.refresh_invoices_list,
            bootstyle=INFO,
            width=15
        )
        filter_button.pack(side="left", padx=20)
        
        reset_button = ttk.Button(
            filter_row2,
            text=self._("Reset Filters"),
            command=self.reset_filters,
            bootstyle=SECONDARY,
            width=15
        )
        reset_button.pack(side="left", padx=5)
        
        # Create treeview for invoices list
        columns = (
            "id", "number", "type", "date", "entity", "total", "paid", "remaining", "status"
        )
        
        self.invoices_tree = ttk.Treeview(
            tab,
            columns=columns,
            show="headings",
            bootstyle=INFO
        )
        
        # Define column headings
        self.invoices_tree.heading("id", text=self._("ID"))
        self.invoices_tree.heading("number", text=self._("Invoice Number"))
        self.invoices_tree.heading("type", text=self._("Type"))
        self.invoices_tree.heading("date", text=self._("Date"))
        self.invoices_tree.heading("entity", text=self._("Supplier/Customer"))
        self.invoices_tree.heading("total", text=self._("Total Amount"))
        self.invoices_tree.heading("paid", text=self._("Paid Amount"))
        self.invoices_tree.heading("remaining", text=self._("Remaining"))
        self.invoices_tree.heading("status", text=self._("Status"))
        
        # Define column widths
        self.invoices_tree.column("id", width=50, stretch=False)
        self.invoices_tree.column("number", width=120)
        self.invoices_tree.column("type", width=80, stretch=False)
        self.invoices_tree.column("date", width=100, stretch=False)
        self.invoices_tree.column("entity", width=150)
        self.invoices_tree.column("total", width=100, stretch=False)
        self.invoices_tree.column("paid", width=100, stretch=False)
        self.invoices_tree.column("remaining", width=100, stretch=False)
        self.invoices_tree.column("status", width=100, stretch=False)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.invoices_tree.yview)
        self.invoices_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.invoices_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add context menu
        self.setup_invoices_context_menu()
        
        # Load initial data
        self.refresh_invoices_list()
        
        # Add tab to notebook
        self.notebook.add(tab, text=self._("Invoices List"))
    
    def setup_invoices_context_menu(self):
        """Setup context menu for invoices treeview"""
        self.invoice_context_menu = ttk.Menu(self.invoices_tree, tearoff=0)
        self.invoice_context_menu.add_command(
            label=self._("View Invoice Details"),
            command=self.view_invoice_details
        )
        self.invoice_context_menu.add_command(
            label=self._("Record Payment"),
            command=self.record_payment_for_selected
        )
        self.invoice_context_menu.add_separator()
        self.invoice_context_menu.add_command(
            label=self._("Cancel Invoice"),
            command=self.cancel_invoice
        )
        
        # Bind right-click to show context menu
        self.invoices_tree.bind("<Button-3>", self.show_invoice_context_menu)
        # Bind double-click to view details
        self.invoices_tree.bind("<Double-1>", lambda event: self.view_invoice_details())
    
    def show_invoice_context_menu(self, event):
        """Show context menu on right-click"""
        # Select row under mouse
        iid = self.invoices_tree.identify_row(event.y)
        if iid:
            # Select this item
            self.invoices_tree.selection_set(iid)
            # Display context menu
            self.invoice_context_menu.tk_popup(event.x_root, event.y_root)
    
    def reset_filters(self):
        """Reset all filters to default values"""
        self.type_filter_var.set("all")
        self.status_filter_var.set("all")
        self.date_from_var.set("")
        self.date_to_var.set("")
        self.refresh_invoices_list()
    
    def refresh_invoices_list(self):
        """Refresh the invoices list based on filters"""
        # Clear existing items
        for item in self.invoices_tree.get_children():
            self.invoices_tree.delete(item)
        
        # Get filter values
        invoice_type = self.type_filter_var.get()
        if invoice_type == "all":
            invoice_type = None
        
        status = self.status_filter_var.get()
        if status == "all":
            status = None
        
        # Process date filters
        start_date = None
        if self.date_from_var.get():
            try:
                start_date = datetime.strptime(self.date_from_var.get(), "%Y-%m-%d")
            except ValueError:
                pass
        
        end_date = None
        if self.date_to_var.get():
            try:
                end_date = datetime.strptime(self.date_to_var.get(), "%Y-%m-%d")
                # Set the time to end of day
                end_date = end_date.replace(hour=23, minute=59, second=59)
            except ValueError:
                pass
        
        # Get invoices based on filters
        invoices = self.invoice_controller.get_all_invoices(
            invoice_type=invoice_type,
            status=status,
            start_date=start_date,
            end_date=end_date
        )
        
        # Add invoices to treeview
        for invoice in invoices:
            paid_amount = invoice.calculate_paid_amount()
            remaining_amount = invoice.total_amount - paid_amount
            
            # Format invoice type with icon
            if invoice.type == "purchase":
                type_display = "🛒 " + self._("Purchase")
            else:
                type_display = "💰 " + self._("Sale")
            
            # Format status with icon and color
            if invoice.status == "pending":
                status_display = "⏳ " + self._("Pending")
            elif invoice.status == "partially_paid":
                status_display = "⚠️ " + self._("Partially Paid")
            elif invoice.status == "paid":
                status_display = "✅ " + self._("Paid")
            else:
                status_display = "❌ " + self._("Cancelled")
            
            self.invoices_tree.insert(
                "",
                "end",
                values=(
                    invoice.id,
                    invoice.invoice_number,
                    type_display,
                    invoice.invoice_date.strftime("%Y-%m-%d"),
                    invoice.entity.name,
                    f"{invoice.total_amount:.2f} {invoice.currency}",
                    f"{paid_amount:.2f} {invoice.currency}",
                    f"{remaining_amount:.2f} {invoice.currency}",
                    status_display
                )
            )
    
    def view_invoice_details(self):
        """View details for the selected invoice"""
        selected_items = self.invoices_tree.selection()
        if not selected_items:
            return
            
        item_id = selected_items[0]
        invoice_id = self.invoices_tree.item(item_id, "values")[0]
        
        # Get invoice data
        invoice = self.invoice_controller.get_invoice_by_id(invoice_id)
        if not invoice:
            return
        
        # Get invoice items and payments
        invoice_items = self.invoice_controller.get_invoice_items(invoice_id)
        payments = self.invoice_controller.get_invoice_payments(invoice_id)
        
        # Create details dialog
        details_dialog = ttk.Toplevel(self.root)
        details_dialog.title(self._("Invoice Details - {0}").format(invoice.invoice_number))
        details_dialog.geometry("700x600")
        details_dialog.transient(self.root)
        
        # Create main frame
        main_frame = ttk.Frame(details_dialog, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # Invoice header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 10))
        
        # Invoice number and type
        invoice_title = ttk.Label(
            header_frame,
            text=f"{invoice.invoice_number} - {self._('Purchase Invoice') if invoice.type == 'purchase' else self._('Sales Invoice')}",
            font=("TkDefaultFont", 14, "bold")
        )
        invoice_title.pack(anchor="w")
        
        # Invoice date and status
        date_status = ttk.Label(
            header_frame,
            text=f"{self._('Date')}: {invoice.invoice_date.strftime('%Y-%m-%d')} | {self._('Status')}: {self._('Pending') if invoice.status == 'pending' else self._('Partially Paid') if invoice.status == 'partially_paid' else self._('Paid')}"
        )
        date_status.pack(anchor="w", pady=5)
        
        # Entity info
        entity_info = ttk.Label(
            header_frame,
            text=f"{self._('Supplier') if invoice.type == 'purchase' else self._('Customer')}: {invoice.entity.name} | {self._('Balance')}: {invoice.entity.balance:.2f} {invoice.entity.currency}"
        )
        entity_info.pack(anchor="w")
        
        # Due date if set
        if invoice.due_date:
            due_date = ttk.Label(
                header_frame,
                text=f"{self._('Due Date')}: {invoice.due_date.strftime('%Y-%m-%d')}",
                font=("TkDefaultFont", 10, "bold")
            )
            due_date.pack(anchor="w", pady=5)
        
        # Create notebook for items and payments
        details_notebook = ttk.Notebook(main_frame)
        details_notebook.pack(fill="both", expand=True, pady=10)
        
        # Items tab
        items_tab = ttk.Frame(details_notebook, padding=10)
        
        # Create treeview for items
        items_columns = ("id", "name", "quantity", "unit", "price", "total")
        
        items_tree = ttk.Treeview(
            items_tab,
            columns=items_columns,
            show="headings",
            bootstyle=INFO
        )
        
        # Define column headings
        items_tree.heading("id", text=self._("ID"))
        items_tree.heading("name", text=self._("Item"))
        items_tree.heading("quantity", text=self._("Quantity"))
        items_tree.heading("unit", text=self._("Unit"))
        items_tree.heading("price", text=self._("Price"))
        items_tree.heading("total", text=self._("Total"))
        
        # Define column widths
        items_tree.column("id", width=50, stretch=False)
        items_tree.column("name", width=200)
        items_tree.column("quantity", width=80, stretch=False)
        items_tree.column("unit", width=80, stretch=False)
        items_tree.column("price", width=100, stretch=False)
        items_tree.column("total", width=100, stretch=False)
        
        # Add scrollbar
        items_scrollbar = ttk.Scrollbar(items_tab, orient="vertical", command=items_tree.yview)
        items_tree.configure(yscrollcommand=items_scrollbar.set)
        
        # Pack treeview and scrollbar
        items_tree.pack(side="left", fill="both", expand=True)
        items_scrollbar.pack(side="right", fill="y")
        
        # Add items to treeview
        for item in invoice_items:
            items_tree.insert(
                "",
                "end",
                values=(
                    item.id,
                    item.item.name,
                    f"{item.quantity:.2f}",
                    item.unit,
                    f"{item.price_per_unit:.2f}",
                    f"{item.total_price:.2f}"
                )
            )
        
        # Add items tab to notebook
        details_notebook.add(items_tab, text=self._("Items"))
        
        # Payments tab
        payments_tab = ttk.Frame(details_notebook, padding=10)
        
        # Create treeview for payments
        payments_columns = ("id", "date", "amount", "method", "fund", "notes")
        
        payments_tree = ttk.Treeview(
            payments_tab,
            columns=payments_columns,
            show="headings",
            bootstyle=INFO
        )
        
        # Define column headings
        payments_tree.heading("id", text=self._("ID"))
        payments_tree.heading("date", text=self._("Date"))
        payments_tree.heading("amount", text=self._("Amount"))
        payments_tree.heading("method", text=self._("Method"))
        payments_tree.heading("fund", text=self._("Fund"))
        payments_tree.heading("notes", text=self._("Notes"))
        
        # Define column widths
        payments_tree.column("id", width=50, stretch=False)
        payments_tree.column("date", width=100, stretch=False)
        payments_tree.column("amount", width=100, stretch=False)
        payments_tree.column("method", width=100, stretch=False)
        payments_tree.column("fund", width=150)
        payments_tree.column("notes", width=200)
        
        # Add scrollbar
        payments_scrollbar = ttk.Scrollbar(payments_tab, orient="vertical", command=payments_tree.yview)
        payments_tree.configure(yscrollcommand=payments_scrollbar.set)
        
        # Pack treeview and scrollbar
        payments_tree.pack(side="left", fill="both", expand=True)
        payments_scrollbar.pack(side="right", fill="y")
        
        # Add payments to treeview
        for payment in payments:
            # Get fund name if fund_id is set
            fund_name = ""
            if payment.fund_id:
                fund = self.fund_controller.get_fund_by_id(payment.fund_id)
                if fund:
                    fund_name = fund.name
            
            payments_tree.insert(
                "",
                "end",
                values=(
                    payment.id,
                    payment.payment_date.strftime("%Y-%m-%d"),
                    f"{payment.amount:.2f} {payment.currency}",
                    payment.payment_method,
                    fund_name,
                    payment.notes or ""
                )
            )
        
        # Add payments tab to notebook
        details_notebook.add(payments_tab, text=self._("Payments"))
        
        # Summary frame
        summary_frame = ttk.LabelFrame(main_frame, text=self._("Summary"), padding=10)
        summary_frame.pack(fill="x", pady=10)
        
        # Create grid for summary
        summary_frame.columnconfigure(0, weight=1)
        summary_frame.columnconfigure(1, weight=1)
        summary_frame.columnconfigure(2, weight=1)
        summary_frame.columnconfigure(3, weight=1)
        
        # Add summary fields
        ttk.Label(summary_frame, text=self._("Subtotal:")).grid(row=0, column=0, sticky="w", pady=2)
        subtotal = sum(item.total_price for item in invoice_items)
        ttk.Label(summary_frame, text=f"{subtotal:.2f} {invoice.currency}").grid(row=0, column=1, sticky="w", pady=2)
        
        ttk.Label(summary_frame, text=self._("Additional Costs:")).grid(row=1, column=0, sticky="w", pady=2)
        ttk.Label(summary_frame, text=f"{invoice.additional_costs:.2f} {invoice.currency}").grid(row=1, column=1, sticky="w", pady=2)
        
        ttk.Label(summary_frame, text=self._("Tax:")).grid(row=0, column=2, sticky="w", pady=2)
        ttk.Label(summary_frame, text=f"{invoice.tax:.2f} {invoice.currency}").grid(row=0, column=3, sticky="w", pady=2)
        
        ttk.Label(summary_frame, text=self._("Total:"), font=("TkDefaultFont", 10, "bold")).grid(row=2, column=0, sticky="w", pady=2)
        ttk.Label(summary_frame, text=f"{invoice.total_amount:.2f} {invoice.currency}", font=("TkDefaultFont", 10, "bold")).grid(row=2, column=1, sticky="w", pady=2)
        
        ttk.Label(summary_frame, text=self._("Paid:"), font=("TkDefaultFont", 10, "bold")).grid(row=1, column=2, sticky="w", pady=2)
        ttk.Label(summary_frame, text=f"{invoice.calculate_paid_amount():.2f} {invoice.currency}", font=("TkDefaultFont", 10, "bold")).grid(row=1, column=3, sticky="w", pady=2)
        
        ttk.Label(summary_frame, text=self._("Remaining:"), font=("TkDefaultFont", 10, "bold")).grid(row=2, column=2, sticky="w", pady=2)
        ttk.Label(summary_frame, text=f"{invoice.calculate_remaining_amount():.2f} {invoice.currency}", font=("TkDefaultFont", 10, "bold")).grid(row=2, column=3, sticky="w", pady=2)
        
        # Actions frame
        actions_frame = ttk.Frame(main_frame)
        actions_frame.pack(fill="x", pady=10)
        
        # Add payment button if invoice is not fully paid and not cancelled
        if invoice.status != "paid" and invoice.status != "cancelled":
            payment_button = ttk.Button(
                actions_frame,
                text=self._("Record Payment"),
                command=lambda: self.show_payment_dialog(invoice, details_dialog),
                bootstyle=SUCCESS,
                width=15
            )
            payment_button.pack(side="left", padx=5)
        
        # Cancel button if invoice is not cancelled
        if invoice.status != "cancelled":
            cancel_button = ttk.Button(
                actions_frame,
                text=self._("Cancel Invoice"),
                command=lambda: self.confirm_cancel_invoice(invoice.id, details_dialog),
                bootstyle=DANGER,
                width=15
            )
            cancel_button.pack(side="left", padx=5)
        
        # Close button
        close_button = ttk.Button(
            actions_frame,
            text=self._("Close"),
            command=details_dialog.destroy,
            bootstyle=SECONDARY,
            width=15
        )
        close_button.pack(side="right", padx=5)
    
    def show_payment_dialog(self, invoice, parent_dialog=None):
        """Show dialog to record a payment for an invoice"""
        # Create payment dialog
        payment_dialog = ttk.Toplevel(parent_dialog or self.root)
        payment_dialog.title(self._("Record Payment - {0}").format(invoice.invoice_number))
        payment_dialog.geometry("400x400")
        payment_dialog.transient(parent_dialog or self.root)
        payment_dialog.grab_set()
        
        # Create main frame
        main_frame = ttk.Frame(payment_dialog, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # Add a title
        title_label = ttk.Label(
            main_frame,
            text=self._("Record Payment"),
            font=("TkDefaultFont", 14, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Create form
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill="x")
        
        # Invoice info
        info_frame = ttk.LabelFrame(form_frame, text=self._("Invoice Information"), padding=10)
        info_frame.pack(fill="x", pady=10)
        
        ttk.Label(info_frame, text=self._("Invoice Number:")).grid(row=0, column=0, sticky="w", pady=2)
        ttk.Label(info_frame, text=invoice.invoice_number).grid(row=0, column=1, sticky="w", pady=2)
        
        ttk.Label(info_frame, text=self._("Entity:")).grid(row=1, column=0, sticky="w", pady=2)
        ttk.Label(info_frame, text=invoice.entity.name).grid(row=1, column=1, sticky="w", pady=2)
        
        ttk.Label(info_frame, text=self._("Total Amount:")).grid(row=2, column=0, sticky="w", pady=2)
        ttk.Label(info_frame, text=f"{invoice.total_amount:.2f} {invoice.currency}").grid(row=2, column=1, sticky="w", pady=2)
        
        ttk.Label(info_frame, text=self._("Remaining:")).grid(row=3, column=0, sticky="w", pady=2)
        remaining = invoice.calculate_remaining_amount()
        ttk.Label(info_frame, text=f"{remaining:.2f} {invoice.currency}").grid(row=3, column=1, sticky="w", pady=2)
        
        # Payment details
        payment_frame = ttk.LabelFrame(form_frame, text=self._("Payment Details"), padding=10)
        payment_frame.pack(fill="x", pady=10)
        
        # Amount field
        ttk.Label(payment_frame, text=self._("Amount:")).grid(row=0, column=0, sticky="w", pady=5)
        amount_var = ttk.DoubleVar(value=remaining)
        amount_entry = ttk.Entry(payment_frame, textvariable=amount_var, width=15)
        amount_entry.grid(row=0, column=1, sticky="w", pady=5)
        ttk.Label(payment_frame, text=invoice.currency).grid(row=0, column=2, sticky="w", pady=5)
        
        # Payment date field
        ttk.Label(payment_frame, text=self._("Payment Date:")).grid(row=1, column=0, sticky="w", pady=5)
        date_var = ttk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        date_entry = ttk.DateEntry(
            payment_frame,
            dateformat="%Y-%m-%d",
            firstweekday=0,
            width=12,
            textvariable=date_var
        )
        date_entry.grid(row=1, column=1, sticky="w", pady=5)
        
        # Payment method field
        ttk.Label(payment_frame, text=self._("Payment Method:")).grid(row=2, column=0, sticky="w", pady=5)
        method_var = ttk.StringVar(value="cash")
        method_combo = ttk.Combobox(
            payment_frame,
            textvariable=method_var,
            values=["cash", "bank_transfer", "check", "credit_card"],
            width=15
        )
        method_combo.grid(row=2, column=1, sticky="w", pady=5)
        
        # Fund field
        ttk.Label(payment_frame, text=self._("Fund:")).grid(row=3, column=0, sticky="w", pady=5)
        
        # Get all funds for the combobox
        funds = self.fund_controller.get_all_funds()
        fund_choices = [(str(fund.id), f"{fund.name} ({fund.currency})") for fund in funds]
        
        fund_var = ttk.StringVar()
        if fund_choices:
            fund_var.set(str(fund_choices[0][0]))
        
        fund_combo = ttk.Combobox(
            payment_frame,
            textvariable=fund_var,
            values=[f"{f[1]}" for f in fund_choices],
            width=25
        )
        fund_combo.grid(row=3, column=1, columnspan=2, sticky="w", pady=5)
        
        # Notes field
        ttk.Label(payment_frame, text=self._("Notes:")).grid(row=4, column=0, sticky="w", pady=5)
        notes_var = ttk.StringVar()
        notes_entry = ttk.Entry(payment_frame, textvariable=notes_var, width=30)
        notes_entry.grid(row=4, column=1, columnspan=2, sticky="ew", pady=5)
        
        # Error message label
        error_var = ttk.StringVar()
        error_label = ttk.Label(main_frame, textvariable=error_var, bootstyle=DANGER)
        error_label.pack(pady=10, fill="x")
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(
            button_frame,
            text=self._("Cancel"),
            command=payment_dialog.destroy,
            bootstyle=SECONDARY,
            width=10
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text=self._("Record Payment"),
            command=lambda: self.record_payment(
                invoice.id,
                amount_var.get(),
                date_var.get(),
                method_var.get(),
                fund_var.get() if fund_var.get() else None,
                notes_var.get(),
                error_var,
                payment_dialog,
                parent_dialog
            ),
            bootstyle=SUCCESS,
            width=15
        ).pack(side="left", padx=5)
    
    def record_payment(self, invoice_id, amount, payment_date, payment_method, fund_id, notes, 
                      error_var, dialog, parent_dialog=None):
        """Record a payment for an invoice"""
        try:
            # Validate amount
            amount = float(amount)
            if amount <= 0:
                error_var.set(self._("Amount must be greater than zero"))
                return
            
            # Parse payment date
            try:
                payment_date = datetime.strptime(payment_date, "%Y-%m-%d")
            except ValueError:
                error_var.set(self._("Invalid date format"))
                return
            
            # Record payment
            result, message = self.invoice_controller.record_payment(
                invoice_id=invoice_id,
                amount=amount,
                payment_date=payment_date,
                payment_method=payment_method,
                fund_id=int(fund_id) if fund_id else None,
                notes=notes
            )
            
            if result:
                # Success
                show_notification(self._("Success"), self._("Payment recorded successfully"))
                dialog.destroy()
                
                # Refresh data
                self.refresh_invoices_list()
                
                # Refresh parent dialog if it exists
                if parent_dialog:
                    parent_dialog.destroy()
                    # Get invoice again with updated data
                    invoice = self.invoice_controller.get_invoice_by_id(invoice_id)
                    if invoice:
                        self.view_invoice_details()
            else:
                # Error
                error_var.set(message)
        
        except (ValueError, TypeError):
            error_var.set(self._("Please enter valid values"))
    
    def record_payment_for_selected(self):
        """Record payment for the selected invoice"""
        selected_items = self.invoices_tree.selection()
        if not selected_items:
            return
            
        item_id = selected_items[0]
        invoice_id = self.invoices_tree.item(item_id, "values")[0]
        
        # Get invoice
        invoice = self.invoice_controller.get_invoice_by_id(invoice_id)
        if not invoice:
            return
        
        # Check if invoice can be paid
        if invoice.status == "paid" or invoice.status == "cancelled":
            show_notification(self._("Error"), self._("This invoice cannot receive payments"))
            return
        
        # Show payment dialog
        self.show_payment_dialog(invoice)
    
    def confirm_cancel_invoice(self, invoice_id, parent_dialog=None):
        """Confirm and cancel an invoice"""
        # Ask for confirmation
        confirm = ttk.Messagebox.yesno(
            title=self._("Confirm Cancellation"),
            message=self._("Are you sure you want to cancel this invoice? This will reverse all stock changes.")
        )
        
        if confirm == "No":
            return
        
        # Cancel invoice
        result, message = self.invoice_controller.cancel_invoice(invoice_id)
        
        if result:
            show_notification(self._("Success"), self._("Invoice cancelled successfully"))
            
            # Close parent dialog if it exists
            if parent_dialog:
                parent_dialog.destroy()
            
            # Refresh invoices list
            self.refresh_invoices_list()
        else:
            ttk.Messagebox.show_error(
                title=self._("Error"),
                message=message
            )
    
    def cancel_invoice(self):
        """Cancel the selected invoice"""
        selected_items = self.invoices_tree.selection()
        if not selected_items:
            return
            
        item_id = selected_items[0]
        invoice_id = self.invoices_tree.item(item_id, "values")[0]
        
        self.confirm_cancel_invoice(invoice_id)
    
    def create_new_purchase_invoice_tab(self):
        """Create the new purchase invoice tab"""
        self.create_invoice_tab("purchase")
    
    def create_new_sales_invoice_tab(self):
        """Create the new sales invoice tab"""
        self.create_invoice_tab("sale")
    
    def create_invoice_tab(self, invoice_type):
        """Create a tab for a new invoice
        
        Args:
            invoice_type: Either 'purchase' or 'sale'
        """
        # Tab title and internal variable naming based on type
        if invoice_type == "purchase":
            tab_title = self._("New Purchase Invoice")
            entity_label = self._("Supplier")
            entity_type = "supplier"
            self.purchase_items = []  # List to store items for purchase invoice
        else:
            tab_title = self._("New Sales Invoice")
            entity_label = self._("Customer")
            entity_type = "customer"
            self.sales_items = []  # List to store items for sales invoice
        
        # Create the tab
        tab = ttk.Frame(self.notebook, padding=10)
        
        # Create main form
        form_frame = ttk.Frame(tab)
        form_frame.pack(fill="both", expand=True)
        
        # Add a title
        title_label = ttk.Label(
            form_frame,
            text=tab_title,
            font=("TkDefaultFont", 14, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Create two column layout
        columns_frame = ttk.Frame(form_frame)
        columns_frame.pack(fill="both", expand=True)
        
        # Left column - entity and settings
        left_frame = ttk.Frame(columns_frame)
        left_frame.pack(side="left", fill="y", padx=(0, 10))
        
        # Entity selection
        entity_frame = ttk.LabelFrame(left_frame, text=entity_label, padding=10)
        entity_frame.pack(fill="x", pady=10)
        
        # Get entities for the combobox
        entities = self.supplier_customer_controller.get_all_entities(entity_type=entity_type)
        entity_choices = [(e.id, e.name) for e in entities]
        
        if invoice_type == "purchase":
            self.purchase_entity_var = ttk.StringVar()
            if entity_choices:
                self.purchase_entity_var.set(str(entity_choices[0][0]))
            
            entity_combo = ttk.Combobox(
                entity_frame,
                textvariable=self.purchase_entity_var,
                values=[f"{e[1]}" for e in entity_choices],
                width=30
            )
        else:
            self.sales_entity_var = ttk.StringVar()
            if entity_choices:
                self.sales_entity_var.set(str(entity_choices[0][0]))
            
            entity_combo = ttk.Combobox(
                entity_frame,
                textvariable=self.sales_entity_var,
                values=[f"{e[1]}" for e in entity_choices],
                width=30
            )
        
        entity_combo.pack(fill="x", pady=5)
        
        # Invoice settings
        settings_frame = ttk.LabelFrame(left_frame, text=self._("Invoice Settings"), padding=10)
        settings_frame.pack(fill="x", pady=10)
        
        # Date field
        ttk.Label(settings_frame, text=self._("Date:")).grid(row=0, column=0, sticky="w", pady=5)
        if invoice_type == "purchase":
            self.purchase_date_var = ttk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
            date_entry = ttk.DateEntry(
                settings_frame,
                dateformat="%Y-%m-%d",
                firstweekday=0,
                width=12,
                textvariable=self.purchase_date_var
            )
        else:
            self.sales_date_var = ttk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
            date_entry = ttk.DateEntry(
                settings_frame,
                dateformat="%Y-%m-%d",
                firstweekday=0,
                width=12,
                textvariable=self.sales_date_var
            )
        date_entry.grid(row=0, column=1, sticky="w", pady=5)
        
        # Due date field
        ttk.Label(settings_frame, text=self._("Due Date:")).grid(row=1, column=0, sticky="w", pady=5)
        if invoice_type == "purchase":
            self.purchase_due_date_var = ttk.StringVar()
            due_date_entry = ttk.DateEntry(
                settings_frame,
                dateformat="%Y-%m-%d",
                firstweekday=0,
                width=12,
                textvariable=self.purchase_due_date_var
            )
        else:
            self.sales_due_date_var = ttk.StringVar()
            due_date_entry = ttk.DateEntry(
                settings_frame,
                dateformat="%Y-%m-%d",
                firstweekday=0,
                width=12,
                textvariable=self.sales_due_date_var
            )
        due_date_entry.grid(row=1, column=1, sticky="w", pady=5)
        ttk.Label(
            settings_frame,
            text=self._("(Optional)"),
            font=("TkDefaultFont", 9, "italic")
        ).grid(row=1, column=2, sticky="w", pady=5)
        
        # Currency field
        ttk.Label(settings_frame, text=self._("Currency:")).grid(row=2, column=0, sticky="w", pady=5)
        if invoice_type == "purchase":
            self.purchase_currency_var = ttk.StringVar(value="USD")
            currency_combo = ttk.Combobox(
                settings_frame,
                textvariable=self.purchase_currency_var,
                values=["USD", "SYP", "EUR"],
                width=10
            )
        else:
            self.sales_currency_var = ttk.StringVar(value="USD")
            currency_combo = ttk.Combobox(
                settings_frame,
                textvariable=self.sales_currency_var,
                values=["USD", "SYP", "EUR"],
                width=10
            )
        currency_combo.grid(row=2, column=1, sticky="w", pady=5)
        
        # Exchange rate field
        ttk.Label(settings_frame, text=self._("Exchange Rate:")).grid(row=3, column=0, sticky="w", pady=5)
        if invoice_type == "purchase":
            self.purchase_exchange_rate_var = ttk.DoubleVar(value=1.0)
            exchange_entry = ttk.Entry(
                settings_frame,
                textvariable=self.purchase_exchange_rate_var,
                width=10
            )
        else:
            self.sales_exchange_rate_var = ttk.DoubleVar(value=1.0)
            exchange_entry = ttk.Entry(
                settings_frame,
                textvariable=self.sales_exchange_rate_var,
                width=10
            )
        exchange_entry.grid(row=3, column=1, sticky="w", pady=5)
        
        # Warehouse selection
        ttk.Label(settings_frame, text=self._("Warehouse:")).grid(row=4, column=0, sticky="w", pady=5)
        
        # Get warehouses for combobox
        warehouses = self.warehouse_controller.get_all_warehouses()
        warehouse_choices = [(w.id, w.name) for w in warehouses]
        
        if invoice_type == "purchase":
            self.purchase_warehouse_var = ttk.StringVar()
            if warehouse_choices:
                self.purchase_warehouse_var.set(str(warehouse_choices[0][0]))
            
            warehouse_combo = ttk.Combobox(
                settings_frame,
                textvariable=self.purchase_warehouse_var,
                values=[f"{w[1]}" for w in warehouse_choices],
                width=20
            )
        else:
            self.sales_warehouse_var = ttk.StringVar()
            if warehouse_choices:
                self.sales_warehouse_var.set(str(warehouse_choices[0][0]))
            
            warehouse_combo = ttk.Combobox(
                settings_frame,
                textvariable=self.sales_warehouse_var,
                values=[f"{w[1]}" for w in warehouse_choices],
                width=20
            )
        warehouse_combo.grid(row=4, column=1, columnspan=2, sticky="w", pady=5)
        
        # Additional costs field
        ttk.Label(settings_frame, text=self._("Additional Costs:")).grid(row=5, column=0, sticky="w", pady=5)
        if invoice_type == "purchase":
            self.purchase_additional_costs_var = ttk.DoubleVar(value=0.0)
            additional_costs_entry = ttk.Entry(
                settings_frame,
                textvariable=self.purchase_additional_costs_var,
                width=10
            )
        else:
            self.sales_additional_costs_var = ttk.DoubleVar(value=0.0)
            additional_costs_entry = ttk.Entry(
                settings_frame,
                textvariable=self.sales_additional_costs_var,
                width=10
            )
        additional_costs_entry.grid(row=5, column=1, sticky="w", pady=5)
        
        # Tax field
        ttk.Label(settings_frame, text=self._("Tax:")).grid(row=6, column=0, sticky="w", pady=5)
        if invoice_type == "purchase":
            self.purchase_tax_var = ttk.DoubleVar(value=0.0)
            tax_entry = ttk.Entry(
                settings_frame,
                textvariable=self.purchase_tax_var,
                width=10
            )
        else:
            self.sales_tax_var = ttk.DoubleVar(value=0.0)
            tax_entry = ttk.Entry(
                settings_frame,
                textvariable=self.sales_tax_var,
                width=10
            )
        tax_entry.grid(row=6, column=1, sticky="w", pady=5)
        
        # Notes field
        ttk.Label(settings_frame, text=self._("Notes:")).grid(row=7, column=0, sticky="w", pady=5)
        if invoice_type == "purchase":
            self.purchase_notes_var = ttk.StringVar()
            notes_entry = ttk.Entry(
                settings_frame,
                textvariable=self.purchase_notes_var,
                width=30
            )
        else:
            self.sales_notes_var = ttk.StringVar()
            notes_entry = ttk.Entry(
                settings_frame,
                textvariable=self.sales_notes_var,
                width=30
            )
        notes_entry.grid(row=7, column=1, columnspan=2, sticky="ew", pady=5)
        
        # Right column - items
        right_frame = ttk.Frame(columns_frame)
        right_frame.pack(side="left", fill="both", expand=True)
        
        # Items frame
        items_frame = ttk.LabelFrame(right_frame, text=self._("Invoice Items"), padding=10)
        items_frame.pack(fill="both", expand=True)
        
        # Add item section
        add_item_frame = ttk.Frame(items_frame)
        add_item_frame.pack(fill="x", pady=(0, 10))
        
        # Item selection
        ttk.Label(add_item_frame, text=self._("Item:")).grid(row=0, column=0, sticky="w", pady=5)
        
        # Get all items for combobox
        items = self.item_controller.get_all_items()
        item_choices = [(item.id, f"{item.name}") for item in items]
        
        if invoice_type == "purchase":
            self.purchase_item_var = ttk.StringVar()
            if item_choices:
                self.purchase_item_var.set(str(item_choices[0][0]))
            
            # Create a dictionary for quick lookup
            self.purchase_items_dict = {str(item.id): item for item in items}
            
            item_combo = ttk.Combobox(
                add_item_frame,
                textvariable=self.purchase_item_var,
                values=[f"{i[1]}" for i in item_choices],
                width=30
            )
            item_combo.grid(row=0, column=1, columnspan=2, sticky="ew", pady=5)
            
            # Update unit options when item changes
            item_combo.bind("<<ComboboxSelected>>", 
                            lambda e: self.update_unit_options(self.purchase_item_var.get(),
                                                             self.purchase_unit_var,
                                                             self.purchase_main_unit_radio,
                                                             self.purchase_sub_unit_radio))
        else:
            self.sales_item_var = ttk.StringVar()
            if item_choices:
                self.sales_item_var.set(str(item_choices[0][0]))
            
            # Create a dictionary for quick lookup
            self.sales_items_dict = {str(item.id): item for item in items}
            
            item_combo = ttk.Combobox(
                add_item_frame,
                textvariable=self.sales_item_var,
                values=[f"{i[1]}" for i in item_choices],
                width=30
            )
            item_combo.grid(row=0, column=1, columnspan=2, sticky="ew", pady=5)
            
            # Update unit options when item changes
            item_combo.bind("<<ComboboxSelected>>", 
                            lambda e: self.update_unit_options(self.sales_item_var.get(),
                                                             self.sales_unit_var,
                                                             self.sales_main_unit_radio,
                                                             self.sales_sub_unit_radio))
        
        # Quantity field
        ttk.Label(add_item_frame, text=self._("Quantity:")).grid(row=1, column=0, sticky="w", pady=5)
        if invoice_type == "purchase":
            self.purchase_quantity_var = ttk.DoubleVar(value=1.0)
            quantity_entry = ttk.Entry(
                add_item_frame,
                textvariable=self.purchase_quantity_var,
                width=10
            )
        else:
            self.sales_quantity_var = ttk.DoubleVar(value=1.0)
            quantity_entry = ttk.Entry(
                add_item_frame,
                textvariable=self.sales_quantity_var,
                width=10
            )
        quantity_entry.grid(row=1, column=1, sticky="w", pady=5)
        
        # Unit selection
        if invoice_type == "purchase":
            self.purchase_unit_var = ttk.StringVar(value="main")
            unit_frame = ttk.Frame(add_item_frame)
            unit_frame.grid(row=1, column=2, sticky="w", pady=5)
            
            # Default to first item's units if available
            main_unit_text = ""
            sub_unit_text = ""
            if items:
                main_unit_text = items[0].main_unit
                sub_unit_text = items[0].sub_unit
            
            self.purchase_main_unit_radio = ttk.Radiobutton(
                unit_frame,
                text=main_unit_text,
                variable=self.purchase_unit_var,
                value="main"
            )
            self.purchase_main_unit_radio.pack(side="left", padx=5)
            
            self.purchase_sub_unit_radio = ttk.Radiobutton(
                unit_frame,
                text=sub_unit_text,
                variable=self.purchase_unit_var,
                value="sub"
            )
            self.purchase_sub_unit_radio.pack(side="left", padx=5)
        else:
            self.sales_unit_var = ttk.StringVar(value="main")
            unit_frame = ttk.Frame(add_item_frame)
            unit_frame.grid(row=1, column=2, sticky="w", pady=5)
            
            # Default to first item's units if available
            main_unit_text = ""
            sub_unit_text = ""
            if items:
                main_unit_text = items[0].main_unit
                sub_unit_text = items[0].sub_unit
            
            self.sales_main_unit_radio = ttk.Radiobutton(
                unit_frame,
                text=main_unit_text,
                variable=self.sales_unit_var,
                value="main"
            )
            self.sales_main_unit_radio.pack(side="left", padx=5)
            
            self.sales_sub_unit_radio = ttk.Radiobutton(
                unit_frame,
                text=sub_unit_text,
                variable=self.sales_unit_var,
                value="sub"
            )
            self.sales_sub_unit_radio.pack(side="left", padx=5)
        
        # Price field
        ttk.Label(add_item_frame, text=self._("Price per Unit:")).grid(row=2, column=0, sticky="w", pady=5)
        if invoice_type == "purchase":
            self.purchase_price_var = ttk.DoubleVar(value=0.0)
            price_entry = ttk.Entry(
                add_item_frame,
                textvariable=self.purchase_price_var,
                width=10
            )
        else:
            self.sales_price_var = ttk.DoubleVar(value=0.0)
            price_entry = ttk.Entry(
                add_item_frame,
                textvariable=self.sales_price_var,
                width=10
            )
        price_entry.grid(row=2, column=1, sticky="w", pady=5)
        
        # Auto-fill price button
        if invoice_type == "purchase":
            autofill_button = ttk.Button(
                add_item_frame,
                text=self._("Use Purchase Price"),
                command=lambda: self.autofill_price("purchase"),
                bootstyle=INFO,
                width=15
            )
        else:
            autofill_button = ttk.Button(
                add_item_frame,
                text=self._("Use Selling Price"),
                command=lambda: self.autofill_price("sale"),
                bootstyle=INFO,
                width=15
            )
        autofill_button.grid(row=2, column=2, sticky="w", pady=5, padx=5)
        
        # Add item button
        if invoice_type == "purchase":
            add_button = ttk.Button(
                add_item_frame,
                text=self._("Add Item"),
                command=lambda: self.add_item_to_invoice("purchase"),
                bootstyle=SUCCESS,
                width=15
            )
        else:
            add_button = ttk.Button(
                add_item_frame,
                text=self._("Add Item"),
                command=lambda: self.add_item_to_invoice("sale"),
                bootstyle=SUCCESS,
                width=15
            )
        add_button.grid(row=3, column=1, columnspan=2, pady=10)
        
        # Items list
        list_frame = ttk.Frame(items_frame)
        list_frame.pack(fill="both", expand=True)
        
        # Create treeview for items
        columns = ("id", "name", "quantity", "unit", "price", "total")
        
        if invoice_type == "purchase":
            self.purchase_items_tree = ttk.Treeview(
                list_frame,
                columns=columns,
                show="headings",
                bootstyle=INFO
            )
            items_tree = self.purchase_items_tree
        else:
            self.sales_items_tree = ttk.Treeview(
                list_frame,
                columns=columns,
                show="headings",
                bootstyle=INFO
            )
            items_tree = self.sales_items_tree
        
        # Define column headings
        items_tree.heading("id", text=self._("ID"))
        items_tree.heading("name", text=self._("Item"))
        items_tree.heading("quantity", text=self._("Quantity"))
        items_tree.heading("unit", text=self._("Unit"))
        items_tree.heading("price", text=self._("Price"))
        items_tree.heading("total", text=self._("Total"))
        
        # Define column widths
        items_tree.column("id", width=50, stretch=False)
        items_tree.column("name", width=200)
        items_tree.column("quantity", width=80, stretch=False)
        items_tree.column("unit", width=80, stretch=False)
        items_tree.column("price", width=100, stretch=False)
        items_tree.column("total", width=100, stretch=False)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=items_tree.yview)
        items_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        items_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add context menu to remove items
        item_context_menu = ttk.Menu(items_tree, tearoff=0)
        item_context_menu.add_command(
            label=self._("Remove Item"),
            command=lambda: self.remove_item_from_invoice(invoice_type)
        )
        
        # Bind right-click to show context menu
        items_tree.bind("<Button-3>", lambda e: self.show_item_context_menu(e, item_context_menu))
        
        # Update total when items change
        if invoice_type == "purchase":
            self.update_purchase_total()
        else:
            self.update_sales_total()
        
        # Summary frame
        summary_frame = ttk.Frame(form_frame)
        summary_frame.pack(fill="x", pady=10)
        
        # Create a border around summary
        summary_border = ttk.LabelFrame(summary_frame, text=self._("Invoice Summary"), padding=10)
        summary_border.pack(fill="x")
        
        # Total display
        if invoice_type == "purchase":
            self.purchase_total_label = ttk.Label(
                summary_border,
                text=self._("Total: 0.00"),
                font=("TkDefaultFont", 12, "bold")
            )
            self.purchase_total_label.pack(side="left", padx=20)
        else:
            self.sales_total_label = ttk.Label(
                summary_border,
                text=self._("Total: 0.00"),
                font=("TkDefaultFont", 12, "bold")
            )
            self.sales_total_label.pack(side="left", padx=20)
        
        # Item count display
        if invoice_type == "purchase":
            self.purchase_count_label = ttk.Label(
                summary_border,
                text=self._("Items: 0")
            )
            self.purchase_count_label.pack(side="left", padx=20)
        else:
            self.sales_count_label = ttk.Label(
                summary_border,
                text=self._("Items: 0")
            )
            self.sales_count_label.pack(side="left", padx=20)
        
        # Error message label
        if invoice_type == "purchase":
            self.purchase_error_var = ttk.StringVar()
            error_label = ttk.Label(
                form_frame,
                textvariable=self.purchase_error_var,
                bootstyle=DANGER
            )
        else:
            self.sales_error_var = ttk.StringVar()
            error_label = ttk.Label(
                form_frame,
                textvariable=self.sales_error_var,
                bootstyle=DANGER
            )
        error_label.pack(pady=10, fill="x")
        
        # Submit button
        if invoice_type == "purchase":
            submit_button = ttk.Button(
                form_frame,
                text=self._("Create Purchase Invoice"),
                command=lambda: self.create_invoice("purchase"),
                bootstyle=SUCCESS,
                width=25
            )
        else:
            submit_button = ttk.Button(
                form_frame,
                text=self._("Create Sales Invoice"),
                command=lambda: self.create_invoice("sale"),
                bootstyle=SUCCESS,
                width=25
            )
        submit_button.pack(pady=10)
        
        # Update unit options initially
        if items:
            if invoice_type == "purchase":
                self.update_unit_options(
                    self.purchase_item_var.get(),
                    self.purchase_unit_var,
                    self.purchase_main_unit_radio,
                    self.purchase_sub_unit_radio
                )
            else:
                self.update_unit_options(
                    self.sales_item_var.get(),
                    self.sales_unit_var,
                    self.sales_main_unit_radio,
                    self.sales_sub_unit_radio
                )
        
        # Add tab to notebook
        tab_text = self._("New Purchase") if invoice_type == "purchase" else self._("New Sale")
        self.notebook.add(tab, text=tab_text)
    
    def update_unit_options(self, item_id, unit_var, main_unit_radio, sub_unit_radio):
        """Update the unit options based on the selected item"""
        # Get the items dictionary based on current tab
        current_tab = self.notebook.index(self.notebook.select())
        if current_tab == 1:  # Purchase invoice tab
            items_dict = self.purchase_items_dict
        else:  # Sales invoice tab
            items_dict = self.sales_items_dict
        
        # Get the item
        item = items_dict.get(item_id)
        if item:
            # Update radio button text
            main_unit_radio.config(text=item.main_unit)
            sub_unit_radio.config(text=item.sub_unit)
    
    def autofill_price(self, invoice_type):
        """Auto-fill price based on selected item"""
        if invoice_type == "purchase":
            item_id = self.purchase_item_var.get()
            item = self.purchase_items_dict.get(item_id)
            if item:
                self.purchase_price_var.set(item.purchase_price)
        else:
            item_id = self.sales_item_var.get()
            item = self.sales_items_dict.get(item_id)
            if item:
                self.sales_price_var.set(item.selling_price)
    
    def add_item_to_invoice(self, invoice_type):
        """Add an item to the invoice"""
        try:
            if invoice_type == "purchase":
                item_id = self.purchase_item_var.get()
                item = self.purchase_items_dict.get(item_id)
                if not item:
                    self.purchase_error_var.set(self._("Please select a valid item"))
                    return
                
                quantity = float(self.purchase_quantity_var.get())
                unit = "main" if self.purchase_unit_var.get() == "main" else "sub"
                price = float(self.purchase_price_var.get())
                
                if quantity <= 0:
                    self.purchase_error_var.set(self._("Quantity must be greater than zero"))
                    return
                
                if price < 0:
                    self.purchase_error_var.set(self._("Price cannot be negative"))
                    return
                
                # Calculate total
                total = quantity * price
                
                # Add to list
                unit_display = item.main_unit if unit == "main" else item.sub_unit
                self.purchase_items.append({
                    "item_id": item.id,
                    "name": item.name,
                    "quantity": quantity,
                    "unit": unit_display,
                    "price_per_unit": price,
                    "total_price": total,
                    "original_unit": unit  # Store the original unit for API
                })
                
                # Update treeview
                self.purchase_items_tree.insert(
                    "",
                    "end",
                    values=(
                        item.id,
                        item.name,
                        f"{quantity:.2f}",
                        unit_display,
                        f"{price:.2f}",
                        f"{total:.2f}"
                    )
                )
                
                # Reset fields
                self.purchase_quantity_var.set(1.0)
                self.purchase_price_var.set(0.0)
                
                # Clear any error
                self.purchase_error_var.set("")
                
                # Update total
                self.update_purchase_total()
            
            else:  # Sales invoice
                item_id = self.sales_item_var.get()
                item = self.sales_items_dict.get(item_id)
                if not item:
                    self.sales_error_var.set(self._("Please select a valid item"))
                    return
                
                quantity = float(self.sales_quantity_var.get())
                unit = "main" if self.sales_unit_var.get() == "main" else "sub"
                price = float(self.sales_price_var.get())
                
                if quantity <= 0:
                    self.sales_error_var.set(self._("Quantity must be greater than zero"))
                    return
                
                if price < 0:
                    self.sales_error_var.set(self._("Price cannot be negative"))
                    return
                
                # Check inventory if it's a sales invoice
                if unit == "main":
                    stock_needed = quantity
                else:
                    stock_needed = quantity / item.conversion_rate
                
                warehouse_id = int(self.sales_warehouse_var.get())
                stock = self.item_controller.get_item_stock(item.id, warehouse_id)
                if stock and stock.quantity < stock_needed:
                    self.sales_error_var.set(
                        self._("Insufficient stock. Available: {0} {1}").format(
                            stock.quantity, item.main_unit
                        )
                    )
                    return
                
                # Calculate total
                total = quantity * price
                
                # Add to list
                unit_display = item.main_unit if unit == "main" else item.sub_unit
                self.sales_items.append({
                    "item_id": item.id,
                    "name": item.name,
                    "quantity": quantity,
                    "unit": unit_display,
                    "price_per_unit": price,
                    "total_price": total,
                    "original_unit": unit  # Store the original unit for API
                })
                
                # Update treeview
                self.sales_items_tree.insert(
                    "",
                    "end",
                    values=(
                        item.id,
                        item.name,
                        f"{quantity:.2f}",
                        unit_display,
                        f"{price:.2f}",
                        f"{total:.2f}"
                    )
                )
                
                # Reset fields
                self.sales_quantity_var.set(1.0)
                self.sales_price_var.set(0.0)
                
                # Clear any error
                self.sales_error_var.set("")
                
                # Update total
                self.update_sales_total()
        
        except (ValueError, TypeError):
            if invoice_type == "purchase":
                self.purchase_error_var.set(self._("Please enter valid numeric values"))
            else:
                self.sales_error_var.set(self._("Please enter valid numeric values"))
    
    def show_item_context_menu(self, event, menu):
        """Show context menu for removing items"""
        # Select row under mouse
        tree = event.widget
        iid = tree.identify_row(event.y)
        if iid:
            # Select this item
            tree.selection_set(iid)
            # Display context menu
            menu.tk_popup(event.x_root, event.y_root)
    
    def remove_item_from_invoice(self, invoice_type):
        """Remove the selected item from the invoice"""
        if invoice_type == "purchase":
            selected_items = self.purchase_items_tree.selection()
            if not selected_items:
                return
                
            # Get the index of the selected item
            index = self.purchase_items_tree.index(selected_items[0])
            
            # Remove from list and treeview
            if 0 <= index < len(self.purchase_items):
                self.purchase_items.pop(index)
                self.purchase_items_tree.delete(selected_items[0])
                
                # Update total
                self.update_purchase_total()
        
        else:  # Sales invoice
            selected_items = self.sales_items_tree.selection()
            if not selected_items:
                return
                
            # Get the index of the selected item
            index = self.sales_items_tree.index(selected_items[0])
            
            # Remove from list and treeview
            if 0 <= index < len(self.sales_items):
                self.sales_items.pop(index)
                self.sales_items_tree.delete(selected_items[0])
                
                # Update total
                self.update_sales_total()
    
    def update_purchase_total(self):
        """Update the purchase invoice total"""
        total = sum(item["total_price"] for item in self.purchase_items)
        
        try:
            # Add additional costs and tax
            additional_costs = float(self.purchase_additional_costs_var.get())
            tax = float(self.purchase_tax_var.get())
            total += additional_costs + tax
        except (ValueError, TypeError):
            pass
        
        # Update labels
        self.purchase_total_label.config(
            text=self._("Total: {0:.2f}").format(total)
        )
        
        self.purchase_count_label.config(
            text=self._("Items: {0}").format(len(self.purchase_items))
        )
    
    def update_sales_total(self):
        """Update the sales invoice total"""
        total = sum(item["total_price"] for item in self.sales_items)
        
        try:
            # Add additional costs and tax
            additional_costs = float(self.sales_additional_costs_var.get())
            tax = float(self.sales_tax_var.get())
            total += additional_costs + tax
        except (ValueError, TypeError):
            pass
        
        # Update labels
        self.sales_total_label.config(
            text=self._("Total: {0:.2f}").format(total)
        )
        
        self.sales_count_label.config(
            text=self._("Items: {0}").format(len(self.sales_items))
        )
    
    def create_invoice(self, invoice_type):
        """Create a new invoice"""
        try:
            if invoice_type == "purchase":
                # Check if there are items
                if not self.purchase_items:
                    self.purchase_error_var.set(self._("Please add at least one item to the invoice"))
                    return
                
                # Get form values
                entity_id = int(self.purchase_entity_var.get())
                warehouse_id = int(self.purchase_warehouse_var.get())
                
                # Process dates
                try:
                    invoice_date = datetime.strptime(self.purchase_date_var.get(), "%Y-%m-%d")
                except ValueError:
                    self.purchase_error_var.set(self._("Invalid invoice date format"))
                    return
                
                due_date = None
                if self.purchase_due_date_var.get():
                    try:
                        due_date = datetime.strptime(self.purchase_due_date_var.get(), "%Y-%m-%d")
                    except ValueError:
                        self.purchase_error_var.set(self._("Invalid due date format"))
                        return
                
                # Get other values
                currency = self.purchase_currency_var.get()
                exchange_rate = float(self.purchase_exchange_rate_var.get())
                additional_costs = float(self.purchase_additional_costs_var.get())
                tax = float(self.purchase_tax_var.get())
                notes = self.purchase_notes_var.get()
                
                # Format items for API
                items_data = []
                for item in self.purchase_items:
                    items_data.append({
                        "item_id": item["item_id"],
                        "quantity": item["quantity"],
                        "unit": item["original_unit"],
                        "price_per_unit": item["price_per_unit"]
                    })
                
                # Create invoice
                result, message = self.invoice_controller.create_invoice(
                    invoice_type="purchase",
                    entity_id=entity_id,
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
                
                if result:
                    # Success
                    show_notification(self._("Success"), self._("Purchase invoice created successfully"))
                    
                    # Reset form
                    self.purchase_items = []
                    for item in self.purchase_items_tree.get_children():
                        self.purchase_items_tree.delete(item)
                    
                    self.purchase_date_var.set(datetime.now().strftime("%Y-%m-%d"))
                    self.purchase_due_date_var.set("")
                    self.purchase_additional_costs_var.set(0.0)
                    self.purchase_tax_var.set(0.0)
                    self.purchase_notes_var.set("")
                    
                    # Update total
                    self.update_purchase_total()
                    
                    # Clear error
                    self.purchase_error_var.set("")
                    
                    # Refresh invoices list and switch to it
                    self.refresh_invoices_list()
                    self.notebook.select(0)  # Switch to invoices list tab
                else:
                    # Error
                    self.purchase_error_var.set(message)
            
            else:  # Sales invoice
                # Check if there are items
                if not self.sales_items:
                    self.sales_error_var.set(self._("Please add at least one item to the invoice"))
                    return
                
                # Get form values
                entity_id = int(self.sales_entity_var.get())
                warehouse_id = int(self.sales_warehouse_var.get())
                
                # Process dates
                try:
                    invoice_date = datetime.strptime(self.sales_date_var.get(), "%Y-%m-%d")
                except ValueError:
                    self.sales_error_var.set(self._("Invalid invoice date format"))
                    return
                
                due_date = None
                if self.sales_due_date_var.get():
                    try:
                        due_date = datetime.strptime(self.sales_due_date_var.get(), "%Y-%m-%d")
                    except ValueError:
                        self.sales_error_var.set(self._("Invalid due date format"))
                        return
                
                # Get other values
                currency = self.sales_currency_var.get()
                exchange_rate = float(self.sales_exchange_rate_var.get())
                additional_costs = float(self.sales_additional_costs_var.get())
                tax = float(self.sales_tax_var.get())
                notes = self.sales_notes_var.get()
                
                # Format items for API
                items_data = []
                for item in self.sales_items:
                    items_data.append({
                        "item_id": item["item_id"],
                        "quantity": item["quantity"],
                        "unit": item["original_unit"],
                        "price_per_unit": item["price_per_unit"]
                    })
                
                # Create invoice
                result, message = self.invoice_controller.create_invoice(
                    invoice_type="sale",
                    entity_id=entity_id,
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
                
                if result:
                    # Success
                    show_notification(self._("Success"), self._("Sales invoice created successfully"))
                    
                    # Reset form
                    self.sales_items = []
                    for item in self.sales_items_tree.get_children():
                        self.sales_items_tree.delete(item)
                    
                    self.sales_date_var.set(datetime.now().strftime("%Y-%m-%d"))
                    self.sales_due_date_var.set("")
                    self.sales_additional_costs_var.set(0.0)
                    self.sales_tax_var.set(0.0)
                    self.sales_notes_var.set("")
                    
                    # Update total
                    self.update_sales_total()
                    
                    # Clear error
                    self.sales_error_var.set("")
                    
                    # Refresh invoices list and switch to it
                    self.refresh_invoices_list()
                    self.notebook.select(0)  # Switch to invoices list tab
                else:
                    # Error
                    self.sales_error_var.set(message)
        
        except (ValueError, TypeError):
            if invoice_type == "purchase":
                self.purchase_error_var.set(self._("Please enter valid values for all fields"))
            else:
                self.sales_error_var.set(self._("Please enter valid values for all fields"))
    
    def create_payments_tab(self):
        """Create the payments tab for viewing and recording payments"""
        tab = ttk.Frame(self.notebook, padding=10)
        
        # Create filters section
        filters_frame = ttk.LabelFrame(tab, text=self._("Filters"), padding=10)
        filters_frame.pack(fill="x", pady=(0, 10))
        
        # Entity type filter
        filter_row1 = ttk.Frame(filters_frame)
        filter_row1.pack(fill="x", pady=5)
        
        ttk.Label(filter_row1, text=self._("Entity Type:"), width=12).pack(side="left")
        self.payment_entity_type_var = ttk.StringVar(value="all")
        
        ttk.Radiobutton(
            filter_row1,
            text=self._("All"),
            variable=self.payment_entity_type_var,
            value="all"
        ).pack(side="left", padx=5)
        
        ttk.Radiobutton(
            filter_row1,
            text=self._("Suppliers"),
            variable=self.payment_entity_type_var,
            value="supplier"
        ).pack(side="left", padx=5)
        
        ttk.Radiobutton(
            filter_row1,
            text=self._("Customers"),
            variable=self.payment_entity_type_var,
            value="customer"
        ).pack(side="left", padx=5)
        
        # Entity selection
        ttk.Label(filter_row1, text=self._("Entity:"), width=8).pack(side="left", padx=(20, 0))
        
        # Get all entities for combobox
        suppliers = self.supplier_customer_controller.get_suppliers()
        customers = self.supplier_customer_controller.get_customers()
        
        all_entities = []
        all_entities.extend(suppliers)
        all_entities.extend([c for c in customers if c not in all_entities])
        
        entity_choices = [("all", self._("All Entities"))]
        entity_choices.extend([(str(e.id), e.name) for e in all_entities])
        
        self.payment_entity_var = ttk.StringVar(value="all")
        
        entity_combo = ttk.Combobox(
            filter_row1,
            textvariable=self.payment_entity_var,
            values=[f"{e[1]}" for e in entity_choices],
            width=30
        )
        entity_combo.current(0)
        entity_combo.pack(side="left", padx=5)
        
        # Date filters
        filter_row2 = ttk.Frame(filters_frame)
        filter_row2.pack(fill="x", pady=5)
        
        ttk.Label(filter_row2, text=self._("Date From:"), width=12).pack(side="left")
        self.payment_date_from_var = ttk.StringVar()
        payment_date_from = ttk.DateEntry(
            filter_row2,
            dateformat="%Y-%m-%d",
            firstweekday=0,
            width=12,
            textvariable=self.payment_date_from_var
        )
        payment_date_from.pack(side="left", padx=5)
        
        ttk.Label(filter_row2, text=self._("To:"), width=3).pack(side="left")
        self.payment_date_to_var = ttk.StringVar()
        payment_date_to = ttk.DateEntry(
            filter_row2,
            dateformat="%Y-%m-%d",
            firstweekday=0,
            width=12,
            textvariable=self.payment_date_to_var
        )
        payment_date_to.pack(side="left", padx=5)
        
        # Buttons
        filter_button = ttk.Button(
            filter_row2,
            text=self._("Apply Filters"),
            command=self.refresh_payments_list,
            bootstyle=INFO,
            width=15
        )
        filter_button.pack(side="left", padx=20)
        
        reset_button = ttk.Button(
            filter_row2,
            text=self._("Reset Filters"),
            command=self.reset_payment_filters,
            bootstyle=SECONDARY,
            width=15
        )
        reset_button.pack(side="left", padx=5)
        
        # Create a direct payment button
        direct_payment_button = ttk.Button(
            filter_row2,
            text=self._("Direct Payment"),
            command=self.show_direct_payment_dialog,
            bootstyle=SUCCESS,
            width=15
        )
        direct_payment_button.pack(side="right", padx=5)
        
        # Create treeview for payments list
        columns = (
            "id", "date", "entity", "amount", "method", "invoice", "fund", "notes"
        )
        
        self.payments_tree = ttk.Treeview(
            tab,
            columns=columns,
            show="headings",
            bootstyle=INFO
        )
        
        # Define column headings
        self.payments_tree.heading("id", text=self._("ID"))
        self.payments_tree.heading("date", text=self._("Date"))
        self.payments_tree.heading("entity", text=self._("Entity"))
        self.payments_tree.heading("amount", text=self._("Amount"))
        self.payments_tree.heading("method", text=self._("Method"))
        self.payments_tree.heading("invoice", text=self._("Invoice"))
        self.payments_tree.heading("fund", text=self._("Fund"))
        self.payments_tree.heading("notes", text=self._("Notes"))
        
        # Define column widths
        self.payments_tree.column("id", width=50, stretch=False)
        self.payments_tree.column("date", width=100, stretch=False)
        self.payments_tree.column("entity", width=150)
        self.payments_tree.column("amount", width=100, stretch=False)
        self.payments_tree.column("method", width=100, stretch=False)
        self.payments_tree.column("invoice", width=120)
        self.payments_tree.column("fund", width=120)
        self.payments_tree.column("notes", width=200)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.payments_tree.yview)
        self.payments_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.payments_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Load initial data
        self.refresh_payments_list()
        
        # Add tab to notebook
        self.notebook.add(tab, text=self._("Payments"))
    
    def reset_payment_filters(self):
        """Reset payment filters to default"""
        self.payment_entity_type_var.set("all")
        self.payment_entity_var.set("all")
        self.payment_date_from_var.set("")
        self.payment_date_to_var.set("")
        self.refresh_payments_list()
    
    def refresh_payments_list(self):
        """Refresh the payments list based on filters"""
        # Clear existing items
        for item in self.payments_tree.get_children():
            self.payments_tree.delete(item)
        
        # Get filter values
        entity_type = self.payment_entity_type_var.get()
        if entity_type == "all":
            entity_type = None
        
        entity_id = self.payment_entity_var.get()
        if entity_id == "all":
            entity_id = None
        else:
            try:
                entity_id = int(entity_id)
            except ValueError:
                entity_id = None
        
        # Process date filters
        start_date = None
        if self.payment_date_from_var.get():
            try:
                start_date = datetime.strptime(self.payment_date_from_var.get(), "%Y-%m-%d")
            except ValueError:
                pass
        
        end_date = None
        if self.payment_date_to_var.get():
            try:
                end_date = datetime.strptime(self.payment_date_to_var.get(), "%Y-%m-%d")
                # Set the time to end of day
                end_date = end_date.replace(hour=23, minute=59, second=59)
            except ValueError:
                pass
        
        # Get all entities to filter and for display
        all_entities = self.supplier_customer_controller.get_all_entities()
        entity_dict = {e.id: e for e in all_entities}
        
        # Filter by entity type
        if entity_type:
            all_entities = [e for e in all_entities if e.type == entity_type or e.type == "both"]
        
        # Filter by specific entity
        if entity_id:
            all_entities = [e for e in all_entities if e.id == entity_id]
        
        # Get all payments for these entities
        all_payments = []
        for entity in all_entities:
            payments = self.supplier_customer_controller.get_entity_payments(
                entity_id=entity.id,
                start_date=start_date,
                end_date=end_date
            )
            all_payments.extend(payments)
        
        # Sort by date, newest first
        all_payments.sort(key=lambda p: p.payment_date, reverse=True)
        
        # Get funds and invoices for display
        funds = self.fund_controller.get_all_funds(active_only=False)
        fund_dict = {f.id: f.name for f in funds}
        
        # Add payments to treeview
        for payment in all_payments:
            # Get entity name
            entity_name = entity_dict[payment.entity_id].name if payment.entity_id in entity_dict else str(payment.entity_id)
            
            # Get invoice number if available
            invoice_text = ""
            if payment.invoice_id:
                invoice = self.invoice_controller.get_invoice_by_id(payment.invoice_id)
                if invoice:
                    invoice_text = invoice.invoice_number
            
            # Get fund name if available
            fund_name = fund_dict.get(payment.fund_id, "") if payment.fund_id else ""
            
            self.payments_tree.insert(
                "",
                "end",
                values=(
                    payment.id,
                    payment.payment_date.strftime("%Y-%m-%d"),
                    entity_name,
                    f"{payment.amount:.2f} {payment.currency}",
                    payment.payment_method,
                    invoice_text,
                    fund_name,
                    payment.notes or ""
                )
            )
    
    def show_direct_payment_dialog(self):
        """Show dialog for recording a direct payment (not tied to an invoice)"""
        # Create payment dialog
        payment_dialog = ttk.Toplevel(self.root)
        payment_dialog.title(self._("Record Direct Payment"))
        payment_dialog.geometry("400x500")
        payment_dialog.transient(self.root)
        payment_dialog.grab_set()
        
        # Create main frame
        main_frame = ttk.Frame(payment_dialog, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # Add a title
        title_label = ttk.Label(
            main_frame,
            text=self._("Record Direct Payment"),
            font=("TkDefaultFont", 14, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Create form
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill="x")
        
        # Entity selection
        entity_frame = ttk.LabelFrame(form_frame, text=self._("Entity"), padding=10)
        entity_frame.pack(fill="x", pady=10)
        
        # Entity type
        ttk.Label(entity_frame, text=self._("Entity Type:")).grid(row=0, column=0, sticky="w", pady=5)
        entity_type_var = ttk.StringVar(value="supplier")
        
        ttk.Radiobutton(
            entity_frame,
            text=self._("Supplier"),
            variable=entity_type_var,
            value="supplier",
            command=lambda: self.update_entity_list(entity_type_var.get(), entity_combo)
        ).grid(row=0, column=1, sticky="w", pady=5, padx=5)
        
        ttk.Radiobutton(
            entity_frame,
            text=self._("Customer"),
            variable=entity_type_var,
            value="customer",
            command=lambda: self.update_entity_list(entity_type_var.get(), entity_combo)
        ).grid(row=0, column=2, sticky="w", pady=5, padx=5)
        
        # Entity selection
        ttk.Label(entity_frame, text=self._("Entity:")).grid(row=1, column=0, sticky="w", pady=5)
        
        # Get all suppliers for initial list
        suppliers = self.supplier_customer_controller.get_suppliers()
        entity_choices = [(str(s.id), s.name) for s in suppliers]
        
        entity_var = ttk.StringVar()
        if entity_choices:
            entity_var.set(str(entity_choices[0][0]))
        
        entity_combo = ttk.Combobox(
            entity_frame,
            textvariable=entity_var,
            values=[f"{e[1]}" for e in entity_choices],
            width=30
        )
        entity_combo.grid(row=1, column=1, columnspan=2, sticky="ew", pady=5)
        if entity_choices:
            entity_combo.current(0)
        
        # Payment details
        payment_frame = ttk.LabelFrame(form_frame, text=self._("Payment Details"), padding=10)
        payment_frame.pack(fill="x", pady=10)
        
        # Payment type
        ttk.Label(payment_frame, text=self._("Payment Type:")).grid(row=0, column=0, sticky="w", pady=5)
        payment_type_var = ttk.StringVar(value="receive")
        
        ttk.Radiobutton(
            payment_frame,
            text=self._("Receive Payment"),
            variable=payment_type_var,
            value="receive"
        ).grid(row=0, column=1, sticky="w", pady=5, padx=5)
        
        ttk.Radiobutton(
            payment_frame,
            text=self._("Make Payment"),
            variable=payment_type_var,
            value="make"
        ).grid(row=0, column=2, sticky="w", pady=5, padx=5)
        
        # Amount field
        ttk.Label(payment_frame, text=self._("Amount:")).grid(row=1, column=0, sticky="w", pady=5)
        amount_var = ttk.DoubleVar(value=0.0)
        amount_entry = ttk.Entry(payment_frame, textvariable=amount_var, width=15)
        amount_entry.grid(row=1, column=1, sticky="w", pady=5)
        
        # Payment date field
        ttk.Label(payment_frame, text=self._("Payment Date:")).grid(row=2, column=0, sticky="w", pady=5)
        date_var = ttk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        date_entry = ttk.DateEntry(
            payment_frame,
            dateformat="%Y-%m-%d",
            firstweekday=0,
            width=12,
            textvariable=date_var
        )
        date_entry.grid(row=2, column=1, sticky="w", pady=5)
        
        # Payment method field
        ttk.Label(payment_frame, text=self._("Payment Method:")).grid(row=3, column=0, sticky="w", pady=5)
        method_var = ttk.StringVar(value="cash")
        method_combo = ttk.Combobox(
            payment_frame,
            textvariable=method_var,
            values=["cash", "bank_transfer", "check", "credit_card"],
            width=15
        )
        method_combo.grid(row=3, column=1, sticky="w", pady=5)
        
        # Fund field
        ttk.Label(payment_frame, text=self._("Fund:")).grid(row=4, column=0, sticky="w", pady=5)
        
        # Get all funds for the combobox
        funds = self.fund_controller.get_all_funds()
        fund_choices = [(str(fund.id), f"{fund.name} ({fund.currency})") for fund in funds]
        
        fund_var = ttk.StringVar()
        if fund_choices:
            fund_var.set(str(fund_choices[0][0]))
        
        fund_combo = ttk.Combobox(
            payment_frame,
            textvariable=fund_var,
            values=[f"{f[1]}" for f in fund_choices],
            width=25
        )
        fund_combo.grid(row=4, column=1, columnspan=2, sticky="w", pady=5)
        if fund_choices:
            fund_combo.current(0)
        
        # Notes field
        ttk.Label(payment_frame, text=self._("Notes:")).grid(row=5, column=0, sticky="w", pady=5)
        notes_var = ttk.StringVar()
        notes_entry = ttk.Entry(payment_frame, textvariable=notes_var, width=30)
        notes_entry.grid(row=5, column=1, columnspan=2, sticky="ew", pady=5)
        
        # Error message label
        error_var = ttk.StringVar()
        error_label = ttk.Label(main_frame, textvariable=error_var, bootstyle=DANGER)
        error_label.pack(pady=10, fill="x")
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(
            button_frame,
            text=self._("Cancel"),
            command=payment_dialog.destroy,
            bootstyle=SECONDARY,
            width=10
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text=self._("Record Payment"),
            command=lambda: self.record_direct_payment(
                entity_var.get(),
                amount_var.get(),
                payment_type_var.get(),
                date_var.get(),
                method_var.get(),
                fund_var.get() if fund_var.get() else None,
                notes_var.get(),
                error_var,
                payment_dialog
            ),
            bootstyle=SUCCESS,
            width=15
        ).pack(side="left", padx=5)
    
    def update_entity_list(self, entity_type, combo):
        """Update the entity combobox based on the selected type"""
        if entity_type == "supplier":
            suppliers = self.supplier_customer_controller.get_suppliers()
            entity_choices = [(str(s.id), s.name) for s in suppliers]
        else:
            customers = self.supplier_customer_controller.get_customers()
            entity_choices = [(str(c.id), c.name) for c in customers]
        
        combo['values'] = [e[1] for e in entity_choices]
        if entity_choices:
            combo.current(0)
    
    def record_direct_payment(self, entity_id, amount, payment_type, payment_date, payment_method, 
                             fund_id, notes, error_var, dialog):
        """Record a direct payment"""
        try:
            # Validate inputs
            entity_id = int(entity_id)
            amount = float(amount)
            
            if amount <= 0:
                error_var.set(self._("Amount must be greater than zero"))
                return
            
            # Make amount negative if making a payment
            if payment_type == "make":
                amount = -amount
            
            # Parse payment date
            try:
                payment_date = datetime.strptime(payment_date, "%Y-%m-%d")
            except ValueError:
                error_var.set(self._("Invalid date format"))
                return
            
            # Record payment
            result, message = self.supplier_customer_controller.add_payment(
                entity_id=entity_id,
                amount=amount,
                payment_method=payment_method,
                fund_id=int(fund_id) if fund_id else None,
                payment_date=payment_date,
                notes=notes
            )
            
            if result:
                # Success
                show_notification(self._("Success"), self._("Payment recorded successfully"))
                dialog.destroy()
                
                # Refresh payments list
                self.refresh_payments_list()
            else:
                # Error
                error_var.set(message)
        
        except (ValueError, TypeError):
            error_var.set(self._("Please enter valid values"))
