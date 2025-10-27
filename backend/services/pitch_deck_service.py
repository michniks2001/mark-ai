"""Pitch deck generation service."""
import json
from typing import Dict, Any
from dedalus_labs import AsyncDedalus, DedalusRunner
from pitch_deck.generator import build_pitch_deck_prompt


async def generate_pitch_deck_structure(
    context: str,
    audience_key: str,
    repo_url: str,
    market_analysis: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate pitch deck structure using Dedalus AI.
    
    Args:
        context: Repository content from vector database
        audience_key: Target audience identifier
        repo_url: GitHub repository URL
        market_analysis: Market analysis data
        
    Returns:
        Dict with title and slides
    """
    print(f"  📊 Generating pitch deck structure...")
    
    # Build prompt with audience-specific requirements
    prompt = build_pitch_deck_prompt(context, audience_key, repo_url)
    
    # Add market analysis to prompt
    market_content = _format_market_analysis_for_prompt(market_analysis)
    
    # Add emphasis on accuracy
    accuracy_note = """
CRITICAL INSTRUCTION: Use ONLY information from the repository context provided above.
- Do NOT make up or assume technologies, features, or details
- If the repository uses Weaviate, say Weaviate (not MongoDB)
- If the repository uses specific libraries, mention those exact libraries
- Base ALL content on the actual code, commits, and documentation provided
"""
    
    full_prompt = f"{prompt}\n\n{accuracy_note}\n\nMarket Analysis Data:\n{market_content}"
    
    # Call Dedalus AI
    client = AsyncDedalus()
    runner = DedalusRunner(client)
    
    result = await runner.run(
        input=full_prompt,
        model="openai/gpt-4o-mini",
    )
    
    output = getattr(result, "final_output", "")
    
    if not output or not output.strip():
        raise ValueError("Empty response from LLM")
    
    print(f"  📝 LLM Response (first 200 chars): {output[:200]}...")
    
    # Parse JSON response
    clean_json = _extract_json(output)
    
    print(f"  🧹 Cleaned JSON (first 200 chars): {clean_json[:200]}...")
    
    try:
        pitch_deck = json.loads(clean_json)
    except json.JSONDecodeError as e:
        print(f"  ❌ JSON Parse Error: {str(e)}")
        print(f"  📄 Full cleaned output: {clean_json[:500]}...")
        raise ValueError(f"Failed to parse pitch deck JSON: {str(e)}")
    
    print(f"  ✓ Generated {len(pitch_deck.get('slides', []))} slides")
    
    return pitch_deck


def _format_market_analysis_for_prompt(market_analysis: Dict[str, Any]) -> str:
    """Format market analysis data for inclusion in prompt."""
    if not market_analysis or "error" in market_analysis:
        return "Market analysis data unavailable."
    
    parts = []
    
    # Market size
    if "market_size" in market_analysis:
        ms = market_analysis["market_size"]
        parts.append(f"Market Size: {ms.get('value', 'N/A')}")
        parts.append(f"Growth Rate: {ms.get('growth_rate', 'N/A')}")
        parts.append(f"Forecast: {ms.get('forecast', 'N/A')}")
    
    # Competitive landscape
    if "competitive_landscape" in market_analysis:
        cl = market_analysis["competitive_landscape"]
        parts.append(f"\nKey Competitors: {', '.join(cl.get('key_competitors', []))}")
        parts.append(f"Competitive Advantage: {cl.get('competitive_advantage', 'N/A')}")
    
    # Trends
    if "trends" in market_analysis:
        trends = market_analysis["trends"]
        parts.append(f"\nCurrent Trends: {', '.join(trends.get('current_trends', []))}")
        parts.append(f"Opportunities: {', '.join(trends.get('opportunities', []))}")
    
    return "\n".join(parts)


def _extract_json(response: str) -> str:
    """Extract JSON from LLM response."""
    import re
    
    clean = response.strip()
    
    # Remove markdown code blocks
    if '```' in clean:
        json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', clean, re.DOTALL)
        if json_match:
            clean = json_match.group(1).strip()
    
    # Extract from first { to last }
    if not clean.startswith('{'):
        json_start = clean.find('{')
        json_end = clean.rfind('}')
        if json_start != -1 and json_end != -1:
            clean = clean[json_start:json_end+1]
    
    return clean
