"""Market analysis using Exa Search MCP server via Dedalus."""
from typing import Dict, Any
from dedalus_labs import AsyncDedalus, DedalusRunner
from .cache import (
    get_cached_market_analysis,
    cache_market_analysis,
    get_cache_key
)
from .google_market_search import search_market_size


async def generate_market_analysis(
    project_description: str,
    tech_stack: str,
    target_audience: str,
    model: str = "openai/gpt-5-mini",
    use_cache: bool = True,
    cache_ttl_days: int = 7
) -> Dict[str, Any]:
    """
    Generate market analysis using Exa Search MCP server.
    Results are cached to avoid redundant API calls.
    
    Args:
        project_description: Brief description of the project
        tech_stack: Technologies used in the project
        target_audience: Target audience label
        model: Model to use for analysis
        use_cache: Whether to use cached results (default: True)
        cache_ttl_days: Cache time-to-live in days (default: 7)
        
    Returns:
        Dictionary with market analysis data
    """
    # Check cache first
    if use_cache:
        cached_data = get_cached_market_analysis(
            project_description,
            tech_stack,
            target_audience
        )
        if cached_data:
            print(f"✓ Using cached market analysis (key: {get_cache_key(project_description, tech_stack, target_audience)[:8]}...)")
            return cached_data
    
    print(f"⚡ Generating fresh market analysis...")
    
    # Step 1: Get market size data from Google search
    print(f"  → Searching Google for market size data...")
    market_size_data = await search_market_size(project_description, tech_stack)
    
    # Step 2: Get competitive intelligence from Exa
    print(f"  → Querying Exa Search for competitive intelligence...")
    client = AsyncDedalus()
    runner = DedalusRunner(client)
    
    # Get audience-specific focus
    from pitch_deck.generator import get_target_audience_config
    audience_config = get_target_audience_config(target_audience.lower().replace(' ', '_').replace('/', '_'))
    market_focus = audience_config.get('market_focus', 'competitive landscape and market opportunity')
    competitor_angle = audience_config.get('competitor_angle', 'competitive advantages')
    
    # Build prompt that will leverage Exa Search MCP
    prompt = f"""You are a market research analyst with access to Exa Search tools. Research the market for this project.

Project to analyze:
- Description: {project_description}
- Tech Stack: {tech_stack}
- Target Audience: {target_audience}

CRITICAL AUDIENCE-SPECIFIC FOCUS:
This analysis is for {target_audience}. They care most about: {market_focus}

When analyzing competitors, focus on: {competitor_angle}

Use the available Exa Search tools to research:

1. **Competitor Research** (TAILORED FOR {target_audience}):
   - Use company_research and web_search_exa to identify key competitors
   - Focus on {competitor_angle}
   - Highlight what makes this project stand out in ways that matter to {target_audience}

2. **Market Trends** (RELEVANT TO {target_audience}):
   - Use web_search_exa to find industry trends
   - Focus on {market_focus}
   - Identify opportunities that align with {target_audience} priorities

3. **Target Audience Insights**:
   - Research specific needs and pain points of {target_audience}
   - Understand what they value most in solutions

Note: Market size data will be provided separately, so focus on competitive landscape, trends, and opportunities.

After gathering information, synthesize it into a structured analysis. Return ONLY valid JSON with this structure:

{{
  "competitive_landscape": {{
    "key_competitors": ["List of 3-5 main competitors"],
    "market_leaders": ["Top 2-3 market leaders"],
    "competitive_advantage": "How this project differentiates"
  }},
  "trends": {{
    "current_trends": ["3-5 key market trends"],
    "opportunities": ["2-3 market opportunities"],
    "challenges": ["2-3 market challenges"]
  }},
  "target_market": {{
    "segment_size": "Size of target market segment",
    "pain_points": ["3-4 key pain points"],
    "adoption_drivers": ["2-3 factors driving adoption"]
  }},
  "sources": ["List of URLs used for research"]
}}

Important:
- Use actual search results from Brave Search
- Cite specific sources and data points
- Be realistic and data-driven
- If data is not available, indicate "Data not available" rather than making up numbers
- Return ONLY the JSON, no markdown formatting
"""
    
    try:
        # Use Exa Search MCP
        result = await runner.run(
            input=prompt,
            model=model,
            mcp_servers=["windsor/exa-search-mcp"],
            stream=False
        )
        
        output = getattr(result, "final_output", "")
        
        if not output or not output.strip():
            raise ValueError("Empty response from Exa Search")
        
        # Try to parse as JSON
        import json
        import re
        
        # Clean output - extract JSON from response
        clean_output = output.strip()
        
        # Strategy 1: Extract from markdown code blocks
        if '```' in clean_output:
            json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', clean_output, re.DOTALL)
            if json_match:
                clean_output = json_match.group(1).strip()
        
        # Strategy 2: Extract from first { to last }
        if not clean_output.startswith('{'):
            json_start = clean_output.find('{')
            json_end = clean_output.rfind('}')
            if json_start != -1 and json_end != -1 and json_end > json_start:
                clean_output = clean_output[json_start:json_end+1]
        
        exa_data = json.loads(clean_output)
        
        # Merge Google market size data with Exa competitive intelligence
        market_data = {
            "market_size": market_size_data,
            **exa_data
        }
        
        print(f"✓ Market analysis complete (Google + Exa)")
        
        # Cache the successful result
        if use_cache:
            try:
                cache_market_analysis(
                    project_description,
                    tech_stack,
                    target_audience,
                    market_data,
                    ttl_days=cache_ttl_days
                )
                print(f"✓ Market analysis cached for {cache_ttl_days} days")
            except Exception as cache_error:
                print(f"Warning: Failed to cache market analysis: {cache_error}")
        
        return market_data
        
    except json.JSONDecodeError as e:
        # Exa Search failed, but we still have Google data
        print(f"⚠️  Exa Search JSON Parse Error: {str(e)}")
        print(f"   Raw output: {output[:200]}...")
        print(f"✓ Continuing with Google market data only")
        
        # Return just the Google market size data
        return {
            "market_size": market_size_data,
            "competitive_landscape": {
                "key_competitors": [],
                "market_leaders": [],
                "competitive_advantage": "Data not available"
            },
            "trends": {
                "current_trends": [],
                "opportunities": [],
                "challenges": []
            },
            "target_market": {
                "segment_size": "Data not available",
                "pain_points": [],
                "adoption_drivers": []
            },
            "sources": []
        }
    except Exception as e:
        print(f"⚠️  Exa Search Error: {str(e)}")
        print(f"✓ Continuing with Google market data only")
        import traceback
        traceback.print_exc()
        return {
            "error": str(e),
            "message": "Failed to generate market analysis"
        }


