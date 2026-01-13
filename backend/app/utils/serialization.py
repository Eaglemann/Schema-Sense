"""Utilities for data serialization and type conversion."""

import numpy as np
from typing import Any
from dataclasses import asdict
from ..models.schema import ColumnAnalysis


def convert_numpy_types(obj: Any) -> Any:
    """
    Pandas loves to use numpy types but JSON hates them.
    
    This was causing 500 errors when we tried to return analysis results.
    Goes through everything and converts np.int64 -> int, np.float64 -> float, etc.
    """
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    return obj


def serialize_column_analysis(column: ColumnAnalysis) -> dict:
    """Turn a ColumnAnalysis into something we can send as JSON"""
    col_dict = asdict(column)
    return convert_numpy_types(col_dict)


def serialize_columns(columns: list[ColumnAnalysis]) -> list[dict]:
    """Convert all column analysis results to JSON-safe format"""
    return [serialize_column_analysis(col) for col in columns]