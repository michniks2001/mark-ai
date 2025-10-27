# Market Analysis Integration Guide

## Overview

The Marketing Tool now includes AI-powered market analysis using the **Exa Search MCP server** integrated with Dedalus:

- **Exa Search MCP**: Comprehensive research including web search, company intelligence, and LinkedIn data

This powerful search tool automatically researches market size, competitors, trends, and opportunities to create comprehensive, data-driven pitch decks.

## What is MCP?

**Model Context Protocol (MCP)** is a standard for connecting AI models to external tools and data sources.

### Exa Search MCP Server

Provides comprehensive research and intelligence capabilities:

- **Company Research**: Deep-dive into company information, funding, products
- **Web Search**: Optimized search with content extraction
- **LinkedIn Search**: Search for companies and people on LinkedIn
- **Code Search**: Find code snippets and documentation (for technical projects)
- **Deep Researcher**: AI-powered comprehensive research reports

## Caching System

To avoid excessive API calls and reduce costs, market analysis results are **automatically cached** for 7 days.

### How Caching Works

1. **Cache Key**: Generated from project description + tech stack + target audience
2. **Storage**: Stored in ChromaDB (same vector database as repository data)
3. **TTL**: 7 days by default (configurable)
4. **Automatic**: No configuration needed - works out of the box

### Benefits

✅ **Faster responses**: Cached results return instantly
✅ **Cost savings**: Avoid redundant API calls to Brave/Exa
✅ **Token efficiency**: No repeated MCP server calls
✅ **Consistent data**: Same analysis for identical requests

### Cache Management

**Check cache statistics:**
```bash
curl http://localhost:8000/market-analysis/cache/stats
```

**Clear expired entries:**
```bash
curl -X POST http://localhost:8000/market-analysis/cache/clear
```

## How It Works

### 1. Market Analysis Flow (with Caching)

```
User requests pitch deck
    ↓
Extract project description from repository
    ↓
Check cache for existing market analysis
    ↓
    Cache HIT? → Return cached data (instant)
    ↓
    Cache MISS? → Continue to Exa Search
    ↓
Dedalus Runner with Exa Search MCP
    ↓
AI performs multiple searches using Exa tools:
    - web_search_exa: Market size, trends, forecasts
    - company_research: Deep competitor analysis
    - linkedin_search: Company intelligence
    ↓
Synthesize data into structured JSON
    ↓
Store in cache (7 day TTL)
    ↓
Format for pitch deck slide
    ↓
Include in PowerPoint/Script
```

### 2. Exa Search MCP Integration

The system uses Dedalus to connect to the **Exa Search MCP server**:

```python
result = await runner.run(
    input=prompt,
    model="openai/gpt-5-mini",
    mcp_servers=["windsor/exa-search-mcp"],  # Exa Search only
    stream=False
)
```

The AI automatically uses the appropriate Exa tools:
- **web_search_exa** for market trends, news, and general research
- **company_research** for deep competitor analysis
- **linkedin_search** for company and people intelligence

## Setup

### 1. Get Exa Search API Key

