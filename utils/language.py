#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Language utilities for ASSI Warehouse Management System
"""

import os
import json
import locale
from typing import Any, Callable, Dict, Optional

# Global variables to store current language
_current_language = 'en_US'

# Define a dummy gettext class to handle missing gettext module
class DummyGettextModule:
    """Dummy gettext module replacement when the real one is not available"""
    def gettext(self, message: str) -> str:
        return message
    
    def install(self) -> None:
        pass

class DummyTranslation:
    """Dummy translation class"""
    def install(self) -> None:
        pass
        
    class gettext:
        @staticmethod
        def translation(domain: str, localedir: Optional[str] = None, languages: Optional[list] = None, **kwargs: Any) -> 'DummyTranslation':
            return DummyTranslation()
            
        @staticmethod
        def install(domain: str, localedir: Optional[str] = None, **kwargs: Any) -> None:
            pass

# Try to import gettext, use dummy module if not available
try:
    import gettext
except ImportError:
    gettext = DummyGettextModule()

# Dictionary to store translations
_translations: Dict[str, Dict[str, str]] = {}

def get_current_language() -> str:
    """Get the currently set language code"""
    return _current_language

def _load_translation_file(lang_code: str) -> Dict[str, str]:
    """Load a translation file for the given language code
    
    Args:
        lang_code: Language code (e.g., 'en_US', 'ar_SA')
        
    Returns:
        Dictionary with translations or empty dict if file not found
    """
    try:
        file_path = os.path.join('translations', lang_code, 'translations.json')
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception:
        return {}
        
def setup_language(lang_code: str) -> None:
    """Setup language for the application
    
    Args:
        lang_code: Language code (e.g., 'en_US', 'ar_SA')
    """
    global _current_language, _translations
    
    # Store the language code
    _current_language = lang_code
    
    # Load the translation file if available
    if lang_code not in _translations:
        _translations[lang_code] = _load_translation_file(lang_code)
    
    # Set locale if possible
    try:
        locale.setlocale(locale.LC_ALL, lang_code)
    except locale.Error:
        try:
            # Try with UTF-8 suffix
            locale.setlocale(locale.LC_ALL, f"{lang_code}.UTF-8")
        except locale.Error:
            # Fall back to default locale
            locale.setlocale(locale.LC_ALL, '')

def switch_language(lang_code: str) -> None:
    """Switch to a different language
    
    Args:
        lang_code: Language code to switch to
    """
    setup_language(lang_code)

# Initialize with English by default
setup_language('en_US')

# Define translation function
def _(text: str) -> str:
    """Translate text based on current language
    
    Args:
        text: Text to translate
        
    Returns:
        Translated text or original if no translation found
    """
    if _current_language in _translations and text in _translations[_current_language]:
        return _translations[_current_language][text]
    return text