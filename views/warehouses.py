#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Warehouses management view for ASSI Warehouse Management System
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import gettext
from controllers.warehouse_controller import WarehouseController
from controllers.item_controller import ItemController
from utils.notifications import show_notification

class WarehousesView:
    """Warehouses management view class"""
    
    def __init__(self, root, back_to_main_menu):
        """Initialize the warehouses view
        
        Args:
            root: The root window
            back_to_main_menu: Callback function to return to main menu
        """
        self.root = root
        self.back_to_main_menu = back_to_main_menu
        self.warehouse_controller = WarehouseController()
        self.item_controller = ItemController()
        
        # Setup translation
        self._ = gettext.gettext
        
        # Set window title
        self.root.title(self._("ASSI WMS - Warehouses Management"))
        
        # Create main frame
        self.frame = ttk.Frame(self.root)
        self.frame.pack(expand=True, fill="both")
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Create tabs
        self.create_warehouses_list_tab()
        self.create_add_warehouse_tab()
        self.create_inventory_tab()
        
        # Add back button
        back_button = ttk.Button(
            self.frame,
            text=self._("Back to Main Menu"),
            command=self.back_to_main_menu,
            bootstyle=SECONDARY,
            width=20
        )
        back_button.pack(pady=10)
    
    def create_warehouses_list_tab(self):
        """Create the warehouses list tab"""
        tab = ttk.Frame(self.notebook, padding=10)
        
        # Add refresh button at the top
        refresh_frame = ttk.Frame(tab)
        refresh_frame.pack(fill="x", pady=(0, 10))
        
        refresh_button = ttk.Button(
            refresh_frame,
            text=self._("Refresh"),
            command=self.refresh_warehouses_list,
            bootstyle=INFO,
            width=15
        )
        refresh_button.pack(side="right")
        
        # Create treeview for warehouses list
        columns = (
            "id", "name", "location", "item_count", "total_value", "status"
        )
        
        self.warehouses_tree = ttk.Treeview(
            tab,
            columns=columns,
            show="headings",
            bootstyle=INFO
        )
        
        # Define column headings
        self.warehouses_tree.heading("id", text=self._("ID"))
        self.warehouses_tree.heading("name", text=self._("Warehouse Name"))
        self.warehouses_tree.heading("location", text=self._("Location"))
        self.warehouses_tree.heading("item_count", text=self._("Item Count"))
        self.warehouses_tree.heading("total_value", text=self._("Inventory Value"))
        self.warehouses_tree.heading("status", text=self._("Status"))
        
        # Define column widths
        self.warehouses_tree.column("id", width=50, stretch=False)
        self.warehouses_tree.column("name", width=200)
        self.warehouses_tree.column("location", width=200)
        self.warehouses_tree.column("item_count", width=100, stretch=False)
        self.warehouses_tree.column("total_value", width=150, stretch=False)
        self.warehouses_tree.column("status", width=100, stretch=False)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.warehouses_tree.yview)
        self.warehouses_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.warehouses_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add context menu
        self.setup_warehouses_context_menu()
        
        # Load initial data
        self.refresh_warehouses_list()
        
        # Add tab to notebook
        self.notebook.add(tab, text=self._("Warehouses List"))
    
    def setup_warehouses_context_menu(self):
        """Setup context menu for warehouses treeview"""
        self.warehouse_context_menu = ttk.Menu(self.warehouses_tree, tearoff=0)
        self.warehouse_context_menu.add_command(
            label=self._("Edit Warehouse"),
            command=self.edit_selected_warehouse
        )
        self.warehouse_context_menu.add_command(
            label=self._("Deactivate Warehouse"),
            command=self.deactivate_selected_warehouse
        )
        self.warehouse_context_menu.add_separator()
        self.warehouse_context_menu.add_command(
            label=self._("View Inventory"),
            command=self.view_warehouse_inventory
        )
        
        # Bind right-click to show context menu
        self.warehouses_tree.bind("<Button-3>", self.show_warehouse_context_menu)
        # Bind double-click to edit
        self.warehouses_tree.bind("<Double-1>", lambda event: self.edit_selected_warehouse())
    
    def show_warehouse_context_menu(self, event):
        """Show context menu on right-click"""
        # Select row under mouse
        iid = self.warehouses_tree.identify_row(event.y)
        if iid:
            # Select this item
            self.warehouses_tree.selection_set(iid)
            # Display context menu
            self.warehouse_context_menu.tk_popup(event.x_root, event.y_root)
    
    def edit_selected_warehouse(self):
        """Open dialog to edit the selected warehouse"""
        selected_items = self.warehouses_tree.selection()
        if not selected_items:
            return
            
        item_id = selected_items[0]
        warehouse_id = self.warehouses_tree.item(item_id, "values")[0]
        
        # Get warehouse data
        warehouse = self.warehouse_controller.get_warehouse_by_id(warehouse_id)
        if not warehouse:
            return
            
        # Create edit dialog
        edit_dialog = ttk.Toplevel(self.root)
        edit_dialog.title(self._("Edit Warehouse"))
        edit_dialog.geometry("400x300")
        edit_dialog.transient(self.root)
        edit_dialog.grab_set()
        
        # Create form in the dialog
        frame = ttk.Frame(edit_dialog, padding=10)
        frame.pack(fill="both", expand=True)
        
        # Name field
        ttk.Label(frame, text=self._("Warehouse Name:")).grid(row=0, column=0, sticky="w", pady=5)
        name_var = ttk.StringVar(value=warehouse.name)
        name_entry = ttk.Entry(frame, textvariable=name_var, width=30)
        name_entry.grid(row=0, column=1, sticky="ew", pady=5)
        
        # Location field
        ttk.Label(frame, text=self._("Location:")).grid(row=1, column=0, sticky="w", pady=5)
        location_var = ttk.StringVar(value=warehouse.location or "")
        location_entry = ttk.Entry(frame, textvariable=location_var, width=30)
        location_entry.grid(row=1, column=1, sticky="ew", pady=5)
        
        # Description field
        ttk.Label(frame, text=self._("Description:")).grid(row=2, column=0, sticky="w", pady=5)
        description_var = ttk.StringVar(value=warehouse.description or "")
        description_entry = ttk.Entry(frame, textvariable=description_var, width=30)
        description_entry.grid(row=2, column=1, sticky="ew", pady=5)
        
        # Status field
        ttk.Label(frame, text=self._("Status:")).grid(row=3, column=0, sticky="w", pady=5)
        status_var = ttk.BooleanVar(value=warehouse.is_active)
        status_check = ttk.Checkbutton(
            frame,
            text=self._("Active"),
            variable=status_var,
            onvalue=True,
            offvalue=False
        )
        status_check.grid(row=3, column=1, sticky="w", pady=5)
        
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
            command=lambda: self.save_warehouse_edits(
                warehouse.id,
                name_var.get(),
                location_var.get(),
                description_var.get(),
                status_var.get(),
                edit_dialog
            ),
            bootstyle=SUCCESS,
            width=10
        ).pack(side="left", padx=5)
    
    def save_warehouse_edits(self, warehouse_id, name, location, description, is_active, dialog):
        """Save edits to a warehouse"""
        result, message = self.warehouse_controller.update_warehouse(
            warehouse_id=warehouse_id,
            name=name,
            location=location,
            description=description,
            is_active=is_active
        )
        
        if result:
            show_notification(self._("Success"), self._("Warehouse updated successfully"))
            dialog.destroy()
            self.refresh_warehouses_list()
        else:
            # Show error in dialog
            error_label = ttk.Label(dialog, text=message, bootstyle=DANGER)
            error_label.pack(pady=10)
    
    def deactivate_selected_warehouse(self):
        """Deactivate the selected warehouse"""
        selected_items = self.warehouses_tree.selection()
        if not selected_items:
            return
            
        item_id = selected_items[0]
        warehouse_id = self.warehouses_tree.item(item_id, "values")[0]
        
        # Confirm deactivation
        confirm = ttk.Messagebox.yesno(
            title=self._("Confirm Deactivation"),
            message=self._("Are you sure you want to deactivate this warehouse?")
        )
        
        if confirm == "No":
            return
            
        # Deactivate warehouse
        result, _ = self.warehouse_controller.update_warehouse(
            warehouse_id=warehouse_id,
            is_active=False
        )
        
        if result:
            show_notification(self._("Success"), self._("Warehouse deactivated successfully"))
            self.refresh_warehouses_list()
    
    def view_warehouse_inventory(self):
        """Switch to inventory tab for the selected warehouse"""
        selected_items = self.warehouses_tree.selection()
        if not selected_items:
            return
            
        item_id = selected_items[0]
        warehouse_id = self.warehouses_tree.item(item_id, "values")[0]
        
        # Switch to inventory tab
        self.notebook.select(2)  # Index of inventory tab
        
        # Set the warehouse in the combobox
        warehouses = self.warehouse_controller.get_all_warehouses()
        for i, warehouse in enumerate(warehouses):
            if str(warehouse.id) == warehouse_id:
                self.inventory_warehouse_combo.current(i)
                # Manually refresh inventory
                self.refresh_inventory()
                break
    
    def refresh_warehouses_list(self):
        """Refresh the warehouses list"""
        # Clear existing items
        for item in self.warehouses_tree.get_children():
            self.warehouses_tree.delete(item)
        
        # Get all warehouses
        warehouses = self.warehouse_controller.get_all_warehouses(active_only=False)
        
        # Add warehouses to treeview
        for warehouse in warehouses:
            # Get stock information
            stocks = self.warehouse_controller.get_warehouse_stock(warehouse.id)
            item_count = len(stocks)
            total_value = self.warehouse_controller.get_warehouse_inventory_value(warehouse.id)
            
            # Add status indicator
            status = self._("Active") if warehouse.is_active else self._("Inactive")
            
            self.warehouses_tree.insert(
                "",
                "end",
                values=(
                    warehouse.id,
                    warehouse.name,
                    warehouse.location or "",
                    item_count,
                    f"{total_value:.2f}",
                    status
                )
            )
    
    def create_add_warehouse_tab(self):
        """Create the add warehouse tab"""
        tab = ttk.Frame(self.notebook, padding=10)
        
        # Create form
        form_frame = ttk.Frame(tab)
        form_frame.pack(fill="both", expand=True)
        
        # Add a title
        title_label = ttk.Label(
            form_frame,
            text=self._("Add New Warehouse"),
            font=("TkDefaultFont", 14, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Create input fields
        fields_frame = ttk.Frame(form_frame)
        fields_frame.pack(fill="x")
        
        # Name field
        name_frame = ttk.Frame(fields_frame)
        name_frame.pack(fill="x", pady=10)
        
        ttk.Label(name_frame, text=self._("Warehouse Name:"), width=15).pack(side="left")
        self.warehouse_name_var = ttk.StringVar()
        name_entry = ttk.Entry(name_frame, textvariable=self.warehouse_name_var, width=30)
        name_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Location field
        location_frame = ttk.Frame(fields_frame)
        location_frame.pack(fill="x", pady=10)
        
        ttk.Label(location_frame, text=self._("Location:"), width=15).pack(side="left")
        self.warehouse_location_var = ttk.StringVar()
        location_entry = ttk.Entry(location_frame, textvariable=self.warehouse_location_var, width=30)
        location_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Description field
        desc_frame = ttk.Frame(fields_frame)
        desc_frame.pack(fill="x", pady=10)
        
        ttk.Label(desc_frame, text=self._("Description:"), width=15).pack(side="left")
        self.warehouse_desc_var = ttk.StringVar()
        desc_entry = ttk.Entry(desc_frame, textvariable=self.warehouse_desc_var, width=30)
        desc_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Add error label (hidden initially)
        self.add_warehouse_error_var = ttk.StringVar()
        self.add_warehouse_error_label = ttk.Label(
            fields_frame,
            textvariable=self.add_warehouse_error_var,
            bootstyle=DANGER
        )
        self.add_warehouse_error_label.pack(pady=10, fill="x")
        
        # Add submit button
        submit_button = ttk.Button(
            fields_frame,
            text=self._("Add Warehouse"),
            command=self.add_warehouse,
            bootstyle=SUCCESS,
            width=20
        )
        submit_button.pack(pady=15)
        
        # Add tab to notebook
        self.notebook.add(tab, text=self._("Add Warehouse"))
    
    def add_warehouse(self):
        """Add a new warehouse"""
        # Reset error message
        self.add_warehouse_error_var.set("")
        
        # Get values
        name = self.warehouse_name_var.get().strip()
        location = self.warehouse_location_var.get().strip()
        description = self.warehouse_desc_var.get().strip()
        
        # Validate inputs
        if not name:
            self.add_warehouse_error_var.set(self._("Warehouse name is required"))
            return
        
        # Create warehouse
        result, message = self.warehouse_controller.create_warehouse(
            name=name,
            location=location,
            description=description
        )
        
        if result:
            # Clear form
            self.warehouse_name_var.set("")
            self.warehouse_location_var.set("")
            self.warehouse_desc_var.set("")
            
            # Show success message
            show_notification(self._("Success"), self._("Warehouse added successfully"))
            
            # Refresh warehouses list and switch to it
            self.refresh_warehouses_list()
            self.notebook.select(0)  # Switch to warehouses list tab
        else:
            # Show error message
            self.add_warehouse_error_var.set(message)
    
    def create_inventory_tab(self):
        """Create the inventory tab"""
        tab = ttk.Frame(self.notebook, padding=10)
        
        # Create top controls frame
        controls_frame = ttk.Frame(tab)
        controls_frame.pack(fill="x", pady=(0, 10))
        
        # Warehouse selection
        ttk.Label(controls_frame, text=self._("Warehouse:")).pack(side="left", padx=(0, 5))
        
        # Get all warehouses for the combobox
        warehouses = self.warehouse_controller.get_all_warehouses()
        warehouse_choices = [(str(w.id), w.name) for w in warehouses]
        
        self.inventory_warehouse_var = ttk.StringVar()
        if warehouse_choices:
            self.inventory_warehouse_var.set(str(warehouse_choices[0][0]))
        
        self.inventory_warehouse_combo = ttk.Combobox(
            controls_frame,
            values=[f"{w[1]}" for w in warehouse_choices],
            width=30
        )
        if warehouse_choices:
            self.inventory_warehouse_combo.current(0)
        self.inventory_warehouse_combo.pack(side="left", padx=5)
        
        # Refresh button
        refresh_button = ttk.Button(
            controls_frame,
            text=self._("Refresh"),
            command=self.refresh_inventory,
            bootstyle=INFO,
            width=10
        )
        refresh_button.pack(side="left", padx=10)
        
        # Export button
        export_button = ttk.Button(
            controls_frame,
            text=self._("Export"),
            command=self.export_inventory,
            bootstyle=SUCCESS,
            width=10
        )
        export_button.pack(side="right")
        
        # Create treeview for inventory
        columns = (
            "id", "item_name", "main_unit", "quantity", "sub_unit", "sub_quantity", 
            "purchase_price", "value", "last_updated"
        )
        
        self.inventory_tree = ttk.Treeview(
            tab,
            columns=columns,
            show="headings",
            bootstyle=INFO
        )
        
        # Define column headings
        self.inventory_tree.heading("id", text=self._("ID"))
        self.inventory_tree.heading("item_name", text=self._("Item Name"))
        self.inventory_tree.heading("main_unit", text=self._("Main Unit"))
        self.inventory_tree.heading("quantity", text=self._("Quantity"))
        self.inventory_tree.heading("sub_unit", text=self._("Sub Unit"))
        self.inventory_tree.heading("sub_quantity", text=self._("Sub Quantity"))
        self.inventory_tree.heading("purchase_price", text=self._("Purchase Price"))
        self.inventory_tree.heading("value", text=self._("Value"))
        self.inventory_tree.heading("last_updated", text=self._("Last Updated"))
        
        # Define column widths
        self.inventory_tree.column("id", width=50, stretch=False)
        self.inventory_tree.column("item_name", width=200)
        self.inventory_tree.column("main_unit", width=80, stretch=False)
        self.inventory_tree.column("quantity", width=80, stretch=False)
        self.inventory_tree.column("sub_unit", width=80, stretch=False)
        self.inventory_tree.column("sub_quantity", width=100, stretch=False)
        self.inventory_tree.column("purchase_price", width=100, stretch=False)
        self.inventory_tree.column("value", width=100, stretch=False)
        self.inventory_tree.column("last_updated", width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.inventory_tree.yview)
        self.inventory_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.inventory_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add a summary frame at the bottom
        summary_frame = ttk.Frame(tab)
        summary_frame.pack(fill="x", pady=10)
        
        # Add summary labels
        self.inventory_count_label = ttk.Label(
            summary_frame,
            text=self._("Total Items: 0")
        )
        self.inventory_count_label.pack(side="left", padx=20)
        
        self.inventory_value_label = ttk.Label(
            summary_frame,
            text=self._("Total Value: 0.00")
        )
        self.inventory_value_label.pack(side="left", padx=20)
        
        # Bind events
        self.inventory_warehouse_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_inventory())
        
        # Load initial data
        self.refresh_inventory()
        
        # Add tab to notebook
        self.notebook.add(tab, text=self._("Inventory"))
    
    def refresh_inventory(self):
        """Refresh the inventory list based on selected warehouse"""
        # Clear existing items
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        
        # Get selected warehouse
        selected_index = self.inventory_warehouse_combo.current()
        if selected_index < 0:
            return
        
        warehouses = self.warehouse_controller.get_all_warehouses()
        if selected_index >= len(warehouses):
            return
        
        warehouse = warehouses[selected_index]
        
        # Get inventory for this warehouse
        stocks = self.warehouse_controller.get_warehouse_stock(warehouse.id)
        
        # Calculate total value
        total_value = 0
        
        # Add inventory to treeview
        for stock in stocks:
            item = stock.item
            
            # Calculate sub-unit quantity
            sub_quantity = stock.quantity * item.conversion_rate
            
            # Calculate value
            value = stock.quantity * item.purchase_price
            total_value += value
            
            self.inventory_tree.insert(
                "",
                "end",
                values=(
                    item.id,
                    item.name,
                    item.main_unit,
                    f"{stock.quantity:.2f}",
                    item.sub_unit,
                    f"{sub_quantity:.2f}",
                    f"{item.purchase_price:.2f}",
                    f"{value:.2f}",
                    stock.updated_at.strftime("%Y-%m-%d %H:%M") if stock.updated_at else ""
                )
            )
        
        # Update summary
        self.inventory_count_label.config(text=self._("Total Items: {0}").format(len(stocks)))
        self.inventory_value_label.config(text=self._("Total Value: {0:.2f}").format(total_value))
    
    def export_inventory(self):
        """Export the inventory to Excel"""
        from utils.export import export_to_excel
        
        # Get selected warehouse
        selected_index = self.inventory_warehouse_combo.current()
        if selected_index < 0:
            return
        
        warehouses = self.warehouse_controller.get_all_warehouses()
        if selected_index >= len(warehouses):
            return
        
        warehouse = warehouses[selected_index]
        
        # Prepare data for export
        rows = []
        for item in self.inventory_tree.get_children():
            values = self.inventory_tree.item(item, "values")
            rows.append({
                "ID": values[0],
                "Item Name": values[1],
                "Main Unit": values[2],
                "Quantity": values[3],
                "Sub Unit": values[4],
                "Sub Quantity": values[5],
                "Purchase Price": values[6],
                "Value": values[7],
                "Last Updated": values[8]
            })
        
        # Export to Excel
        filename = f"inventory_{warehouse.name}_{warehouse.id}.xlsx"
        success = export_to_excel(rows, filename, self._("Inventory for {0}").format(warehouse.name))
        
        if success:
            show_notification(
                self._("Export Complete"),
                self._("Inventory exported to {0}").format(filename)
            )
