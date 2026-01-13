// What we send to the backend when analyzing a file
export interface AnalysisRequest {
  file: File;
  table_name: string;
}

// Basic info about the CSV file we're analyzing
export interface FileInfo {
  name: string;
  separator: string; // what splits the columns - comma, semicolon, tab, etc.
  encoding: string;  // character encoding - usually utf-8
  rows: number;
  columns: number;
}

// Everything we figured out about each column
export interface ColumnAnalysis {
  name: string;
  data_type: string;        // what we think it is (email, phone, etc.)
  mysql_type: string;       // the MySQL type we'll actually use
  sample_values: string[];  // a few example values to show
  null_count: number;
  unique_count: number;
  total_count: number;
  null_percentage: number;
  description: string;              // what the AI thinks this column is for
  cleaning_recommendations: string[]; // suggestions to clean up messy data
}

// Summary stats for the entire file
export interface AnalysisSummary {
  total_columns: number;
  columns_with_nulls: number;
  avg_null_percentage: number;
  total_recommendations: number; // how many cleanup suggestions we found
}

// Everything the backend sends back after analysis
export interface AnalysisResponse {
  success: boolean;
  table_name: string;    // cleaned up table name
  file_info: FileInfo;
  ddl: string;           // the CREATE TABLE statement you can copy-paste
  columns: ColumnAnalysis[];
  summary: AnalysisSummary;
}

// Health check to see if the backend is alive
export interface HealthResponse {
  status: string;          // "healthy" or something went wrong
  groq_available: boolean; // whether the AI stuff is working
  version: string;
}