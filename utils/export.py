#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Export utilities for ASSI Warehouse Management System
"""

import os
import csv
import json
from datetime import datetime
from typing import Dict, List, Optional, Union

def export_to_csv(data: List[Dict], filename: str, columns: Optional[Dict[str, str]] = None) -> str:
    """Export data to CSV file
    
    Args:
        data: List of dictionaries to export
        filename: Base name for the file
        columns: Optional column mapping {field: display_name}
        
    Returns:
        Path to created file or empty string if export failed
    """
    try:
        # Create exports directory if it doesn't exist
        export_dir = os.path.join('static', 'exports')
        os.makedirs(export_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = os.path.join(export_dir, f"{filename}_{timestamp}.csv")
        
        if not data:
            return ""
            
        # Use provided columns or keys from first data item
        fieldnames = list(columns.keys()) if columns else list(data[0].keys())
        headers = list(columns.values()) if columns else fieldnames
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
            
            # Write headers with display names
            header_row = {fieldnames[i]: headers[i] for i in range(len(fieldnames))}
            writer.writerow(header_row)
            
            # Write data rows
            for row in data:
                writer.writerow(row)
                
        return filepath
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return ""
        
def export_to_json(data: Union[List, Dict], filename: str) -> str:
    """Export data to JSON file
    
    Args:
        data: Data to export (list or dictionary)
        filename: Base name for the file
        
    Returns:
        Path to created file or empty string if export failed
    """
    try:
        # Create exports directory if it doesn't exist
        export_dir = os.path.join('static', 'exports')
        os.makedirs(export_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = os.path.join(export_dir, f"{filename}_{timestamp}.json")
        
        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=2, ensure_ascii=False)
                
        return filepath
    except Exception as e:
        print(f"Error exporting to JSON: {e}")
        return ""