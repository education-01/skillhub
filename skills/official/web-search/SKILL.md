---
name: web-search
description: "Search the web using DuckDuckGo. Use when: user needs to find information, research topics, or look up something online. Privacy-focused, no API key needed."
homepage: https://duckduckgo.com
metadata: { "openclaw": { "emoji": "🔍", "requires": { "bins": ["curl"] } } }
---

# Web Search Skill

Search the web using DuckDuckGo HTML endpoint.

## When to Use

✅ **USE this skill when:**

- "Search for..."
- "Look up..."
- "Find information about..."
- "What is..."
- Research and fact-checking
- Finding documentation

## When NOT to Use

❌ **DON'T use this skill when:**

- Need real-time news → use news APIs
- Academic research → use Google Scholar
- Image search → use image search engines
- Local business info → use maps services
- Code examples → search GitHub directly

## Commands

### Basic Search

```bash
# Search and get HTML results
curl -s "https://html.duckduckgo.com/html/?q=python+tutorial"
```

### With User Agent

```bash
curl -s -A "Mozilla/5.0" "https://html.duckduckgo.com/html/?q=your+query"
```

### Parse Results

```bash
# Extract result titles and URLs
curl -s -A "Mozilla/5.0" "https://html.duckduckgo.com/html/?q=python" | \
  grep -oP 'class="result__a"[^>]*>\K[^<]+' | head -5
```

### Alternative: textise dot iitty

```bash
# Simpler text-based search
curl -s "https://lite.duckduckgo.com/lite/?q=your+query"
```

## Quick Responses

**"Search for Python async tutorial"**

```bash
curl -s -A "Mozilla/5.0" "https://html.duckduckgo.com/html/?q=python+async+tutorial"
```

**"What is machine learning?"**

```bash
curl -s -A "Mozilla/5.0" "https://html.duckduckgo.com/html/?q=what+is+machine+learning"
```

## Tips

- Use `+` for spaces in queries
- Add `-A "Mozilla/5.0"` for better results
- Parse with `grep`, `sed`, or Python
- Respect rate limits

## Notes

- No API key needed
- Privacy-focused (DuckDuckGo)
- May be rate limited
- For heavy use, consider official APIs
