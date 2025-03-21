#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Items management view for ASSI Warehouse Management System
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import gettext
from controllers.item_controller import ItemController
from controllers.warehouse_controller import WarehouseController
from utils.notifications import show_notification

class ItemsView:
    """Items management view class"""
    
    def __init__(self, root, back_to_main_menu):
        """Initialize the items view
        
        Args:
            root: The root window
            back_to_main_menu: Callback function to return to main menu
        """
        self.root = root
        self.back_to_main_menu = back_to_main_menu
        self.item_controller = ItemController()
        self.warehouse_controller = WarehouseController()
        
        # Setup translation
        self._ = gettext.gettext
        
        # Set window title
        self.root.title(self._("ASSI WMS - Items Management"))
        
        # Create main frame
        self.frame = ttk.Frame(self.root)
        self.frame.pack(expand=True, fill="both")
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Create tabs
        self.create_items_list_tab()
        self.create_add_item_tab()
        self.create_stock_management_tab()
        self.create_stock_transfer_tab()
        
        # Add back button
        back_button = ttk.Button(
            self.frame,
            text=self._("Back to Main Menu"),
            command=self.back_to_main_menu,
            bootstyle=SECONDARY,
            width=20
        )
        back_button.pack(pady=10)
    
    def create_items_list_tab(self):
        """Create the items list tab"""
        tab = ttk.Frame(self.notebook, padding=10)
        
        # Add refresh button at the top
        refresh_frame = ttk.Frame(tab)
        refresh_frame.pack(fill="x", pady=(0, 10))
        
        refresh_button = ttk.Button(
            refresh_frame,
            text=self._("Refresh"),
            command=self.refresh_items_list,
            bootstyle=INFO,
            width=15
        )
        refresh_button.pack(side="right")
        
        # Create treeview for items list
        columns = (
            "id", "name", "main_unit", "sub_unit", "conversion", 
            "purchase_price", "selling_price", "total_stock", "status"
        )
        
        self.items_tree = ttk.Treeview(
            tab,
            columns=columns,
            show="headings",
            bootstyle=INFO
        )
        
        # Define column headings
        self.items_tree.heading("id", text=self._("ID"))
        self.items_tree.heading("name", text=self._("Item Name"))
        self.items_tree.heading("main_unit", text=self._("Main Unit"))
        self.items_tree.heading("sub_unit", text=self._("Sub Unit"))
        self.items_tree.heading("conversion", text=self._("Conversion Rate"))
        self.items_tree.heading("purchase_price", text=self._("Purchase Price"))
        self.items_tree.heading("selling_price", text=self._("Selling Price"))
        self.items_tree.heading("total_stock", text=self._("Total Stock"))
        self.items_tree.heading("status", text=self._("Status"))
        
        # Define column widths
        self.items_tree.column("id", width=50, stretch=False)
        self.items_tree.column("name", width=200)
        self.items_tree.column("main_unit", width=80, stretch=False)
        self.items_tree.column("sub_unit", width=80, stretch=False)
        self.items_tree.column("conversion", width=100, stretch=False)
        self.items_tree.column("purchase_price", width=100, stretch=False)
        self.items_tree.column("selling_price", width=100, stretch=False)
        self.items_tree.column("total_stock", width=100, stretch=False)
        self.items_tree.column("status", width=80, stretch=False)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.items_tree.yview)
        self.items_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.items_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add context menu
        self.setup_items_context_menu()
        
        # Load initial data
        self.refresh_items_list()
        
        # Add tab to notebook
        self.notebook.add(tab, text=self._("Items List"))
    
    def setup_items_context_menu(self):
        """Setup context menu for items treeview"""
        self.item_context_menu = ttk.Menu(self.items_tree, tearoff=0)
        self.item_context_menu.add_command(
            label=self._("Edit Item"),
            command=self.edit_selected_item
        )
        self.item_context_menu.add_command(
            label=self._("Deactivate Item"),
            command=self.deactivate_selected_item
        )
        self.item_context_menu.add_separator()
        self.item_context_menu.add_command(
            label=self._("View Stock Details"),
            command=self.view_stock_details
        )
        self.item_context_menu.add_command(
            label=self._("Add/Remove Stock"),
            command=self.manage_selected_item_stock
        )
        
        # Bind right-click to show context menu
        self.items_tree.bind("<Button-3>", self.show_item_context_menu)
        # Bind double-click to edit
        self.items_tree.bind("<Double-1>", lambda event: self.edit_selected_item())
    
    def show_item_context_menu(self, event):
        """Show context menu on right-click"""
        # Select row under mouse
        iid = self.items_tree.identify_row(event.y)
        if iid:
            # Select this item
            self.items_tree.selection_set(iid)
            # Display context menu
            self.item_context_menu.tk_popup(event.x_root, event.y_root)
    
    def edit_selected_item(self):
        """Open dialog to edit the selected item"""
        selected_items = self.items_tree.selection()
        if not selected_items:
            return
            
        item_id = selected_items[0]
        item_id = self.items_tree.item(item_id, "values")[0]
        
        # Get item data
        item = self.item_controller.get_item_by_id(item_id)
        if not item:
            return
            
        # Create edit dialog
        edit_dialog = ttk.Toplevel(self.root)
        edit_dialog.title(self._("Edit Item"))
        edit_dialog.geometry("500x400")
        edit_dialog.transient(self.root)
        edit_dialog.grab_set()
        
        # Create form in the dialog
        frame = ttk.Frame(edit_dialog, padding=10)
        frame.pack(fill="both", expand=True)
        
        # Name field
        ttk.Label(frame, text=self._("Item Name:")).grid(row=0, column=0, sticky="w", pady=5)
        name_var = ttk.StringVar(value=item.name)
        name_entry = ttk.Entry(frame, textvariable=name_var, width=30)
        name_entry.grid(row=0, column=1, sticky="ew", pady=5)
        
        # Description field
        ttk.Label(frame, text=self._("Description:")).grid(row=1, column=0, sticky="w", pady=5)
        description_var = ttk.StringVar(value=item.description or "")
        description_entry = ttk.Entry(frame, textvariable=description_var, width=30)
        description_entry.grid(row=1, column=1, sticky="ew", pady=5)
        
        # Main unit field
        ttk.Label(frame, text=self._("Main Unit:")).grid(row=2, column=0, sticky="w", pady=5)
        main_unit_var = ttk.StringVar(value=item.main_unit)
        main_unit_entry = ttk.Entry(frame, textvariable=main_unit_var, width=15)
        main_unit_entry.grid(row=2, column=1, sticky="w", pady=5)
        
        # Sub unit field
        ttk.Label(frame, text=self._("Sub Unit:")).grid(row=3, column=0, sticky="w", pady=5)
        sub_unit_var = ttk.StringVar(value=item.sub_unit)
        sub_unit_entry = ttk.Entry(frame, textvariable=sub_unit_var, width=15)
        sub_unit_entry.grid(row=3, column=1, sticky="w", pady=5)
        
        # Conversion rate field
        ttk.Label(frame, text=self._("Conversion Rate:")).grid(row=4, column=0, sticky="w", pady=5)
        conversion_var = ttk.DoubleVar(value=item.conversion_rate)
        conversion_entry = ttk.Entry(frame, textvariable=conversion_var, width=15)
        conversion_entry.grid(row=4, column=1, sticky="w", pady=5)
        
        # Conversion explanation
        conversion_label = ttk.Label(
            frame,
            text=self._("(How many {0} in 1 {1})").format(item.sub_unit, item.main_unit),
            font=("TkDefaultFont", 9, "italic")
        )
        conversion_label.grid(row=4, column=2, sticky="w", pady=5)
        
        # Purchase price field
        ttk.Label(frame, text=self._("Purchase Price:")).grid(row=5, column=0, sticky="w", pady=5)
        purchase_var = ttk.DoubleVar(value=item.purchase_price)
        purchase_entry = ttk.Entry(frame, textvariable=purchase_var, width=15)
        purchase_entry.grid(row=5, column=1, sticky="w", pady=5)
        
        # Selling price field
        ttk.Label(frame, text=self._("Selling Price:")).grid(row=6, column=0, sticky="w", pady=5)
        selling_var = ttk.DoubleVar(value=item.selling_price)
        selling_entry = ttk.Entry(frame, textvariable=selling_var, width=15)
        selling_entry.grid(row=6, column=1, sticky="w", pady=5)
        
        # Status field
        ttk.Label(frame, text=self._("Status:")).grid(row=7, column=0, sticky="w", pady=5)
        status_var = ttk.BooleanVar(value=item.is_active)
        status_check = ttk.Checkbutton(
            frame,
            text=self._("Active"),
            variable=status_var,
            onvalue=True,
            offvalue=False
        )
        status_check.grid(row=7, column=1, sticky="w", pady=5)
        
        # Current stock (display only)
        ttk.Label(frame, text=self._("Current Stock:")).grid(row=8, column=0, sticky="w", pady=5)
        stock_label = ttk.Label(
            frame,
            text=f"{item.get_total_stock()} {item.main_unit}",
            font=("TkDefaultFont", 10, "bold")
        )
        stock_label.grid(row=8, column=1, sticky="w", pady=5)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=9, column=0, columnspan=3, pady=15)
        
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
            command=lambda: self.save_item_edits(
                item.id,
                name_var.get(),
                description_var.get(),
                main_unit_var.get(),
                sub_unit_var.get(),
                conversion_var.get(),
                purchase_var.get(),
                selling_var.get(),
                status_var.get(),
                edit_dialog
            ),
            bootstyle=SUCCESS,
            width=10
        ).pack(side="left", padx=5)
    
    def save_item_edits(self, item_id, name, description, main_unit, sub_unit, 
                         conversion_rate, purchase_price, selling_price, is_active, dialog):
        """Save edits to an item"""
        result, message = self.item_controller.update_item(
            item_id=item_id,
            name=name,
            description=description,
            main_unit=main_unit,
            sub_unit=sub_unit,
            conversion_rate=conversion_rate,
            purchase_price=purchase_price,
            selling_price=selling_price,
            is_active=is_active
        )
        
        if result:
            show_notification(self._("Success"), self._("Item updated successfully"))
            dialog.destroy()
            self.refresh_items_list()
        else:
            # Show error in dialog
            error_label = ttk.Label(dialog, text=message, bootstyle=DANGER)
            error_label.pack(pady=10)
    
    def deactivate_selected_item(self):
        """Deactivate the selected item"""
        selected_items = self.items_tree.selection()
        if not selected_items:
            return
            
        item_id = selected_items[0]
        item_id = self.items_tree.item(item_id, "values")[0]
        
        # Confirm deactivation
        confirm = ttk.Messagebox.yesno(
            title=self._("Confirm Deactivation"),
            message=self._("Are you sure you want to deactivate this item?")
        )
        
        if confirm == "No":
            return
            
        # Deactivate item
        result, _ = self.item_controller.update_item(
            item_id=item_id,
            is_active=False
        )
        
        if result:
            show_notification(self._("Success"), self._("Item deactivated successfully"))
            self.refresh_items_list()
    
    def view_stock_details(self):
        """View stock details for the selected item"""
        selected_items = self.items_tree.selection()
        if not selected_items:
            return
            
        item_id = selected_items[0]
        item_id = self.items_tree.item(item_id, "values")[0]
        
        # Get item
        item = self.item_controller.get_item_by_id(item_id)
        if not item:
            return
        
        # Get stock information
        stocks = self.item_controller.get_item_stock(item_id)
        
        # Create dialog
        dialog = ttk.Toplevel(self.root)
        dialog.title(self._("Stock Details for {0}").format(item.name))
        dialog.geometry("500x400")
        dialog.transient(self.root)
        
        # Create frame
        frame = ttk.Frame(dialog, padding=10)
        frame.pack(fill="both", expand=True)
        
        # Item details at the top
        details_frame = ttk.Frame(frame)
        details_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(
            details_frame,
            text=item.name,
            font=("TkDefaultFont", 14, "bold")
        ).pack(anchor="w")
        
        ttk.Label(
            details_frame,
            text=self._("Main Unit: {0}, Sub Unit: {1}, Conversion: 1 {0} = {2} {1}").format(
                item.main_unit, item.sub_unit, item.conversion_rate
            )
        ).pack(anchor="w", pady=5)
        
        ttk.Label(
            details_frame,
            text=self._("Total Stock: {0} {1} ({2:.1f} {3})").format(
                item.get_total_stock(), item.main_unit,
                item.get_total_stock() * item.conversion_rate, item.sub_unit
            ),
            font=("TkDefaultFont", 10, "bold")
        ).pack(anchor="w")
        
        # Create treeview for stock by warehouse
        columns = ("warehouse_id", "warehouse", "quantity", "sub_quantity", "last_updated")
        
        stock_tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            bootstyle=INFO
        )
        
        # Define column headings
        stock_tree.heading("warehouse_id", text=self._("ID"))
        stock_tree.heading("warehouse", text=self._("Warehouse"))
        stock_tree.heading("quantity", text=self._("Quantity ({0})").format(item.main_unit))
        stock_tree.heading("sub_quantity", text=self._("Quantity ({0})").format(item.sub_unit))
        stock_tree.heading("last_updated", text=self._("Last Updated"))
        
        # Define column widths
        stock_tree.column("warehouse_id", width=50, stretch=False)
        stock_tree.column("warehouse", width=150)
        stock_tree.column("quantity", width=100, stretch=False)
        stock_tree.column("sub_quantity", width=100, stretch=False)
        stock_tree.column("last_updated", width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=stock_tree.yview)
        stock_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        stock_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Get warehouse names
        warehouses = self.warehouse_controller.get_all_warehouses(active_only=False)
        warehouse_dict = {w.id: w.name for w in warehouses}
        
        # Add stocks to treeview
        for stock in stocks:
            warehouse_name = warehouse_dict.get(stock.warehouse_id, str(stock.warehouse_id))
            
            # Calculate sub-unit quantity
            sub_quantity = stock.quantity * item.conversion_rate
            
            stock_tree.insert(
                "",
                "end",
                values=(
                    stock.warehouse_id,
                    warehouse_name,
                    f"{stock.quantity:.2f}",
                    f"{sub_quantity:.2f}",
                    stock.updated_at.strftime("%Y-%m-%d %H:%M") if stock.updated_at else ""
                )
            )
        
        # Add a close button
        ttk.Button(
            dialog,
            text=self._("Close"),
            command=dialog.destroy,
            bootstyle=SECONDARY,
            width=15
        ).pack(pady=10)
    
    def manage_selected_item_stock(self):
        """Open stock management tab for the selected item"""
        selected_items = self.items_tree.selection()
        if not selected_items:
            return
            
        item_id = selected_items[0]
        item_id = self.items_tree.item(item_id, "values")[0]
        
        # Switch to stock management tab
        self.notebook.select(2)  # Index of stock management tab
        
        # Set the selected item in the combobox
        items = self.item_controller.get_all_items()
        for i, item in enumerate(items):
            if str(item.id) == item_id:
                self.stock_item_combo.current(i)
                # Trigger the event to update UI
                self.update_stock_management_ui()
                break
    
    def refresh_items_list(self):
        """Refresh the items list"""
        # Clear existing items
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
        
        # Get all items
        items = self.item_controller.get_all_items(active_only=False)
        
        # Add items to treeview
        for item in items:
            # Get total stock
            total_stock = item.get_total_stock()
            
            # Add status indicator
            status = self._("Active") if item.is_active else self._("Inactive")
            
            self.items_tree.insert(
                "",
                "end",
                values=(
                    item.id,
                    item.name,
                    item.main_unit,
                    item.sub_unit,
                    f"1:{item.conversion_rate}",
                    f"{item.purchase_price:.2f}",
                    f"{item.selling_price:.2f}",
                    f"{total_stock:.2f}",
                    status
                )
            )
    
    def create_add_item_tab(self):
        """Create the add item tab"""
        tab = ttk.Frame(self.notebook, padding=10)
        
        # Create form
        form_frame = ttk.Frame(tab)
        form_frame.pack(fill="both", expand=True)
        
        # Add a title
        title_label = ttk.Label(
            form_frame,
            text=self._("Add New Item"),
            font=("TkDefaultFont", 14, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Create input fields
        fields_frame = ttk.Frame(form_frame)
        fields_frame.pack(fill="x")
        
        # Name field
        name_frame = ttk.Frame(fields_frame)
        name_frame.pack(fill="x", pady=10)
        
        ttk.Label(name_frame, text=self._("Item Name:"), width=15).pack(side="left")
        self.item_name_var = ttk.StringVar()
        name_entry = ttk.Entry(name_frame, textvariable=self.item_name_var, width=30)
        name_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Description field
        desc_frame = ttk.Frame(fields_frame)
        desc_frame.pack(fill="x", pady=10)
        
        ttk.Label(desc_frame, text=self._("Description:"), width=15).pack(side="left")
        self.item_desc_var = ttk.StringVar()
        desc_entry = ttk.Entry(desc_frame, textvariable=self.item_desc_var, width=30)
        desc_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Main unit field
        main_unit_frame = ttk.Frame(fields_frame)
        main_unit_frame.pack(fill="x", pady=10)
        
        ttk.Label(main_unit_frame, text=self._("Main Unit:"), width=15).pack(side="left")
        self.main_unit_var = ttk.StringVar(value="bag")
        main_unit_entry = ttk.Entry(main_unit_frame, textvariable=self.main_unit_var, width=15)
        main_unit_entry.pack(side="left", padx=5)
        
        # Sub unit field
        sub_unit_frame = ttk.Frame(fields_frame)
        sub_unit_frame.pack(fill="x", pady=10)
        
        ttk.Label(sub_unit_frame, text=self._("Sub Unit:"), width=15).pack(side="left")
        self.sub_unit_var = ttk.StringVar(value="kg")
        sub_unit_entry = ttk.Entry(sub_unit_frame, textvariable=self.sub_unit_var, width=15)
        sub_unit_entry.pack(side="left", padx=5)
        
        # Conversion rate field
        conversion_frame = ttk.Frame(fields_frame)
        conversion_frame.pack(fill="x", pady=10)
        
        ttk.Label(conversion_frame, text=self._("Conversion Rate:"), width=15).pack(side="left")
        self.conversion_var = ttk.DoubleVar(value=50.0)
        conversion_entry = ttk.Entry(conversion_frame, textvariable=self.conversion_var, width=15)
        conversion_entry.pack(side="left", padx=5)
        
        ttk.Label(
            conversion_frame,
            text=self._("(e.g., 1 bag = 50 kg)"),
            font=("TkDefaultFont", 9, "italic")
        ).pack(side="left", padx=5)
        
        # Purchase price field
        purchase_frame = ttk.Frame(fields_frame)
        purchase_frame.pack(fill="x", pady=10)
        
        ttk.Label(purchase_frame, text=self._("Purchase Price:"), width=15).pack(side="left")
        self.purchase_var = ttk.DoubleVar(value=0.0)
        purchase_entry = ttk.Entry(purchase_frame, textvariable=self.purchase_var, width=15)
        purchase_entry.pack(side="left", padx=5)
        
        # Selling price field
        selling_frame = ttk.Frame(fields_frame)
        selling_frame.pack(fill="x", pady=10)
        
        ttk.Label(selling_frame, text=self._("Selling Price:"), width=15).pack(side="left")
        self.selling_var = ttk.DoubleVar(value=0.0)
        selling_entry = ttk.Entry(selling_frame, textvariable=self.selling_var, width=15)
        selling_entry.pack(side="left", padx=5)
        
        # Add error label (hidden initially)
        self.add_item_error_var = ttk.StringVar()
        self.add_item_error_label = ttk.Label(
            fields_frame,
            textvariable=self.add_item_error_var,
            bootstyle=DANGER
        )
        self.add_item_error_label.pack(pady=10, fill="x")
        
        # Add submit button
        submit_button = ttk.Button(
            fields_frame,
            text=self._("Add Item"),
            command=self.add_item,
            bootstyle=SUCCESS,
            width=20
        )
        submit_button.pack(pady=15)
        
        # Add tab to notebook
        self.notebook.add(tab, text=self._("Add Item"))
    
    def add_item(self):
        """Add a new item"""
        # Reset error message
        self.add_item_error_var.set("")
        
        # Get values
        name = self.item_name_var.get().strip()
        description = self.item_desc_var.get().strip()
        main_unit = self.main_unit_var.get().strip()
        sub_unit = self.sub_unit_var.get().strip()
        
        try:
            conversion_rate = float(self.conversion_var.get())
            purchase_price = float(self.purchase_var.get())
            selling_price = float(self.selling_var.get())
        except (ValueError, tkinter.TclError):
            self.add_item_error_var.set(self._("Please enter valid numbers for rates and prices"))
            return
        
        # Validate inputs
        if not name:
            self.add_item_error_var.set(self._("Item name is required"))
            return
        
        if not main_unit:
            self.add_item_error_var.set(self._("Main unit is required"))
            return
        
        if not sub_unit:
            self.add_item_error_var.set(self._("Sub unit is required"))
            return
        
        if conversion_rate <= 0:
            self.add_item_error_var.set(self._("Conversion rate must be greater than zero"))
            return
        
        if purchase_price < 0:
            self.add_item_error_var.set(self._("Purchase price cannot be negative"))
            return
        
        if selling_price < 0:
            self.add_item_error_var.set(self._("Selling price cannot be negative"))
            return
        
        # Create item
        result, message = self.item_controller.create_item(
            name=name,
            main_unit=main_unit,
            sub_unit=sub_unit,
            conversion_rate=conversion_rate,
            purchase_price=purchase_price,
            selling_price=selling_price,
            description=description
        )
        
        if result:
            # Clear form
            self.item_name_var.set("")
            self.item_desc_var.set("")
            self.main_unit_var.set("bag")
            self.sub_unit_var.set("kg")
            self.conversion_var.set(50.0)
            self.purchase_var.set(0.0)
            self.selling_var.set(0.0)
            
            # Show success message
            show_notification(self._("Success"), self._("Item added successfully"))
            
            # Refresh items list and switch to it
            self.refresh_items_list()
            self.notebook.select(0)  # Switch to items list tab
        else:
            # Show error message
            self.add_item_error_var.set(message)
    
    def create_stock_management_tab(self):
        """Create the stock management tab"""
        tab = ttk.Frame(self.notebook, padding=10)
        
        # Top section for item selection
        selection_frame = ttk.Frame(tab)
        selection_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(selection_frame, text=self._("Select Item:")).pack(side="left", padx=(0, 10))
        
        # Get all items for combobox
        items = self.item_controller.get_all_items()
        item_choices = [(item.id, f"{item.name} ({item.main_unit})") for item in items]
        
        self.stock_item_var = ttk.StringVar()
        if item_choices:
            self.stock_item_var.set(str(item_choices[0][0]))
        
        self.stock_item_combo = ttk.Combobox(
            selection_frame,
            values=[f"{item[1]}" for item in item_choices],
            width=40
        )
        self.stock_item_combo.pack(side="left", fill="x", expand=True)
        
        # Update UI when selection changes
        self.stock_item_combo.bind("<<ComboboxSelected>>", lambda e: self.update_stock_management_ui())
        
        # Middle section for item details and warehouse selection
        details_frame = ttk.LabelFrame(tab, text=self._("Item Details"), padding=10)
        details_frame.pack(fill="x", pady=10)
        
        # Item details (will be populated dynamically)
        self.item_details_frame = ttk.Frame(details_frame)
        self.item_details_frame.pack(fill="x", pady=5)
        
        self.item_name_label = ttk.Label(self.item_details_frame, text="")
        self.item_name_label.pack(anchor="w", pady=2)
        
        self.item_units_label = ttk.Label(self.item_details_frame, text="")
        self.item_units_label.pack(anchor="w", pady=2)
        
        self.item_stock_label = ttk.Label(self.item_details_frame, text="")
        self.item_stock_label.pack(anchor="w", pady=2)
        
        # Warehouse selection
        warehouse_frame = ttk.Frame(details_frame)
        warehouse_frame.pack(fill="x", pady=10)
        
        ttk.Label(warehouse_frame, text=self._("Warehouse:")).pack(side="left", padx=(0, 10))
        
        # Get all warehouses for combobox
        warehouses = self.warehouse_controller.get_all_warehouses()
        warehouse_choices = [(w.id, w.name) for w in warehouses]
        
        self.stock_warehouse_var = ttk.StringVar()
        if warehouse_choices:
            self.stock_warehouse_var.set(str(warehouse_choices[0][0]))
        
        warehouse_combo = ttk.Combobox(
            warehouse_frame,
            values=[f"{w[1]}" for w in warehouse_choices],
            width=30
        )
        warehouse_combo.pack(side="left", fill="x", expand=True)
        
        # Bottom section for quantity adjustment
        adjustment_frame = ttk.LabelFrame(tab, text=self._("Stock Adjustment"), padding=10)
        adjustment_frame.pack(fill="x", pady=10)
        
        # Quantity adjustment
        amount_frame = ttk.Frame(adjustment_frame)
        amount_frame.pack(fill="x", pady=10)
        
        ttk.Label(amount_frame, text=self._("Adjustment Type:")).pack(side="left", padx=(0, 10))
        
        self.adjustment_type_var = ttk.StringVar(value="add")
        ttk.Radiobutton(
            amount_frame,
            text=self._("Add Stock"),
            variable=self.adjustment_type_var,
            value="add"
        ).pack(side="left", padx=10)
        
        ttk.Radiobutton(
            amount_frame,
            text=self._("Remove Stock"),
            variable=self.adjustment_type_var,
            value="remove"
        ).pack(side="left", padx=10)
        
        # Quantity input
        quantity_frame = ttk.Frame(adjustment_frame)
        quantity_frame.pack(fill="x", pady=10)
        
        ttk.Label(quantity_frame, text=self._("Quantity:")).pack(side="left", padx=(0, 10))
        
        self.adjustment_quantity_var = ttk.DoubleVar(value=0.0)
        quantity_entry = ttk.Entry(
            quantity_frame,
            textvariable=self.adjustment_quantity_var,
            width=15
        )
        quantity_entry.pack(side="left", padx=5)
        
        # Unit selection
        self.adjustment_unit_var = ttk.StringVar(value="main")
        self.main_unit_radio = ttk.Radiobutton(
            quantity_frame,
            text="",  # Will be set dynamically
            variable=self.adjustment_unit_var,
            value="main"
        )
        self.main_unit_radio.pack(side="left", padx=10)
        
        self.sub_unit_radio = ttk.Radiobutton(
            quantity_frame,
            text="",  # Will be set dynamically
            variable=self.adjustment_unit_var,
            value="sub"
        )
        self.sub_unit_radio.pack(side="left", padx=10)
        
        # Notes
        notes_frame = ttk.Frame(adjustment_frame)
        notes_frame.pack(fill="x", pady=10)
        
        ttk.Label(notes_frame, text=self._("Notes:")).pack(side="left", padx=(0, 10))
        
        self.adjustment_notes_var = ttk.StringVar()
        notes_entry = ttk.Entry(
            notes_frame,
            textvariable=self.adjustment_notes_var,
            width=40
        )
        notes_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Error/message label
        self.stock_message_var = ttk.StringVar()
        message_label = ttk.Label(
            adjustment_frame,
            textvariable=self.stock_message_var
        )
        message_label.pack(fill="x", pady=10)
        
        # Submit button
        submit_button = ttk.Button(
            adjustment_frame,
            text=self._("Apply Adjustment"),
            command=self.apply_stock_adjustment,
            bootstyle=SUCCESS,
            width=20
        )
        submit_button.pack(pady=10)
        
        # Initialize UI with first item
        if items:
            self.stock_item_combo.current(0)
            self.update_stock_management_ui()
        
        # Add tab to notebook
        self.notebook.add(tab, text=self._("Stock Management"))
    
    def update_stock_management_ui(self):
        """Update the stock management UI based on selected item"""
        # Get selected item index
        selected_index = self.stock_item_combo.current()
        if selected_index < 0:
            return
        
        # Get all items and find the selected one
        items = self.item_controller.get_all_items()
        if selected_index >= len(items):
            return
        
        item = items[selected_index]
        
        # Update item details
        self.item_name_label.config(
            text=f"{item.name}",
            font=("TkDefaultFont", 12, "bold")
        )
        
        self.item_units_label.config(
            text=self._("Main Unit: {0}, Sub Unit: {1}, Conversion: 1 {0} = {2} {1}").format(
                item.main_unit, item.sub_unit, item.conversion_rate
            )
        )
        
        self.item_stock_label.config(
            text=self._("Total Stock: {0} {1} ({2:.1f} {3})").format(
                item.get_total_stock(), item.main_unit,
                item.get_total_stock() * item.conversion_rate, item.sub_unit
            )
        )
        
        # Update unit radio buttons
        self.main_unit_radio.config(text=item.main_unit)
        self.sub_unit_radio.config(text=item.sub_unit)
    
    def apply_stock_adjustment(self):
        """Apply the stock adjustment"""
        # Reset message
        self.stock_message_var.set("")
        
        try:
            # Get selected item
            selected_index = self.stock_item_combo.current()
            if selected_index < 0:
                self.stock_message_var.set(self._("Please select an item"))
                return
            
            items = self.item_controller.get_all_items()
            item = items[selected_index]
            
            # Get selected warehouse
            warehouse_id = int(self.stock_warehouse_var.get())
            
            # Get adjustment quantity and type
            quantity = float(self.adjustment_quantity_var.get())
            if quantity <= 0:
                self.stock_message_var.set(self._("Quantity must be greater than zero"))
                return
            
            # Convert to main unit if sub unit was selected
            if self.adjustment_unit_var.get() == "sub":
                quantity = quantity / item.conversion_rate
            
            # Apply adjustment based on type
            if self.adjustment_type_var.get() == "add":
                result, message = self.item_controller.update_stock(
                    item_id=item.id,
                    warehouse_id=warehouse_id,
                    quantity_change=quantity
                )
            else:  # remove
                result, message = self.item_controller.update_stock(
                    item_id=item.id,
                    warehouse_id=warehouse_id,
                    quantity_change=-quantity
                )
            
            if result:
                # Success
                self.stock_message_var.set(self._("Stock updated successfully"))
                # Reset form
                self.adjustment_quantity_var.set(0.0)
                self.adjustment_notes_var.set("")
                # Update UI
                self.update_stock_management_ui()
                # Refresh items list
                self.refresh_items_list()
                # Show notification
                if self.adjustment_type_var.get() == "add":
                    show_notification(
                        self._("Stock Added"),
                        self._("{0} {1} added to {2}").format(
                            quantity, item.main_unit, self.stock_item_combo.get().split(" (")[0]
                        )
                    )
                else:
                    show_notification(
                        self._("Stock Removed"),
                        self._("{0} {1} removed from {2}").format(
                            quantity, item.main_unit, self.stock_item_combo.get().split(" (")[0]
                        )
                    )
            else:
                # Error
                self.stock_message_var.set(message)
        
        except ValueError:
            self.stock_message_var.set(self._("Please enter valid numeric values"))
    
    def create_stock_transfer_tab(self):
        """Create the stock transfer tab"""
        tab = ttk.Frame(self.notebook, padding=10)
        
        # Add a title
        title_label = ttk.Label(
            tab,
            text=self._("Transfer Stock Between Warehouses"),
            font=("TkDefaultFont", 14, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Create form
        form_frame = ttk.Frame(tab)
        form_frame.pack(fill="x")
        
        # Item selection
        item_frame = ttk.Frame(form_frame)
        item_frame.pack(fill="x", pady=10)
        
        ttk.Label(item_frame, text=self._("Item:"), width=15).pack(side="left")
        
        # Get all items for combobox
        items = self.item_controller.get_all_items()
        item_choices = [(item.id, f"{item.name} ({item.main_unit})") for item in items]
        
        self.transfer_item_var = ttk.StringVar()
        if item_choices:
            self.transfer_item_var.set(str(item_choices[0][0]))
        
        transfer_item_combo = ttk.Combobox(
            item_frame,
            values=[f"{item[1]}" for item in item_choices],
            width=30
        )
        transfer_item_combo.pack(side="left", padx=5, fill="x", expand=True)
        transfer_item_combo.current(0)
        
        # Source warehouse selection
        source_frame = ttk.Frame(form_frame)
        source_frame.pack(fill="x", pady=10)
        
        ttk.Label(source_frame, text=self._("From Warehouse:"), width=15).pack(side="left")
        
        # Get all warehouses for combobox
        warehouses = self.warehouse_controller.get_all_warehouses()
        warehouse_choices = [(w.id, w.name) for w in warehouses]
        
        self.source_warehouse_var = ttk.StringVar()
        if warehouse_choices:
            self.source_warehouse_var.set(str(warehouse_choices[0][0]))
        
        source_combo = ttk.Combobox(
            source_frame,
            values=[f"{w[1]}" for w in warehouse_choices],
            width=30
        )
        source_combo.pack(side="left", padx=5, fill="x", expand=True)
        if warehouse_choices:
            source_combo.current(0)
        
        # Destination warehouse selection
        dest_frame = ttk.Frame(form_frame)
        dest_frame.pack(fill="x", pady=10)
        
        ttk.Label(dest_frame, text=self._("To Warehouse:"), width=15).pack(side="left")
        
        self.dest_warehouse_var = ttk.StringVar()
        if len(warehouse_choices) > 1:
            self.dest_warehouse_var.set(str(warehouse_choices[1][0]))
        elif warehouse_choices:
            self.dest_warehouse_var.set(str(warehouse_choices[0][0]))
        
        dest_combo = ttk.Combobox(
            dest_frame,
            values=[f"{w[1]}" for w in warehouse_choices],
            width=30
        )
        dest_combo.pack(side="left", padx=5, fill="x", expand=True)
        if len(warehouse_choices) > 1:
            dest_combo.current(1)
        elif warehouse_choices:
            dest_combo.current(0)
        
        # Quantity field
        quantity_frame = ttk.Frame(form_frame)
        quantity_frame.pack(fill="x", pady=10)
        
        ttk.Label(quantity_frame, text=self._("Quantity:"), width=15).pack(side="left")
        
        self.transfer_quantity_var = ttk.DoubleVar(value=0.0)
        quantity_entry = ttk.Entry(
            quantity_frame,
            textvariable=self.transfer_quantity_var,
            width=15
        )
        quantity_entry.pack(side="left", padx=5)
        
        # Get selected item for unit options
        if items:
            selected_item = items[0]
            
            # Unit selection
            self.transfer_unit_var = ttk.StringVar(value="main")
            main_unit_radio = ttk.Radiobutton(
                quantity_frame,
                text=selected_item.main_unit,
                variable=self.transfer_unit_var,
                value="main"
            )
            main_unit_radio.pack(side="left", padx=10)
            
            sub_unit_radio = ttk.Radiobutton(
                quantity_frame,
                text=selected_item.sub_unit,
                variable=self.transfer_unit_var,
                value="sub"
            )
            sub_unit_radio.pack(side="left", padx=10)
            
            # Update unit labels when item changes
            def update_unit_labels(event):
                selected_index = transfer_item_combo.current()
                if selected_index >= 0 and selected_index < len(items):
                    item = items[selected_index]
                    main_unit_radio.config(text=item.main_unit)
                    sub_unit_radio.config(text=item.sub_unit)
            
            transfer_item_combo.bind("<<ComboboxSelected>>", update_unit_labels)
        
        # Notes field
        notes_frame = ttk.Frame(form_frame)
        notes_frame.pack(fill="x", pady=10)
        
        ttk.Label(notes_frame, text=self._("Notes:"), width=15).pack(side="left")
        
        self.transfer_notes_var = ttk.StringVar()
        notes_entry = ttk.Entry(
            notes_frame,
            textvariable=self.transfer_notes_var,
            width=40
        )
        notes_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Add error/success message label
        self.transfer_message_var = ttk.StringVar()
        self.transfer_message_label = ttk.Label(
            form_frame,
            textvariable=self.transfer_message_var
        )
        self.transfer_message_label.pack(pady=10, fill="x")
        
        # Add submit button
        submit_button = ttk.Button(
            form_frame,
            text=self._("Transfer Stock"),
            command=self.transfer_stock,
            bootstyle=SUCCESS,
            width=20
        )
        submit_button.pack(pady=15)
        
        # Add tab to notebook
        self.notebook.add(tab, text=self._("Stock Transfer"))
    
    def transfer_stock(self):
        """Transfer stock between warehouses"""
        # Reset message
        self.transfer_message_var.set("")
        self.transfer_message_label.configure(bootstyle="")
        
        try:
            # Get selected item
            selected_index = self.stock_item_combo.current()
            if selected_index < 0:
                self.transfer_message_var.set(self._("Please select an item"))
                self.transfer_message_label.configure(bootstyle=DANGER)
                return
            
            items = self.item_controller.get_all_items()
            item = items[selected_index]
            
            # Get warehouses
            source_id = int(self.source_warehouse_var.get())
            dest_id = int(self.dest_warehouse_var.get())
            
            if source_id == dest_id:
                self.transfer_message_var.set(self._("Source and destination warehouses must be different"))
                self.transfer_message_label.configure(bootstyle=DANGER)
                return
            
            # Get quantity
            quantity = float(self.transfer_quantity_var.get())
            if quantity <= 0:
                self.transfer_message_var.set(self._("Quantity must be greater than zero"))
                self.transfer_message_label.configure(bootstyle=DANGER)
                return
            
            # Convert to main unit if sub unit was selected
            if self.transfer_unit_var.get() == "sub":
                quantity = quantity / item.conversion_rate
            
            # Perform transfer
            result, message = self.item_controller.transfer_stock(
                item_id=item.id,
                from_warehouse_id=source_id,
                to_warehouse_id=dest_id,
                quantity=quantity
            )
            
            if result:
                # Success
                self.transfer_message_var.set(self._("Stock transferred successfully"))
                self.transfer_message_label.configure(bootstyle=SUCCESS)
                
                # Reset form
                self.transfer_quantity_var.set(0.0)
                self.transfer_notes_var.set("")
                
                # Update UI and refresh
                self.update_stock_management_ui()
                self.refresh_items_list()
                
                # Show notification
                show_notification(
                    self._("Stock Transferred"),
                    self._("{0} {1} transferred successfully").format(
                        quantity, item.main_unit
                    )
                )
            else:
                # Error
                self.transfer_message_var.set(message)
                self.transfer_message_label.configure(bootstyle=DANGER)
        
        except ValueError:
            self.transfer_message_var.set(self._("Please enter valid numeric values"))
            self.transfer_message_label.configure(bootstyle=DANGER)
