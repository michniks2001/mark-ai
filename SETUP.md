# Marketing Tool - Complete Setup Guide

## Overview
This guide will help you set up and run the Marketing Tool, which generates AI-powered pitch decks from GitHub repositories.

## Prerequisites

- **Python 3.13+** (for backend)
- **Node.js 18+** (for frontend)
- **uv** (Python package manager) - Install: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Git** (for repository cloning)

## Initial Setup

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd marketing-tool
```

### 2. Backend Setup

```bash
cd backend

# Install dependencies with uv
uv sync

# Create .env file
cat > .env << EOF
DEDALUS_API_KEY=your_dedalus_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
OPIK_API_KEY=your_opik_api_key_here
EOF

# Activate virtual environment
source .venv/bin/activate

# Test the backend
uvicorn main:app --reload
```

Backend should now be running at `http://localhost:8000`

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend should now be running at `http://localhost:5173`

## Quick Start (After Initial Setup)

### Option 1: Start Both Servers Automatically
```bash
./start-dev.sh
```

### Option 2: Start Manually

**Terminal 1 - Backend:**
```bash
cd backend
source .venv/bin/activate
uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## Environment Variables

### Backend (.env)
```bash
# Required
DEDALUS_API_KEY=dsk_live_xxxxx    # Get from dedaluslabs.ai
GOOGLE_API_KEY=AIzaSyxxxxx        # Get from Google Cloud Console
EXA_API_KEY=exa_xxxxx              # Get from exa.ai (for market analysis)

# Optional
OPIK_API_KEY=xxxxx                # For observability (optional)
```

### Getting API Keys

1. **Dedalus API Key**
   - Sign up at [dedaluslabs.ai](https://dedaluslabs.ai)
   - Navigate to dashboard → Settings → API Keys
   - Generate a new key

2. **Google API Key** (for Gemini models)
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Enable Gemini API

3. **Exa API Key** (for market analysis)
   - Sign up at [Exa AI](https://exa.ai/)
   - Navigate to [API Keys Dashboard](https://dashboard.exa.ai/api-keys)
   - Generate a new API key

## Verify Installation

### 1. Check Backend Health
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

### 2. Check Target Audiences
```bash
curl http://localhost:8000/target-audiences
# Should return list of 6 audiences
```

### 3. Test Frontend
- Open `http://localhost:5173` in browser
- You should see the "AI Pitch Deck Generator" interface
- Dropdown should populate with target audiences

## Usage

### Generate a Pitch Deck

1. **Open the frontend**: `http://localhost:5173`

2. **Fill the form**:
   - **Repository URL**: `https://github.com/username/repo`
   - **Target Audience**: Select from dropdown (e.g., "Seed Stage Investors")
   - **Branch**: Optional (leave empty for default branch)
   - **Format**: Choose "PowerPoint (.pptx)" or "Presenter Script"

3. **Click "Generate Pitch Deck"**
   - First time: Will index the repository (~30-60 seconds)
   - Subsequent times: Much faster (uses cached vector DB)

4. **Download or View**:
   - PowerPoint: Click "Download PowerPoint" button
   - Script: View inline with speaker notes

### Using the CLI

```bash
cd backend

# Index a repository
python run_tools.py "https://github.com/username/repo" "investors" --index

# Search indexed repository
python run_tools.py "https://github.com/username/repo" "investors" --search "What are the main features?"

# Check collection stats
python run_tools.py "https://github.com/username/repo" "investors" --stats
```

## Project Structure

```
marketing-tool/
├── backend/
│   ├── main.py                 # FastAPI app
│   ├── tools/
│   │   └── tools.py           # Repository cloning
│   ├── vectorstore/
│   │   ├── embeddings.py      # FastEmbed wrapper
│   │   ├── store.py           # Chroma client
│   │   ├── chunker.py         # Text chunking
│   │   ├── indexer.py         # Index repos
│   │   └── retrieval.py       # Query vector DB
│   ├── pitch_deck/
│   │   └── generator.py       # PowerPoint generation
│   ├── .vectordb/             # Vector database storage
│   └── temp_pitch_decks/      # Generated files
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── PitchDeckGenerator.jsx
│   │   ├── lib/
│   │   │   └── api.js         # API client
│   │   └── App.jsx
│   └── vite.config.js         # Proxy configuration
└── start-dev.sh               # Development startup script
```

## API Endpoints

- `GET /health` - Health check
- `GET /target-audiences` - List available audiences
- `POST /generate-pitch-deck` - Generate pitch deck
- `GET /download-pitch-deck/{filename}` - Download file
- `POST /test-dedalus` - Test Dedalus integration
- `GET /dedalus-ping` - Ping Dedalus service

Full API documentation: `http://localhost:8000/docs`

## Troubleshooting

### Backend Issues

**"Module not found" errors**
```bash
cd backend
uv sync
```

**"DEDALUS_API_KEY not found"**
- Check `.env` file exists in `backend/` directory
- Verify API key is correct
- Restart the server after adding the key

**"Collection not found"**
- Repository hasn't been indexed yet
- The endpoint auto-indexes, but you can pre-index with CLI

### Frontend Issues

**"Failed to load target audiences"**
- Ensure backend is running: `http://localhost:8000/health`
- Check browser console for errors
- Verify proxy configuration in `vite.config.js`

**CORS errors**
- Should be handled by Vite proxy automatically
- If issues persist, check backend CORS middleware in `main.py`

**API calls fail**
- Check backend is accessible
- Verify proxy is working: Network tab in browser DevTools
- Ensure both servers are running

### Generation Issues

**Timeouts**
- Large repositories take longer on first index
- Subsequent generations are faster
- Check backend logs for errors

**"Failed to parse pitch deck JSON"**
- Model returned invalid JSON
- Check `raw_output` in response
- May need to adjust prompt in `generator.py`

**Empty or poor quality content**
- Repository may have limited documentation
- Try a different target audience
- Check vector DB has indexed content: `--stats` CLI command

## Performance Tips

1. **Pre-index repositories** before generating pitch decks
2. **Use cached vector DB** for faster subsequent generations
3. **Choose appropriate target audience** for better results
4. **Ensure good documentation** in repositories for better content

## Development

### Backend Development
```bash
cd backend
source .venv/bin/activate

# Run with auto-reload
uvicorn main:app --reload

# Run tests (if available)
pytest
```

### Frontend Development
```bash
cd frontend

# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Production Deployment

### Backend
```bash
cd backend
uv sync --no-dev
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend
```bash
cd frontend
npm run build
# Serve the dist/ folder with your preferred static server
```

## Support

For issues or questions:
1. Check this guide first
2. Review `PITCH_DECK_GUIDE.md` for detailed usage
3. Check backend logs for errors
4. Open an issue on GitHub

## Next Steps

- Explore different target audiences
- Try generating pitch decks for various repositories
- Customize slide templates in `backend/pitch_deck/generator.py`
- Add new target audiences
- Integrate with CI/CD for automated pitch deck generation
