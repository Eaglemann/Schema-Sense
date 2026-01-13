"""Enhanced CSV parsing service with intelligent detection capabilities."""

import io
import pandas as pd
import chardet
from typing import Tuple, Dict
from ..core.config import settings


class CSVParsingError(Exception):
    """Custom exception for CSV parsing errors."""
    pass


class CSVParser:
    """
    Enhanced CSV parser with automatic detection capabilities.
    
    Handles the messy reality of CSV files in the wild - different encodings,
    separators, and formatting quirks that break naive parsers.
    """
    
    def __init__(self):
        self.separators = settings.supported_separators
        self.encodings = settings.supported_encodings
    
    def detect_encoding(self, content: bytes) -> str:
        """
        Try to figure out what encoding this file is using.
        
        Uses chardet to detect, but has some fallbacks for common edge cases.
        ASCII gets promoted to UTF-8 since they're compatible and UTF-8 is more flexible.
        """
        try:
            detected = chardet.detect(content)
            encoding = detected.get('encoding', 'utf-8')
            
            # ASCII is just a subset of UTF-8, so upgrade it
            if encoding and encoding.lower() in ['ascii']:
                encoding = 'utf-8'
                
            return encoding or 'utf-8'
        except Exception:
            # If detection fails completely, UTF-8 is a reasonable default
            return 'utf-8'
    
    def detect_separator(self, content: str, max_lines: int = 10) -> str:
        """
        Try to figure out what separator this CSV is using.
        
        The basic idea: count how many times each potential separator appears
        on each line, and pick the one that's most consistent. A real CSV
        should have the same number of separators on each line.
        """
        lines = content.split('\n')[:max_lines]
        lines = [line.strip() for line in lines if line.strip()]
        
        if not lines:
            return ','
        
        separator_scores = {}
        
        for sep in self.separators:
            counts = []
            for line in lines:
                counts.append(line.count(sep))
            
            if counts and max(counts) > 0:
                # Calculate consistency score
                avg_count = sum(counts) / len(counts)
                variance = sum((x - avg_count) ** 2 for x in counts) / len(counts)
                
                # Good separator appears consistently (low variance) and frequently
                if avg_count > 1 and variance < avg_count:
                    separator_scores[sep] = avg_count / (1 + variance)
        
        if separator_scores:
            return max(separator_scores.items(), key=lambda x: x[1])[0]
        
        return ','  # Default fallback
    
    def parse_csv(self, content: bytes) -> Tuple[pd.DataFrame, Dict[str, any]]:
        """
        Parse CSV content with intelligent detection and robust error handling.
        
        Args:
            content: Raw file bytes
            
        Returns:
            Tuple of (DataFrame, parsing_info)
            
        Raises:
            CSVParsingError: If parsing fails completely
        """
        if len(content) == 0:
            raise CSVParsingError("File is empty")
        
        if len(content) > settings.max_file_size:
            raise CSVParsingError(f"File too large (max {settings.max_file_size // (1024*1024)}MB)")
        
        # Detect encoding
        encoding = self.detect_encoding(content)
        
        # Decode content with fallback handling
        text_content = self._decode_content(content, encoding)
        
        # Detect separator
        separator = self.detect_separator(text_content)
        
        # Parse with multiple attempts
        df, used_params = self._parse_with_fallbacks(text_content, separator, encoding)
        
        if df is None or len(df.columns) <= 1 or len(df) == 0:
            raise CSVParsingError(
                "Could not parse CSV file. Please ensure your file:\n"
                "• Has proper CSV formatting\n"
                "• Contains data (not just headers)\n"
                "• Uses supported separators (comma, semicolon, tab, pipe)\n"
                "• Has valid encoding (UTF-8, Latin-1, etc.)"
            )
        
        # Clean and prepare DataFrame
        df = self._clean_dataframe(df)
        
        parsing_info = {
            'separator': used_params.get('sep', separator),
            'encoding': encoding,
            'rows': len(df),
            'columns': len(df.columns)
        }
        
        return df, parsing_info
    
    def _decode_content(self, content: bytes, primary_encoding: str) -> str:
        """Decode content with fallback encoding attempts."""
        # Try primary encoding first
        for encoding in [primary_encoding] + self.encodings:
            try:
                return content.decode(encoding)
            except UnicodeDecodeError:
                continue
        
        # Last resort with error handling
        try:
            return content.decode('utf-8', errors='replace')
        except Exception:
            raise CSVParsingError("Could not decode file with any supported encoding")
    
    def _parse_with_fallbacks(self, text_content: str, primary_sep: str, encoding: str) -> Tuple[pd.DataFrame, Dict]:
        """Attempt parsing with various separator combinations."""
        parsing_attempts = [
            {'sep': primary_sep, 'encoding': encoding},
            {'sep': ',', 'encoding': encoding},
            {'sep': ';', 'encoding': encoding},
            {'sep': '\t', 'encoding': encoding},
            {'sep': '|', 'encoding': encoding},
        ]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_attempts = []
        for attempt in parsing_attempts:
            key = (attempt['sep'], attempt['encoding'])
            if key not in seen:
                seen.add(key)
                unique_attempts.append(attempt)
        
        for params in unique_attempts:
            try:
                csv_buffer = io.StringIO(text_content)
                
                df = pd.read_csv(
                    csv_buffer,
                    sep=params['sep'],
                    dtype=str,  # Read everything as string initially
                    na_values=['', 'NULL', 'null', 'None', 'none', 'N/A', 'n/a', 'NA', 'na'],
                    keep_default_na=True,
                    skip_blank_lines=True,
                    on_bad_lines='skip'  # Skip malformed lines
                )
                
                # Validate successful parsing
                if len(df.columns) > 1 and len(df) > 0:
                    return df, params
                    
            except Exception:
                continue
        
        return None, {}
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare the DataFrame."""
        # Clean column names
        df.columns = df.columns.astype(str).str.strip()
        
        # Remove completely empty rows
        df = df.dropna(how='all').reset_index(drop=True)
        
        # Handle duplicate column names
        df.columns = self._handle_duplicate_columns(df.columns.tolist())
        
        return df
    
    def _handle_duplicate_columns(self, columns: list) -> list:
        """Handle duplicate column names by adding suffixes."""
        seen = {}
        result = []
        
        for col in columns:
            if col in seen:
                seen[col] += 1
                result.append(f"{col}_{seen[col]}")
            else:
                seen[col] = 0
                result.append(col)
        
        return result