# Cost and Resource Analysis
# Tour Guide System

This document provides a comprehensive analysis of API costs, token usage, and resource management for the Tour Guide system.

---

## 1. Overview

The Tour Guide system uses three external APIs:
- **Google Maps Directions API** - Route fetching
- **YouTube Data API v3** - Video search
- **Spotify Web API** - Music search
- **Wikipedia API** - Historical facts (free, no cost)

---

## 2. API Cost Breakdown

### 2.1 Google Maps Directions API

| Metric | Value |
|--------|-------|
| **Pricing Model** | Pay-as-you-go |
| **Free Tier** | $200/month credit |
| **Cost per Request** | $0.005 (Directions) |
| **Requests per Route** | 1 |

**Usage Estimate (per month):**
| Scenario | Routes/Month | Cost |
|----------|--------------|------|
| Light Usage | 100 | $0.50 |
| Medium Usage | 500 | $2.50 |
| Heavy Usage | 2,000 | $10.00 |

**Note:** $200 free credit covers ~40,000 route requests per month.

### 2.2 YouTube Data API v3

| Metric | Value |
|--------|-------|
| **Pricing Model** | Quota-based (free) |
| **Daily Quota** | 10,000 units |
| **Cost per Search** | 100 units |
| **Searches per Day (max)** | 100 |

**Usage Estimate (per route):**
| Junctions | Searches | Units Used |
|-----------|----------|------------|
| 5 | 5 | 500 |
| 10 | 10 | 1,000 |
| 20 | 20 | 2,000 |

**Daily Capacity:**
- Maximum routes per day: ~100 (with 10 junctions each)
- No monetary cost (quota-based)

### 2.3 Spotify Web API

| Metric | Value |
|--------|-------|
| **Pricing Model** | Free (rate-limited) |
| **Rate Limit** | ~180 requests/minute |
| **Cost** | $0 |

**Usage:** Unlimited within rate limits, no monetary cost.

### 2.4 Wikipedia API

| Metric | Value |
|--------|-------|
| **Pricing Model** | Free |
| **Rate Limit** | Reasonable use policy |
| **Cost** | $0 |

---

## 3. Total Cost Analysis

### 3.1 Cost per Route

| Component | Cost per Request | Requests per Route (10 junctions) | Total |
|-----------|-----------------|-----------------------------------|-------|
| Google Maps | $0.005 | 1 | $0.005 |
| YouTube | $0 (quota) | 10 | $0 |
| Spotify | $0 | 10 | $0 |
| Wikipedia | $0 | 10 | $0 |
| **Total** | | | **$0.005** |

### 3.2 Monthly Cost Projection

| Usage Level | Routes/Month | Google Maps | YouTube | Spotify | Wikipedia | **Total** |
|-------------|--------------|-------------|---------|---------|-----------|-----------|
| Light | 100 | $0.50 | $0 | $0 | $0 | **$0.50** |
| Medium | 500 | $2.50 | $0 | $0 | $0 | **$2.50** |
| Heavy | 2,000 | $10.00 | $0 | $0 | $0 | **$10.00** |
| Enterprise | 10,000 | $50.00 | $0 | $0 | $0 | **$50.00** |

**Note:** All scenarios fall within Google's $200/month free credit.

---

## 4. Token/Compute Usage

### 4.1 API Request Statistics

| API | Avg Response Size | Avg Latency |
|-----|-------------------|-------------|
| Google Maps | ~5 KB | 200-500ms |
| YouTube | ~10 KB | 300-800ms |
| Spotify | ~8 KB | 200-600ms |
| Wikipedia | ~15 KB | 300-700ms |

### 4.2 Per-Junction Processing

| Operation | Time (avg) | Memory |
|-----------|------------|--------|
| Video Agent | 1-3 sec | ~10 MB |
| Music Agent | 1-2 sec | ~8 MB |
| History Agent | 1-3 sec | ~12 MB |
| Judge Agent | <100ms | ~2 MB |
| **Total per Junction** | 2-4 sec | ~32 MB |

### 4.3 Route Processing Summary

| Junctions | Total Time | Peak Memory | API Calls |
|-----------|------------|-------------|-----------|
| 5 | 10-20 sec | ~50 MB | 16 |
| 10 | 20-40 sec | ~80 MB | 31 |
| 20 | 40-80 sec | ~120 MB | 61 |

