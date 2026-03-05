---
name: web-search
version: 1.0.0
description: Web search using DuckDuckGo with result summaries
author: SkillHub
tags: search, web, duckduckgo
---

# Web Search Skill

Search the web using DuckDuckGo and get summarized results.

## Features

- DuckDuckGo search (privacy-focused)
- Result summarization
- Multiple result limit options
- Safe search support
- No API key required

## Usage

### Basic Search
```python
results = search("Python programming tutorial")
```

### Search with Options
```python
results = search(
    query="machine learning",
    max_results=10,
    safe_search=True
)
```

### Get Summary
```python
summary = search_and_summarize("what is AI")
```

## Output Format

Returns search results including:
- Title
- URL
- Snippet/description
- Summary (if requested)

## Actions

- `search`: Perform a web search
- `search_and_summarize`: Search and return summarized results

## Notes

- Uses DuckDuckGo HTML scraping (no API required)
- Respects rate limits
- Privacy-focused (no tracking)
