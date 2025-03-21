#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Authentication controller for ASSI Warehouse Management System
"""

from models.user import User
from database.db_setup import session

class AuthController:
    """Controller for authentication operations"""
    
    def authenticate(self, username, password):
        """Authenticate a user with username and password
        
        Args:
            username: User's username
            password: User's password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        # Find user by username
        user = session.query(User).filter_by(username=username).first()
        
        # Check if user exists and password is correct
        if user and user.check_password(password):
            # Record login time
            user.record_login()
            session.commit()
            return user
            
        return None
        
    def register_user(self, username, password, full_name=None, is_admin=False):
        """Register a new user
        
        Args:
            username: User's username
            password: User's password
            full_name: User's full name (optional)
            is_admin: Whether the user is an admin (default: False)
            
        Returns:
            Tuple of (success, user or error message)
        """
        # Check if username already exists
        existing_user = session.query(User).filter_by(username=username).first()
        if existing_user:
            return False, "Username already exists"
            
        # Create new user
        new_user = User(
            username=username,
            full_name=full_name,
            is_admin=is_admin
        )
        
        # Set password
        new_user.set_password(password)
        
        try:
            # Add to database
            session.add(new_user)
            session.commit()
            return True, new_user
        except Exception as e:
            session.rollback()
            return False, str(e)
            
    def change_password(self, user_id, current_password, new_password):
        """Change a user's password
        
        Args:
            user_id: ID of the user
            current_password: Current password
            new_password: New password
            
        Returns:
            Tuple of (success, message)
        """
        # Find user
        user = session.query(User).get(user_id)
        
        if not user:
            return False, "User not found"
            
        # Check current password
        if not user.check_password(current_password):
            return False, "Current password is incorrect"
            
        # Set new password
        user.set_password(new_password)
        
        try:
            session.commit()
            return True, "Password changed successfully"
        except Exception as e:
            session.rollback()
            return False, str(e)
            
    def get_all_users(self):
        """Get all users (admin function)
        
        Returns:
            List of User objects
        """
        return session.query(User).all()
        
    def delete_user(self, user_id, admin_id):
        """Delete a user (admin function)
        
        Args:
            user_id: ID of the user to delete
            admin_id: ID of the admin performing the deletion
            
        Returns:
            Tuple of (success, message)
        """
        # Check if admin exists
        admin = session.query(User).get(admin_id)
        
        if not admin or not admin.is_admin:
            return False, "Not authorized to delete users"
            
        # Check if user exists
        user = session.query(User).get(user_id)
        
        if not user:
            return False, "User not found"
            
        # Can't delete self
        if user_id == admin_id:
            return False, "Cannot delete your own account"
            
        try:
            session.delete(user)
            session.commit()
            return True, "User deleted successfully"
        except Exception as e:
            session.rollback()
            return False, str(e)