---

## 5. Cost Optimization Strategies

### 5.1 Implemented Optimizations

1. **Parallel Processing**: Agents run concurrently, reducing total time
2. **Timeout Limits**: 10-second timeout prevents runaway requests
3. **Error Handling**: Failed requests don't retry excessively

### 5.2 Recommended Optimizations

1. **Caching**
   - Cache route responses for repeated source/destination pairs
   - Cache API responses for common locations
   - Estimated savings: 30-50% on repeated queries

2. **Batch Processing**
   - Group multiple junction searches where possible
   - Use YouTube batch endpoints (future)

3. **Smart Query Building**
   - More specific queries = fewer irrelevant results
   - Reduce search iterations per junction

4. **Rate Limiting**
   - Implement request throttling
   - Spread requests over time during peak usage

---

## 6. Budget Management

### 6.1 Monitoring Metrics

| Metric | How to Track |
|--------|--------------|
| Google Maps usage | Google Cloud Console |
| YouTube quota | Google Cloud Console |
| Spotify rate limits | Response headers |
| Total routes processed | Application logs |

### 6.2 Alerts and Thresholds

| Threshold | Action |
|-----------|--------|
| Google Maps > $150/month | Warning alert |
| YouTube quota > 8,000/day | Reduce frequency |
| Spotify rate limit hit | Implement backoff |

### 6.3 Budget Allocation

| Category | Monthly Budget | Notes |
|----------|---------------|-------|
| Google Maps | $50 (within free tier) | Covered by $200 credit |
| Development/Testing | $10 | Debugging, iteration |
| Buffer | $20 | Unexpected usage |
| **Total** | **$80** | Conservative estimate |

---

## 7. Cost Comparison with Alternatives

### 7.1 LLM-Based Alternative (for context)

If using LLM APIs (GPT-4, Claude) instead of search APIs:

| Model | Input Cost | Output Cost | Est. Cost/Junction |
|-------|------------|-------------|-------------------|
| GPT-4 | $0.03/1K tokens | $0.06/1K tokens | $0.05-0.10 |
| GPT-3.5 | $0.001/1K tokens | $0.002/1K tokens | $0.005-0.01 |
| Claude 3 | $0.015/1K tokens | $0.075/1K tokens | $0.03-0.08 |

**Current approach (Search APIs) is ~10-100x cheaper than LLM-based approaches.**

### 7.2 Self-Hosted Alternative

| Component | Monthly Cost | Notes |
|-----------|--------------|-------|
| Server (VM) | $20-50 | For self-hosted search |
| Storage | $5-10 | Content caching |
| Maintenance | ~10 hours | DevOps time |

**Conclusion:** Cloud APIs are more cost-effective for our scale.

---

## 8. Usage Tracking Implementation

### 8.1 Logging Cost Metrics

```python
# Example cost tracking (conceptual)
class CostTracker:
    def __init__(self):
        self.google_maps_calls = 0
        self.youtube_calls = 0
        self.spotify_calls = 0

    def log_route(self, num_junctions: int):
        self.google_maps_calls += 1
        self.youtube_calls += num_junctions
        self.spotify_calls += num_junctions

    def get_estimated_cost(self) -> float:
        return self.google_maps_calls * 0.005
```

### 8.2 Recommended Monitoring Dashboard

Track these metrics:
- Daily/weekly/monthly route count
- API calls per service
- Error rates per API
- Average processing time
- Estimated monthly cost

---

## 9. Summary

| Metric | Value |
|--------|-------|
| **Cost per Route** | ~$0.005 |
| **Monthly Budget (Medium Usage)** | $2.50 |
| **Primary Cost Driver** | Google Maps API |
| **Free APIs** | YouTube (quota), Spotify, Wikipedia |
| **Optimization Potential** | 30-50% with caching |

The Tour Guide system is designed to be **cost-effective**, primarily leveraging free API tiers and quota-based services. The only monetary cost is Google Maps Directions API, which is fully covered by the $200/month free credit for typical usage scenarios.

---

## 10. References

- [Google Maps Platform Pricing](https://developers.google.com/maps/billing-and-pricing/pricing)
- [YouTube API Quota Calculator](https://developers.google.com/youtube/v3/determine_quota_cost)
- [Spotify API Rate Limits](https://developer.spotify.com/documentation/web-api/concepts/rate-limits)