1. Sign up at [Exa AI](https://exa.ai/)
2. Navigate to [API Keys Dashboard](https://dashboard.exa.ai/api-keys)
3. Generate a new API key
4. Plans available:
   - **Free tier**: Limited queries for testing
   - **Paid plans**: Higher limits and advanced features

### 2. Add to Environment

Edit `backend/.env`:

```bash
EXA_API_KEY=your_actual_exa_api_key_here
```

### 3. Restart Backend

```bash
cd backend
uvicorn main:app --reload
```

## Market Analysis Output

### Structure

```json
{
  "market_size": {
    "value": "$X billion",
    "growth_rate": "X% CAGR",
    "forecast": "Expected to reach $Y billion by 2028"
  },
  "competitive_landscape": {
    "key_competitors": ["Competitor A", "Competitor B", "Competitor C"],
    "market_leaders": ["Leader 1", "Leader 2"],
    "competitive_advantage": "Unique differentiator"
  },
  "trends": {
    "current_trends": ["Trend 1", "Trend 2", "Trend 3"],
    "opportunities": ["Opportunity 1", "Opportunity 2"],
    "challenges": ["Challenge 1", "Challenge 2"]
  },
  "target_market": {
    "segment_size": "X million users",
    "pain_points": ["Pain point 1", "Pain point 2"],
    "adoption_drivers": ["Driver 1", "Driver 2"]
  },
  "sources": ["https://source1.com", "https://source2.com"]
}
```

### Slide Content

The market analysis is automatically formatted into a concise slide:

```
• Market Size: $X billion (Y% CAGR)
• Key Trend: AI adoption accelerating
• Key Trend: Cloud migration increasing
• Key Competitors: CompanyA, CompanyB, CompanyC
• Opportunity: Underserved SMB market
```

### Speaker Notes

Detailed notes for presenters:

```
Market Overview: The market is valued at $X billion with a growth rate of Y% CAGR.
Expected to reach $Z billion by 2028.

Competitive Landscape: Main competitors include CompanyA, CompanyB, CompanyC.
Our advantage: Unique AI-powered approach with better UX.

Key Trends: AI adoption, cloud migration, automation demand

Target Market: Segment size is X million users.
Key pain points: High costs, complexity
```

## API Endpoints

### POST /market-analysis

Generate standalone market analysis (for testing).

**Request:**
```json
{
  "project_description": "An AI-powered code review tool",
  "tech_stack": "Python, FastAPI, React",
  "target_audience": "Enterprise Buyers",
  "model": "openai/gpt-5-mini"
}
```

**Response:**
```json
{
  "market_data": { ... },
  "slide_content": "Formatted slide content",
  "speaker_notes": "Detailed speaker notes"
}
```

### POST /generate-pitch-deck

Market analysis is automatically included when generating pitch decks.

**Request:**
```json
{
  "repository_url": "https://github.com/username/repo",
  "audience_key": "seed_investors",
  "branch": "main",
  "format": "pptx"
}
```

The generated pitch deck will include a "Market Analysis" slide with:
- AI-researched market data
- Competitive landscape
- Trends and opportunities
- Cited sources

## MCP Server Details

### Brave Search MCP Server

- **Identifier**: `tsion/brave-search-mcp`
- **Provider**: Brave Search API
- **Documentation**: [GitHub](https://github.com/brave/brave-search-mcp-server)

### Available Tools

The MCP server provides these tools (used automatically by AI):

1. **brave_web_search**: Comprehensive web searches
2. **brave_news_search**: Current news articles
3. **brave_local_search**: Local business data (Pro plan)
4. **brave_video_search**: Video content
5. **brave_image_search**: Image content
6. **brave_summarizer**: AI-powered summaries

### Search Parameters

The AI automatically uses appropriate parameters:

- **query**: Search terms (max 400 chars)
- **country**: Country code (default: "US")
- **count**: Results per page (1-20)
- **safesearch**: Content filtering ("moderate")
- **freshness**: Time filter (e.g., "pm" for past month)

## Usage Examples

### Example 1: Generate Pitch Deck with Market Analysis

```bash
curl -X POST http://localhost:8000/generate-pitch-deck \
  -H "Content-Type: application/json" \
  -d '{
    "repository_url": "https://github.com/username/ai-tool",
    "audience_key": "seed_investors",
    "format": "pptx"
  }'
```

**Result**: PowerPoint with Market Analysis slide containing:
- AI market size and growth data
- Competitor research
- Industry trends
- Target market insights

### Example 2: Standalone Market Analysis

```bash
curl -X POST http://localhost:8000/market-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "project_description": "AI code review tool for enterprises",
    "tech_stack": "Python, React, PostgreSQL",
    "target_audience": "Enterprise Buyers"
  }'
```

**Result**: JSON with market data, slide content, and speaker notes.

### Example 3: Frontend Usage

The frontend automatically includes market analysis when generating pitch decks. No additional configuration needed.

## Customization

### Adjust Search Queries

Edit `backend/market_analysis/analyzer.py`:

```python
prompt = f"""You are a market research analyst...

Perform multiple searches to gather comprehensive data:
- Search for market size and industry reports
- Search for competitors and similar solutions
- Search for recent news and trends
- Search for target audience insights
- ADD YOUR CUSTOM SEARCHES HERE
"""
```

### Change Market Analysis Slide Position

Edit `backend/pitch_deck/generator.py` to reorder slides in the prompt.

### Customize Formatting

Edit formatting functions in `backend/market_analysis/analyzer.py`:

- `format_market_analysis_for_slide()`: Slide content
- `format_market_analysis_speaker_notes()`: Speaker notes

## Troubleshooting

### "BRAVE_API_KEY not found"

**Cause**: API key not set in environment
**Fix**:
```bash
# Add to backend/.env
BRAVE_API_KEY=your_key_here

# Restart backend
uvicorn main:app --reload
```

### "Failed to generate market analysis"

**Cause**: MCP server connection issue or API limit reached
**Fix**:
- Check Brave API key is valid
- Verify you haven't exceeded API quota (2,000/month on free plan)
- Check backend logs for detailed error

### "Data not available" in market analysis

**Cause**: AI couldn't find relevant data via search
**Fix**:
- This is expected for very niche or new projects
- The slide will indicate data is unavailable
- Recommend manual market research

### Market analysis takes too long

**Cause**: Multiple search queries being performed
**Fix**:
- This is normal (30-60 seconds)
- Consider upgrading to Brave Pro for faster responses
- Results are cached in pitch deck, so regeneration is fast

## Best Practices

1. **Use descriptive project descriptions**: Better descriptions = better search queries
2. **Choose appropriate target audience**: Influences what market data is prioritized
3. **Review and verify data**: AI-generated market data should be validated
4. **Cite sources**: Speaker notes include source URLs for verification
5. **Supplement with manual research**: Use AI data as a starting point

## API Limits

### Brave Search Free Plan
- 2,000 queries/month
- Basic web search only
- No local search or AI summaries

### Brave Search Pro Plan
- Higher query limits
- Local business search
- AI-powered summaries
- Extra snippets

**Recommendation**: Start with free plan, upgrade if needed.

## Privacy & Data

- All searches go through Brave Search API
- No data is stored by Brave beyond standard API logs
- Market analysis results are included in generated pitch decks
- Sources are cited for transparency

## Future Enhancements

Potential improvements:

1. **Cache market data**: Store results to reduce API calls
2. **Custom search queries**: Let users specify what to research
3. **Multiple MCP servers**: Integrate additional data sources
4. **Real-time updates**: Refresh market data periodically
5. **Competitive analysis deep-dive**: Dedicated competitor research

## Support

For issues with:
- **Brave Search API**: [Brave Support](https://brave.com/search/api/)
- **MCP Server**: [GitHub Issues](https://github.com/brave/brave-search-mcp-server/issues)
- **Dedalus Integration**: [Dedalus Docs](https://docs.dedaluslabs.ai/)
- **This Tool**: Check backend logs and GitHub issues

## Resources

- [Brave Search API Docs](https://brave.com/search/api/)
- [Brave MCP Server GitHub](https://github.com/brave/brave-search-mcp-server)
- [Dedalus MCP Integration](https://docs.dedaluslabs.ai/examples/04-mcp-integration)
- [Model Context Protocol](https://modelcontextprotocol.io/)
