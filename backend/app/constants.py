"""Backend application constants."""

# Data type detection patterns
TYPE_PATTERNS = {
    'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    'phone': r'^[\+]?[\d\s\-\(\)\.]{7,20}$',
    'url': r'^https?://[^\s]+$',
    'date': r'^\d{4}-\d{2}-\d{2}|\d{2}[/\-]\d{2}[/\-]\d{4}|\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}$',
    'time': r'^\d{1,2}:\d{2}(:\d{2})?(\s?(AM|PM|am|pm))?$',
    'boolean': r'^(true|false|yes|no|y|n|1|0|t|f)$',
    'uuid': r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
}

# MySQL data type limits
MYSQL_LIMITS = {
    'tinyint_max': 255,
    'smallint_max': 65535,
    'int_max': 4294967295,
    'varchar_max': 65535,
    'text_threshold': 1000
}

# Data quality thresholds
QUALITY_THRESHOLDS = {
    'high_null_percentage': 50,
    'medium_null_percentage': 20,
    'low_null_percentage': 5,
    'outlier_multiplier': 1.5  # IQR multiplier for outlier detection
}

# Error messages
ERROR_MESSAGES = {
    'csv_parsing_failed': 'Could not parse CSV file with any common separator',
    'empty_file': 'Uploaded file is empty',
    'unsupported_format': 'Please upload a CSV file (.csv extension required)',
    'analysis_failed': 'Analysis failed due to an unexpected error',
    'ai_service_unavailable': 'AI description service is temporarily unavailable'
}