#!/usr/bin/env python3
"""
Web Search Skill - DuckDuckGo search with summaries
"""

import urllib.request
import urllib.parse
import urllib.error
import re
import html
from typing import Dict, Any, List, Optional


class WebSearchSkill:
    """Web search using DuckDuckGo"""
    
    def __init__(self):
        self.base_url = "https://html.duckduckgo.com/html/"
        self.timeout = 15
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    def search(self, query: str, max_results: int = 5, safe_search: bool = True) -> Dict[str, Any]:
        """
        Perform a web search
        
        Args:
            query: Search query
            max_results: Maximum number of results to return (1-20)
            safe_search: Enable safe search
            
        Returns:
            Dictionary with search results
        """
        try:
            # Validate max_results
            max_results = max(1, min(20, max_results))
            
            # Fetch search results
            html_content = self._fetch_search_results(query, safe_search)
            if not html_content:
                return {
                    'success': False,
                    'error': 'Failed to fetch search results'
                }
            
            # Parse results
            results = self._parse_results(html_content, max_results)
            
            return {
                'success': True,
                'query': query,
                'results': results,
                'count': len(results)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def search_and_summarize(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Search and return summarized results
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            Dictionary with search results and summary
        """
        search_result = self.search(query, max_results)
        
        if not search_result.get('success'):
            return search_result
        
        results = search_result.get('results', [])
        
        # Create summary
        summary = self._create_summary(query, results)
        
        return {
            'success': True,
            'query': query,
            'summary': summary,
            'results': results,
            'count': len(results)
        }
    
    def _fetch_search_results(self, query: str, safe_search: bool = True) -> Optional[str]:
        """Fetch HTML search results from DuckDuckGo"""
        try:
            # Build URL with parameters
            params = {
                'q': query,
                'kl': 'wt-wt',  # Worldwide
            }
            
            if safe_search:
                params['kp'] = '1'  # Safe search on
            
            url = f"{self.base_url}?{urllib.parse.urlencode(params)}"
            
            # Create request
            req = urllib.request.Request(url)
            req.add_header('User-Agent', self.user_agent)
            req.add_header('Accept', 'text/html')
            
            # Fetch
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                return response.read().decode('utf-8', errors='ignore')
        except urllib.error.URLError as e:
            print(f"URL Error: {e}")
            return None
        except Exception as e:
            print(f"Error fetching results: {e}")
            return None
    
    def _parse_results(self, html_content: str, max_results: int) -> List[Dict]:
        """Parse search results from HTML"""
        results = []
        
        try:
            # Find result containers
            # DuckDuckGo HTML uses specific class names
            result_pattern = r'<a[^>]+class="result__a"[^>]*href="([^"]+)"[^>]*>([^<]+)</a>'
            snippet_pattern = r'<a[^>]+class="result__snippet"[^>]*>([^<]+)</a>'
            
            # Find all results
            result_matches = re.findall(result_pattern, html_content, re.IGNORECASE)
            snippet_matches = re.findall(snippet_pattern, html_content, re.IGNORECASE)
            
            for i, (url, title) in enumerate(result_matches[:max_results]):
                # Clean URL (DuckDuckGo uses redirect URLs)
                clean_url = self._clean_url(url)
                
                # Get snippet if available
                snippet = snippet_matches[i] if i < len(snippet_matches) else ""
                snippet = html.unescape(snippet).strip()
                
                # Clean title
                title = html.unescape(title).strip()
                
                results.append({
                    'title': title,
                    'url': clean_url,
                    'snippet': snippet
                })
        
        except Exception as e:
            print(f"Error parsing results: {e}")
        
        return results
    
    def _clean_url(self, url: str) -> str:
        """Clean DuckDuckGo redirect URL"""
        try:
            # DuckDuckGo uses redirect URLs like:
            # /l/?uddg=https%3A%2F%2Fexample.com
            if '/l/?uddg=' in url:
                parsed = urllib.parse.urlparse(url)
                params = urllib.parse.parse_qs(parsed.query)
                if 'uddg' in params:
                    return params['uddg'][0]
            
            # Unescape URL
            url = html.unescape(url)
            
            return url
        except Exception:
            return url
    
    def _create_summary(self, query: str, results: List[Dict]) -> str:
        """Create a summary of search results"""
        if not results:
            return f"No results found for '{query}'"
        
        summary_parts = [f"Found {len(results)} results for '{query}':\n"]
        
        for i, result in enumerate(results, 1):
            summary_parts.append(f"{i}. {result['title']}")
            if result['snippet']:
                summary_parts.append(f"   {result['snippet'][:150]}...")
        
        return '\n'.join(summary_parts)


# Skill interface
_skill_instance = None

def get_skill():
    """Get or create skill instance"""
    global _skill_instance
    if _skill_instance is None:
        _skill_instance = WebSearchSkill()
    return _skill_instance


def execute(action: str, **kwargs) -> Dict[str, Any]:
    """
    Execute skill action
    
    Args:
        action: Action to perform (search, search_and_summarize)
        **kwargs: Action-specific parameters
        
    Returns:
        Result dictionary
    """
    skill = get_skill()
    
    if action == 'search':
        query = kwargs.get('query')
        max_results = kwargs.get('max_results', 5)
        safe_search = kwargs.get('safe_search', True)
        
        if not query:
            return {'success': False, 'error': 'Missing query parameter'}
        
        return skill.search(query, max_results, safe_search)
    
    elif action == 'search_and_summarize':
        query = kwargs.get('query')
        max_results = kwargs.get('max_results', 5)
        
        if not query:
            return {'success': False, 'error': 'Missing query parameter'}
        
        return skill.search_and_summarize(query, max_results)
    
    else:
        return {
            'success': False,
            'error': f'Unknown action: {action}. Available actions: search, search_and_summarize'
        }


if __name__ == '__main__':
    # Test the skill
    print("Testing Web Search Skill...")
    
    # Test basic search
    result = execute('search', query='Python programming', max_results=3)
    print(f"\nSearch results:\n{result}")
    
    # Test search and summarize
    result = execute('search_and_summarize', query='machine learning', max_results=3)
    print(f"\nSearch summary:\n{result.get('summary', '')}")
