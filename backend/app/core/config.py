"""Configuration management for the SchemaSense application."""

from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Uses Pydantic for validation and type conversion. All settings can be
    overridden via environment variables or .env file.
    """
    
    # Basic app info
    app_name: str = Field(default="SchemaSense", description="Application name")
    app_version: str = Field(default="2.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode - enables auto-reload and detailed errors")
    
    # Server binding
    host: str = Field(default="0.0.0.0", description="Server host - 0.0.0.0 allows external connections")
    port: int = Field(default=8000, description="Server port")
    
    # CORS setup for our separate React frontend
    cors_origins: list[str] | str = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        description="Allowed CORS origins - React dev server and potential backup port"
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(v)
    
    # AI service integration
    groq_api_key: Optional[str] = Field(default=None, description="Groq API key for AI column descriptions")
    
    # File upload limits
    max_file_size: int = Field(default=100 * 1024 * 1024, description="Max file size (100MB) - should be enough for most CSVs")
    analysis_timeout: int = Field(default=300, description="Analysis timeout in seconds - 5 minutes for large files")
    
    # CSV parsing configuration
    supported_separators: list[str] = Field(
        default=[',', ';', '\t', '|', ' '],
        description="CSV separators we can auto-detect - covers most common formats"
    )
    supported_encodings: list[str] = Field(
        default=['utf-8', 'latin1', 'cp1252', 'iso-8859-1'],
        description="File encodings to try - utf-8 first, then common legacy encodings"
    )
    
    
    class Config:
        env_file = ".env"      # look for .env file in current directory
        case_sensitive = False  # GROQ_API_KEY and groq_api_key both work
        
    @property
    def groq_available(self) -> bool:
        """Check if we actually have a Groq API key to use"""
        return self.groq_api_key is not None and len(self.groq_api_key.strip()) > 0


# Create the global settings instance - this gets imported everywhere
settings = Settings()