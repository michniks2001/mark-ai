"""
Clean, refactored Pitch Deck Generator API.

Flow:
1. Receive request with repo URL and audience
2. Index repository into vector database
3. Retrieve relevant context
4. Analyze sector (primary + secondary tech)
5. Generate market analysis (parallel)
6. Generate pitch deck structure (parallel)
7. Create PowerPoint and script
8. Return files
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
from dotenv import load_dotenv
from pydantic import BaseModel
from pathlib import Path
import tempfile
import asyncio

# Import services
from tools.tools import get_repo, cleanup_repo
from vectorstore.indexer import index_repo
from vectorstore.retrieval import retrieve_context
from vectorstore.store import get_repo_hash
from services.sector_analyzer import analyze_repository_sector
from market_analysis.analyzer import generate_market_analysis
from services.pitch_deck_service import generate_pitch_deck_structure
from pitch_deck.generator import (
    TARGET_AUDIENCES,
    create_powerpoint,
    generate_script
)
from market_analysis.cache import get_cache_stats, clear_expired_cache
from routers import github

load_dotenv()

app = FastAPI(
    title="Pitch Deck Generator API",
    description="AI-powered pitch deck generation from GitHub repositories",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(github.router, prefix="/api/github", tags=["github"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class PitchDeckRequest(BaseModel):
    repository_url: str
    audience_key: str = "general_audience"


class PitchDeckResponse(BaseModel):
    success: bool
    message: str
    powerpoint_path: str = None
    script_path: str = None
    error: str = None


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "Pitch Deck Generator API",
        "version": "1.0.0"
    }


@app.get("/target-audiences")
async def get_target_audiences():
    """Get available target audiences."""
    return {
        "audiences": [
            {"key": key, **config}
            for key, config in TARGET_AUDIENCES.items()
        ]
    }


@app.post("/generate-pitch-deck")
async def generate_pitch_deck(body: PitchDeckRequest):
    """
    Generate pitch deck from GitHub repository.
    
    Flow:
    1. Index repository
    2. Retrieve context
    3. Analyze sector
    4. Generate market analysis (parallel)
    5. Generate pitch deck (parallel)
    6. Create files
    """
    try:
        # ====================================================================
        # STEP 1: INDEX REPOSITORY
        # ====================================================================
        print(f"\n{'='*60}")
        print(f"📦 STEP 1: Indexing repository")
        print(f"{'='*60}")
        
        repo_hash = get_repo_hash(body.repository_url)
        persist_dir = f".vectordb/repo_{repo_hash}"
        
        # Clone and index
        repo_path = get_repo(body.repository_url)
        index_repo(repo_path, body.repository_url, persist_dir)
        cleanup_repo(repo_path)
        
        print(f"✓ Repository indexed successfully\n")
        
        # ====================================================================
        # STEP 2: RETRIEVE CONTEXT
        # ====================================================================
        print(f"{'='*60}")
        print(f"📚 STEP 2: Retrieving context from vector database")
        print(f"{'='*60}")
        
        # Retrieve more context to prevent hallucination
        query = f"Analyze this repository: {body.repository_url}. Focus on: dependencies, tech stack, architecture, features, and implementation details."
        context = retrieve_context(
            query=query,
            repo_url=body.repository_url,
            k=30,  # More chunks
            persist_dir=persist_dir,
            max_context_chars=20000  # More content
        )
        
        print(f"✓ Retrieved {len(context)} characters of context")
        print(f"  📄 Context preview (first 500 chars): {context[:500]}...\n")
        
        # ====================================================================
        # STEP 3: ANALYZE SECTOR
        # ====================================================================
        print(f"{'='*60}")
        print(f"🔍 STEP 3: Analyzing repository sector")
        print(f"{'='*60}")
        
        repo_name = body.repository_url.split('/')[-1].replace('-', ' ').replace('_', ' ').title()
        
        sector_data = await analyze_repository_sector(context, repo_name)
        
        primary_sector = sector_data["primary_sector"]
        secondary_tech = sector_data["secondary_tech"]
        description = sector_data["description"]
        
        print(f"✓ Sector analysis complete\n")
        
        # ====================================================================
        # STEP 4: GENERATE MARKET ANALYSIS
        # ====================================================================
        print(f"{'='*60}")
        print(f"📊 STEP 4: Generating market analysis")
        print(f"{'='*60}")
        print(f"  → Market analysis for {primary_sector} + {', '.join(secondary_tech)}")
        
        # Generate market analysis first
        market_analysis = await generate_market_analysis(
            project_description=primary_sector,
            tech_stack=", ".join(secondary_tech) if secondary_tech else "Software",
            target_audience=TARGET_AUDIENCES[body.audience_key]["label"]
        )
        
        print(f"✓ Market analysis complete\n")
        
        # ====================================================================
        # STEP 5: GENERATE PITCH DECK (with market data)
        # ====================================================================
        print(f"{'='*60}")
        print(f"📝 STEP 5: Generating pitch deck structure")
        print(f"{'='*60}")
        print(f"  → Pitch deck for {TARGET_AUDIENCES[body.audience_key]['label']}")
        print(f"  → Including market data: ${market_analysis.get('market_size', {}).get('value', 'N/A')}")
        
        # Generate pitch deck with market analysis data
        pitch_deck_structure = await generate_pitch_deck_structure(
            context=context,
            audience_key=body.audience_key,
            repo_url=body.repository_url,
            market_analysis=market_analysis  # Now has actual data!
        )
        
        print(f"✓ Pitch deck generation complete\n")
        
        # ====================================================================
        # STEP 6: CREATE FILES
        # ====================================================================
        print(f"{'='*60}")
        print(f"📄 STEP 6: Creating PowerPoint and script")
        print(f"{'='*60}")
        
        # Create temp directory for outputs (matches old code)
        temp_dir = Path("temp_pitch_decks")
        temp_dir.mkdir(exist_ok=True)
        
        # Create filename with repo hash (matches old code pattern)
        filename = f"pitch_deck_{repo_hash}_{body.audience_key}.pptx"
        pptx_path = temp_dir / filename
        
        # Create PowerPoint
        create_powerpoint(
            pitch_deck_structure,
            str(pptx_path)
        )
        print(f"  ✓ PowerPoint created: {pptx_path}")
        
        # Generate script
        script_filename = f"script_{repo_hash}_{body.audience_key}.txt"
        script_path = temp_dir / script_filename
        script = generate_script(pitch_deck_structure)
        script_path.write_text(script)
        print(f"  ✓ Script created: {script_path}")
        
        print(f"\n{'='*60}")
        print(f"✅ SUCCESS: Pitch deck generated!")
        print(f"{'='*60}\n")
        
        # Return response with download URLs (matches old code format)
        return {
            "success": True,
            "message": "Pitch deck generated successfully",
            "format": "pptx",
            "download_url": f"/download-pitch-deck/{filename}",
            "script_url": f"/download-pitch-deck/{script_filename}",
            "pitch_data": pitch_deck_structure,
            "powerpoint_path": str(pptx_path),
            "script_path": str(script_path)
        }
        
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"❌ ERROR: {str(e)}")
        print(f"{'='*60}\n")
        
        return PitchDeckResponse(
            success=False,
            message="Failed to generate pitch deck",
            error=str(e)
        )


@app.get("/download-pitch-deck/{filename}")
async def download_pitch_deck(filename: str):
    """Download a generated pitch deck file (PowerPoint or script)."""
    file_path = Path("temp_pitch_decks") / filename
    
    if not file_path.exists():
        return {"error": "File not found"}
    
    # Determine media type based on extension
    if filename.endswith('.pptx'):
        media_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    elif filename.endswith('.txt'):
        media_type = "text/plain"
    else:
        media_type = "application/octet-stream"
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type=media_type
    )


@app.get("/cache/stats")
async def cache_stats():
    """Get cache statistics."""
    return get_cache_stats()


@app.post("/cache/clear")
async def clear_cache():
    """Clear expired cache entries."""
    try:
        cleared_count = clear_expired_cache()
        return {
            "success": True,
            "cleared_entries": cleared_count,
            "message": f"Cleared {cleared_count} expired cache entries"
        }
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
