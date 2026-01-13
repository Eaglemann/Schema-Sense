import axios from 'axios';
import { API_BASE_URL } from '../config';
import { AnalysisResponse, HealthResponse } from '../types/api';

// Upload a file and get the MySQL schema back
export const analyzeFile = async (file: File, tableName: string): Promise<AnalysisResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('table_name', tableName);

  // Give it plenty of time - big files and AI are both slow
  const response = await axios.post<AnalysisResponse>(`${API_BASE_URL}/api/analyze`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    timeout: 60000,
  });

  return response.data;
};

// Ping the backend to see if everything's working
export const checkHealth = async (): Promise<HealthResponse> => {
  const response = await axios.get<HealthResponse>(`${API_BASE_URL}/api/health`);
  return response.data;
};