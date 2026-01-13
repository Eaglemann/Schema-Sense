"""API routes for the SchemaSense application."""

from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from ..models.schema import AnalysisResponse, HealthResponse
from ..services.csv_parser import CSVParser
from ..services.schema_inference import SchemaInferenceEngine
from ..services.ddl_generator import DDLGenerator
from ..services.description_generator import DescriptionGenerator
from ..utils.serialization import serialize_columns
from ..utils.error_handler import handle_api_error, CSVParsingError
from ..core.config import settings
from ..constants import ERROR_MESSAGES

# Initialize our service layer - these do the heavy lifting
csv_parser = CSVParser()
schema_engine = SchemaInferenceEngine()
ddl_generator = DDLGenerator()
description_generator = DescriptionGenerator.create_with_groq()  # auto-detects if Groq API key is available

# Create the API router with common prefix
router = APIRouter(prefix="/api", tags=["api"])


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_csv(
    file: UploadFile = File(...),
    table_name: str = Form("my_table")
):
    """
    Upload a CSV, get back MySQL DDL. That's it.
    
    Takes the file, figures out what data types to use, gets AI descriptions
    if possible, and returns a CREATE TABLE you can copy-paste.
    """
    try:
        # Basic validation - make sure we got a CSV file
        if not file.filename or not file.filename.lower().endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail=ERROR_MESSAGES['unsupported_format']
            )
        
        # Read the uploaded file into memory
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(
                status_code=400,
                detail=ERROR_MESSAGES['empty_file']
            )
        
        # Step 1: Parse the CSV with our smart parser
        # This handles encoding detection, separator detection, etc.
        try:
            df, parsing_info = csv_parser.parse_csv(content)
        except CSVParsingError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Step 2: Analyze each column to determine data types and quality
        columns = []
        for col_name in df.columns:
            analysis = schema_engine.analyze_column(df[col_name])
            columns.append(analysis)
        
        # Step 3: Generate AI descriptions (or fallback to rule-based ones)
        columns = await description_generator.generate_descriptions(columns)
        
        # Step 4: Generate the actual MySQL DDL
        ddl = ddl_generator.generate_ddl(table_name, columns)
        
        # Step 5: Calculate some summary stats for the frontend
        summary = {
            "total_columns": len(columns),
            "columns_with_nulls": sum(1 for col in columns if col.null_count > 0),
            "avg_null_percentage": round(
                sum(col.null_percentage for col in columns) / len(columns) if columns else 0,
                2
            ),
            "total_recommendations": sum(len(col.cleaning_recommendations) for col in columns)
        }
        
        # Package everything up for the frontend
        return AnalysisResponse(
            success=True,
            table_name=table_name,
            file_info={
                "name": file.filename,
                "separator": parsing_info["separator"],
                "encoding": parsing_info["encoding"],
                "rows": parsing_info["rows"],
                "columns": parsing_info["columns"]
            },
            ddl=ddl,
            columns=serialize_columns(columns),  # convert numpy types to JSON-safe types
            summary=summary
        )
        
    except HTTPException:
        raise  # Don't wrap HTTP exceptions - just pass them through
    except Exception as e:
        # Use centralized error handler for consistency
        raise handle_api_error(e)


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check if we're alive and if Groq is working"""
    return HealthResponse(
        status="healthy",
        groq_available=settings.groq_available,  # tells you if AI descriptions will work
        version=settings.app_version
    )