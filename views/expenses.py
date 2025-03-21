#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Expenses management view for ASSI Warehouse Management System
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import gettext
from datetime import datetime
from controllers.expense_controller import ExpenseController
from controllers.fund_controller import FundController
from utils.notifications import show_notification

class ExpensesView:
    """Expenses management view class"""
    
    def __init__(self, root, back_to_main_menu):
        """Initialize the expenses view
        
        Args:
            root: The root window
            back_to_main_menu: Callback function to return to main menu
        """
        self.root = root
        self.back_to_main_menu = back_to_main_menu
        self.expense_controller = ExpenseController()
        self.fund_controller = FundController()
        
        # Setup translation
        self._ = gettext.gettext
        
        # Set window title
        self.root.title(self._("ASSI WMS - Expense Management"))
        
        # Create main frame
        self.frame = ttk.Frame(self.root)
        self.frame.pack(expand=True, fill="both")
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Create tabs
        self.create_expenses_list_tab()
        self.create_add_expense_tab()
        self.create_categories_tab()
        
        # Add back button
        back_button = ttk.Button(
            self.frame,
            text=self._("Back to Main Menu"),
            command=self.back_to_main_menu,
            bootstyle=SECONDARY,
            width=20
        )
        back_button.pack(pady=10)
    
    def create_expenses_list_tab(self):
        """Create the expenses list tab"""
        tab = ttk.Frame(self.notebook, padding=10)
        
        # Create filters section
        filters_frame = ttk.LabelFrame(tab, text=self._("Filters"), padding=10)
        filters_frame.pack(fill="x", pady=(0, 10))
        
        # Date filters
        filter_row1 = ttk.Frame(filters_frame)
        filter_row1.pack(fill="x", pady=5)
        
        ttk.Label(filter_row1, text=self._("Date From:"), width=10).pack(side="left")
        self.date_from_var = ttk.StringVar()
        date_from = ttk.DateEntry(
            filter_row1,
            dateformat="%Y-%m-%d",
            firstweekday=0,
            width=12,
            textvariable=self.date_from_var
        )
        date_from.pack(side="left", padx=5)
        
        ttk.Label(filter_row1, text=self._("To:"), width=3).pack(side="left")
        self.date_to_var = ttk.StringVar()
        date_to = ttk.DateEntry(
            filter_row1,
            dateformat="%Y-%m-%d",
            firstweekday=0,
            width=12,
            textvariable=self.date_to_var
        )
        date_to.pack(side="left", padx=5)
        
        # Category filter
        ttk.Label(filter_row1, text=self._("Category:"), width=8).pack(side="left", padx=(20, 0))
        
        # Get categories for combobox
        categories = self.expense_controller.get_all_categories()
        category_choices = [("all", self._("All Categories"))]
        category_choices.extend([(str(c.id), c.name) for c in categories])
        
        self.category_filter_var = ttk.StringVar(value="all")
        category_combo = ttk.Combobox(
            filter_row1,
            textvariable=self.category_filter_var,
            values=[f"{c[1]}" for c in category_choices],
            width=20
        )
        category_combo.current(0)
        category_combo.pack(side="left", padx=5)
        
        # Buttons
        filter_button = ttk.Button(
            filter_row1,
            text=self._("Apply Filters"),
            command=self.refresh_expenses_list,
            bootstyle=INFO,
            width=15
        )
        filter_button.pack(side="left", padx=20)
        
        reset_button = ttk.Button(
            filter_row1,
            text=self._("Reset Filters"),
            command=self.reset_filters,
            bootstyle=SECONDARY,
            width=15
        )
        reset_button.pack(side="left", padx=5)
        
        # Create treeview for expenses list
        columns = (
            "id", "date", "category", "amount", "currency", "description", "fund"
        )
        
        self.expenses_tree = ttk.Treeview(
            tab,
            columns=columns,
            show="headings",
            bootstyle=INFO
        )
        
        # Define column headings
        self.expenses_tree.heading("id", text=self._("ID"))
        self.expenses_tree.heading("date", text=self._("Date"))
        self.expenses_tree.heading("category", text=self._("Category"))
        self.expenses_tree.heading("amount", text=self._("Amount"))
        self.expenses_tree.heading("currency", text=self._("Currency"))
        self.expenses_tree.heading("description", text=self._("Description"))
        self.expenses_tree.heading("fund", text=self._("Fund"))
        
        # Define column widths
        self.expenses_tree.column("id", width=50, stretch=False)
        self.expenses_tree.column("date", width=100, stretch=False)
        self.expenses_tree.column("category", width=150)
        self.expenses_tree.column("amount", width=100, stretch=False)
        self.expenses_tree.column("currency", width=80, stretch=False)
        self.expenses_tree.column("description", width=250)
        self.expenses_tree.column("fund", width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.expenses_tree.yview)
        self.expenses_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.expenses_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add summary frame at the bottom
        summary_frame = ttk.Frame(tab)
        summary_frame.pack(fill="x", pady=10)
        
        # Total expenses label
        self.total_expenses_label = ttk.Label(
            summary_frame,
            text=self._("Total Expenses: 0.00"),
            font=("TkDefaultFont", 12, "bold")
        )
        self.total_expenses_label.pack(side="left", padx=20)
        
        # Load initial data
        self.refresh_expenses_list()
        
        # Add tab to notebook
        self.notebook.add(tab, text=self._("Expenses List"))
    
    def reset_filters(self):
        """Reset all filters to default values"""
        self.date_from_var.set("")
        self.date_to_var.set("")
        self.category_filter_var.set("all")
        self.refresh_expenses_list()
    
    def refresh_expenses_list(self):
        """Refresh the expenses list based on filters"""
        # Clear existing items
        for item in self.expenses_tree.get_children():
            self.expenses_tree.delete(item)
        
        # Get filter values
        category_id = self.category_filter_var.get()
        if category_id == "all":
            category_id = None
        else:
            try:
                category_id = int(category_id)
            except ValueError:
                category_id = None
        
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
        
        # Get expenses based on filters
        expenses = self.expense_controller.get_all_expenses(
            start_date=start_date,
            end_date=end_date,
            category_id=category_id
        )
        
        # Get funds for display
        funds = self.fund_controller.get_all_funds(active_only=False)
        fund_dict = {f.id: f.name for f in funds}
        
        # Add expenses to treeview
        total_expenses = 0
        
        for expense in expenses:
            # Get fund name if available
            fund_name = fund_dict.get(expense.fund_id, "") if expense.fund_id else ""
            
            # Calculate total in USD for summary
            if expense.currency == "USD":
                total_expenses += expense.amount
            else:
                # Convert to USD using exchange rate
                total_expenses += expense.amount / expense.exchange_rate
            
            self.expenses_tree.insert(
                "",
                "end",
                values=(
                    expense.id,
                    expense.expense_date.strftime("%Y-%m-%d"),
                    expense.category.name,
                    f"{expense.amount:.2f}",
                    expense.currency,
                    expense.description or "",
                    fund_name
                )
            )
        
        # Update summary
        self.total_expenses_label.config(
            text=self._("Total Expenses: {0:.2f} USD").format(total_expenses)
        )
    
    def create_add_expense_tab(self):
        """Create the add expense tab"""
        tab = ttk.Frame(self.notebook, padding=10)
        
        # Create form
        form_frame = ttk.Frame(tab)
        form_frame.pack(fill="both", expand=True)
        
        # Add a title
        title_label = ttk.Label(
            form_frame,
            text=self._("Add New Expense"),
            font=("TkDefaultFont", 14, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Create input fields
        fields_frame = ttk.Frame(form_frame)
        fields_frame.pack(fill="x")
        
        # Category field
        category_frame = ttk.Frame(fields_frame)
        category_frame.pack(fill="x", pady=10)
        
        ttk.Label(category_frame, text=self._("Category:"), width=15).pack(side="left")
        
        # Get categories for combobox
        categories = self.expense_controller.get_all_categories()
        category_choices = [(str(c.id), c.name) for c in categories]
        
        self.expense_category_var = ttk.StringVar()
        if category_choices:
            self.expense_category_var.set(str(category_choices[0][0]))
        
        category_combo = ttk.Combobox(
            category_frame,
            textvariable=self.expense_category_var,
            values=[f"{c[1]}" for c in category_choices],
            width=30
        )
        if category_choices:
            category_combo.current(0)
        category_combo.pack(side="left", padx=5, fill="x", expand=True)
        
        # Amount field
        amount_frame = ttk.Frame(fields_frame)
        amount_frame.pack(fill="x", pady=10)
        
        ttk.Label(amount_frame, text=self._("Amount:"), width=15).pack(side="left")
        self.expense_amount_var = ttk.DoubleVar(value=0.0)
        amount_entry = ttk.Entry(amount_frame, textvariable=self.expense_amount_var, width=15)
        amount_entry.pack(side="left", padx=5)
        
        # Currency field
        ttk.Label(amount_frame, text=self._("Currency:")).pack(side="left", padx=(20, 5))
        self.expense_currency_var = ttk.StringVar(value="USD")
        currency_combo = ttk.Combobox(
            amount_frame,
            textvariable=self.expense_currency_var,
            values=["USD", "SYP", "EUR"],
            width=10
        )
        currency_combo.pack(side="left")
        
        # Exchange rate field
        exchange_frame = ttk.Frame(fields_frame)
        exchange_frame.pack(fill="x", pady=10)
        
        ttk.Label(exchange_frame, text=self._("Exchange Rate:"), width=15).pack(side="left")
        self.expense_exchange_rate_var = ttk.DoubleVar(value=1.0)
        exchange_entry = ttk.Entry(exchange_frame, textvariable=self.expense_exchange_rate_var, width=15)
        exchange_entry.pack(side="left", padx=5)
        
        ttk.Label(
            exchange_frame,
            text=self._("(to USD)"),
            font=("TkDefaultFont", 9, "italic")
        ).pack(side="left")
        
        # Date field
        date_frame = ttk.Frame(fields_frame)
        date_frame.pack(fill="x", pady=10)
        
        ttk.Label(date_frame, text=self._("Date:"), width=15).pack(side="left")
        self.expense_date_var = ttk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        date_entry = ttk.DateEntry(
            date_frame,
            dateformat="%Y-%m-%d",
            firstweekday=0,
            width=12,
            textvariable=self.expense_date_var
        )
        date_entry.pack(side="left", padx=5)
        
        # Fund field
        fund_frame = ttk.Frame(fields_frame)
        fund_frame.pack(fill="x", pady=10)
        
        ttk.Label(fund_frame, text=self._("Fund:"), width=15).pack(side="left")
        
        # Get funds for combobox
        funds = self.fund_controller.get_all_funds()
        fund_choices = [(str(f.id), f"{f.name} ({f.currency})") for f in funds]
        fund_choices.insert(0, ("", self._("-- No Fund --")))
        
        self.expense_fund_var = ttk.StringVar(value="")
        fund_combo = ttk.Combobox(
            fund_frame,
            textvariable=self.expense_fund_var,
            values=[f"{f[1]}" for f in fund_choices],
            width=30
        )
        fund_combo.current(0)
        fund_combo.pack(side="left", padx=5, fill="x", expand=True)
        
        # Description field
        desc_frame = ttk.Frame(fields_frame)
        desc_frame.pack(fill="x", pady=10)
        
        ttk.Label(desc_frame, text=self._("Description:"), width=15).pack(side="left")
        self.expense_desc_var = ttk.StringVar()
        desc_entry = ttk.Entry(desc_frame, textvariable=self.expense_desc_var, width=40)
        desc_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Add error label (hidden initially)
        self.add_expense_error_var = ttk.StringVar()
        self.add_expense_error_label = ttk.Label(
            fields_frame,
            textvariable=self.add_expense_error_var,
            bootstyle=DANGER
        )
        self.add_expense_error_label.pack(pady=10, fill="x")
        
        # Add submit button
        submit_button = ttk.Button(
            fields_frame,
            text=self._("Add Expense"),
            command=self.add_expense,
            bootstyle=SUCCESS,
            width=20
        )
        submit_button.pack(pady=15)
        
        # Add tab to notebook
        self.notebook.add(tab, text=self._("Add Expense"))
    
    def add_expense(self):
        """Add a new expense"""
        # Reset error message
        self.add_expense_error_var.set("")
        
        try:
            # Get form values
            category_id = int(self.expense_category_var.get())
            amount = float(self.expense_amount_var.get())
            currency = self.expense_currency_var.get()
            exchange_rate = float(self.expense_exchange_rate_var.get())
            description = self.expense_desc_var.get()
            
            # Get fund ID if selected
            fund_id = None
            if self.expense_fund_var.get():
                fund_id = int(self.expense_fund_var.get())
            
            # Parse expense date
            try:
                expense_date = datetime.strptime(self.expense_date_var.get(), "%Y-%m-%d")
            except ValueError:
                self.add_expense_error_var.set(self._("Invalid date format"))
                return
            
            # Validate inputs
            if amount <= 0:
                self.add_expense_error_var.set(self._("Amount must be greater than zero"))
                return
            
            if exchange_rate <= 0:
                self.add_expense_error_var.set(self._("Exchange rate must be greater than zero"))
                return
            
            # Create expense
            result, message = self.expense_controller.create_expense(
                category_id=category_id,
                amount=amount,
                expense_date=expense_date,
                currency=currency,
                exchange_rate=exchange_rate,
                description=description,
                fund_id=fund_id
            )
            
            if result:
                # Clear form
                self.expense_amount_var.set(0.0)
                self.expense_desc_var.set("")
                self.expense_date_var.set(datetime.now().strftime("%Y-%m-%d"))
                
                # Show success message
                show_notification(self._("Success"), self._("Expense added successfully"))
                
                # Refresh expenses list and switch to it
                self.refresh_expenses_list()
                self.notebook.select(0)  # Switch to expenses list tab
            else:
                # Show error message
                self.add_expense_error_var.set(message)
        
        except (ValueError, TypeError):
            self.add_expense_error_var.set(self._("Please enter valid values for all fields"))
    
    def create_categories_tab(self):
        """Create the expense categories tab"""
        tab = ttk.Frame(self.notebook, padding=10)
        
        # Create two columns layout
        columns_frame = ttk.Frame(tab)
        columns_frame.pack(fill="both", expand=True)
        
        # Left column - categories list
        left_frame = ttk.LabelFrame(columns_frame, text=self._("Categories"), padding=10)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Create treeview for categories
        columns = ("id", "name", "description")
        
        self.categories_tree = ttk.Treeview(
            left_frame,
            columns=columns,
            show="headings",
            bootstyle=INFO
        )
        
        # Define column headings
        self.categories_tree.heading("id", text=self._("ID"))
        self.categories_tree.heading("name", text=self._("Category Name"))
        self.categories_tree.heading("description", text=self._("Description"))
        
        # Define column widths
        self.categories_tree.column("id", width=50, stretch=False)
        self.categories_tree.column("name", width=150)
        self.categories_tree.column("description", width=250)
        
        # Add scrollbar
        cat_scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.categories_tree.yview)
        self.categories_tree.configure(yscrollcommand=cat_scrollbar.set)
        
        # Pack treeview and scrollbar
        self.categories_tree.pack(side="left", fill="both", expand=True)
        cat_scrollbar.pack(side="right", fill="y")
        
        # Add context menu
        self.setup_categories_context_menu()
        
        # Right column - add/edit category
        right_frame = ttk.LabelFrame(columns_frame, text=self._("Add New Category"), padding=10)
        right_frame.pack(side="right", fill="y", padx=(5, 0), pady=0)
        
        # Name field
        ttk.Label(right_frame, text=self._("Category Name:")).grid(row=0, column=0, sticky="w", pady=5)
        self.category_name_var = ttk.StringVar()
        name_entry = ttk.Entry(right_frame, textvariable=self.category_name_var, width=25)
        name_entry.grid(row=0, column=1, sticky="ew", pady=5)
        
        # Description field
        ttk.Label(right_frame, text=self._("Description:")).grid(row=1, column=0, sticky="w", pady=5)
        self.category_desc_var = ttk.StringVar()
        desc_entry = ttk.Entry(right_frame, textvariable=self.category_desc_var, width=25)
        desc_entry.grid(row=1, column=1, sticky="ew", pady=5)
        
        # Error message
        self.category_error_var = ttk.StringVar()
        error_label = ttk.Label(right_frame, textvariable=self.category_error_var, bootstyle=DANGER)
        error_label.grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)
        
        # Add button
        add_button = ttk.Button(
            right_frame,
            text=self._("Add Category"),
            command=self.add_category,
            bootstyle=SUCCESS,
            width=15
        )
        add_button.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Load categories
        self.refresh_categories()
        
        # Add tab to notebook
        self.notebook.add(tab, text=self._("Categories"))
    
    def setup_categories_context_menu(self):
        """Setup context menu for categories treeview"""
        self.category_context_menu = ttk.Menu(self.categories_tree, tearoff=0)
        self.category_context_menu.add_command(
            label=self._("Edit Category"),
            command=self.edit_selected_category
        )
        
        # Bind right-click to show context menu
        self.categories_tree.bind("<Button-3>", self.show_category_context_menu)
        # Bind double-click to edit
        self.categories_tree.bind("<Double-1>", lambda event: self.edit_selected_category())
    
    def show_category_context_menu(self, event):
        """Show context menu on right-click"""
        # Select row under mouse
        iid = self.categories_tree.identify_row(event.y)
        if iid:
            # Select this item
            self.categories_tree.selection_set(iid)
            # Display context menu
            self.category_context_menu.tk_popup(event.x_root, event.y_root)
    
    def refresh_categories(self):
        """Refresh the categories list"""
        # Clear existing items
        for item in self.categories_tree.get_children():
            self.categories_tree.delete(item)
        
        # Get all categories
        categories = self.expense_controller.get_all_categories()
        
        # Add categories to treeview
        for category in categories:
            self.categories_tree.insert(
                "",
                "end",
                values=(
                    category.id,
                    category.name,
                    category.description or ""
                )
            )
    
    def add_category(self):
        """Add a new expense category"""
        # Reset error message
        self.category_error_var.set("")
        
        # Get values
        name = self.category_name_var.get().strip()
        description = self.category_desc_var.get().strip()
        
        # Validate inputs
        if not name:
            self.category_error_var.set(self._("Category name is required"))
            return
        
        # Create category
        result, message = self.expense_controller.create_category(
            name=name,
            description=description
        )
        
        if result:
            # Clear form
            self.category_name_var.set("")
            self.category_desc_var.set("")
            
            # Show success message
            show_notification(self._("Success"), self._("Category added successfully"))
            
            # Refresh categories
            self.refresh_categories()
            
            # Also refresh the category combobox in the add expense tab
            categories = self.expense_controller.get_all_categories()
            category_choices = [(str(c.id), c.name) for c in categories]
            
            # Update the combobox in the add expense tab
            if categories:
                # Get the combobox from the add expense tab
                fields_frame = self.notebook.children['!frame3'].children['!frame2']
                category_frame = fields_frame.children['!frame']
                category_combo = category_frame.children['!combobox']
                
                # Update the values
                category_combo['values'] = [c[1] for c in category_choices]
                
                # Set to the newly added category
                self.expense_category_var.set(str(categories[-1].id))
                category_combo.current(len(categories) - 1)
        else:
            # Show error message
            self.category_error_var.set(message)
    
    def edit_selected_category(self):
        """Edit the selected category"""
        selected_items = self.categories_tree.selection()
        if not selected_items:
            return
            
        item_id = selected_items[0]
        category_id = self.categories_tree.item(item_id, "values")[0]
        
        # Get category data
        category = self.expense_controller.get_category_by_id(category_id)
        if not category:
            return
        
        # Create edit dialog
        edit_dialog = ttk.Toplevel(self.root)
        edit_dialog.title(self._("Edit Category"))
        edit_dialog.geometry("350x200")
        edit_dialog.transient(self.root)
        edit_dialog.grab_set()
        
        # Create form in the dialog
        frame = ttk.Frame(edit_dialog, padding=10)
        frame.pack(fill="both", expand=True)
        
        # Name field
        ttk.Label(frame, text=self._("Category Name:")).grid(row=0, column=0, sticky="w", pady=5)
        name_var = ttk.StringVar(value=category.name)
        name_entry = ttk.Entry(frame, textvariable=name_var, width=25)
        name_entry.grid(row=0, column=1, sticky="ew", pady=5)
        
        # Description field
        ttk.Label(frame, text=self._("Description:")).grid(row=1, column=0, sticky="w", pady=5)
        desc_var = ttk.StringVar(value=category.description or "")
        desc_entry = ttk.Entry(frame, textvariable=desc_var, width=25)
        desc_entry.grid(row=1, column=1, sticky="ew", pady=5)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=15)
        
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
            command=lambda: self.save_category_edits(
                category.id,
                name_var.get(),
                desc_var.get(),
                edit_dialog
            ),
            bootstyle=SUCCESS,
            width=10
        ).pack(side="left", padx=5)
    
    def save_category_edits(self, category_id, name, description, dialog):
        """Save edits to a category"""
        # Validate name
        if not name.strip():
            # Show error in dialog
            error_label = ttk.Label(dialog, text=self._("Category name is required"), bootstyle=DANGER)
            error_label.pack(pady=10)
            return
        
        result, message = self.expense_controller.update_category(
            category_id=category_id,
            name=name,
            description=description
        )
        
        if result:
            show_notification(self._("Success"), self._("Category updated successfully"))
            dialog.destroy()
            self.refresh_categories()
            
            # Also refresh the category combobox in the add expense tab
            categories = self.expense_controller.get_all_categories()
            category_choices = [(str(c.id), c.name) for c in categories]
            
            # Update the combobox in the add expense tab
            if categories:
                # Get the combobox from the add expense tab
                fields_frame = self.notebook.children['!frame3'].children['!frame2']
                category_frame = fields_frame.children['!frame']
                category_combo = category_frame.children['!combobox']
                
                # Update the values
                category_combo['values'] = [c[1] for c in category_choices]
        else:
            # Show error in dialog
            error_label = ttk.Label(dialog, text=message, bootstyle=DANGER)
            error_label.pack(pady=10)
