"""AI-powered column description generation service."""

import json
import logging
from typing import List, Optional
from groq import Groq
from ..models.schema import ColumnAnalysis
from ..core.config import settings

logger = logging.getLogger(__name__)


class DescriptionGenerationError(Exception):
    """Exception raised when description generation fails."""
    pass


class DescriptionGenerator:
    """Generate human-readable column descriptions using LLM or rule-based fallbacks."""
    
    def __init__(self, groq_client: Optional[Groq] = None):
        self.client = groq_client
        self.model_name = "gemma2-9b-it"  # Better model with higher token limits
        self.max_description_length = 200
    
    async def generate_descriptions(self, columns: List[ColumnAnalysis]) -> List[ColumnAnalysis]:
        """
        Generate descriptions for all columns.
        
        Args:
            columns: List of column analyses to enhance with descriptions
            
        Returns:
            Enhanced columns with AI-generated or rule-based descriptions
        """
        if not self.client or not settings.groq_available:
            return self._generate_fallback_descriptions(columns)
        
        try:
            return await self._generate_ai_descriptions(columns)
        except Exception as e:
            logger.warning(f"AI description generation failed: {e}")
            return self._generate_fallback_descriptions(columns)
    
    async def _generate_ai_descriptions(self, columns: List[ColumnAnalysis]) -> List[ColumnAnalysis]:
        """Generate descriptions using Groq AI with gemma2-9b-it model."""
        # Process in reasonable batches for gemma2-9b-it which has better token handling
        batch_size = 15 if len(columns) > 15 else len(columns)
        
        for i in range(0, len(columns), batch_size):
            batch_columns = columns[i:i + batch_size]
            
            # Build concise column context
            column_info = []
            for col in batch_columns:
                info = f"{col.name} ({col.mysql_type})"
                if col.sample_values:
                    info += f": {col.sample_values[0]}"
                if col.null_percentage > 20:
                    info += f" [{col.null_percentage:.0f}% nulls]"
                column_info.append(info)
            
            prompt = f"""Generate concise business descriptions (max {self.max_description_length} chars each) for these database columns:

{chr(10).join(column_info)}

Return valid JSON:
{{"descriptions": ["description 1", "description 2", ...]}}

Each description should explain the business purpose and data format."""

            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2000,  # gemma2-9b-it can handle higher token counts
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
                
                descriptions = self._parse_ai_response(response.choices[0].message.content)
                
                # Apply descriptions to batch
                for j, col in enumerate(batch_columns):
                    if j < len(descriptions) and descriptions[j]:
                        col.description = descriptions[j][:self.max_description_length]
                    else:
                        col.description = self._generate_fallback_description(col)
                        
            except Exception as e:
                logger.warning(f"AI generation failed for batch, using fallbacks: {str(e)}")
                for col in batch_columns:
                    col.description = self._generate_fallback_description(col)
        
        return columns
    
    def _parse_ai_response(self, response_content: str) -> List[str]:
        """Parse the AI response and extract descriptions."""
        try:
            result = json.loads(response_content)
            return result.get("descriptions", [])
        except json.JSONDecodeError as e:
            # Try to fix incomplete JSON by adding closing brackets
            try:
                # Check if the response was cut off mid-JSON
                if '"descriptions":' in response_content and not response_content.strip().endswith('}'):
                    # Attempt to salvage partial JSON
                    if '"descriptions": [' in response_content:
                        # Extract partial descriptions array
                        start_idx = response_content.find('"descriptions": [') + len('"descriptions": [')
                        partial = response_content[start_idx:].rstrip()
                        
                        # Remove incomplete last entry if it exists
                        if partial.count('"') % 2 == 1:  # Odd number of quotes means incomplete string
                            last_quote = partial.rfind('"')
                            if last_quote > 0:
                                partial = partial[:last_quote]
                                # Remove trailing comma if exists
                                partial = partial.rstrip().rstrip(',')
                        
                        # Complete the JSON structure
                        fixed_json = f'{{"descriptions": [{partial}]}}'
                        result = json.loads(fixed_json)
                        return result.get("descriptions", [])
                
                # Fallback: try to extract as a simple array
                if response_content.strip().startswith('['):
                    return json.loads(response_content)
                    
            except (json.JSONDecodeError, ValueError):
                pass
            
            raise ValueError(f"Could not parse AI response as JSON: {str(e)}")
    
    def _generate_fallback_descriptions(self, columns: List[ColumnAnalysis]) -> List[ColumnAnalysis]:
        """Generate rule-based descriptions for all columns."""
        for col in columns:
            col.description = self._generate_fallback_description(col)
        return columns
    
    def _generate_fallback_description(self, col: ColumnAnalysis) -> str:
        """Generate a rule-based description for a single column."""
        name_lower = col.name.lower()
        
        # Pattern-based descriptions
        if any(word in name_lower for word in ['id', 'key', 'pk']):
            desc = f"Unique identifier field for {self._humanize_name(col.name)}"
        elif 'name' in name_lower or 'title' in name_lower:
            desc = "Name or title field containing descriptive text"
        elif any(word in name_lower for word in ['date', 'time', 'created', 'updated', 'modified']):
            desc = f"Timestamp field for {self._humanize_name(col.name)} events"
        elif any(word in name_lower for word in ['email', 'mail']):
            desc = "Email address field with validation format requirements"
        elif any(word in name_lower for word in ['phone', 'tel', 'mobile']):
            desc = "Phone number field supporting various international formats"
        elif any(word in name_lower for word in ['url', 'link', 'website']):
            desc = "URL field for web addresses and external links"
        elif any(word in name_lower for word in ['address', 'addr', 'location']):
            desc = f"Address field storing {self._humanize_name(col.name)} information"
        elif any(word in name_lower for word in ['amount', 'price', 'cost', 'value', 'total', 'sum']):
            desc = f"Monetary value field for {self._humanize_name(col.name)} calculations"
        elif any(word in name_lower for word in ['count', 'number', 'qty', 'quantity']):
            desc = f"Numeric count field for {self._humanize_name(col.name)} tracking"
        elif any(word in name_lower for word in ['status', 'state', 'flag']):
            desc = f"Status indicator field for {self._humanize_name(col.name)}"
        elif any(word in name_lower for word in ['description', 'desc', 'comment', 'note']):
            desc = f"Descriptive text field containing {self._humanize_name(col.name)} details"
        elif col.data_type == 'boolean':
            desc = f"Boolean flag indicating {self._humanize_name(col.name)} state"
        elif col.data_type in ['decimal', 'int', 'bigint', 'tinyint', 'smallint']:
            desc = f"Numeric field ({col.mysql_type}) with {col.unique_count} unique values"
        elif 'string' in col.data_type:
            desc = f"Text field ({col.mysql_type}) containing {self._humanize_name(col.name)} data"
        else:
            desc = f"Data field of type {col.mysql_type} with {col.unique_count} distinct values"
        
        # Add quality indicators if relevant
        if col.null_percentage > 20:
            desc += f" (High null rate: {col.null_percentage}%)"
        elif len(col.cleaning_recommendations) > 2:
            desc += " (Multiple data quality issues detected)"
        
        return desc[:self.max_description_length]
    
    def _humanize_name(self, name: str) -> str:
        """Convert column name to human-readable format."""
        # Replace underscores and camelCase with spaces
        humanized = name.replace('_', ' ')
        
        # Handle camelCase
        import re
        humanized = re.sub(r'([a-z])([A-Z])', r'\1 \2', humanized)
        
        # Clean up and return
        return humanized.lower().strip()
    
    @classmethod
    def create_with_groq(cls) -> 'DescriptionGenerator':
        """Factory method to create generator with Groq client if available."""
        client = None
        if settings.groq_available:
            try:
                client = Groq(api_key=settings.groq_api_key)
            except Exception:
                client = None
        
        return cls(groq_client=client)