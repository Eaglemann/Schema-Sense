import { APP_CONFIG, ERROR_MESSAGES } from '../constants';

// Make sure the file isn't obviously broken before we send it
export const validateFile = (file: File): string | null => {
  if (!file.name.toLowerCase().endsWith('.csv')) {
    return ERROR_MESSAGES.INVALID_FILE_TYPE;
  }

  if (file.size > APP_CONFIG.MAX_FILE_SIZE) {
    return `File size exceeds ${APP_CONFIG.MAX_FILE_SIZE / 1024 / 1024}MB limit`;
  }

  if (file.size === 0) {
    return ERROR_MESSAGES.EMPTY_FILE;
  }

  return null;
};

// MySQL is picky about table names, so we fix them up
export const sanitizeTableName = (tableName: string): string => {
  return tableName
    .replace(/[^a-zA-Z0-9_]/g, '_') // turn weird chars into underscores
    .replace(/^[^a-zA-Z_]/, '_')    // can't start with numbers
    .substring(0, 64);              // MySQL has a 64 character limit
};