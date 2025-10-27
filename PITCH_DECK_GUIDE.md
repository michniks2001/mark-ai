# Pitch Deck Generator - Usage Guide

## Overview
The pitch deck generator creates professional PowerPoint presentations and presenter scripts from GitHub repositories using AI analysis and vector embeddings.

## Features
- **6 Predefined Target Audiences** with tailored content
- **PowerPoint Generation** with speaker notes
- **Presenter Script** in markdown format
- **Vector DB Integration** for efficient context retrieval
- **Auto-indexing** of repositories

## Target Audiences

### 1. Seed Stage Investors
- **Focus**: Problem-solution fit, market opportunity, founding team, early traction, funding ask
- **Tone**: Compelling, data-driven, visionary
- **Best for**: Early-stage fundraising pitches

### 2. Series A Investors
- **Focus**: Product-market fit, growth metrics, unit economics, competitive advantage, scaling strategy
- **Tone**: Metrics-focused, strategic, proven
- **Best for**: Growth-stage fundraising

### 3. Enterprise Buyers
- **Focus**: ROI, security, integration, support, compliance, case studies
- **Tone**: Professional, trustworthy, technical
- **Best for**: B2B sales presentations

### 4. Technical Team / Engineers
- **Focus**: Architecture, tech stack, scalability, code quality, developer experience, documentation
- **Tone**: Technical, detailed, pragmatic
- **Best for**: Technical deep-dives, hiring pitches

### 5. Product Managers
- **Focus**: Features, roadmap, user experience, market fit, competitive analysis
- **Tone**: Strategic, user-focused, analytical
- **Best for**: Product strategy discussions

### 6. General Audience
- **Focus**: What it does, why it matters, key benefits, use cases
- **Tone**: Accessible, clear, engaging
- **Best for**: General presentations, demos

## API Endpoints

### GET /target-audiences
Returns list of available target audiences with their configurations.

```bash
curl http://localhost:8000/target-audiences
```

### POST /generate-pitch-deck
Generate a pitch deck from a repository.

**Request Body:**
```json
{
  "repository_url": "https://github.com/username/repo",
  "audience_key": "seed_investors",
  "branch": "main",
  "format": "pptx"
}
```

**Parameters:**
- `repository_url` (required): GitHub repository URL
- `audience_key` (required): One of the predefined audience keys
- `branch` (optional): Git branch to analyze (defaults to default branch)
- `format` (required): Either "pptx" or "script"

**Response (PowerPoint):**
```json
{
  "format": "pptx",
  "download_url": "/download-pitch-deck/pitch_deck_abc123_seed_investors.pptx",
  "pitch_data": {
    "title": "Project Name",
    "slides": [...]
  }
}
```

**Response (Script):**
```json
{
  "format": "script",
  "content": "# Presentation Script...",
  "pitch_data": {
    "title": "Project Name",
    "slides": [...]
  }
}
```

### GET /download-pitch-deck/{filename}
Download a generated PowerPoint file.

## Pitch Deck Structure

Each generated pitch deck includes:

1. **Cover Slide**: Project name and tagline
2. **Problem**: What problem does this solve?
3. **Solution**: How does the project address it?
4. **Product/Features**: Core capabilities
5. **Technology**: Tech stack and architecture
6. **Traction/Progress**: Development momentum
7. **Roadmap**: Future plans
8. **Call to Action**: Next steps for the audience

## Frontend Usage

1. **Start the backend**:
```bash
cd backend
uvicorn main:app --reload
```

2. **Start the frontend**:
```bash
cd frontend
npm run dev
```

3. **Open browser**: http://localhost:5173

4. **Fill the form**:
   - Enter GitHub repository URL
   - Select target audience
   - Choose output format (PowerPoint or Script)
   - Click "Generate Pitch Deck"

5. **Download or view**:
   - PowerPoint: Click "Download PowerPoint" button
   - Script: View inline with speaker notes

## CLI Usage

You can also use the CLI to test:

```bash
# Index a repository first (optional, auto-indexes if needed)
python run_tools.py "https://github.com/username/repo" "investors" --index

# Check stats
python run_tools.py "https://github.com/username/repo" "investors" --stats

# Search for specific content
python run_tools.py "https://github.com/username/repo" "investors" --search "What are the main features?"
```

## How It Works

1. **Repository Analysis**:
   - Clones repository (shallow, filtered)
   - Extracts commits (source files only, no tests/examples)
   - Collects documentation (README, docs/, etc.)

2. **Vector Indexing**:
   - Chunks documentation (1500 chars, 200 overlap)
   - Chunks commits (per-file with diffs)
   - Generates embeddings using FastEmbed
   - Stores in Chroma vector database

3. **Context Retrieval**:
   - Builds query based on target audience
   - Retrieves top 15-20 relevant chunks
   - Assembles context (≤15k chars)

4. **AI Generation**:
   - Passes context + structured prompt to Dedalus
   - Model generates pitch deck JSON
   - Parses and validates structure

5. **Output Creation**:
   - **PowerPoint**: Uses python-pptx to create slides with speaker notes
   - **Script**: Formats as markdown with "On Screen" and "What to Say" sections

## Customization

### Adding New Audiences

Edit `backend/pitch_deck/generator.py`:

```python
TARGET_AUDIENCES = {
    "your_audience_key": {
        "label": "Your Audience Name",
        "focus": "what to emphasize",
        "tone": "how to present"
    }
}
```

### Adjusting Slide Structure

Modify the prompt in `build_pitch_deck_prompt()` to add/remove/reorder slides.

### Changing Models

Update the model in `main.py`:
```python
model="openai/gpt-5-mini"  # or "google/gemini-2.5-flash"
```

## Troubleshooting

### "Collection not found"
- The repository hasn't been indexed yet
- Solution: The endpoint auto-indexes, but you can pre-index with CLI

### "Failed to parse pitch deck JSON"
- Model returned invalid JSON
- Solution: Check raw_output in response, adjust prompt if needed

### PowerPoint download fails
- File not generated or deleted
- Solution: Check backend logs, ensure temp_pitch_decks/ directory exists

### Timeout errors
- Repository too large or network issues
- Solution: Use vector DB (already implemented), check network

## File Structure

```
backend/
├── main.py                    # FastAPI endpoints
├── tools/
│   └── tools.py              # Repository cloning and filtering
├── vectorstore/
│   ├── embeddings.py         # FastEmbed wrapper
│   ├── store.py              # Chroma client
│   ├── chunker.py            # Text chunking
│   ├── indexer.py            # Index repo data
│   └── retrieval.py          # Query and retrieve
├── pitch_deck/
│   └── generator.py          # PowerPoint and script generation
└── .vectordb/                # Persisted vector database

frontend/
└── src/
    └── components/
        └── PitchDeckGenerator.jsx  # React UI
```

## Next Steps

- Add PDF export option
- Implement slide customization UI
- Add more audience templates
- Support private repositories (auth)
- Add slide preview before download
- Implement batch generation for multiple audiences
