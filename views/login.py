#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Login view for ASSI Warehouse Management System
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import gettext
from controllers.auth import AuthController

class LoginView:
    """Login view class"""
    
    def __init__(self, root, switch_to_main_menu):
        """Initialize the login view
        
        Args:
            root: The root window
            switch_to_main_menu: Callback function to switch to main menu
        """
        self.root = root
        self.switch_to_main_menu = switch_to_main_menu
        self.auth_controller = AuthController()
        
        # Setup translation
        self._ = gettext.gettext
        
        # Create main frame
        self.frame = ttk.Frame(self.root, padding=20)
        self.frame.pack(expand=True, fill="both")
        
        # Create a style for larger font
        font_size = 12
        
        # Create logo or header
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(pady=20)
        
        header_label = ttk.Label(
            header_frame, 
            text="ASSI Warehouse Management System",
            font=("TkDefaultFont", 18, "bold"),
            bootstyle=PRIMARY
        )
        header_label.pack()
        
        # Create login form
        form_frame = ttk.Frame(self.frame, padding=10)
        form_frame.pack(pady=20)
        
        # Username field
        username_frame = ttk.Frame(form_frame)
        username_frame.pack(fill="x", pady=10)
        
        username_label = ttk.Label(
            username_frame, 
            text=self._("Username:"),
            font=("TkDefaultFont", font_size),
            width=12,
            anchor="e"
        )
        username_label.pack(side="left", padx=5)
        
        self.username_entry = ttk.Entry(username_frame, font=("TkDefaultFont", font_size))
        self.username_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Password field
        password_frame = ttk.Frame(form_frame)
        password_frame.pack(fill="x", pady=10)
        
        password_label = ttk.Label(
            password_frame, 
            text=self._("Password:"),
            font=("TkDefaultFont", font_size),
            width=12,
            anchor="e"
        )
        password_label.pack(side="left", padx=5)
        
        self.password_entry = ttk.Entry(
            password_frame, 
            show="*",
            font=("TkDefaultFont", font_size)
        )
        self.password_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Error message label (hidden initially)
        self.error_label = ttk.Label(
            form_frame, 
            text="",
            bootstyle=DANGER,
            font=("TkDefaultFont", font_size)
        )
        self.error_label.pack(pady=10)
        
        # Login button
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(pady=15)
        
        self.login_button = ttk.Button(
            button_frame, 
            text=self._("Login"),
            command=self.login,
            bootstyle=SUCCESS,
            width=15,
            padding=10
        )
        self.login_button.pack()
        
        # Bind Enter key to login
        self.root.bind("<Return>", lambda event: self.login())
        
        # Set initial focus to username field
        self.username_entry.focus_set()
    
    def login(self):
        """Handle login button click"""
        # Clear any previous error message
        self.error_label.config(text="")
        
        # Get username and password
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        # Validate inputs
        if not username:
            self.error_label.config(text=self._("Username is required"))
            self.username_entry.focus_set()
            return
            
        if not password:
            self.error_label.config(text=self._("Password is required"))
            self.password_entry.focus_set()
            return
        
        # Attempt authentication
        user = self.auth_controller.authenticate(username, password)
        
        if user:
            # Authentication successful
            self.switch_to_main_menu()
        else:
            # Authentication failed
            self.error_label.config(text=self._("Invalid username or password"))
            self.password_entry.delete(0, 'end')
            self.password_entry.focus_set()
