"""CSV parsing and column detection utilities."""

import csv
from typing import Optional, Tuple


def detect_delimiter(file_path: str) -> str:
    """Auto-detect CSV delimiter"""
    with open(file_path, 'r', encoding='utf-8') as f:
        sample = f.read(1024)
        sniffer = csv.Sniffer()
        try:
            delimiter = sniffer.sniff(sample).delimiter
            return delimiter
        except:
            # Fallback to semicolon if detection fails
            return ';'


def find_column_indices(header: list) -> Tuple[Optional[int], Optional[int], Optional[int], Optional[int]]:
    """Find column indices for title, director, year, and trailer columns."""
    title_col = director_col = year_col = trailer_col = None
    
    # More flexible column matching
    title_keywords = ['title', 'movie', 'film', 'name']
    director_keywords = ['director', 'directed', 'filmmaker']
    year_keywords = ['year', 'date', 'released']
    trailer_keywords = ['trailer', 'link', 'url', 'video']
    
    for i, col_name in enumerate(header):
        col_lower = col_name.lower().strip()
        
        if title_col is None and any(keyword in col_lower for keyword in title_keywords):
            title_col = i
        elif director_col is None and any(keyword in col_lower for keyword in director_keywords):
            director_col = i
        elif year_col is None and any(keyword in col_lower for keyword in year_keywords):
            year_col = i
        elif trailer_col is None and any(keyword in col_lower for keyword in trailer_keywords):
            trailer_col = i
    
    return title_col, director_col, year_col, trailer_col
