#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASSI Warehouse Management System
Main Entry Point
"""

import os
import sys
import gettext
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# Setup path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import database initialization
from database.db_setup import init_db, create_admin_if_not_exists

# Import views
from views.login import LoginView
from views.main_menu import MainMenuView
from views.funds import FundsView
from views.items import ItemsView
from views.invoices import InvoicesView
from views.warehouses import WarehousesView
from views.expenses import ExpensesView
from views.suppliers_customers import SuppliersCustomersView
from views.reports import ReportsView

# Import utility for language
from utils.language import setup_language, get_current_language, switch_language

class Application:
    """Main application class for ASSI Warehouse Management System"""
    
    def __init__(self):
        # Initialize database
        init_db()
        create_admin_if_not_exists()
        
        # Setup language support
        self.current_language = get_current_language()
        setup_language(self.current_language)
        
        # Initialize the main window
        self.root = ttk.Window(themename="superhero")  # Using a dark theme from ttkbootstrap
        self.root.title("ASSI Warehouse Management System")
        self.root.geometry("1024x768")  # Setting a default window size
        
        # Start with login view
        self.current_view = None
        self.show_login()
        
        # Add menu bar with language switcher
        self.setup_menubar()
        
    def setup_menubar(self):
        """Setup the application menu bar"""
        menubar = ttk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Language menu
        lang_menu = ttk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Language", menu=lang_menu)
        lang_menu.add_command(label="English", command=lambda: self.change_language("en_US"))
        lang_menu.add_command(label="Arabic (العربية)", command=lambda: self.change_language("ar_SA"))
    
    def change_language(self, lang_code):
        """Change the application language"""
        switch_language(lang_code)
        self.current_language = lang_code
        
        # Refresh the current view
        if isinstance(self.current_view, LoginView):
            self.show_login()
        else:
            self.show_main_menu()
    
    def show_login(self):
        """Display the login view"""
        # Clear current view
        if self.current_view:
            try:
                self.current_view.frame.destroy()
            except:
                pass
        
        # Create login view
        self.current_view = LoginView(self.root, self.show_main_menu)
    
    def show_main_menu(self):
        """Display the main menu view"""
        # Clear current view
        if self.current_view:
            try:
                self.current_view.frame.destroy()
            except:
                pass
        
        # Create main menu view
        self.current_view = MainMenuView(self.root, {
            'funds': self.show_funds,
            'items': self.show_items,
            'invoices': self.show_invoices,
            'warehouses': self.show_warehouses,
            'expenses': self.show_expenses,
            'suppliers_customers': self.show_suppliers_customers,
            'reports': self.show_reports,
            'logout': self.show_login
        })
    
    def show_funds(self):
        """Display the funds management view"""
        if self.current_view:
            try:
                self.current_view.frame.destroy()
            except:
                pass
        self.current_view = FundsView(self.root, self.show_main_menu)
    
    def show_items(self):
        """Display the items management view"""
        if self.current_view:
            try:
                self.current_view.frame.destroy()
            except:
                pass
        self.current_view = ItemsView(self.root, self.show_main_menu)
    
    def show_invoices(self):
        """Display the invoices management view"""
        if self.current_view:
            try:
                self.current_view.frame.destroy()
            except:
                pass
        self.current_view = InvoicesView(self.root, self.show_main_menu)
    
    def show_warehouses(self):
        """Display the warehouses management view"""
        if self.current_view:
            try:
                self.current_view.frame.destroy()
            except:
                pass
        self.current_view = WarehousesView(self.root, self.show_main_menu)
    
    def show_expenses(self):
        """Display the expenses management view"""
        if self.current_view:
            try:
                self.current_view.frame.destroy()
            except:
                pass
        self.current_view = ExpensesView(self.root, self.show_main_menu)
    
    def show_suppliers_customers(self):
        """Display the suppliers and customers management view"""
        if self.current_view:
            try:
                self.current_view.frame.destroy()
            except:
                pass
        self.current_view = SuppliersCustomersView(self.root, self.show_main_menu)
    
    def show_reports(self):
        """Display the reports view"""
        if self.current_view:
            try:
                self.current_view.frame.destroy()
            except:
                pass
        self.current_view = ReportsView(self.root, self.show_main_menu)
    
    def run(self):
        """Run the application main loop"""
        self.root.mainloop()


if __name__ == "__main__":
    app = Application()
    app.run()
