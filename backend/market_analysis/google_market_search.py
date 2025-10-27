"""Google search tool for market size data using Google Custom Search API."""
import os
import httpx
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
import re

# Try to import playwright for dynamic content
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


def _extract_sector_keywords(project_description: str, tech_stack: str) -> str:
    """
    Extract market sector keywords from project description and tech stack.
    Focus on industry/category rather than specific app name.
    Handles multiple overlapping sectors (e.g., "AI + EdTech").
    
    Args:
        project_description: Project name/description
        tech_stack: Technologies used
        
    Returns:
        Sector-focused search keywords (may combine multiple sectors)
    """
    # Primary sector mappings (industry vertical)
    primary_sectors = {
        'mental health': 'mental health',
        'therapy': 'mental health',
        'wellness': 'wellness',
        'health': 'healthcare',
        'medical': 'healthcare',
        'fitness': 'fitness',
        'education': 'education',
        'learning': 'education',
        'teaching': 'education',
        'student': 'education',
        'finance': 'finance',
        'banking': 'banking',
        'payment': 'payments',
        'shopping': 'e-commerce',
        'ecommerce': 'e-commerce',
        'retail': 'retail',
        'food': 'food delivery',
        'restaurant': 'food',
        'delivery': 'delivery',
        'logistics': 'logistics',
        'travel': 'travel',
        'booking': 'booking',
        'hotel': 'hospitality',
        'social': 'social media',
        'messaging': 'messaging',
        'chat': 'messaging',
        'productivity': 'productivity',
        'collaboration': 'collaboration',
        'workplace': 'workplace',
        'code': 'software development',
        'developer': 'developer tools',
        'programming': 'software development',
        'analytics': 'analytics',
        'data': 'data',
        'crm': 'CRM',
        'sales': 'sales',
        'marketing': 'marketing',
        'hr': 'HR',
        'recruitment': 'recruitment',
        'hiring': 'recruitment',
        'real estate': 'real estate',
        'property': 'real estate',
        'gaming': 'gaming',
        'game': 'gaming',
        'entertainment': 'entertainment',
        'music': 'music',
        'video': 'video',
        'streaming': 'streaming',
        'iot': 'IoT',
        'blockchain': 'blockchain',
        'crypto': 'cryptocurrency',
        'nft': 'NFT',
    }
    
    # Technology/approach modifiers (how it's done)
    tech_modifiers = {
        'ai': 'AI-powered',
        'artificial intelligence': 'AI-powered',
        'ml': 'machine learning',
        'machine learning': 'machine learning',
        'automation': 'automation',
        'saas': 'SaaS',
        'cloud': 'cloud-based',
        'mobile': 'mobile',
        'web': 'web-based',
        'platform': 'platform',
        'marketplace': 'marketplace',
    }
    
    # Combine and lowercase
    combined = f"{project_description} {tech_stack}".lower()
    
    # Find all matching primary sectors
    matched_sectors = []
    for keyword, sector in primary_sectors.items():
        if keyword in combined:
            if sector not in matched_sectors:
                matched_sectors.append(sector)
    
    # Find all matching tech modifiers
    matched_modifiers = []
    for keyword, modifier in tech_modifiers.items():
        if keyword in combined:
            if modifier not in matched_modifiers:
                matched_modifiers.append(modifier)
    
    # Debug logging
    if matched_sectors or matched_modifiers:
        print(f"  🔍 Sector Detection: sectors={matched_sectors}, modifiers={matched_modifiers}")
    
    # Build combined search query
    if matched_sectors and matched_modifiers:
        # Combine: "AI-powered education" or "machine learning healthcare"
        primary = matched_sectors[0]
        modifier = matched_modifiers[0]
        
        # Handle special combinations - prioritize the PRIMARY sector
        if 'education' in matched_sectors and any('AI' in m or 'machine learning' in m for m in matched_modifiers):
            return "AI in education edtech artificial intelligence learning platforms educational technology"
        elif 'healthcare' in matched_sectors and any('AI' in m or 'machine learning' in m for m in matched_modifiers):
            return "AI in healthcare digital health artificial intelligence medical technology"
        elif 'finance' in matched_sectors and any('AI' in m or 'machine learning' in m for m in matched_modifiers):
            return "AI in finance fintech artificial intelligence financial services"
        elif 'mental health' in matched_sectors and any('AI' in m or 'machine learning' in m for m in matched_modifiers):
            return "AI mental health digital therapy artificial intelligence wellness apps"
        elif 'fitness' in matched_sectors and any('AI' in m or 'machine learning' in m for m in matched_modifiers):
            return "AI fitness wellness artificial intelligence health tracking"
        elif 'gaming' in matched_sectors and 'blockchain' in matched_modifiers:
            return "blockchain gaming NFT gaming web3 games"
        elif 'real estate' in matched_sectors and 'blockchain' in matched_modifiers:
            return "blockchain real estate proptech tokenization"
        else:
            return f"{modifier} {primary} technology market"
    
    elif matched_sectors:
        # Just primary sector
        primary = matched_sectors[0]
        
        # Map to full search terms
        sector_terms = {
            'mental health': 'mental health apps digital therapy wellness',
            'healthcare': 'healthcare digital health medical technology',
            'fitness': 'fitness wellness apps health tracking',
            'education': 'edtech education technology e-learning',
            'finance': 'fintech financial technology digital banking',
            'banking': 'digital banking fintech financial services',
            'payments': 'payment processing fintech digital payments',
            'e-commerce': 'e-commerce online retail digital commerce',
            'retail': 'retail technology digital retail',
            'food delivery': 'food delivery restaurant technology',
            'food': 'food technology restaurant apps',
            'delivery': 'delivery logistics last-mile delivery',
            'logistics': 'logistics supply chain technology',
            'travel': 'travel technology tourism digital booking',
            'booking': 'booking reservation technology',
            'hospitality': 'hospitality technology hotel management',
            'social media': 'social media social networking',
            'messaging': 'messaging communication apps',
            'productivity': 'productivity software workplace tools',
            'collaboration': 'collaboration software team tools',
            'workplace': 'workplace technology enterprise software',
            'software development': 'software development developer tools',
            'developer tools': 'developer tools software engineering',
            'analytics': 'data analytics business intelligence',
            'data': 'data management big data',
            'CRM': 'CRM customer relationship management',
            'sales': 'sales technology sales enablement',
            'marketing': 'marketing automation martech',
            'HR': 'HR technology human resources software',
            'recruitment': 'recruitment hiring technology ATS',
            'real estate': 'proptech real estate technology',
            'gaming': 'gaming video games entertainment',
            'entertainment': 'entertainment media streaming',
            'music': 'music streaming audio entertainment',
            'video': 'video streaming media',
            'streaming': 'streaming media entertainment',
            'IoT': 'IoT internet of things smart devices',
            'blockchain': 'blockchain cryptocurrency web3',
            'cryptocurrency': 'cryptocurrency blockchain digital assets',
            'NFT': 'NFT digital collectibles blockchain',
        }
        
        return sector_terms.get(primary, f"{primary} technology software")
    
    elif matched_modifiers:
        # Just tech modifier
        modifier = matched_modifiers[0]
        return f"{modifier} software applications"
    
    # Fallback: use tech stack + generic software
    if tech_stack and tech_stack != "Software Development":
        return f"{tech_stack} software applications"
    
    # Last resort: generic software market
    return "software applications SaaS"


