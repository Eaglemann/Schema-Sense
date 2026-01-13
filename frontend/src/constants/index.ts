// Random numbers that seemed reasonable when I wrote this
export const APP_CONFIG = {
  MAX_FILE_SIZE: 100 * 1024 * 1024, // 100MB should be enough for most people
  SUPPORTED_FORMATS: [".csv"],
  REQUEST_TIMEOUT: 60000, // Big files take a while to process
  COPY_FEEDBACK_DURATION: 2000, // Quick flash to show the copy worked
} as const;

// Error messages that hopefully make sense to users
export const ERROR_MESSAGES = {
  INVALID_FILE_TYPE: "I can only work with CSV files - sorry!",
  EMPTY_FILE: "That file seems to be empty...",
  ANALYSIS_FAILED: "Something went wrong. Mind trying again?",
  ANALYSIS_TIMEOUT:
    "That file took too long to process. Maybe try a smaller one?",
  COPY_FAILED: "Couldn't copy that for some reason",
};

// Text that shows up in the UI
export const UI_TEXT = {
  APP_TITLE: "SchemaSense",
  APP_DESCRIPTION: "Instantly transform raw CSV data into production-ready MySQL schemas with AI-powered insights.",
  UPLOAD_PROMPT: "Drop your CSV here or click to browse",
  UPLOAD_HINT: "Works with comma, semicolon, tab, and pipe separated files",
  ANALYZING: "Working with your data...",
  ANALYZING_SUBTITLE: "Hang tight, big files take a minute",
} as const;
