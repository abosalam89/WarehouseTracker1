#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Authentication controller for ASSI Warehouse Management System
"""

from database.db_setup import session
from models.user import User
from datetime import datetime

class AuthController:
    """Controller for authentication operations"""
    
    def authenticate(self, username, password):
        """Authenticate a user with username and password"""
        user = session.query(User).filter_by(username=username).first()
        
        if user and user.check_password(password):
            # Update last login time
            user.last_login = datetime.utcnow()
            session.commit()
            return user
        
        return None
    
    def register_user(self, username, password, full_name=None, is_admin=False):
        """Register a new user"""
        # Check if username already exists
        existing_user = session.query(User).filter_by(username=username).first()
        if existing_user:
            return False, "Username already exists"
        
        # Create new user
        user = User(username=username, full_name=full_name, is_admin=is_admin)
        user.set_password(password)
        
        try:
            session.add(user)
            session.commit()
            return True, "User registered successfully"
        except Exception as e:
            session.rollback()
            return False, f"Error registering user: {str(e)}"
    
    def change_password(self, user_id, current_password, new_password):
        """Change a user's password"""
        user = session.query(User).filter_by(id=user_id).first()
        
        if not user:
            return False, "User not found"
        
        if not user.check_password(current_password):
            return False, "Current password is incorrect"
        
        try:
            user.set_password(new_password)
            session.commit()
            return True, "Password changed successfully"
        except Exception as e:
            session.rollback()
            return False, f"Error changing password: {str(e)}"
    
    def get_all_users(self):
        """Get all users (admin function)"""
        return session.query(User).all()
    
    def delete_user(self, user_id, admin_id):
        """Delete a user (admin function)"""
        admin = session.query(User).filter_by(id=admin_id).first()
        
        if not admin or not admin.is_admin:
            return False, "Unauthorized operation"
        
        user = session.query(User).filter_by(id=user_id).first()
        
        if not user:
            return False, "User not found"
        
        if user.is_admin and session.query(User).filter_by(is_admin=True).count() <= 1:
            return False, "Cannot delete the last admin user"
        
        try:
            session.delete(user)
            session.commit()
            return True, "User deleted successfully"
        except Exception as e:
            session.rollback()
            return False, f"Error deleting user: {str(e)}"