async def _fetch_dynamic_content(url: str, timeout: int = 10) -> str:
    """
    Fetch content from dynamic JavaScript-rendered pages using Playwright.
    
    Args:
        url: URL to fetch
        timeout: Request timeout in seconds
        
    Returns:
        Extracted text content
    """
    if not PLAYWRIGHT_AVAILABLE:
        return ""
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            # Navigate and wait for content
            await page.goto(url, timeout=timeout * 1000, wait_until='networkidle')
            
            # Wait a bit for any lazy-loaded content
            await page.wait_for_timeout(2000)
            
            # Get text content
            content = await page.inner_text('body')
            
            await browser.close()
            
            # Clean up whitespace
            text = ' '.join(content.split())
            
            return text[:5000]
            
    except Exception as e:
        print(f"⚠️  Playwright failed for {url}: {str(e)}")
        return ""


async def _fetch_page_content(url: str, timeout: int = 5, use_dynamic: bool = False) -> str:
    """
    Fetch and extract text content from a web page.
    
    Args:
        url: URL to fetch
        timeout: Request timeout in seconds
        use_dynamic: Whether to use Playwright for dynamic content
        
    Returns:
        Extracted text content
    """
    # Check if URL is likely to have dynamic content
    dynamic_domains = ['linkedin.com', 'facebook.com', 'twitter.com', 'x.com', 'reddit.com', 
                       'instagram.com', 'medium.com', 'substack.com']
    
    is_dynamic = use_dynamic or any(domain in url.lower() for domain in dynamic_domains)
    
    # Try Playwright first for dynamic sites
    if is_dynamic and PLAYWRIGHT_AVAILABLE:
        print(f"    🎭 Using Playwright for dynamic content...")
        content = await _fetch_dynamic_content(url, timeout)
        if content:
            return content
        print(f"    ⚠️  Playwright failed, falling back to static scraping...")
    
    # Fallback to static scraping
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=timeout) as client:
            response = await client.get(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            
            if response.status_code != 200:
                return ""
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean up whitespace
            text = ' '.join(text.split())
            
            return text[:5000]  # Limit to first 5000 chars
            
    except Exception as e:
        print(f"⚠️  Failed to fetch {url}: {str(e)}")
        return ""


async def search_market_size(
    project_description: str,
    tech_stack: str
) -> Dict[str, Any]:
    """
    Search Google for market size data related to the project.
    
    Args:
        project_description: Brief description of the project
        tech_stack: Technologies used in the project
        
    Returns:
        Dictionary with market size information
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    
    if not api_key:
        return {
            "value": "Data not available (Google API key not configured)",
            "growth_rate": "N/A",
            "forecast": "N/A",
            "sources": []
        }
    
    # If no custom search engine ID, use a default search approach
    if not search_engine_id:
        return await _fallback_search(project_description, tech_stack, api_key)
    
    # Construct search query focused on market sector
    # Extract key terms and focus on industry/sector
    sector_keywords = _extract_sector_keywords(project_description, tech_stack)
    query = f"{sector_keywords} market size 2024 forecast growth rate industry report"
    
    print(f"🔍 Google Search Query: {query}")
    print(f"   (Searching for sector: {sector_keywords})")
    print(f"🔑 Using API Key: {api_key[:20]}...")
    print(f"🔑 Using Search Engine ID: {search_engine_id}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/customsearch/v1",
                params={
                    "key": api_key,
                    "cx": search_engine_id,
                    "q": query,
                    "num": 5  # Get top 5 results
                },
                timeout=10.0
            )
            
            print(f"📊 Google API Response Status: {response.status_code}")
            
            if response.status_code != 200:
                error_detail = ""
                try:
                    error_data = response.json()
                    error_detail = error_data.get("error", {}).get("message", "")
                except:
                    pass
                
                # If 403, likely API not enabled
                if response.status_code == 403:
                    return {
                        "value": "Google Custom Search API not enabled",
                        "growth_rate": "N/A",
                        "forecast": "N/A",
                        "sources": [],
                        "error": "Enable Custom Search API in Google Cloud Console",
                        "setup_url": "https://console.cloud.google.com/apis/library/customsearch.googleapis.com"
                    }
                
                return {
                    "value": f"Search failed (status {response.status_code})",
                    "growth_rate": "N/A",
                    "forecast": "N/A",
                    "sources": [],
                    "error": error_detail
                }
            
            data = response.json()
            items = data.get("items", [])
            
            print(f"📄 Found {len(items)} search results")
            
            if not items:
                print("⚠️  No search results returned from Google")
                return {
                    "value": "No market data found",
                    "growth_rate": "N/A",
                    "forecast": "N/A",
                    "sources": []
                }
            
            # Extract sources and fetch actual page content
            sources = []
            all_content = []
            
            print(f"🌐 Fetching content from top {len(items)} results...")
            
            # Filter out sites that typically require authentication
            auth_domains = ['linkedin.com', 'facebook.com', 'twitter.com', 'x.com', 
                           'instagram.com', 'reddit.com', 'medium.com']
            
            filtered_items = []
            for item in items:
                link = item.get("link", "")
                # Skip auth-required sites for market research
                if not any(domain in link.lower() for domain in auth_domains):
                    filtered_items.append(item)
            
            # If we filtered everything, use original list
            if not filtered_items:
                filtered_items = items
                print(f"  ⚠️  All results require auth, using anyway...")
            else:
                print(f"  ✓ Filtered to {len(filtered_items)} public sources")
            
            # Fetch pages in parallel for speed
            import asyncio
            
            fetch_tasks = []
            for i, item in enumerate(filtered_items[:3], 1):  # Only fetch top 3 to save time
                title = item.get("title", "")
                link = item.get("link", "")
                snippet = item.get("snippet", "")
                
                print(f"  [{i}] Queuing: {link[:60]}...")
                
                # Create fetch task
                fetch_tasks.append({
                    'task': _fetch_page_content(link, timeout=3),  # Reduced timeout
                    'title': title,
                    'link': link,
                    'snippet': snippet
                })
            
            # Fetch all pages in parallel
            print(f"  ⚡ Fetching {len(fetch_tasks)} pages in parallel...")
            results = await asyncio.gather(*[t['task'] for t in fetch_tasks], return_exceptions=True)
            
            # Process results
            for i, (result, task_info) in enumerate(zip(results, fetch_tasks), 1):
                title = task_info['title']
                link = task_info['link']
                snippet = task_info['snippet']
                
                if isinstance(result, Exception):
                    print(f"  ⚠️  Error fetching {title[:40]}: {str(result)[:50]}")
                    all_content.append(snippet)
                    page_content = ""
                elif result:
                    all_content.append(result)
                    print(f"  ✓ [{i}] Got {len(result)} chars from {title[:40]}...")
                    page_content = result
                else:
                    # Fallback to snippet if page fetch fails
                    all_content.append(snippet)
                    print(f"  ⚠️  [{i}] Using snippet for {title[:40]}...")
                    page_content = ""
                
                sources.append({
                    "title": title,
                    "url": link,
                    "snippet": snippet,
                    "content_fetched": bool(page_content)
                })
            
            # Combine all content for analysis
            combined_text = " ".join(all_content)
            
            print(f"📝 Total content length: {len(combined_text)} characters")
            print(f"📄 Sample: {combined_text[:200]}...")
            
            market_value = _extract_market_value(combined_text)
            growth_rate = _extract_growth_rate(combined_text)
            forecast = _extract_forecast(combined_text)
            
            print(f"💰 Extracted market value: {market_value}")
            print(f"📈 Extracted growth rate: {growth_rate}")
            print(f"🔮 Extracted forecast: {forecast}")
            
            return {
                "value": market_value,
                "growth_rate": growth_rate,
                "forecast": forecast,
                "sources": sources,
                "content_length": len(combined_text)
            }
            
    except Exception as e:
        return {
            "value": f"Search error: {str(e)}",
            "growth_rate": "N/A",
            "forecast": "N/A",
            "sources": []
        }


async def _fallback_search(
    project_description: str,
    tech_stack: str,
    api_key: str
) -> Dict[str, Any]:
    """
    Fallback search using Google's general search without custom search engine.
    Uses SerpAPI or similar service if available.
    """
    # For now, return a placeholder
    # In production, you could integrate with SerpAPI, ScraperAPI, etc.
    return {
        "value": "Configure GOOGLE_SEARCH_ENGINE_ID for market data",
        "growth_rate": "N/A",
        "forecast": "N/A",
        "sources": [],
        "note": "To enable market size search, set up Google Custom Search Engine"
    }


def _extract_market_value(text: str) -> str:
    """Extract market value from text snippets."""
    import re
    
    # Look for patterns like "$X billion", "$X.X trillion", etc.
    patterns = [
        r'\$\s*[\d,]+\.?\d*\s*(?:billion|trillion|million|B|T|M)\b',
        r'(?:USD|US\$)\s*[\d,]+\.?\d*\s*(?:billion|trillion|million|B|T|M)\b',
        r'[\d,]+\.?\d*\s*(?:billion|trillion|million)\s*(?:dollars|USD|US\$)',
        r'(?:valued|worth|size|market).*?\$\s*[\d,]+\.?\d*\s*(?:billion|trillion|million|B|T|M)',
        r'(?:valued|worth|size|market).*?[\d,]+\.?\d*\s*(?:billion|trillion|million)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0).strip()
    
    # If no match, return a generic message with sources available
    return "See search results for market size estimates"


def _extract_growth_rate(text: str) -> str:
    """Extract growth rate from text snippets."""
    import re
    
    # Look for patterns like "X% CAGR", "growing at X%", etc.
    patterns = [
        r'[\d.]+\s*%\s*CAGR',
        r'CAGR\s+of\s+[\d.]+\s*%',
        r'compound\s+annual\s+growth\s+rate.*?[\d.]+\s*%',
        r'grow(?:ing|th|s)?\s+(?:at|by|of)\s+[\d.]+\s*%',
        r'[\d.]+\s*%\s+(?:annual|yearly)\s+growth',
        r'growth\s+rate.*?[\d.]+\s*%',
        r'[\d.]+\s*%.*?(?:growth|CAGR)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0).strip()
    
    return "See search results for growth rate estimates"


def _extract_forecast(text: str) -> str:
    """Extract market forecast from text snippets."""
    import re
    
    # Look for future projections
    patterns = [
        r'(?:by|reach|expected|projected|forecast).*?\$\s*[\d,]+\.?\d*\s*(?:billion|trillion|million|B|T|M).*?(?:by|in)\s+\d{4}',
        r'(?:by|in)\s+\d{4}.*?\$\s*[\d,]+\.?\d*\s*(?:billion|trillion|million|B|T|M)',
        r'\d{4}.*?(?:reach|expected|projected).*?\$\s*[\d,]+\.?\d*\s*(?:billion|trillion|million|B|T|M)',
        r'(?:reach|expected|projected).*?[\d,]+\.?\d*\s*(?:billion|trillion|million).*?\d{4}',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0).strip()
    
    return "See search results for forecast estimates"
