#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Funds management view for ASSI Warehouse Management System
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import gettext
from datetime import datetime
from controllers.fund_controller import FundController
from utils.notifications import show_notification

class FundsView:
    """Funds management view class"""
    
    def __init__(self, root, back_to_main_menu):
        """Initialize the funds view
        
        Args:
            root: The root window
            back_to_main_menu: Callback function to return to main menu
        """
        self.root = root
        self.back_to_main_menu = back_to_main_menu
        self.fund_controller = FundController()
        
        # Setup translation
        self._ = gettext.gettext
        
        # Set window title
        self.root.title(self._("ASSI WMS - Funds Management"))
        
        # Create main frame
        self.frame = ttk.Frame(self.root)
        self.frame.pack(expand=True, fill="both")
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Create tabs
        self.create_funds_list_tab()
        self.create_add_fund_tab()
        self.create_transactions_tab()
        self.create_transfer_tab()
        
        # Add back button
        back_button = ttk.Button(
            self.frame,
            text=self._("Back to Main Menu"),
            command=self.back_to_main_menu,
            bootstyle=SECONDARY,
            width=20
        )
        back_button.pack(pady=10)

    def create_funds_list_tab(self):
        """Create the funds list tab"""
        tab = ttk.Frame(self.notebook, padding=10)
        
        # Add refresh button at the top
        refresh_frame = ttk.Frame(tab)
        refresh_frame.pack(fill="x", pady=(0, 10))
        
        refresh_button = ttk.Button(
            refresh_frame,
            text=self._("Refresh"),
            command=self.refresh_funds_list,
            bootstyle=INFO,
            width=15
        )
        refresh_button.pack(side="right")
        
        # Create treeview for funds list
        columns = (
            "id", "name", "currency", "exchange_rate", "balance", "usd_equivalent", "last_update"
        )
        
        self.funds_tree = ttk.Treeview(
            tab,
            columns=columns,
            show="headings",
            bootstyle=INFO
        )
        
        # Define column headings
        self.funds_tree.heading("id", text=self._("ID"))
        self.funds_tree.heading("name", text=self._("Fund Name"))
        self.funds_tree.heading("currency", text=self._("Currency"))
        self.funds_tree.heading("exchange_rate", text=self._("Exchange Rate"))
        self.funds_tree.heading("balance", text=self._("Balance"))
        self.funds_tree.heading("usd_equivalent", text=self._("USD Equivalent"))
        self.funds_tree.heading("last_update", text=self._("Last Update"))
        
        # Define column widths
        self.funds_tree.column("id", width=50, stretch=False)
        self.funds_tree.column("name", width=150)
        self.funds_tree.column("currency", width=80, stretch=False)
        self.funds_tree.column("exchange_rate", width=100, stretch=False)
        self.funds_tree.column("balance", width=100)
        self.funds_tree.column("usd_equivalent", width=120)
        self.funds_tree.column("last_update", width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.funds_tree.yview)
        self.funds_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.funds_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add context menu
        self.setup_funds_context_menu()
        
        # Load initial data
        self.refresh_funds_list()
        
        # Add tab to notebook
        self.notebook.add(tab, text=self._("Funds List"))
        
    def setup_funds_context_menu(self):
        """Setup context menu for funds treeview"""
        self.fund_context_menu = ttk.Menu(self.funds_tree, tearoff=0)
        self.fund_context_menu.add_command(
            label=self._("Edit Fund"),
            command=self.edit_selected_fund
        )
        self.fund_context_menu.add_command(
            label=self._("Deactivate Fund"),
            command=self.deactivate_selected_fund
        )
        self.fund_context_menu.add_separator()
        self.fund_context_menu.add_command(
            label=self._("View Transactions"),
            command=self.view_fund_transactions
        )
        
        # Bind right-click to show context menu
        self.funds_tree.bind("<Button-3>", self.show_fund_context_menu)
        # Bind double-click to edit
        self.funds_tree.bind("<Double-1>", lambda event: self.edit_selected_fund())
        
    def show_fund_context_menu(self, event):
        """Show context menu on right-click"""
        # Select row under mouse
        iid = self.funds_tree.identify_row(event.y)
        if iid:
            # Select this item
            self.funds_tree.selection_set(iid)
            # Display context menu
            self.fund_context_menu.tk_popup(event.x_root, event.y_root)
    
    def edit_selected_fund(self):
        """Open dialog to edit the selected fund"""
        selected_items = self.funds_tree.selection()
        if not selected_items:
            return
            
        item_id = selected_items[0]
        fund_id = self.funds_tree.item(item_id, "values")[0]
        
        # Get fund data
        fund = self.fund_controller.get_fund_by_id(fund_id)
        if not fund:
            return
            
        # Create edit dialog
        edit_dialog = ttk.Toplevel(self.root)
        edit_dialog.title(self._("Edit Fund"))
        edit_dialog.geometry("400x300")
        edit_dialog.transient(self.root)
        edit_dialog.grab_set()
        
        # Create form in the dialog
        frame = ttk.Frame(edit_dialog, padding=10)
        frame.pack(fill="both", expand=True)
        
        # Name field
        ttk.Label(frame, text=self._("Fund Name:")).grid(row=0, column=0, sticky="w", pady=5)
        name_var = ttk.StringVar(value=fund.name)
        name_entry = ttk.Entry(frame, textvariable=name_var, width=30)
        name_entry.grid(row=0, column=1, sticky="ew", pady=5)
        
        # Currency field
        ttk.Label(frame, text=self._("Currency:")).grid(row=1, column=0, sticky="w", pady=5)
        currency_var = ttk.StringVar(value=fund.currency)
        currency_combo = ttk.Combobox(
            frame,
            textvariable=currency_var,
            values=["USD", "SYP", "EUR", "GBP"],
            width=10
        )
        currency_combo.grid(row=1, column=1, sticky="w", pady=5)
        
        # Exchange rate field
        ttk.Label(frame, text=self._("Exchange Rate:")).grid(row=2, column=0, sticky="w", pady=5)
        exchange_rate_var = ttk.DoubleVar(value=fund.exchange_rate)
        exchange_rate_entry = ttk.Entry(frame, textvariable=exchange_rate_var, width=15)
        exchange_rate_entry.grid(row=2, column=1, sticky="w", pady=5)
        
        # Status field
        ttk.Label(frame, text=self._("Status:")).grid(row=3, column=0, sticky="w", pady=5)
        status_var = ttk.BooleanVar(value=fund.is_active)
        status_check = ttk.Checkbutton(
            frame,
            text=self._("Active"),
            variable=status_var,
            onvalue=True,
            offvalue=False
        )
        status_check.grid(row=3, column=1, sticky="w", pady=5)
        
        # Current balance (display only)
        ttk.Label(frame, text=self._("Current Balance:")).grid(row=4, column=0, sticky="w", pady=5)
        balance_label = ttk.Label(
            frame,
            text=f"{fund.balance} {fund.currency}",
            font=("TkDefaultFont", 10, "bold")
        )
        balance_label.grid(row=4, column=1, sticky="w", pady=5)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=15)
        
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
            command=lambda: self.save_fund_edits(
                fund.id,
                name_var.get(),
                currency_var.get(),
                exchange_rate_var.get(),
                status_var.get(),
                edit_dialog
            ),
            bootstyle=SUCCESS,
            width=10
        ).pack(side="left", padx=5)
    
    def save_fund_edits(self, fund_id, name, currency, exchange_rate, is_active, dialog):
        """Save edits to a fund"""
        result, message = self.fund_controller.update_fund(
            fund_id=fund_id,
            name=name,
            currency=currency,
            exchange_rate=exchange_rate,
            is_active=is_active
        )
        
        if result:
            show_notification(self._("Success"), self._("Fund updated successfully"))
            dialog.destroy()
            self.refresh_funds_list()
        else:
            # Show error in dialog
            error_label = ttk.Label(dialog, text=message, bootstyle=DANGER)
            error_label.pack(pady=10)
    
    def deactivate_selected_fund(self):
        """Deactivate the selected fund"""
        selected_items = self.funds_tree.selection()
        if not selected_items:
            return
            
        item_id = selected_items[0]
        fund_id = self.funds_tree.item(item_id, "values")[0]
        
        # Confirm deactivation
        confirm = ttk.Messagebox.yesno(
            title=self._("Confirm Deactivation"),
            message=self._("Are you sure you want to deactivate this fund?")
        )
        
        if confirm == "No":
            return
            
        # Deactivate fund
        result, _ = self.fund_controller.update_fund(
            fund_id=fund_id,
            is_active=False
        )
        
        if result:
            show_notification(self._("Success"), self._("Fund deactivated successfully"))
            self.refresh_funds_list()
    
    def view_fund_transactions(self):
        """View transactions for the selected fund"""
        selected_items = self.funds_tree.selection()
        if not selected_items:
            return
            
        item_id = selected_items[0]
        fund_id = self.funds_tree.item(item_id, "values")[0]
        fund_name = self.funds_tree.item(item_id, "values")[1]
        
        # Switch to transactions tab and filter for this fund
        self.notebook.select(2)  # Index of transactions tab
        self.fund_filter_var.set(fund_id)
        self.refresh_transactions()
    
    def refresh_funds_list(self):
        """Refresh the funds list"""
        # Clear existing items
        for item in self.funds_tree.get_children():
            self.funds_tree.delete(item)
        
        # Get all funds
        funds = self.fund_controller.get_all_funds(active_only=False)
        
        # Add funds to treeview
        for fund in funds:
            # Calculate USD equivalent
            usd_equivalent = fund.balance / fund.exchange_rate if fund.exchange_rate > 0 else 0
            
            # Format last update date
            last_update = fund.updated_at.strftime("%Y-%m-%d %H:%M") if fund.updated_at else ""
            
            # Add status indicator to name
            display_name = fund.name
            if not fund.is_active:
                display_name += " [" + self._("Inactive") + "]"
            
            self.funds_tree.insert(
                "",
                "end",
                values=(
                    fund.id,
                    display_name,
                    fund.currency,
                    f"{fund.exchange_rate:.2f}",
                    f"{fund.balance:.2f}",
                    f"{usd_equivalent:.2f}",
                    last_update
                )
            )
    
    def create_add_fund_tab(self):
        """Create the add fund tab"""
        tab = ttk.Frame(self.notebook, padding=10)
        
        # Create form
        form_frame = ttk.Frame(tab)
        form_frame.pack(fill="both", expand=True)
        
        # Add a title
        title_label = ttk.Label(
            form_frame,
            text=self._("Add New Fund"),
            font=("TkDefaultFont", 14, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Create input fields
        fields_frame = ttk.Frame(form_frame)
        fields_frame.pack(fill="x")
        
        # Name field
        name_frame = ttk.Frame(fields_frame)
        name_frame.pack(fill="x", pady=10)
        
        ttk.Label(name_frame, text=self._("Fund Name:"), width=15).pack(side="left")
        self.fund_name_var = ttk.StringVar()
        name_entry = ttk.Entry(name_frame, textvariable=self.fund_name_var, width=30)
        name_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Currency field
        currency_frame = ttk.Frame(fields_frame)
        currency_frame.pack(fill="x", pady=10)
        
        ttk.Label(currency_frame, text=self._("Currency:"), width=15).pack(side="left")
        self.fund_currency_var = ttk.StringVar(value="USD")
        currency_combo = ttk.Combobox(
            currency_frame,
            textvariable=self.fund_currency_var,
            values=["USD", "SYP", "EUR", "GBP"],
            width=10
        )
        currency_combo.pack(side="left", padx=5)
        
        # Exchange rate field
        exchange_frame = ttk.Frame(fields_frame)
        exchange_frame.pack(fill="x", pady=10)
        
        ttk.Label(exchange_frame, text=self._("Exchange Rate:"), width=15).pack(side="left")
        self.fund_exchange_rate_var = ttk.DoubleVar(value=1.0)
        exchange_entry = ttk.Entry(exchange_frame, textvariable=self.fund_exchange_rate_var, width=15)
        exchange_entry.pack(side="left", padx=5)
        
        # Initial balance field
        balance_frame = ttk.Frame(fields_frame)
        balance_frame.pack(fill="x", pady=10)
        
        ttk.Label(balance_frame, text=self._("Initial Balance:"), width=15).pack(side="left")
        self.fund_balance_var = ttk.DoubleVar(value=0.0)
        balance_entry = ttk.Entry(balance_frame, textvariable=self.fund_balance_var, width=15)
        balance_entry.pack(side="left", padx=5)
        
        # Add error label (hidden initially)
        self.add_fund_error_var = ttk.StringVar()
        self.add_fund_error_label = ttk.Label(
            fields_frame,
            textvariable=self.add_fund_error_var,
            bootstyle=DANGER
        )
        self.add_fund_error_label.pack(pady=10, fill="x")
        
        # Add submit button
        submit_button = ttk.Button(
            fields_frame,
            text=self._("Add Fund"),
            command=self.add_fund,
            bootstyle=SUCCESS,
            width=20
        )
        submit_button.pack(pady=15)
        
        # Add tab to notebook
        self.notebook.add(tab, text=self._("Add Fund"))
    
    def add_fund(self):
        """Add a new fund"""
        # Reset error message
        self.add_fund_error_var.set("")
        
        # Get values
        name = self.fund_name_var.get().strip()
        currency = self.fund_currency_var.get()
        
        try:
            exchange_rate = float(self.fund_exchange_rate_var.get())
            initial_balance = float(self.fund_balance_var.get())
        except (ValueError, tkinter.TclError):
            self.add_fund_error_var.set(self._("Please enter valid numbers for exchange rate and initial balance"))
            return
        
        # Validate inputs
        if not name:
            self.add_fund_error_var.set(self._("Fund name is required"))
            return
        
        if exchange_rate <= 0:
            self.add_fund_error_var.set(self._("Exchange rate must be greater than zero"))
            return
        
        # Create fund
        result, message = self.fund_controller.create_fund(
            name=name,
            currency=currency,
            exchange_rate=exchange_rate,
            initial_balance=initial_balance
        )
        
        if result:
            # Clear form
            self.fund_name_var.set("")
            self.fund_currency_var.set("USD")
            self.fund_exchange_rate_var.set(1.0)
            self.fund_balance_var.set(0.0)
            
            # Show success message
            show_notification(self._("Success"), self._("Fund added successfully"))
            
            # Refresh funds list and switch to it
            self.refresh_funds_list()
            self.notebook.select(0)  # Switch to funds list tab
        else:
            # Show error message
            self.add_fund_error_var.set(message)
    
    def create_transactions_tab(self):
        """Create the transactions tab"""
        tab = ttk.Frame(self.notebook, padding=10)
        
        # Create filters frame
        filters_frame = ttk.Frame(tab)
        filters_frame.pack(fill="x", pady=(0, 10))
        
        # Fund filter
        ttk.Label(filters_frame, text=self._("Fund:")).pack(side="left", padx=(0, 5))
        self.fund_filter_var = ttk.StringVar(value="all")
        
        # Get all funds for the combobox
        funds = self.fund_controller.get_all_funds()
        fund_choices = [("all", self._("All Funds"))]
        fund_choices.extend([(str(fund.id), fund.name) for fund in funds])
        
        fund_filter = ttk.Combobox(
            filters_frame,
            textvariable=self.fund_filter_var,
            width=20
        )
        fund_filter['values'] = [f[0] for f in fund_choices]
        fund_filter.pack(side="left", padx=(0, 10))
        
        # Date filters
        ttk.Label(filters_frame, text=self._("From:")).pack(side="left", padx=(10, 5))
        self.date_from_var = ttk.StringVar()
        date_from_entry = ttk.DateEntry(
            filters_frame,
            dateformat="%Y-%m-%d",
            firstweekday=0,
            startdate=datetime.now(),
            width=12,
            textvariable=self.date_from_var
        )
        date_from_entry.pack(side="left", padx=(0, 10))
        
        ttk.Label(filters_frame, text=self._("To:")).pack(side="left", padx=(0, 5))
        self.date_to_var = ttk.StringVar()
        date_to_entry = ttk.DateEntry(
            filters_frame,
            dateformat="%Y-%m-%d",
            firstweekday=0,
            startdate=datetime.now(),
            width=12,
            textvariable=self.date_to_var
        )
        date_to_entry.pack(side="left", padx=(0, 10))
        
        # Filter button
        filter_button = ttk.Button(
            filters_frame,
            text=self._("Apply Filter"),
            command=self.refresh_transactions,
            bootstyle=INFO,
            width=15
        )
        filter_button.pack(side="left", padx=10)
        
        # Reset filter button
        reset_button = ttk.Button(
            filters_frame,
            text=self._("Reset"),
            command=self.reset_transaction_filters,
            bootstyle=SECONDARY,
            width=10
        )
        reset_button.pack(side="left")
        
        # Create treeview for transactions
        columns = (
            "id", "date", "fund", "type", "amount", "description", "reference"
        )
        
        self.transactions_tree = ttk.Treeview(
            tab,
            columns=columns,
            show="headings",
            bootstyle=INFO
        )
        
        # Define column headings
        self.transactions_tree.heading("id", text=self._("ID"))
        self.transactions_tree.heading("date", text=self._("Date"))
        self.transactions_tree.heading("fund", text=self._("Fund"))
        self.transactions_tree.heading("type", text=self._("Type"))
        self.transactions_tree.heading("amount", text=self._("Amount"))
        self.transactions_tree.heading("description", text=self._("Description"))
        self.transactions_tree.heading("reference", text=self._("Reference"))
        
        # Define column widths
        self.transactions_tree.column("id", width=50, stretch=False)
        self.transactions_tree.column("date", width=120, stretch=False)
        self.transactions_tree.column("fund", width=120)
        self.transactions_tree.column("type", width=80, stretch=False)
        self.transactions_tree.column("amount", width=100, stretch=False)
        self.transactions_tree.column("description", width=250)
        self.transactions_tree.column("reference", width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.transactions_tree.yview)
        self.transactions_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.transactions_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Load initial data
        self.refresh_transactions()
        
        # Add tab to notebook
        self.notebook.add(tab, text=self._("Transactions"))
    
    def reset_transaction_filters(self):
        """Reset transaction filters to default"""
        self.fund_filter_var.set("all")
        self.date_from_var.set("")
        self.date_to_var.set("")
        self.refresh_transactions()
    
    def refresh_transactions(self):
        """Refresh the transactions list based on filters"""
        # Clear existing items
        for item in self.transactions_tree.get_children():
            self.transactions_tree.delete(item)
        
        # Get filter values
        fund_id = self.fund_filter_var.get()
        if fund_id == "all":
            fund_id = None
        else:
            try:
                fund_id = int(fund_id)
            except ValueError:
                fund_id = None
        
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
            except ValueError:
                pass
        
        # Get transactions based on filters
        if fund_id:
            transactions = self.fund_controller.get_fund_transactions(
                fund_id=fund_id,
                start_date=start_date,
                end_date=end_date
            )
        else:
            # TODO: Get transactions for all funds (would need method in controller)
            transactions = []
            funds = self.fund_controller.get_all_funds()
            for fund in funds:
                fund_transactions = self.fund_controller.get_fund_transactions(
                    fund_id=fund.id,
                    start_date=start_date,
                    end_date=end_date
                )
                transactions.extend(fund_transactions)
            
            # Sort by date (newest first)
            transactions.sort(key=lambda x: x.created_at, reverse=True)
        
        # Add transactions to treeview
        funds_dict = {fund.id: fund.name for fund in self.fund_controller.get_all_funds(active_only=False)}
        
        for transaction in transactions:
            # Determine the icon based on transaction type
            icon = "⬇️" if transaction.transaction_type == "deposit" else "⬆️"
            
            # Format the amount with color based on transaction type
            if transaction.transaction_type == "deposit":
                amount_str = f"+{transaction.amount:.2f}"
            else:
                amount_str = f"-{transaction.amount:.2f}"
            
            # Get fund name
            fund_name = funds_dict.get(transaction.fund_id, str(transaction.fund_id))
            
            # Format reference
            reference = ""
            if transaction.reference_type and transaction.reference_id:
                reference = f"{transaction.reference_type} #{transaction.reference_id}"
            
            self.transactions_tree.insert(
                "",
                "end",
                values=(
                    transaction.id,
                    transaction.created_at.strftime("%Y-%m-%d %H:%M"),
                    fund_name,
                    f"{icon} {transaction.transaction_type}",
                    amount_str,
                    transaction.description,
                    reference
                )
            )
    
    def create_transfer_tab(self):
        """Create the fund transfer tab"""
        tab = ttk.Frame(self.notebook, padding=10)
        
        # Add a title
        title_label = ttk.Label(
            tab,
            text=self._("Transfer Between Funds"),
            font=("TkDefaultFont", 14, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Create form
        form_frame = ttk.Frame(tab)
        form_frame.pack(fill="x")
        
        # Get all funds for selection
        funds = self.fund_controller.get_all_funds()
        fund_choices = [(str(fund.id), f"{fund.name} ({fund.currency})") for fund in funds]
        
        # Source fund field
        source_frame = ttk.Frame(form_frame)
        source_frame.pack(fill="x", pady=10)
        
        ttk.Label(source_frame, text=self._("From Fund:"), width=15).pack(side="left")
        self.source_fund_var = ttk.StringVar()
        if fund_choices:
            self.source_fund_var.set(fund_choices[0][0])
        
        source_combo = ttk.Combobox(
            source_frame,
            textvariable=self.source_fund_var,
            width=30
        )
        source_combo['values'] = [f"{f[1]}" for f in fund_choices]
        source_combo.pack(side="left", padx=5, fill="x", expand=True)
        
        # Destination fund field
        dest_frame = ttk.Frame(form_frame)
        dest_frame.pack(fill="x", pady=10)
        
        ttk.Label(dest_frame, text=self._("To Fund:"), width=15).pack(side="left")
        self.dest_fund_var = ttk.StringVar()
        if len(fund_choices) > 1:
            self.dest_fund_var.set(fund_choices[1][0])
        elif fund_choices:
            self.dest_fund_var.set(fund_choices[0][0])
        
        dest_combo = ttk.Combobox(
            dest_frame,
            textvariable=self.dest_fund_var,
            width=30
        )
        dest_combo['values'] = [f"{f[1]}" for f in fund_choices]
        dest_combo.pack(side="left", padx=5, fill="x", expand=True)
        
        # Amount field
        amount_frame = ttk.Frame(form_frame)
        amount_frame.pack(fill="x", pady=10)
        
        ttk.Label(amount_frame, text=self._("Amount:"), width=15).pack(side="left")
        self.transfer_amount_var = ttk.DoubleVar(value=0.0)
        amount_entry = ttk.Entry(amount_frame, textvariable=self.transfer_amount_var, width=15)
        amount_entry.pack(side="left", padx=5)
        
        # Description field
        desc_frame = ttk.Frame(form_frame)
        desc_frame.pack(fill="x", pady=10)
        
        ttk.Label(desc_frame, text=self._("Description:"), width=15).pack(side="left")
        self.transfer_desc_var = ttk.StringVar()
        desc_entry = ttk.Entry(desc_frame, textvariable=self.transfer_desc_var, width=40)
        desc_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Add error/success message label
        self.transfer_message_var = ttk.StringVar()
        self.transfer_message_label = ttk.Label(
            form_frame,
            textvariable=self.transfer_message_var
        )
        self.transfer_message_label.pack(pady=10, fill="x")
        
        # Add exchange rate info label
        self.exchange_info_var = ttk.StringVar()
        exchange_info_label = ttk.Label(
            form_frame,
            textvariable=self.exchange_info_var,
            font=("TkDefaultFont", 10, "italic")
        )
        exchange_info_label.pack(pady=5, fill="x")
        
        # Update exchange rate info when funds are selected
        source_combo.bind("<<ComboboxSelected>>", self.update_exchange_info)
        dest_combo.bind("<<ComboboxSelected>>", self.update_exchange_info)
        
        # Add submit button
        submit_button = ttk.Button(
            form_frame,
            text=self._("Transfer"),
            command=self.transfer_funds,
            bootstyle=SUCCESS,
            width=20
        )
        submit_button.pack(pady=15)
        
        # Update exchange info initially
        self.update_exchange_info()
        
        # Add tab to notebook
        self.notebook.add(tab, text=self._("Transfer"))
    
    def update_exchange_info(self, event=None):
        """Update the exchange rate information label"""
        try:
            source_id = int(self.source_fund_var.get())
            dest_id = int(self.dest_fund_var.get())
            
            # Get fund objects
            source_fund = self.fund_controller.get_fund_by_id(source_id)
            dest_fund = self.fund_controller.get_fund_by_id(dest_id)
            
            if source_fund and dest_fund:
                if source_fund.currency != dest_fund.currency:
                    # Calculate exchange info
                    source_amount = 100  # Example amount
                    # Convert to a common currency (USD) then to target currency
                    usd_value = source_amount / source_fund.exchange_rate
                    dest_amount = usd_value * dest_fund.exchange_rate
                    
                    info = self._("Exchange rate: {0} {1} ≈ {2:.2f} {3}").format(
                        source_amount,
                        source_fund.currency,
                        dest_amount,
                        dest_fund.currency
                    )
                    self.exchange_info_var.set(info)
                else:
                    self.exchange_info_var.set(self._("Both funds use the same currency ({0})").format(source_fund.currency))
            else:
                self.exchange_info_var.set("")
        except (ValueError, AttributeError):
            self.exchange_info_var.set("")
    
    def transfer_funds(self):
        """Transfer funds between accounts"""
        # Reset message
        self.transfer_message_var.set("")
        self.transfer_message_label.configure(bootstyle="")
        
        try:
            source_id = int(self.source_fund_var.get())
            dest_id = int(self.dest_fund_var.get())
            amount = float(self.transfer_amount_var.get())
            description = self.transfer_desc_var.get()
            
            # Validate inputs
            if source_id == dest_id:
                self.transfer_message_var.set(self._("Source and destination funds must be different"))
                self.transfer_message_label.configure(bootstyle=DANGER)
                return
            
            if amount <= 0:
                self.transfer_message_var.set(self._("Amount must be greater than zero"))
                self.transfer_message_label.configure(bootstyle=DANGER)
                return
            
            # Perform transfer
            result, message = self.fund_controller.transfer_between_funds(
                from_fund_id=source_id,
                to_fund_id=dest_id,
                amount=amount,
                description=description
            )
            
            if result:
                # Success
                self.transfer_message_var.set(self._("Transfer completed successfully"))
                self.transfer_message_label.configure(bootstyle=SUCCESS)
                
                # Clear form
                self.transfer_amount_var.set(0.0)
                self.transfer_desc_var.set("")
                
                # Refresh funds list and transactions
                self.refresh_funds_list()
                self.refresh_transactions()
                
                # Show notification
                show_notification(
                    self._("Transfer Complete"),
                    self._("Funds transferred successfully")
                )
            else:
                # Error
                self.transfer_message_var.set(message)
                self.transfer_message_label.configure(bootstyle=DANGER)
        
        except ValueError:
            self.transfer_message_var.set(self._("Please enter valid numeric values"))
            self.transfer_message_label.configure(bootstyle=DANGER)
