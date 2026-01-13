"""MySQL DDL generation service."""

import re
from typing import List
from ..models.schema import ColumnAnalysis


class DDLGenerator:
    """Generate production-ready MySQL CREATE TABLE statements."""
    
    def __init__(self):
        self.reserved_words = {
            'select', 'insert', 'update', 'delete', 'from', 'where', 'join',
            'inner', 'outer', 'left', 'right', 'on', 'order', 'by', 'group',
            'having', 'union', 'create', 'table', 'index', 'key', 'primary',
            'foreign', 'references', 'constraint', 'alter', 'drop', 'database',
            'schema', 'view', 'procedure', 'function', 'trigger', 'user',
            'grant', 'revoke', 'commit', 'rollback', 'transaction'
        }
    
    def generate_ddl(self, table_name: str, columns: List[ColumnAnalysis]) -> str:
        """
        Generate a complete MySQL CREATE TABLE statement.
        
        Args:
            table_name: Name of the table to create
            columns: List of analyzed columns
            
        Returns:
            Complete DDL statement ready for execution
        """
        # Sanitize table name
        clean_table_name = self._sanitize_identifier(table_name)
        
        # Generate column definitions
        column_definitions = []
        for col in columns:
            col_def = self._generate_column_definition(col)
            column_definitions.append(col_def)
        
        # Build complete DDL
        ddl_parts = [
            f"CREATE TABLE `{clean_table_name}` (",
            ",\n".join(column_definitions),
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"
        ]
        
        return "\n".join(ddl_parts)
    
    def _generate_column_definition(self, column: ColumnAnalysis) -> str:
        """Generate a single column definition."""
        # Sanitize column name
        clean_name = self._sanitize_identifier(column.name)
        
        # Handle reserved words
        if clean_name.lower() in self.reserved_words:
            clean_name = f"{clean_name}_col"
        
        # Determine NULL constraint
        nullable = "NULL" if column.null_count > 0 else "NOT NULL"
        
        # Prepare comment (escape single quotes)
        comment = ""
        if column.description:
            escaped_desc = column.description.replace("'", "\\'")[:100]
            comment = f"COMMENT '{escaped_desc}'"
        
        # Build column definition
        parts = [
            f"    `{clean_name}`",
            column.mysql_type,
            nullable,
            comment
        ]
        
        return " ".join(filter(None, parts))
    
    def _sanitize_identifier(self, name: str) -> str:
        """
        Sanitize database identifier (table/column name).
        
        Rules:
        - Only alphanumeric characters and underscores
        - Cannot start with a number
        - Cannot be empty
        - Maximum length considerations
        """
        if not name:
            return "unnamed_column"
        
        # Replace invalid characters with underscores
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', str(name))
        
        # Ensure it doesn't start with a number
        if sanitized and sanitized[0].isdigit():
            sanitized = f"col_{sanitized}"
        
        # Handle empty result
        if not sanitized:
            return "unnamed_column"
        
        # Limit length (MySQL identifier limit is 64 characters)
        if len(sanitized) > 64:
            sanitized = sanitized[:61] + "_tr"  # "_tr" for "truncated"
        
        return sanitized
    
