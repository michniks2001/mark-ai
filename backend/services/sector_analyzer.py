"""Sector analysis service using Dedalus AI."""
import json
import re
from typing import Dict, List, Optional
from dedalus_labs import AsyncDedalus, DedalusRunner


async def analyze_repository_sector(context: str, repo_name: str) -> Dict[str, any]:
    """
    Analyze repository content to extract primary sector and technologies.
    
    Args:
        context: Repository content from vector database
        repo_name: Name of the repository
        
    Returns:
        Dict with primary_sector, secondary_tech, and description
    """
    print(f"🔍 Analyzing repository content for sector detection...")
    
    # Build analysis prompt with emphasis on accuracy
    analysis_prompt = f"""CRITICAL: Analyze ONLY the actual repository content provided below. Do NOT make assumptions or add information not present in the content.

Repository: {repo_name}

ACTUAL REPOSITORY CONTENT:
{context[:5000]}

Extract from the ACTUAL content above:
1. PRIMARY purpose/sector (e.g., education, healthcare, finance)
2. ACTUAL technologies/dependencies used (check package.json, requirements.txt, imports, etc.)
3. Brief description based on README or code
4. Key features mentioned in the code or documentation

IMPORTANT: 
- Only list technologies that are ACTUALLY mentioned in the content
- If you see "weaviate" in dependencies, list it. If you see "mongodb", list it.
- Do NOT guess or hallucinate technologies
- Base your analysis ONLY on the provided content

Respond in JSON format:
{{
    "primary_sector": "education/healthcare/finance/etc",
    "secondary_tech": ["AI", "machine learning"],
    "description": "Brief description based on actual content",
    "key_features": ["feature1", "feature2"]
}}"""

    # Call Dedalus AI
    client = AsyncDedalus()
    runner = DedalusRunner(client)
    
    try:
        print(f"  🤖 Calling LLM for sector analysis...")
        
        result = await runner.run(
            input=analysis_prompt,
            model="openai/gpt-4o-mini",
        )
        
        output = getattr(result, "final_output", "")
        
        if not output or not output.strip():
            raise ValueError("Empty LLM response")
        
        # Extract JSON from response (handles markdown code blocks)
        clean_json = _extract_json_from_response(output)
        
        # Parse JSON
        sector_data = json.loads(clean_json)
        
        primary_sector = sector_data.get("primary_sector", "software")
        secondary_tech = sector_data.get("secondary_tech", [])
        description = sector_data.get("description", repo_name)
        
        print(f"  ✓ Primary Sector: {primary_sector}")
        print(f"  ✓ Secondary Tech: {', '.join(secondary_tech)}")
        print(f"  ✓ Description: {description[:100]}...")
        
        return {
            "primary_sector": primary_sector,
            "secondary_tech": secondary_tech,
            "description": description,
            "success": True
        }
        
    except Exception as e:
        print(f"  ⚠️  Sector analysis failed: {str(e)}")
        
        # Fallback to simple detection
        return {
            "primary_sector": "software",
            "secondary_tech": _detect_tech_from_context(context),
            "description": repo_name,
            "success": False
        }


def _extract_json_from_response(response: str) -> str:
    """Extract JSON from LLM response that may contain markdown or explanatory text."""
    clean = response.strip()
    
    # Strategy 1: Extract from markdown code blocks
    if '```' in clean:
        json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', clean, re.DOTALL)
        if json_match:
            clean = json_match.group(1).strip()
    
    # Strategy 2: Extract from first { to last }
    if not clean.startswith('{'):
        json_start = clean.find('{')
        json_end = clean.rfind('}')
        if json_start != -1 and json_end != -1 and json_end > json_start:
            clean = clean[json_start:json_end+1]
    
    return clean


def _detect_tech_from_context(context: str) -> List[str]:
    """Fallback: Detect tech stack from context using keywords."""
    tech_indicators = {
        'AI': ['ai', 'artificial intelligence', 'machine learning', 'ml', 'gpt', 'llm'],
        'Python': ['python', '.py', 'django', 'flask', 'fastapi'],
        'JavaScript': ['javascript', '.js', 'react', 'vue', 'angular', 'node'],
        'TypeScript': ['typescript', '.ts', 'tsx'],
        'Blockchain': ['blockchain', 'web3', 'ethereum', 'smart contract'],
    }
    
    detected = []
    context_lower = context.lower() if context else ""
    
    for tech, indicators in tech_indicators.items():
        if any(ind in context_lower for ind in indicators):
            detected.append(tech)
    
    return detected[:3]  # Return top 3
