// Where our backend lives - defaults to localhost:8000 if no .env file
export const API_BASE_URL: string =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
