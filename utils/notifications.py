#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Notification utilities for ASSI Warehouse Management System
"""

from flask import flash

def show_notification(title, message, duration=3000, category='info'):
    """Show a notification
    
    Args:
        title: Notification title
        message: Notification message
        duration: Display duration in milliseconds (default: 3000)
        category: Flash message category (default: info)
    """
    # For web app, use Flask's flash messaging
    full_message = f"{title}: {message}" if title else message
    flash(full_message, category)