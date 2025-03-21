#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Suppliers and Customers management view for ASSI Warehouse Management System
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import gettext
from datetime import datetime
from controllers.supplier_customer_controller import SupplierCustomerController
from controllers.fund_controller import FundController
from utils.notifications import show_notification

class SuppliersCustomersView:
    """Suppliers and Customers management view class"""
    
    def __init__(self, root, back_to_main_menu):
        """Initialize the suppliers and customers view
        
        Args:
            root: The root window
            back_to_main_menu: Callback function to return to main menu
        """
        self.root = root
        self.back_to_main_menu = back_to_main_menu
        self.sc_controller = SupplierCustomerController()
        self.fund_controller = FundController()
        
        # Setup translation
        self._ = gettext.gettext
        
        # Set window title
        self.root.title(self._("ASSI WMS - Suppliers & Customers"))
        
        # Create main frame
        self.frame = ttk.Frame(self.root)
        self.frame.pack(expand=True, fill="both")
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Create tabs
        self.create_suppliers_tab()
        self.create_customers_tab()
        self.create_add_entity_tab()
        self.create_balances_tab()
        
        # Add back button
        back_button = ttk.Button(
            self.frame,
            text=self._("Back to Main Menu"),
            command=self.back_to_main_menu,
            bootstyle=SECONDARY,
            width=20
        )
        back_button.pack(pady=10)
    
    def create_suppliers_tab(self):
        """Create the suppliers tab"""
        tab = ttk.Frame(self.notebook, padding=10)
        
        # Add refresh button at the top
        refresh_frame = ttk.Frame(tab)
        refresh_frame.pack(fill="x", pady=(0, 10))
        
        refresh_button = ttk.Button(
            refresh_frame,
            text=self._("Refresh"),
            command=self.refresh_suppliers_list,
            bootstyle=INFO,
            width=15
        )
        refresh_button.pack(side="right")
        
        # Create treeview for suppliers list
        columns = (
            "id", "name", "balance", "currency", "phone", "email", "address"
        )
        
        self.suppliers_tree = ttk.Treeview(
            tab,
            columns=columns,
            show="headings",
            bootstyle=INFO
        )
        
        # Define column headings
        self.suppliers_tree.heading("id", text=self._("ID"))
        self.suppliers_tree.heading("name", text=self._("Supplier Name"))
        self.suppliers_tree.heading("balance", text=self._("Balance"))
        self.suppliers_tree.heading("currency", text=self._("Currency"))
        self.suppliers_tree.heading("phone", text=self._("Phone"))
        self.suppliers_tree.heading("email", text=self._("Email"))
        self.suppliers_tree.heading("address", text=self._("Address"))
        
        # Define column widths
        self.suppliers_tree.column("id", width=50, stretch=False)
        self.suppliers_tree.column("name", width=200)
        self.suppliers_tree.column("balance", width=100, stretch=False)
        self.suppliers_tree.column("currency", width=80, stretch=False)
        self.suppliers_tree.column("phone", width=120)
        self.suppliers_tree.column("email", width=150)
        self.suppliers_tree.column("address", width=200)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.suppliers_tree.yview)
        self.suppliers_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.suppliers_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add context menu
        self.setup_entity_context_menu(self.suppliers_tree, "supplier")
        
        # Load initial data
        self.refresh_suppliers_list()
        
        # Add tab to notebook
        self.notebook.add(tab, text=self._("Suppliers"))
    
    def create_customers_tab(self):
        """Create the customers tab"""
        tab = ttk.Frame(self.notebook, padding=10)
        
        # Add refresh button at the top
        refresh_frame = ttk.Frame(tab)
        refresh_frame.pack(fill="x", pady=(0, 10))
        
        refresh_button = ttk.Button(
            refresh_frame,
            text=self._("Refresh"),
            command=self.refresh_customers_list,
            bootstyle=INFO,
            width=15
        )
        refresh_button.pack(side="right")
        
        # Create treeview for customers list
        columns = (
            "id", "name", "balance", "currency", "phone", "email", "address"
        )
        
        self.customers_tree = ttk.Treeview(
            tab,
            columns=columns,
            show="headings",
            bootstyle=INFO
        )
        
        # Define column headings
        self.customers_tree.heading("id", text=self._("ID"))
        self.customers_tree.heading("name", text=self._("Customer Name"))
        self.customers_tree.heading("balance", text=self._("Balance"))
        self.customers_tree.heading("currency", text=self._("Currency"))
        self.customers_tree.heading("phone", text=self._("Phone"))
        self.customers_tree.heading("email", text=self._("Email"))
        self.customers_tree.heading("address", text=self._("Address"))
        
        # Define column widths
        self.customers_tree.column("id", width=50, stretch=False)
        self.customers_tree.column("name", width=200)
        self.customers_tree.column("balance", width=100, stretch=False)
        self.customers_tree.column("currency", width=80, stretch=False)
        self.customers_tree.column("phone", width=120)
        self.customers_tree.column("email", width=150)
        self.customers_tree.column("address", width=200)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.customers_tree.yview)
        self.customers_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.customers_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add context menu
        self.setup_entity_context_menu(self.customers_tree, "customer")
        
        # Load initial data
        self.refresh_customers_list()
        
        # Add tab to notebook
        self.notebook.add(tab, text=self._("Customers"))
    
    def setup_entity_context_menu(self, tree, entity_type):
        """Setup context menu for suppliers or customers treeview
        
        Args:
            tree: The treeview widget
            entity_type: Either 'supplier' or 'customer'
        """
        context_menu = ttk.Menu(tree, tearoff=0)
        context_menu.add_command(
            label=self._("Edit"),
            command=lambda: self.edit_selected_entity(tree, entity_type)
        )
        context_menu.add_separator()
        context_menu.add_command(
            label=self._("View Payment History"),
            command=lambda: self.view_payment_history(tree)
        )
        context_menu.add_command(
            label=self._("Make Payment") if entity_type == "supplier" else self._("Receive Payment"),
            command=lambda: self.show_payment_dialog(tree, entity_type)
        )
        
        # Bind right-click to show context menu
        tree.bind("<Button-3>", lambda e: self.show_entity_context_menu(e, context_menu))
        # Bind double-click to edit
        tree.bind("<Double-1>", lambda e: self.edit_selected_entity(tree, entity_type))
    
    def show_entity_context_menu(self, event, menu):
        """Show context menu on right-click"""
        # Select row under mouse
        tree = event.widget
        iid = tree.identify_row(event.y)
        if iid:
            # Select this item
            tree.selection_set(iid)
            # Display context menu
            menu.tk_popup(event.x_root, event.y_root)
    
    def refresh_suppliers_list(self):
        """Refresh the suppliers list"""
        # Clear existing items
        for item in self.suppliers_tree.get_children():
            self.suppliers_tree.delete(item)
        
        # Get all suppliers
        suppliers = self.sc_controller.get_suppliers()
        
        # Add suppliers to treeview
        for supplier in suppliers:
            self.suppliers_tree.insert(
                "",
                "end",
                values=(
                    supplier.id,
                    supplier.name,
                    f"{supplier.balance:.2f}",
                    supplier.currency,
                    supplier.phone or "",
                    supplier.email or "",
                    supplier.address or ""
                )
            )
    
    def refresh_customers_list(self):
        """Refresh the customers list"""
        # Clear existing items
        for item in self.customers_tree.get_children():
            self.customers_tree.delete(item)
        
        # Get all customers
        customers = self.sc_controller.get_customers()
        
        # Add customers to treeview
        for customer in customers:
            self.customers_tree.insert(
                "",
                "end",
                values=(
                    customer.id,
                    customer.name,
                    f"{customer.balance:.2f}",
                    customer.currency,
                    customer.phone or "",
                    customer.email or "",
                    customer.address or ""
                )
            )
    
    def edit_selected_entity(self, tree, entity_type):
        """Open dialog to edit the selected supplier or customer
        
        Args:
            tree: The treeview widget
            entity_type: Either 'supplier' or 'customer'
        """
        selected_items = tree.selection()
        if not selected_items:
            return
            
        item_id = selected_items[0]
        entity_id = tree.item(item_id, "values")[0]
        
        # Get entity data
        entity = self.sc_controller.get_entity_by_id(entity_id)
        if not entity:
            return
            
        # Create edit dialog
        edit_dialog = ttk.Toplevel(self.root)
        edit_dialog.title(self._("Edit {0}").format(self._("Supplier") if entity_type == "supplier" else self._("Customer")))
        edit_dialog.geometry("500x400")
        edit_dialog.transient(self.root)
        edit_dialog.grab_set()
        
        # Create form in the dialog
        frame = ttk.Frame(edit_dialog, padding=10)
        frame.pack(fill="both", expand=True)
        
        # Name field
        ttk.Label(frame, text=self._("Name:")).grid(row=0, column=0, sticky="w", pady=5)
        name_var = ttk.StringVar(value=entity.name)
        name_entry = ttk.Entry(frame, textvariable=name_var, width=30)
        name_entry.grid(row=0, column=1, sticky="ew", pady=5)
        
        # Type field
        ttk.Label(frame, text=self._("Type:")).grid(row=1, column=0, sticky="w", pady=5)
        type_var = ttk.StringVar(value=entity.type)
        
        type_frame = ttk.Frame(frame)
        type_frame.grid(row=1, column=1, sticky="w", pady=5)
        
        ttk.Radiobutton(
            type_frame,
            text=self._("Supplier"),
            variable=type_var,
            value="supplier"
        ).pack(side="left", padx=5)
        
        ttk.Radiobutton(
            type_frame,
            text=self._("Customer"),
            variable=type_var,
            value="customer"
        ).pack(side="left", padx=5)
        
        ttk.Radiobutton(
            type_frame,
            text=self._("Both"),
            variable=type_var,
            value="both"
        ).pack(side="left", padx=5)
        
        # Phone field
        ttk.Label(frame, text=self._("Phone:")).grid(row=2, column=0, sticky="w", pady=5)
        phone_var = ttk.StringVar(value=entity.phone or "")
        phone_entry = ttk.Entry(frame, textvariable=phone_var, width=20)
        phone_entry.grid(row=2, column=1, sticky="w", pady=5)
        
        # Email field
        ttk.Label(frame, text=self._("Email:")).grid(row=3, column=0, sticky="w", pady=5)
        email_var = ttk.StringVar(value=entity.email or "")
        email_entry = ttk.Entry(frame, textvariable=email_var, width=30)
        email_entry.grid(row=3, column=1, sticky="ew", pady=5)
        
        # Address field
        ttk.Label(frame, text=self._("Address:")).grid(row=4, column=0, sticky="w", pady=5)
        address_var = ttk.StringVar(value=entity.address or "")
        address_entry = ttk.Entry(frame, textvariable=address_var, width=40)
        address_entry.grid(row=4, column=1, sticky="ew", pady=5)
        
        # Currency field
        ttk.Label(frame, text=self._("Currency:")).grid(row=5, column=0, sticky="w", pady=5)
        currency_var = ttk.StringVar(value=entity.currency)
        currency_combo = ttk.Combobox(
            frame,
            textvariable=currency_var,
            values=["USD", "SYP", "EUR"],
            width=10
        )
        currency_combo.grid(row=5, column=1, sticky="w", pady=5)
        
        # Exchange rate field
        ttk.Label(frame, text=self._("Exchange Rate:")).grid(row=6, column=0, sticky="w", pady=5)
        exchange_rate_var = ttk.DoubleVar(value=entity.exchange_rate)
        exchange_rate_entry = ttk.Entry(frame, textvariable=exchange_rate_var, width=15)
        exchange_rate_entry.grid(row=6, column=1, sticky="w", pady=5)
        
        # Notes field
        ttk.Label(frame, text=self._("Notes:")).grid(row=7, column=0, sticky="w", pady=5)
        notes_var = ttk.StringVar(value=entity.notes or "")
        notes_entry = ttk.Entry(frame, textvariable=notes_var, width=40)
        notes_entry.grid(row=7, column=1, sticky="ew", pady=5)
        
        # Balance display (read-only)
        ttk.Label(frame, text=self._("Current Balance:")).grid(row=8, column=0, sticky="w", pady=5)
        balance_frame = ttk.Frame(frame)
        balance_frame.grid(row=8, column=1, sticky="w", pady=5)
        
        balance_label = ttk.Label(
            balance_frame,
            text=f"{entity.balance:.2f} {entity.currency}",
            font=("TkDefaultFont", 10, "bold")
        )
        balance_label.pack(side="left")
        
        # Add hint about balance
        ttk.Label(
            balance_frame,
            text=self._("(Adjusted with payments)"),
            font=("TkDefaultFont", 9, "italic")
        ).pack(side="left", padx=5)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=9, column=0, columnspan=2, pady=15)
        
        ttk.Button(
            button_frame,
            text=self._("Cancel"),
            command=edit_dialog.destroy,
            bootstyle=SECONDARY,
            width=10
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text=self._("Save"),
            command=lambda: self.save_entity_edits(
                entity.id,
                name_var.get(),
                type_var.get(),
                phone_var.get(),
                email_var.get(),
                address_var.get(),
                currency_var.get(),
                exchange_rate_var.get(),
                notes_var.get(),
                edit_dialog
            ),
            bootstyle=SUCCESS,
            width=10
        ).pack(side="left", padx=5)
    
    def save_entity_edits(self, entity_id, name, entity_type, phone, email, address, 
                          currency, exchange_rate, notes, dialog):
        """Save edits to a supplier or customer"""
        result, message = self.sc_controller.update_entity(
            entity_id=entity_id,
            name=name,
            entity_type=entity_type,
            phone=phone,
            email=email,
            address=address,
            currency=currency,
            exchange_rate=exchange_rate,
            notes=notes
        )
        
        if result:
            show_notification(self._("Success"), self._("Entity updated successfully"))
            dialog.destroy()
            self.refresh_suppliers_list()
            self.refresh_customers_list()
        else:
            # Show error in dialog
            error_label = ttk.Label(dialog, text=message, bootstyle=DANGER)
            error_label.pack(pady=10)
    
    def view_payment_history(self, tree):
        """View payment history for the selected entity"""
        selected_items = tree.selection()
        if not selected_items:
            return
            
        item_id = selected_items[0]
        entity_id = tree.item(item_id, "values")[0]
        entity_name = tree.item(item_id, "values")[1]
        
        # Get entity data
        entity = self.sc_controller.get_entity_by_id(entity_id)
        if not entity:
            return
            
        # Create dialog
        dialog = ttk.Toplevel(self.root)
        dialog.title(self._("Payment History - {0}").format(entity_name))
        dialog.geometry("800x500")
        dialog.transient(self.root)
        
        # Create main frame
        main_frame = ttk.Frame(dialog, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # Entity info at the top
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(
            info_frame,
            text=entity_name,
            font=("TkDefaultFont", 14, "bold")
        ).pack(anchor="w")
        
        ttk.Label(
            info_frame,
            text=self._("Type: {0} | Balance: {1} {2}").format(
                self._("Supplier") if entity.type == "supplier" else 
                self._("Customer") if entity.type == "customer" else 
                self._("Supplier & Customer"),
                entity.balance,
                entity.currency
            )
        ).pack(anchor="w", pady=2)
        
        if entity.phone or entity.email:
            contact_info = []
            if entity.phone:
                contact_info.append(f"Phone: {entity.phone}")
            if entity.email:
                contact_info.append(f"Email: {entity.email}")
            
            ttk.Label(
                info_frame,
                text=" | ".join(contact_info)
            ).pack(anchor="w", pady=2)
        
        # Create treeview for payments
        columns = (
            "id", "date", "amount", "currency", "method", "invoice", "fund", "notes"
        )
        
        payments_tree = ttk.Treeview(
            main_frame,
            columns=columns,
            show="headings",
            bootstyle=INFO
        )
        
        # Define column headings
        payments_tree.heading("id", text=self._("ID"))
        payments_tree.heading("date", text=self._("Date"))
        payments_tree.heading("amount", text=self._("Amount"))
        payments_tree.heading("currency", text=self._("Currency"))
        payments_tree.heading("method", text=self._("Method"))
        payments_tree.heading("invoice", text=self._("Invoice"))
        payments_tree.heading("fund", text=self._("Fund"))
        payments_tree.heading("notes", text=self._("Notes"))
        
        # Define column widths
        payments_tree.column("id", width=50, stretch=False)
        payments_tree.column("date", width=100, stretch=False)
        payments_tree.column("amount", width=100, stretch=False)
        payments_tree.column("currency", width=80, stretch=False)
        payments_tree.column("method", width=100, stretch=False)
        payments_tree.column("invoice", width=120)
        payments_tree.column("fund", width=120)
        payments_tree.column("notes", width=200)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=payments_tree.yview)
        payments_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        payments_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Get payment data
        payments = self.sc_controller.get_entity_payments(entity_id)
        
        # Get funds for display
        funds = self.fund_controller.get_all_funds(active_only=False)
        fund_dict = {f.id: f.name for f in funds}
        
        # Add payments to treeview
        for payment in payments:
            # Get fund name if available
            fund_name = fund_dict.get(payment.fund_id, "") if payment.fund_id else ""
            
            # Get invoice number if available
            invoice_text = f"#{payment.invoice_id}" if payment.invoice_id else ""
            
            payments_tree.insert(
                "",
                "end",
                values=(
                    payment.id,
                    payment.payment_date.strftime("%Y-%m-%d"),
                    f"{payment.amount:.2f}",
                    payment.currency,
                    payment.payment_method,
                    invoice_text,
                    fund_name,
                    payment.notes or ""
                )
            )
        
        # Add close button
        close_button = ttk.Button(
            dialog,
            text=self._("Close"),
            command=dialog.destroy,
            bootstyle=SECONDARY,
            width=15
        )
        close_button.pack(pady=10)
    
    def show_payment_dialog(self, tree, entity_type):
        """Show dialog to record a payment for a supplier or customer
        
        Args:
            tree: The treeview widget
            entity_type: Either 'supplier' or 'customer'
        """
        selected_items = tree.selection()
        if not selected_items:
            return
            
        item_id = selected_items[0]
        entity_id = tree.item(item_id, "values")[0]
        entity_name = tree.item(item_id, "values")[1]
        
        # Get entity data
        entity = self.sc_controller.get_entity_by_id(entity_id)
        if not entity:
            return
            
        # Create payment dialog
        payment_dialog = ttk.Toplevel(self.root)
        payment_dialog.title(self._("{0} Payment - {1}").format(
            self._("Make") if entity_type == "supplier" else self._("Receive"), 
            entity_name
        ))
        payment_dialog.geometry("400x400")
        payment_dialog.transient(self.root)
        payment_dialog.grab_set()
        
        # Create main frame
        main_frame = ttk.Frame(payment_dialog, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # Add a title
        title_label = ttk.Label(
            main_frame,
            text=self._("{0} Payment").format(
                self._("Make") if entity_type == "supplier" else self._("Receive")
            ),
            font=("TkDefaultFont", 14, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Entity info
        info_frame = ttk.LabelFrame(main_frame, text=self._("Entity Information"), padding=10)
        info_frame.pack(fill="x", pady=10)
        
        ttk.Label(info_frame, text=self._("Name:")).grid(row=0, column=0, sticky="w", pady=2)
        ttk.Label(info_frame, text=entity_name).grid(row=0, column=1, sticky="w", pady=2)
        
        ttk.Label(info_frame, text=self._("Type:")).grid(row=1, column=0, sticky="w", pady=2)
        ttk.Label(info_frame, text=self._("Supplier") if entity.type == "supplier" else self._("Customer")).grid(row=1, column=1, sticky="w", pady=2)
        
        ttk.Label(info_frame, text=self._("Balance:")).grid(row=2, column=0, sticky="w", pady=2)
        ttk.Label(info_frame, text=f"{entity.balance:.2f} {entity.currency}").grid(row=2, column=1, sticky="w", pady=2)
        
        # Payment details
        payment_frame = ttk.LabelFrame(main_frame, text=self._("Payment Details"), padding=10)
        payment_frame.pack(fill="x", pady=10)
        
        # Amount field
        ttk.Label(payment_frame, text=self._("Amount:")).grid(row=0, column=0, sticky="w", pady=5)
        amount_var = ttk.DoubleVar(value=abs(entity.balance) if entity.balance != 0 else 0)
        amount_entry = ttk.Entry(payment_frame, textvariable=amount_var, width=15)
        amount_entry.grid(row=0, column=1, sticky="w", pady=5)
        ttk.Label(payment_frame, text=entity.currency).grid(row=0, column=2, sticky="w", pady=5)
        
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
        if fund_choices:
            fund_combo.current(0)
        
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
                entity.id,
                amount_var.get(),
                entity_type,
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
    
    def record_payment(self, entity_id, amount, entity_type, payment_date, payment_method, 
                       fund_id, notes, error_var, dialog):
        """Record a payment for a supplier or customer"""
        try:
            # Validate amount
            amount = float(amount)
            if amount <= 0:
                error_var.set(self._("Amount must be greater than zero"))
                return
            
            # Negate amount for supplier payments (we pay them)
            if entity_type == "supplier":
                amount = -amount
            
            # Parse payment date
            try:
                payment_date = datetime.strptime(payment_date, "%Y-%m-%d")
            except ValueError:
                error_var.set(self._("Invalid date format"))
                return
            
            # Record payment
            result, message = self.sc_controller.add_payment(
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
                
                # Refresh lists
                self.refresh_suppliers_list()
                self.refresh_customers_list()
            else:
                # Error
                error_var.set(message)
        
        except (ValueError, TypeError):
            error_var.set(self._("Please enter valid values"))
    
    def create_add_entity_tab(self):
        """Create the add supplier/customer tab"""
        tab = ttk.Frame(self.notebook, padding=10)
        
        # Create form
        form_frame = ttk.Frame(tab)
        form_frame.pack(fill="both", expand=True)
        
        # Add a title
        title_label = ttk.Label(
            form_frame,
            text=self._("Add New Supplier or Customer"),
            font=("TkDefaultFont", 14, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Create input fields
        fields_frame = ttk.Frame(form_frame)
        fields_frame.pack(fill="x")
        
        # Name field
        name_frame = ttk.Frame(fields_frame)
        name_frame.pack(fill="x", pady=10)
        
        ttk.Label(name_frame, text=self._("Name:"), width=15).pack(side="left")
        self.entity_name_var = ttk.StringVar()
        name_entry = ttk.Entry(name_frame, textvariable=self.entity_name_var, width=30)
        name_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Type field
        type_frame = ttk.Frame(fields_frame)
        type_frame.pack(fill="x", pady=10)
        
        ttk.Label(type_frame, text=self._("Type:"), width=15).pack(side="left")
        self.entity_type_var = ttk.StringVar(value="supplier")
        
        type_options = ttk.Frame(type_frame)
        type_options.pack(side="left", padx=5)
        
        ttk.Radiobutton(
            type_options,
            text=self._("Supplier"),
            variable=self.entity_type_var,
            value="supplier"
        ).pack(side="left", padx=5)
        
        ttk.Radiobutton(
            type_options,
            text=self._("Customer"),
            variable=self.entity_type_var,
            value="customer"
        ).pack(side="left", padx=5)
        
        ttk.Radiobutton(
            type_options,
            text=self._("Both"),
            variable=self.entity_type_var,
            value="both"
        ).pack(side="left", padx=5)
        
        # Phone field
        phone_frame = ttk.Frame(fields_frame)
        phone_frame.pack(fill="x", pady=10)
        
        ttk.Label(phone_frame, text=self._("Phone:"), width=15).pack(side="left")
        self.entity_phone_var = ttk.StringVar()
        phone_entry = ttk.Entry(phone_frame, textvariable=self.entity_phone_var, width=20)
        phone_entry.pack(side="left", padx=5)
        
        # Email field
        email_frame = ttk.Frame(fields_frame)
        email_frame.pack(fill="x", pady=10)
        
        ttk.Label(email_frame, text=self._("Email:"), width=15).pack(side="left")
        self.entity_email_var = ttk.StringVar()
        email_entry = ttk.Entry(email_frame, textvariable=self.entity_email_var, width=30)
        email_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Address field
        address_frame = ttk.Frame(fields_frame)
        address_frame.pack(fill="x", pady=10)
        
        ttk.Label(address_frame, text=self._("Address:"), width=15).pack(side="left")
        self.entity_address_var = ttk.StringVar()
        address_entry = ttk.Entry(address_frame, textvariable=self.entity_address_var, width=40)
        address_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Currency field
        currency_frame = ttk.Frame(fields_frame)
        currency_frame.pack(fill="x", pady=10)
        
        ttk.Label(currency_frame, text=self._("Currency:"), width=15).pack(side="left")
        self.entity_currency_var = ttk.StringVar(value="USD")
        currency_combo = ttk.Combobox(
            currency_frame,
            textvariable=self.entity_currency_var,
            values=["USD", "SYP", "EUR"],
            width=10
        )
        currency_combo.pack(side="left", padx=5)
        
        # Exchange rate field
        exchange_frame = ttk.Frame(fields_frame)
        exchange_frame.pack(fill="x", pady=10)
        
        ttk.Label(exchange_frame, text=self._("Exchange Rate:"), width=15).pack(side="left")
        self.entity_exchange_rate_var = ttk.DoubleVar(value=1.0)
        exchange_entry = ttk.Entry(exchange_frame, textvariable=self.entity_exchange_rate_var, width=15)
        exchange_entry.pack(side="left", padx=5)
        
        ttk.Label(
            exchange_frame,
            text=self._("(to USD)"),
            font=("TkDefaultFont", 9, "italic")
        ).pack(side="left")
        
        # Notes field
        notes_frame = ttk.Frame(fields_frame)
        notes_frame.pack(fill="x", pady=10)
        
        ttk.Label(notes_frame, text=self._("Notes:"), width=15).pack(side="left")
        self.entity_notes_var = ttk.StringVar()
        notes_entry = ttk.Entry(notes_frame, textvariable=self.entity_notes_var, width=40)
        notes_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Add error label (hidden initially)
        self.add_entity_error_var = ttk.StringVar()
        self.add_entity_error_label = ttk.Label(
            fields_frame,
            textvariable=self.add_entity_error_var,
            bootstyle=DANGER
        )
        self.add_entity_error_label.pack(pady=10, fill="x")
        
        # Add submit button
        submit_button = ttk.Button(
            fields_frame,
            text=self._("Add Entity"),
            command=self.add_entity,
            bootstyle=SUCCESS,
            width=20
        )
        submit_button.pack(pady=15)
        
        # Add tab to notebook
        self.notebook.add(tab, text=self._("Add Entity"))
    
    def add_entity(self):
        """Add a new supplier or customer"""
        # Reset error message
        self.add_entity_error_var.set("")
        
        # Get values
        name = self.entity_name_var.get().strip()
        entity_type = self.entity_type_var.get()
        phone = self.entity_phone_var.get().strip()
        email = self.entity_email_var.get().strip()
        address = self.entity_address_var.get().strip()
        currency = self.entity_currency_var.get()
        
        try:
            exchange_rate = float(self.entity_exchange_rate_var.get())
        except (ValueError, tkinter.TclError):
            self.add_entity_error_var.set(self._("Please enter a valid exchange rate"))
            return
        
        notes = self.entity_notes_var.get().strip()
        
        # Validate inputs
        if not name:
            self.add_entity_error_var.set(self._("Name is required"))
            return
        
        if exchange_rate <= 0:
            self.add_entity_error_var.set(self._("Exchange rate must be greater than zero"))
            return
        
        # Create entity
        result, message = self.sc_controller.create_entity(
            name=name,
            entity_type=entity_type,
            phone=phone,
            email=email,
            address=address,
            currency=currency,
            exchange_rate=exchange_rate,
            notes=notes
        )
        
        if result:
            # Clear form
            self.entity_name_var.set("")
            self.entity_type_var.set("supplier")
            self.entity_phone_var.set("")
            self.entity_email_var.set("")
            self.entity_address_var.set("")
            self.entity_currency_var.set("USD")
            self.entity_exchange_rate_var.set(1.0)
            self.entity_notes_var.set("")
            
            # Show success message
            show_notification(self._("Success"), self._("Entity added successfully"))
            
            # Refresh lists
            self.refresh_suppliers_list()
            self.refresh_customers_list()
            
            # Switch to appropriate tab
            if entity_type in ["supplier", "both"]:
                self.notebook.select(0)  # Suppliers tab
            else:
                self.notebook.select(1)  # Customers tab
        else:
            # Show error message
            self.add_entity_error_var.set(message)
    
    def create_balances_tab(self):
        """Create the outstanding balances tab"""
        tab = ttk.Frame(self.notebook, padding=10)
        
        # Create filters section
        filters_frame = ttk.Frame(tab)
        filters_frame.pack(fill="x", pady=(0, 10))
        
        # Entity type selector
        ttk.Label(filters_frame, text=self._("Show:")).pack(side="left", padx=(0, 5))
        self.balance_type_var = ttk.StringVar(value="all")
        
        ttk.Radiobutton(
            filters_frame,
            text=self._("All"),
            variable=self.balance_type_var,
            value="all",
            command=self.refresh_balances_list
        ).pack(side="left", padx=5)
        
        ttk.Radiobutton(
            filters_frame,
            text=self._("Receivables (Customers)"),
            variable=self.balance_type_var,
            value="receivables",
            command=self.refresh_balances_list
        ).pack(side="left", padx=5)
        
        ttk.Radiobutton(
            filters_frame,
            text=self._("Payables (Suppliers)"),
            variable=self.balance_type_var,
            value="payables",
            command=self.refresh_balances_list
        ).pack(side="left", padx=5)
        
        # Minimum balance filter
        min_balance_frame = ttk.Frame(filters_frame)
        min_balance_frame.pack(side="right")
        
        ttk.Label(min_balance_frame, text=self._("Min Balance:")).pack(side="left", padx=5)
        self.min_balance_var = ttk.DoubleVar(value=0.0)
        min_balance_entry = ttk.Entry(min_balance_frame, textvariable=self.min_balance_var, width=10)
        min_balance_entry.pack(side="left", padx=5)
        
        ttk.Button(
            min_balance_frame,
            text=self._("Apply"),
            command=self.refresh_balances_list,
            bootstyle=INFO,
            width=8
        ).pack(side="left", padx=5)
        
        # Create treeview for balances
        columns = (
            "id", "name", "type", "balance", "currency", "usd_equivalent", "phone"
        )
        
        self.balances_tree = ttk.Treeview(
            tab,
            columns=columns,
            show="headings",
            bootstyle=INFO
        )
        
        # Define column headings
        self.balances_tree.heading("id", text=self._("ID"))
        self.balances_tree.heading("name", text=self._("Name"))
        self.balances_tree.heading("type", text=self._("Type"))
        self.balances_tree.heading("balance", text=self._("Balance"))
        self.balances_tree.heading("currency", text=self._("Currency"))
        self.balances_tree.heading("usd_equivalent", text=self._("USD Equivalent"))
        self.balances_tree.heading("phone", text=self._("Phone"))
        
        # Define column widths
        self.balances_tree.column("id", width=50, stretch=False)
        self.balances_tree.column("name", width=200)
        self.balances_tree.column("type", width=100, stretch=False)
        self.balances_tree.column("balance", width=100, stretch=False)
        self.balances_tree.column("currency", width=80, stretch=False)
        self.balances_tree.column("usd_equivalent", width=120, stretch=False)
        self.balances_tree.column("phone", width=120)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.balances_tree.yview)
        self.balances_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.balances_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add context menu
        self.setup_balances_context_menu()
        
        # Add summary frame at the bottom
        summary_frame = ttk.Frame(tab)
        summary_frame.pack(fill="x", pady=10)
        
        # Summary labels
        self.receivables_label = ttk.Label(
            summary_frame,
            text=self._("Total Receivables: 0.00 USD"),
            font=("TkDefaultFont", 10, "bold")
        )
        self.receivables_label.pack(side="left", padx=20)
        
        self.payables_label = ttk.Label(
            summary_frame,
            text=self._("Total Payables: 0.00 USD"),
            font=("TkDefaultFont", 10, "bold")
        )
        self.payables_label.pack(side="left", padx=20)
        
        self.net_position_label = ttk.Label(
            summary_frame,
            text=self._("Net Position: 0.00 USD"),
            font=("TkDefaultFont", 12, "bold")
        )
        self.net_position_label.pack(side="right", padx=20)
        
        # Load initial data
        self.refresh_balances_list()
        
        # Add tab to notebook
        self.notebook.add(tab, text=self._("Outstanding Balances"))
    
    def setup_balances_context_menu(self):
        """Setup context menu for balances treeview"""
        self.balances_context_menu = ttk.Menu(self.balances_tree, tearoff=0)
        self.balances_context_menu.add_command(
            label=self._("Make Payment"),
            command=lambda: self.show_payment_dialog_from_balances("supplier")
        )
        self.balances_context_menu.add_command(
            label=self._("Receive Payment"),
            command=lambda: self.show_payment_dialog_from_balances("customer")
        )
        self.balances_context_menu.add_separator()
        self.balances_context_menu.add_command(
            label=self._("View Payment History"),
            command=self.view_payment_history_from_balances
        )
        
        # Bind right-click to show context menu
        self.balances_tree.bind("<Button-3>", self.show_balances_context_menu)
    
    def show_balances_context_menu(self, event):
        """Show context menu on right-click"""
        # Select row under mouse
        iid = self.balances_tree.identify_row(event.y)
        if iid:
            # Select this item
            self.balances_tree.selection_set(iid)
            # Get entity type
            entity_type = self.balances_tree.item(iid, "values")[2].lower()
            
            # Disable/enable menu items based on entity type
            if "supplier" in entity_type:
                self.balances_context_menu.entryconfig(0, state="normal")  # Make Payment
            else:
                self.balances_context_menu.entryconfig(0, state="disabled")
            
            if "customer" in entity_type:
                self.balances_context_menu.entryconfig(1, state="normal")  # Receive Payment
            else:
                self.balances_context_menu.entryconfig(1, state="disabled")
            
            # Display context menu
            self.balances_context_menu.tk_popup(event.x_root, event.y_root)
    
    def show_payment_dialog_from_balances(self, entity_type):
        """Show payment dialog from balances tab"""
        selected_items = self.balances_tree.selection()
        if not selected_items:
            return
            
        item_id = selected_items[0]
        entity_id = self.balances_tree.item(item_id, "values")[0]
        
        # Create a dummy treeview to pass to show_payment_dialog
        # This is a workaround to reuse the existing method
        dummy_tree = ttk.Treeview(self.root)
        dummy_tree.insert("", "end", values=(entity_id,))
        dummy_tree.selection_set(dummy_tree.get_children()[0])
        
        self.show_payment_dialog(dummy_tree, entity_type)
    
    def view_payment_history_from_balances(self):
        """View payment history from balances tab"""
        selected_items = self.balances_tree.selection()
        if not selected_items:
            return
            
        item_id = selected_items[0]
        entity_id = self.balances_tree.item(item_id, "values")[0]
        
        # Create a dummy treeview to pass to view_payment_history
        dummy_tree = ttk.Treeview(self.root)
        dummy_tree.insert("", "end", values=(entity_id,))
        dummy_tree.selection_set(dummy_tree.get_children()[0])
        
        self.view_payment_history(dummy_tree)
    
    def refresh_balances_list(self):
        """Refresh the outstanding balances list"""
        # Clear existing items
        for item in self.balances_tree.get_children():
            self.balances_tree.delete(item)
        
        # Get filter values
        entity_type = self.balance_type_var.get()
        if entity_type == "all":
            entity_type = None
        elif entity_type == "receivables":
            entity_type = "customer"
        elif entity_type == "payables":
            entity_type = "supplier"
        
        try:
            min_balance = float(self.min_balance_var.get())
        except (ValueError, tkinter.TclError):
            min_balance = 0.0
        
        # Get entities with outstanding balances
        entities = self.sc_controller.get_outstanding_balances(
            entity_type=entity_type,
            min_balance=min_balance
        )
        
        # Add entities to treeview
        total_receivables = 0.0
        total_payables = 0.0
        
        for entity in entities:
            # Set type display based on entity type
            type_display = ""
            if entity.type == "supplier":
                type_display = self._("Supplier")
            elif entity.type == "customer":
                type_display = self._("Customer")
            else:  # both
                # For entities that are both, show the role based on balance
                if entity.balance > 0:
                    type_display = self._("Customer")
                else:
                    type_display = self._("Supplier")
            
            # Calculate USD equivalent
            usd_equivalent = entity.balance / entity.exchange_rate if entity.exchange_rate > 0 else 0
            
            # Update totals
            if entity.balance > 0:  # Customer owes us (receivable)
                total_receivables += usd_equivalent
            else:  # We owe supplier (payable)
                total_payables += abs(usd_equivalent)
            
            self.balances_tree.insert(
                "",
                "end",
                values=(
                    entity.id,
                    entity.name,
                    type_display,
                    f"{abs(entity.balance):.2f}",
                    entity.currency,
                    f"{abs(usd_equivalent):.2f}",
                    entity.phone or ""
                )
            )
        
        # Update summary labels
        self.receivables_label.config(
            text=self._("Total Receivables: {0:.2f} USD").format(total_receivables)
        )
        
        self.payables_label.config(
            text=self._("Total Payables: {0:.2f} USD").format(total_payables)
        )
        
        net_position = total_receivables - total_payables
        self.net_position_label.config(
            text=self._("Net Position: {0:.2f} USD").format(net_position)
        )