def format_market_analysis_for_slide(market_data: Dict[str, Any]) -> str:
    """
    Format market analysis data into slide content.
    
    Args:
        market_data: Market analysis dictionary
        
    Returns:
        Formatted string for slide content
    """
    if "error" in market_data:
        error_msg = market_data.get("error", "Unknown error")
        print(f"⚠️  Formatting market analysis with error: {error_msg}")
        return f"Market analysis data unavailable ({error_msg}). Please conduct manual research."
    
    content_parts = []
    
    # Market Size
    if "market_size" in market_data:
        ms = market_data["market_size"]
        value = ms.get('value', 'N/A')
        growth = ms.get('growth_rate', 'N/A')
        
        # Check if we have real data or just placeholders
        if value and value != 'N/A' and 'not found' not in value.lower() and 'configure' not in value.lower():
            content_parts.append(f"• Market Size: {value}")
            if growth and growth != 'N/A' and 'not found' not in growth.lower():
                content_parts.append(f"• Growth Rate: {growth}")
        else:
            print(f"⚠️  Market size data not available: {value}")
    
    # Key Trends
    if "trends" in market_data and "current_trends" in market_data["trends"]:
        trends = market_data["trends"]["current_trends"][:2]  # Top 2 trends
        if trends:
            content_parts.append("• Key Trends:")
            for trend in trends:
                content_parts.append(f"  - {trend}")
    
    # Competitive Landscape
    if "competitive_landscape" in market_data:
        comp = market_data["competitive_landscape"]
        if "key_competitors" in comp and comp["key_competitors"]:
            competitors = ", ".join(comp["key_competitors"][:3])
            content_parts.append(f"• Key Competitors: {competitors}")
    
    # Opportunities
    if "trends" in market_data and "opportunities" in market_data["trends"]:
        opps = market_data["trends"]["opportunities"][:2]
        if opps:
            content_parts.append("• Market Opportunities:")
            for opp in opps:
                content_parts.append(f"  - {opp}")
    
    if not content_parts:
        print("⚠️  No market analysis content available")
        return "Market analysis in progress. Competitive intelligence and trends available from Exa Search."
    
    return "\n".join(content_parts)


def format_market_analysis_speaker_notes(market_data: Dict[str, Any]) -> str:
    """
    Format market analysis data into speaker notes.
    
    Args:
        market_data: Market analysis dictionary
        
    Returns:
        Formatted string for speaker notes
    """
    if "error" in market_data:
        return "Market data could not be retrieved. Recommend conducting independent market research before presenting."
    
    notes_parts = []
    
    # Market Overview
    if "market_size" in market_data:
        ms = market_data["market_size"]
        notes_parts.append(
            f"Market Overview: The market is valued at {ms.get('value', 'N/A')} "
            f"with a growth rate of {ms.get('growth_rate', 'N/A')}. "
            f"{ms.get('forecast', '')}"
        )
    
    # Competitive Positioning
    if "competitive_landscape" in market_data:
        comp = market_data["competitive_landscape"]
        notes_parts.append(
            f"Competitive Landscape: Main competitors include {', '.join(comp.get('key_competitors', [])[:3])}. "
            f"Our advantage: {comp.get('competitive_advantage', 'To be determined')}"
        )
    
    # Market Trends
    if "trends" in market_data:
        trends = market_data["trends"]
        notes_parts.append(
            f"Key Trends: {', '.join(trends.get('current_trends', [])[:3])}"
        )
    
    # Target Market
    if "target_market" in market_data:
        tm = market_data["target_market"]
        notes_parts.append(
            f"Target Market: Segment size is {tm.get('segment_size', 'N/A')}. "
            f"Key pain points: {', '.join(tm.get('pain_points', [])[:2])}"
        )
    
    # Sources
    if "sources" in market_data and market_data["sources"]:
        sources_list = market_data["sources"][:3]
        notes_parts.append(f"Sources: {', '.join(sources_list)}")
    
    return "\n\n".join(notes_parts) if notes_parts else "Conduct additional market research as needed."
