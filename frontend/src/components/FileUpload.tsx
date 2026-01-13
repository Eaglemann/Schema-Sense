import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, Loader2, AlertCircle } from 'lucide-react';
import { AnalysisResponse } from '../types/api';
import { analyzeFile as apiAnalyzeFile } from '../services/api';
import { ERROR_MESSAGES, UI_TEXT } from '../constants';
import { validateFile, sanitizeTableName } from '../utils/validation';

interface FileUploadProps {
  onAnalysisComplete: (result: AnalysisResponse) => void;
  onAnalysisStart: () => void;
  isAnalyzing: boolean;
}

const FileUpload: React.FC<FileUploadProps> = ({ onAnalysisComplete, onAnalysisStart, isAnalyzing }) => {
  const [tableName, setTableName] = useState<string>('my_table');
  const [error, setError] = useState<string>('');
  const [dragActive, setDragActive] = useState<boolean>(false); // highlight the drop zone when dragging

  // This does all the work - validates file, sends it, handles errors
  const analyzeFile = useCallback(async (file: File): Promise<void> => {
    // Make sure the file looks reasonable first
    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }

    setError(''); // wipe any old error messages
    onAnalysisStart(); // let the parent know we're busy

    try {
      const sanitizedTableName = sanitizeTableName(tableName);
      const result = await apiAnalyzeFile(file, sanitizedTableName);
      onAnalysisComplete(result);
    } catch (err: any) {
      console.error('Analysis error:', err);
      
      // Try to figure out what went wrong and tell the user
      let errorMessage = ERROR_MESSAGES.ANALYSIS_FAILED;
      if (err.response?.data?.detail) {
        // Backend gave us details about what broke
        errorMessage = err.response.data.detail;
      } else if (err.message?.includes('timeout')) {
        // File was too big or backend is slow
        errorMessage = ERROR_MESSAGES.ANALYSIS_TIMEOUT;
      }
      
      setError(errorMessage);
      onAnalysisStart(); // hack to reset the loading state
    }
  }, [tableName, onAnalysisStart, onAnalysisComplete]);

  // Handle drag and drop stuff
  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      analyzeFile(file);
    }
    setDragActive(false); // stop highlighting
  }, [analyzeFile]); // only depends on analyzeFile, tableName gets captured

  const onDragEnter = useCallback(() => {
    setDragActive(true);
  }, []);

  const onDragLeave = useCallback(() => {
    setDragActive(false);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    onDragEnter,
    onDragLeave,
    accept: {
      'text/csv': ['.csv'],
    },
    maxFiles: 1,
    disabled: isAnalyzing,
  });

  // When someone clicks the file input button instead of dragging
  const handleManualUpload = (event: React.ChangeEvent<HTMLInputElement>): void => {
    const file = event.target.files?.[0];
    if (file) {
      analyzeFile(file);
    }
  };

  return (
    <div className="space-y-6">
      {/* Table Name Input */}
      <div>
        <label htmlFor="tableName" className="block text-sm font-medium text-gray-700 mb-2">
          Table Name
        </label>
        <input
          type="text"
          id="tableName"
          value={tableName}
          onChange={(e) => setTableName(sanitizeTableName(e.target.value))}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="my_table"
          disabled={isAnalyzing}
        />
        <p className="text-xs text-gray-500 mt-1">
          Only letters, numbers, and underscores allowed
        </p>
      </div>

      {/* File Drop Zone */}
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200 cursor-pointer
          ${dragActive || isDragActive 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-gray-300 bg-gray-50 hover:border-gray-400 hover:bg-gray-100'
          }
          ${isAnalyzing ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} disabled={isAnalyzing} />
        
        {isAnalyzing ? (
          <div className="space-y-4">
            <Loader2 className="w-12 h-12 text-blue-600 mx-auto animate-spin" />
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {UI_TEXT.ANALYZING}
              </h3>
              <p className="text-gray-600">
                {UI_TEXT.ANALYZING_SUBTITLE}
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex justify-center">
              {dragActive || isDragActive ? (
                <Upload className="w-12 h-12 text-blue-600" />
              ) : (
                <FileText className="w-12 h-12 text-gray-400" />
              )}
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {dragActive || isDragActive
                  ? 'Drop your CSV file here'
                  : 'Upload CSV File'
                }
              </h3>
              <p className="text-gray-600">
                {UI_TEXT.UPLOAD_PROMPT}
              </p>
              <p className="text-sm text-gray-500 mt-2">
                {UI_TEXT.UPLOAD_HINT}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Manual Upload Button */}
      {!isAnalyzing && (
        <div className="text-center">
          <span className="text-gray-500">or</span>
          <div className="mt-2">
            <label htmlFor="file-upload" className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 cursor-pointer transition-colors">
              <Upload className="w-4 h-4 mr-2" />
              Choose File
            </label>
            <input
              id="file-upload"
              type="file"
              accept=".csv"
              onChange={handleManualUpload}
              className="hidden"
            />
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
          <div>
            <h4 className="text-sm font-medium text-red-800">Upload Error</h4>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default FileUpload;