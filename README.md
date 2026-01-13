# SchemaSense

Instantly transform raw CSV data into production-ready MySQL schemas with AI-powered insights.

## How to Run

### Prerequisites

- Python 3.12+ with uv
- Node.js 18+ with npm

### Setup

```bash
# Clone the repo
unzip the file
cd schema-sense

# Backend setup
cd backend
uv sync
cp .env.example .env
# Edit .env and add the Groq API key if you want AI descriptions
cd ..

# Frontend setup
cd frontend
npm install
cd ..
```

### Start Both Apps

```bash
# Terminal 1: Start backend (port 8000)
cd backend
uv run fastapi dev

# Terminal 2: Start frontend (port 3000)
cd frontend
npm run dev
```

Then go to http://localhost:3000

## Project Structure

```
schema-sense/
├── backend/              # FastAPI backend
│   ├── main.py          # App entry point
│   ├── app/
│   │   ├── core/        # Config and settings
│   │   ├── models/      # Data models
│   │   ├── services/    # Business logic
│   │   ├── api/         # API routes
│   │   ├── utils/       # Helper functions
│   │   └── constants.py # App constants
│   ├── tests/           # Tests
│   ├── pyproject.toml   # Python deps
│   └── .env             # Environment vars
├── frontend/            # Vite React TypeScript frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── services/    # API calls
│   │   ├── types/       # TypeScript types
│   │   ├── utils/       # Helper functions
│   │   └── constants/   # App constants
│   ├── package.json     # Node deps
│   ├── vite.config.ts   # Vite configuration
│   ├── .env             # Environment variables
│   └── dist/            # Production build
```
