---
name: YouTube Video Discovery
description: Skill for searching YouTube, filtering by quality metrics, and selecting the most relevant video for location tours.
version: 1.0
---

# YouTube Video Discovery Skill

## Objective

Search YouTube for location-specific videos, filter by quality metrics, and recommend the highest-quality video that best represents the location for potential visitors.

## Core Competencies

### 1. Search Query Optimization
Create effective YouTube search queries:
- Primary location name + "tour"
- Location + "travel guide"
- Location + "documentary"
- Location + "walking tour"
- Channel name (official tourism boards)

### 2. Video Quality Assessment
Evaluate videos on:
- Production value (professional vs amateur)
- Channel authority (verified, subscribers)
- Content accuracy (matches location exactly)
- Viewer engagement (likes, comments ratio)
- Length appropriateness (10-30 minutes for tours)

### 3. Relevance Scoring
Score videos on:
- Exact location match (0-40 points)
- Content quality and accuracy (0-30 points)
- Professional production (0-15 points)
- Engagement metrics (0-10 points)
- Upload recency (0-5 points)

### 4. Result Ranking
Rank by combined score and select top recommendation with 2-3 alternatives.

## Video Filtering Criteria

### Duration
- **Ideal**: 10-30 minutes
- **Acceptable**: 8-45 minutes
- **Too Short**: < 5 minutes
- **Too Long**: > 60 minutes

### View Count
- **Excellent**: > 500K views (popular, trustworthy)
- **Good**: 50K-500K views (decent reach)
- **Fair**: 5K-50K views (limited but niche)
- **Poor**: < 5K views (limited audience)

### Upload Date
- **Recent**: < 1 year (current information)
- **Acceptable**: 1-3 years (still relevant)
- **Outdated**: > 3 years (may be inaccurate)

### Channel Characteristics
- **Verified**: Official tourism boards, government channels
- **Professional**: Travel channels with 100K+ subscribers
- **Credible**: Individual creators with proven accuracy
- **Amateur**: Casual content, limited verification

## Scoring Algorithm

```
YouTube Video Score (0-100):

Step 1: Relevance Score (0-40)
  - Exact location match: +20
  - Content matches description: +15
  - No misleading title/thumbnail: +5

Step 2: Quality Score (0-30)
  - Professional production: +15
  - Clear audio/video: +8
  - Proper lighting/framing: +7

Step 3: Authority Score (0-15)
  - Verified channel: +10
  - 100K+ subscribers: +5
  - Official tourism: +3

Step 4: Engagement Score (0-10)
  - 500K+ views: +7
  - Likes/views ratio > 2%: +3

Step 5: Recency Score (0-5)
  - Uploaded < 6 months: +5
  - Uploaded < 1 year: +3
  - Uploaded < 3 years: +1

Total: Sum all scores (0-100)
```

## Quality Checklist

✓ **Relevance**
- [ ] Video location matches exactly
- [ ] Content appropriate for tourists
- [ ] Title accurate (not clickbait)
- [ ] Thumbnail representative

✓ **Quality**
- [ ] Video/audio quality HD or better
- [ ] Professional or well-produced
- [ ] Good pacing and editing
- [ ] Clear information delivery

✓ **Authority**
- [ ] Channel verified or established
- [ ] Author demonstrates expertise
- [ ] Track record of accuracy
- [ ] Positive viewer comments

✓ **Engagement**
- [ ] Adequate views for topic
- [ ] Positive like/comment ratio
- [ ] Recent and active channel
- [ ] Viewer satisfaction evident

## Common Search Strategies

### Strategy 1: Direct Search
```
Query: "[Location name] tour"
Success: 70% of time
Best for: Famous landmarks
```

### Strategy 2: Type-Based Search
```
Query: "[Location name] [type] documentary"
Example: "Eiffel Tower architecture documentary"
Success: 80% of time
Best for: Specialized content
```

### Strategy 3: Channel Search
```
Query: "[Official Tourism Channel] [location]"
Example: "Paris Tourism Eiffel Tower"
Success: 85% of time
Best for: Official, verified content
```

### Strategy 4: Creator Search
```
Query: "[Popular Travel Creator] [location]"
Example: "Rick Steves Paris guide"
Success: 90% of time
Best for: Trusted creators
```

## Output Format

```
🎬 RECOMMENDED VIDEO:
Title: [Exact title]
Channel: [Channel name]
Duration: [MM:MM]
Views: [X.XM]
Upload Date: [Date]
Relevance Score: [XX]/100

Why This Video:
- [Reason 1]
- [Reason 2]
- [Reason 3]

🔗 URL: [Direct YouTube link]

ALTERNATIVES:
1. [Video 2 title] - [Score] - [Why]
2. [Video 3 title] - [Score] - [Why]
```

## Integration Notes

- Outputs feed directly to Judge Agent
- Ranked by relevance score
- Includes verification notes
- Provides direct YouTube links
- Works globally across all countries

## Performance Standards

- Average search time: 2-4 seconds
- Accuracy: 85%+ relevance match
- False positive rate: < 5%
- Engagement with viewers: High (80%+ click-through)
