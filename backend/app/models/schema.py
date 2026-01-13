"""Data models and schemas for the SchemaSense application."""

from dataclasses import dataclass
from typing import List
from pydantic import BaseModel


@dataclass
class ColumnAnalysis:
    """
    Everything we know about a single column after analysis.
    
    This gets passed around between all the services and eventually
    serialized to JSON for the frontend. The description field gets
    filled in by either the AI service or rule-based fallback.
    """
    name: str                              # column name from the CSV
    data_type: str                         # our internal type classification  
    mysql_type: str                        # actual MySQL DDL type
    sample_values: List[str]               # first few values for display
    null_count: int
    unique_count: int
    total_count: int
    null_percentage: float
    description: str                       # human-readable description
    cleaning_recommendations: List[str]    # data quality suggestions


class FileInfo(BaseModel):
    """Basic metadata about the CSV file we parsed."""
    name: str        # original filename
    separator: str   # comma, semicolon, etc.
    encoding: str    # utf-8, latin1, etc.  
    rows: int        # total data rows (excluding header)
    columns: int     # number of columns


class AnalysisSummary(BaseModel):
    """High-level stats that the frontend shows in the overview tab."""
    total_columns: int
    columns_with_nulls: int             # how many columns have missing data
    avg_null_percentage: float          # average percentage of nulls across all columns
    total_recommendations: int          # total number of data quality suggestions


class AnalysisResponse(BaseModel):
    """
    The main response we send back to the frontend with everything it needs.
    
    Contains the generated DDL, column analysis, and summary stats.
    The columns are converted from ColumnAnalysis dataclass to dict for JSON serialization.
    """
    success: bool                    # always True if we got this far
    table_name: str                  # sanitized table name
    file_info: FileInfo             # basic file metadata
    ddl: str                        # ready-to-use CREATE TABLE statement
    columns: List[dict]             # ColumnAnalysis objects as dicts
    summary: AnalysisSummary        # high-level stats


class HealthResponse(BaseModel):
    """Simple health check response for monitoring."""
    status: str              # "healthy" or error message
    groq_available: bool     # whether AI descriptions are working
    version: str             # app version for debugging