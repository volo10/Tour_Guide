---
name: API Web Fetching
description: Core skill for fetching data from external APIs (YouTube, Spotify, Wikipedia) and parsing structured responses for tour content discovery.
version: 1.0
---

# API Web Fetching Skill

## Objective

Reliably fetch data from external APIs (YouTube, Spotify, Wikipedia, etc.) and parse responses to extract relevant information for tour guide content recommendations.

## Core APIs

### YouTube Data API
**Purpose**: Search and retrieve video information
```
Endpoint: /search
Parameters:
  - q: search query
  - part: snippet
  - maxResults: 5
  - videoEmbeddable: true
  - videoDuration: medium

Response Fields:
  - videoId
  - title
  - description
  - channelTitle
  - publishedAt
  - thumbnails
```

### Spotify Web API
**Purpose**: Search and retrieve track information
```
Endpoint: /search
Parameters:
  - q: search query
  - type: track
  - limit: 5
  - market: [country code]

Response Fields:
  - name
  - artist
  - album
  - duration_ms
  - popularity
  - external_urls.spotify
  - preview_url
```

### Wikipedia API
**Purpose**: Fetch historical and contextual information
```
Endpoint: /api.php
Parameters:
  - action: query
  - titles: [location name]
  - format: json
  - prop: extracts|pageimages

Response Fields:
  - extract (text content)
  - pageimage
  - pageid
  - title
```

## Web Fetching Process

### Step 1: Construct Query
- Build API-specific search queries
- Include proper formatting and encoding
- Add authentication tokens (API keys)
- Set appropriate parameters

### Step 2: Execute Request
- Send HTTP request (GET/POST)
- Handle timeouts (30-second limit)
- Manage rate limits
- Retry on failure (max 3 attempts)

### Step 3: Parse Response
- Validate JSON structure
- Extract relevant fields
- Verify data completeness
- Handle missing or malformed data

### Step 4: Clean & Format
- Remove HTML tags
- Decode special characters
- Truncate lengthy content
- Standardize date formats

### Step 5: Output Results
- Return structured data
- Include source attribution
- Note retrieval timestamp
- Indicate data reliability

## Error Handling

### Network Errors
```
Error: Connection timeout
Solution: Retry with exponential backoff
Max attempts: 3
```

### API Errors
```
Error: Rate limit exceeded
Solution: Queue request, try later
Error: Invalid API key
Solution: Verify authentication
Error: No results found
Solution: Refine query, try alternatives
```

### Data Errors
```
Error: Malformed JSON
Solution: Log and skip entry
Error: Missing required fields
Solution: Use default values where safe
Error: Invalid format
Solution: Validate and transform
```

## Quality Checklist

✓ **API Accuracy**
- [ ] Correct endpoint used
- [ ] Parameters properly formatted
- [ ] Authentication tokens valid
- [ ] Response contains expected fields

✓ **Data Validity**
- [ ] JSON properly parsed
- [ ] Required fields present
- [ ] Data types correct
- [ ] No null/undefined critical fields

✓ **Error Handling**
- [ ] Timeout handled gracefully
- [ ] Rate limits respected
- [ ] Invalid results logged
- [ ] Fallback options available

✓ **Performance**
- [ ] Request completes < 30 seconds
- [ ] Minimal API calls made
- [ ] Caching used when possible
- [ ] Batch requests optimized

## Application Guidelines

1. **Construct Query**: Build API-specific search query
2. **Set Parameters**: Configure API parameters
3. **Add Auth**: Include API keys/tokens
4. **Execute**: Send HTTP request
5. **Parse**: Extract and validate response
6. **Transform**: Format for downstream use
7. **Validate**: Ensure data quality
8. **Return**: Provide structured output

## Integration Notes

- Used by all three content-finding agents
- Enables real-time data retrieval
- Supports error recovery and retries
- Caches results to minimize API calls
- Respects rate limits of each service

## Performance Benchmarks

| Task | Typical Time | Max Time |
|------|------|---|
| YouTube search (5 results) | 2-4 seconds | 10 seconds |
| Spotify search (5 results) | 1-2 seconds | 5 seconds |
| Wikipedia fetch | 1-3 seconds | 8 seconds |
| Error recovery | 2-5 seconds | 15 seconds |

## Security Considerations

✓ **API Keys**: Store securely, never expose
✓ **Rate Limiting**: Respect API quotas
✓ **Data Privacy**: Don't log sensitive info
✓ **HTTPS**: Always use secure connections
✓ **Validation**: Verify all external data

## Example Implementations

### YouTube Search Example
```
Query: "Eiffel Tower Paris tour"
Parameters:
  - maxResults: 5
  - videoDuration: medium
  - relevanceLanguage: en

Returns:
- [Video ID, Title, Channel, Duration, Views]
- [Video ID, Title, Channel, Duration, Views]
- ... (up to 5 results)
```

### Spotify Search Example
```
Query: "La Vie en Rose"
Parameters:
  - type: track
  - market: FR

Returns:
- [Track Name, Artist, Duration, URL, Preview]
```

### Wikipedia Fetch Example
```
Query: "Eiffel Tower"

Returns:
- [Historical extract, key facts, images]
```

This skill ensures reliable, consistent API data retrieval across all tour guide agents.
