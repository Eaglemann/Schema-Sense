"""Schema inference engine for intelligent MySQL type detection."""

import pandas as pd
import re
from typing import Tuple, List
from ..models.schema import ColumnAnalysis
from ..constants import TYPE_PATTERNS


class SchemaInferenceEngine:
    """
    The brain of the operation - figures out what MySQL data types to use.
    
    Does pattern matching for common formats (emails, phones, etc.) and 
    statistical analysis for numeric types to pick optimal sizes.
    """
    
    def __init__(self):
        # Use centralized patterns from constants
        self.type_patterns = TYPE_PATTERNS
    
    def analyze_column(self, series: pd.Series) -> ColumnAnalysis:
        """
        This is where we analyze a single column and figure out everything about it.
        
        We look at the data patterns, calculate stats, detect outliers, and decide
        what MySQL data type would work best. Returns all the info the frontend needs.
        """
        name = series.name
        total_count = len(series)
        null_count = series.isnull().sum()
        null_percentage = (null_count / total_count) * 100 if total_count > 0 else 0
        unique_count = series.nunique()
        
        # Get some sample values to show the user what we're working with
        non_null_series = series.dropna()
        sample_values = []
        if len(non_null_series) > 0:
            sample_values = non_null_series.astype(str).head(5).tolist()
        
        # The main event - figure out what data type this should be
        data_type, mysql_type = self._infer_types(series)
        
        # Look for data quality issues and suggest fixes
        cleaning_recommendations = self._generate_cleaning_recommendations(
            series, data_type, null_percentage
        )
        
        return ColumnAnalysis(
            name=name,
            data_type=data_type,
            mysql_type=mysql_type,
            sample_values=sample_values,
            null_count=int(null_count),
            unique_count=int(unique_count),
            total_count=total_count,
            null_percentage=round(float(null_percentage), 2),
            description="",  # Will be populated by description generator
            cleaning_recommendations=cleaning_recommendations
        )
    
    def _infer_types(self, series: pd.Series) -> Tuple[str, str]:
        """
        Infer the most appropriate data type using hierarchical analysis.
        
        Returns:
            Tuple of (logical_type, mysql_type)
        """
        non_null_series = series.dropna()
        
        if len(non_null_series) == 0:
            return "unknown", "TEXT"
        
        # Convert to string and clean for pattern analysis
        str_series = non_null_series.astype(str).str.strip()
        
        # Phase 1: Pattern-based detection (high confidence)
        pattern_type = self._detect_patterns(str_series)
        if pattern_type:
            return pattern_type, self._get_mysql_type_for_pattern(pattern_type)
        
        # Phase 2: Numeric type detection
        numeric_type = self._detect_numeric_types(non_null_series)
        if numeric_type:
            return numeric_type
        
        # Phase 3: String type analysis
        return self._analyze_string_type(str_series)
    
    def _detect_patterns(self, str_series: pd.Series) -> str:
        """Detect specific patterns in string data."""
        total_count = len(str_series)
        threshold = 0.8  # 80% must match pattern
        
        for pattern_name, pattern in self.type_patterns.items():
            try:
                matches = str_series.str.match(pattern, case=False, na=False).sum()
                if matches > total_count * threshold:
                    return pattern_name
            except re.error:
                continue  # Skip invalid regex patterns
        
        return None
    
    def _detect_numeric_types(self, series: pd.Series) -> Tuple[str, str]:
        """Detect and classify numeric types."""
        try:
            numeric_series = pd.to_numeric(series, errors='coerce')
            valid_numeric = ~numeric_series.isnull()
            
            # Must be at least 90% numeric to qualify
            if valid_numeric.sum() < len(series) * 0.9:
                return None
            
            valid_numbers = numeric_series[valid_numeric]
            
            # Check if all values are integers
            if (valid_numbers % 1 == 0).all():
                return self._classify_integer_type(valid_numbers)
            else:
                return self._classify_decimal_type(valid_numbers)
                
        except Exception:
            return None
    
    def _classify_integer_type(self, series: pd.Series) -> Tuple[str, str]:
        """Classify integer type based on value range."""
        min_val = series.min()
        max_val = series.max()
        
        if min_val >= 0:
            # Unsigned integers
            if max_val <= 255:
                return "tinyint_unsigned", "TINYINT UNSIGNED"
            elif max_val <= 65535:
                return "smallint_unsigned", "SMALLINT UNSIGNED"
            elif max_val <= 4294967295:
                return "int_unsigned", "INT UNSIGNED"
            else:
                return "bigint_unsigned", "BIGINT UNSIGNED"
        else:
            # Signed integers
            if min_val >= -128 and max_val <= 127:
                return "tinyint", "TINYINT"
            elif min_val >= -32768 and max_val <= 32767:
                return "smallint", "SMALLINT"
            elif min_val >= -2147483648 and max_val <= 2147483647:
                return "int", "INT"
            else:
                return "bigint", "BIGINT"
    
    def _classify_decimal_type(self, series: pd.Series) -> Tuple[str, str]:
        """Classify decimal/float type based on precision needs."""
        # Analyze decimal precision requirements
        try:
            # Convert to string to count decimal places
            str_values = series.astype(str)
            decimal_places = str_values.str.split('.').str[1].str.len()
            max_decimal_places = decimal_places.max()
            
            if pd.isna(max_decimal_places) or max_decimal_places <= 4:
                return "decimal", "DECIMAL(15,4)"
            elif max_decimal_places <= 6:
                return "decimal", "DECIMAL(20,6)"
            else:
                return "float", "FLOAT"
        except Exception:
            return "decimal", "DECIMAL(15,4)"
    
    def _analyze_string_type(self, str_series: pd.Series) -> Tuple[str, str]:
        """Analyze string data to determine appropriate VARCHAR or TEXT type."""
        max_length = str_series.str.len().max()
        
        # Determine appropriate string type based on length characteristics
        if max_length <= 10:
            size = min(50, max_length + 10)
            return "short_string", f"VARCHAR({size})"
        elif max_length <= 100:
            size = min(255, max_length + 20)
            return "string", f"VARCHAR({size})"
        elif max_length <= 255:
            return "string", "VARCHAR(255)"
        elif max_length <= 1000:
            return "medium_string", "TEXT"
        else:
            return "long_string", "LONGTEXT"
    
    def _get_mysql_type_for_pattern(self, pattern_name: str) -> str:
        """Get MySQL type for detected patterns."""
        type_mapping = {
            'email': 'VARCHAR(100)',
            'phone': 'VARCHAR(25)',
            'url': 'VARCHAR(500)',
            'date': 'DATE',
            'time': 'TIME',
            'boolean': 'BOOLEAN',
            'uuid': 'CHAR(36)',
        }
        return type_mapping.get(pattern_name, 'TEXT')
    
    def _generate_cleaning_recommendations(
        self, 
        series: pd.Series, 
        data_type: str, 
        null_percentage: float
    ) -> List[str]:
        """Generate comprehensive data cleaning recommendations."""
        recommendations = []
        
        # Null value analysis
        if null_percentage > 50:
            recommendations.append(
                f"High null rate ({null_percentage:.1f}%) - evaluate column necessity"
            )
        elif null_percentage > 20:
            recommendations.append(
                f"Significant null rate ({null_percentage:.1f}%) - implement null handling strategy"
            )
        elif null_percentage > 5:
            recommendations.append(
                f"Moderate null rate ({null_percentage:.1f}%) - consider default values"
            )
        
        non_null_series = series.dropna()
        if len(non_null_series) == 0:
            return recommendations
        
        # Data type specific recommendations
        if "string" in data_type:
            recommendations.extend(self._analyze_string_quality(non_null_series))
        elif data_type in ['decimal', 'int', 'bigint', 'tinyint', 'smallint']:
            recommendations.extend(self._analyze_numeric_quality(non_null_series))
        elif data_type in ['email', 'phone', 'url']:
            recommendations.extend(self._analyze_pattern_quality(non_null_series, data_type))
        
        return recommendations
    
    def _analyze_string_quality(self, series: pd.Series) -> List[str]:
        """Analyze string data quality issues."""
        recommendations = []
        str_series = series.astype(str)
        
        # Whitespace analysis
        trimmed = str_series.str.strip()
        if not str_series.equals(trimmed):
            recommendations.append("Leading/trailing whitespace detected - consider trimming")
        
        # Case consistency
        if str_series.nunique() != str_series.str.lower().nunique():
            recommendations.append("Inconsistent casing detected - standardize case if needed")
        
        # Length analysis
        max_len = str_series.str.len().max()
        if max_len > 1000:
            recommendations.append("Very long text values detected - consider TEXT type or truncation")
        
        # Empty strings (different from nulls)
        empty_count = (str_series == '').sum()
        if empty_count > 0:
            empty_pct = (empty_count / len(str_series)) * 100
            recommendations.append(f"Empty strings detected ({empty_pct:.1f}%) - standardize with nulls")
        
        return recommendations
    
    def _analyze_numeric_quality(self, series: pd.Series) -> List[str]:
        """Analyze numeric data quality issues."""
        recommendations = []
        
        try:
            numeric_series = pd.to_numeric(series, errors='coerce')
            numeric_series = numeric_series.dropna()
            
            if len(numeric_series) == 0:
                return recommendations
            
            # Outlier detection using IQR method
            Q1 = numeric_series.quantile(0.25)
            Q3 = numeric_series.quantile(0.75)
            IQR = Q3 - Q1
            
            if IQR > 0:
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = numeric_series[
                    (numeric_series < lower_bound) | (numeric_series > upper_bound)
                ]
                
                if len(outliers) > 0:
                    outlier_pct = (len(outliers) / len(numeric_series)) * 100
                    recommendations.append(
                        f"Statistical outliers detected ({outlier_pct:.1f}%) - review extreme values"
                    )
            
            # Range analysis
            value_range = numeric_series.max() - numeric_series.min()
            if value_range == 0:
                recommendations.append("All numeric values are identical - consider constant handling")
            
        except Exception:
            recommendations.append("Numeric parsing issues detected - verify data format")
        
        return recommendations
    
    def _analyze_pattern_quality(self, series: pd.Series, pattern_type: str) -> List[str]:
        """Analyze quality issues for pattern-based types."""
        recommendations = []
        
        if pattern_type == 'email':
            # Check for common email issues
            str_series = series.astype(str)
            if (str_series.str.contains('@.*@', na=False)).any():
                recommendations.append("Multiple @ symbols detected in some email addresses")
                
        elif pattern_type == 'phone':
            # Check phone number consistency
            str_series = series.astype(str)
            lengths = str_series.str.len()
            if lengths.std() > 2:
                recommendations.append("Inconsistent phone number formats - consider standardization")
        
        return recommendations