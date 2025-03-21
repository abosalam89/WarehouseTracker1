#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main menu view for ASSI Warehouse Management System
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import gettext

class MainMenuView:
    """Main menu view class"""
    
    def __init__(self, root, navigation_callbacks):
        """Initialize the main menu view
        
        Args:
            root: The root window
            navigation_callbacks: Dictionary of callbacks for navigation
        """
        self.root = root
        self.callbacks = navigation_callbacks
        
        # Setup translation
        self._ = gettext.gettext
        
        # Set window title
        self.root.title(self._("ASSI Warehouse Management System - Main Menu"))
        
        # Create main frame
        self.frame = ttk.Frame(self.root)
        self.frame.pack(expand=True, fill="both")
        
        # Create a two-column layout
        self.create_sidebar()
        self.create_dashboard()
    
    def create_sidebar(self):
        """Create the sidebar with navigation buttons"""
        sidebar = ttk.Frame(self.frame, bootstyle=SECONDARY, padding=10)
        sidebar.pack(side="left", fill="y", padx=0, pady=0)
        
        # Company name or logo at the top
        header = ttk.Label(
            sidebar, 
            text="ASSI WMS",
            font=("TkDefaultFont", 16, "bold"),
            bootstyle=INVERSE
        )
        header.pack(pady=20, padx=10)
        
        # Navigation buttons
        nav_buttons = [
            {"text": self._("Funds"), "icon": "💰", "callback": "funds"},
            {"text": self._("Items"), "icon": "📦", "callback": "items"},
            {"text": self._("Invoices"), "icon": "📄", "callback": "invoices"},
            {"text": self._("Warehouses"), "icon": "🏢", "callback": "warehouses"},
            {"text": self._("Expenses"), "icon": "💸", "callback": "expenses"},
            {"text": self._("Suppliers & Customers"), "icon": "👥", "callback": "suppliers_customers"},
            {"text": self._("Reports"), "icon": "📊", "callback": "reports"},
            {"text": self._("Logout"), "icon": "🚪", "callback": "logout"}
        ]
        
        for btn in nav_buttons:
            button_frame = ttk.Frame(sidebar)
            button_frame.pack(fill="x", pady=5, padx=10)
            
            # Create the button with icon and text
            button = ttk.Button(
                button_frame,
                text=f"{btn['icon']} {btn['text']}",
                command=lambda cb=btn['callback']: self.navigate(cb),
                bootstyle=f"{SECONDARY}-outline",
                width=20
            )
            button.pack(fill="x")
    
    def create_dashboard(self):
        """Create the main dashboard area"""
        dashboard = ttk.Frame(self.frame, padding=20)
        dashboard.pack(side="right", fill="both", expand=True)
        
        # Welcome header
        header_frame = ttk.Frame(dashboard)
        header_frame.pack(fill="x", pady=20)
        
        welcome_label = ttk.Label(
            header_frame,
            text=self._("Welcome to ASSI Warehouse Management System"),
            font=("TkDefaultFont", 18, "bold"),
            bootstyle=PRIMARY
        )
        welcome_label.pack(anchor="w")
        
        date_label = ttk.Label(
            header_frame,
            text=self._("Select a module from the sidebar to get started"),
            font=("TkDefaultFont", 12),
            bootstyle=SECONDARY
        )
        date_label.pack(anchor="w", pady=5)
        
        # Quick access cards
        cards_frame = ttk.Frame(dashboard)
        cards_frame.pack(fill="both", expand=True, pady=20)
        
        # Create a grid layout for cards
        cards_frame.columnconfigure(0, weight=1)
        cards_frame.columnconfigure(1, weight=1)
        cards_frame.columnconfigure(2, weight=1)
        
        # Quick access cards data
        quick_access = [
            {
                "title": self._("Inventory Management"),
                "description": self._("Manage items, stock levels, and warehouses"),
                "icon": "📦",
                "callback": "items"
            },
            {
                "title": self._("Sales & Purchases"),
                "description": self._("Create and manage invoices and payments"),
                "icon": "💼",
                "callback": "invoices"
            },
            {
                "title": self._("Financial Overview"),
                "description": self._("Track funds, expenses, and generate reports"),
                "icon": "📊",
                "callback": "reports"
            },
            {
                "title": self._("Supplier & Customer Management"),
                "description": self._("Manage suppliers, customers, and balances"),
                "icon": "👥",
                "callback": "suppliers_customers"
            },
            {
                "title": self._("Warehouse Operations"),
                "description": self._("Manage warehouses and stock transfers"),
                "icon": "🏢",
                "callback": "warehouses"
            },
            {
                "title": self._("Expense Tracking"),
                "description": self._("Record and categorize business expenses"),
                "icon": "💸",
                "callback": "expenses"
            }
        ]
        
        # Create cards in grid layout
        for i, card_data in enumerate(quick_access):
            row = i // 3
            col = i % 3
            
            card = ttk.Frame(cards_frame, padding=10, bootstyle=f"{PRIMARY}-light")
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            # Make the entire card clickable
            card.bind("<Button-1>", lambda event, cb=card_data["callback"]: self.navigate(cb))
            
            # Add hover effect
            card.bind("<Enter>", lambda event, widget=card: widget.configure(bootstyle=f"{SECONDARY}-light"))
            card.bind("<Leave>", lambda event, widget=card: widget.configure(bootstyle=f"{PRIMARY}-light"))
            
            # Card icon and title in one row
            header_frame = ttk.Frame(card)
            header_frame.pack(fill="x", pady=5)
            
            icon_label = ttk.Label(
                header_frame,
                text=card_data["icon"],
                font=("TkDefaultFont", 16)
            )
            icon_label.pack(side="left")
            
            title_label = ttk.Label(
                header_frame,
                text=card_data["title"],
                font=("TkDefaultFont", 12, "bold")
            )
            title_label.pack(side="left", padx=5)
            
            # Card description
            description_label = ttk.Label(
                card,
                text=card_data["description"],
                wraplength=200
            )
            description_label.pack(pady=5, fill="x")
    
    def navigate(self, destination):
        """Navigate to the selected destination
        
        Args:
            destination: The destination key from navigation_callbacks
        """
        if destination in self.callbacks:
            self.callbacks[destination]()
