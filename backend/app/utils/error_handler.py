"""Centralized error handling utilities."""

import logging
from typing import Any, Dict
from fastapi import HTTPException
from ..constants import ERROR_MESSAGES

logger = logging.getLogger(__name__)


class SchemaSenseError(Exception):
    """Our own exception class so we can add HTTP status codes"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class CSVParsingError(SchemaSenseError):
    """When CSV files are messed up or can't be read"""
    def __init__(self, message: str = ERROR_MESSAGES['csv_parsing_failed']):
        super().__init__(message, 400)


class AnalysisError(SchemaSenseError):
    """When something goes wrong during schema analysis"""
    def __init__(self, message: str = ERROR_MESSAGES['analysis_failed']):
        super().__init__(message, 500)


def handle_api_error(error: Exception) -> HTTPException:
    """
    Turn any error into something FastAPI can return to the user.
    Keeps error messages consistent and doesn't leak internals.
    """
    if isinstance(error, SchemaSenseError):
        return HTTPException(status_code=error.status_code, detail=error.message)
    
    # Log the real error for debugging but don't show it to users
    logger.error(f"Unexpected error: {type(error).__name__}: {str(error)}")
    
    return HTTPException(
        status_code=500,
        detail=ERROR_MESSAGES['analysis_failed']
    )


def create_error_response(message: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
    """Build a standard error response dict"""
    response = {
        "success": False,
        "error": message
    }
    
    if details:
        response["details"] = details
    
    return response