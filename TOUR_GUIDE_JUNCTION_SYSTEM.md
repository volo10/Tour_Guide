---
name: Tour Guide Junction-Based System
description: Turn-by-turn navigation enhancement where agents activate at each junction/intersection along a 10-minute drive route, providing precise, location-specific content for each turn.
version: 2.0
---

# Tour Guide System v2.0 - Junction-Based Navigation

**Updated:** November 21, 2025
**Previous Version:** Global address-based
**New Version:** Turn-by-turn junction-based

---

## Overview

The Tour Guide System now operates as a **junction-based, turn-by-turn navigator** where agents activate at each intersection/junction along a predefined 10-minute drive route. Instead of analyzing entire cities or neighborhoods, each agent provides **precise, real-time content** for the specific junction ahead.

### Key Change

**Before (v1.0):**
- Input: City, landmark, or full address
- Output: Single comprehensive recommendation
- Scope: Entire location

**After (v2.0):**
- Input: Route with GPS waypoints + 10-minute drive sequence
- Output: Content for each individual junction (left/right/straight turns)
- Scope: Specific intersection/junction at each turn

---

## How It Works: Junction-Based Flow

### 1. Route Input
```
Route: 10-minute drive sequence
Source: Google Maps Navigation API
Waypoints: GPS coordinates for each junction
Turns: ["Left", "Right", "Straight", "U-turn", etc.]
```

### 2. Junction Identification
System identifies upcoming junctions:
- **Junction 1:** "In 500m, turn LEFT onto Main Street"
- **Junction 2:** "In 1.2km, turn RIGHT onto Park Avenue"
- **Junction 3:** "In 2.5km, go STRAIGHT at intersection"
- (And so on for entire 10-minute route)

### 3. Per-Junction Agent Activation
For **EACH junction**, all 3 content agents activate:

```
JUNCTION 1: Main Street (Left Turn)
├─ 🎬 Video Finder
│  └─ Find video of Main Street area/this intersection
├─ 🎵 Music Finder
│  └─ Find music matching Main Street atmosphere
├─ 📖 History Finder
│  └─ Find facts about Main Street at this location
└─ 🏆 Judge
   └─ Evaluate and rank the three recommendations

JUNCTION 2: Park Avenue (Right Turn)
├─ 🎬 Video Finder
│  └─ Find video of Park Avenue/this intersection
├─ 🎵 Music Finder
│  └─ Find music matching Park Avenue atmosphere
├─ 📖 History Finder
│  └─ Find facts about Park Avenue at this location
└─ 🏆 Judge
   └─ Evaluate and rank the three recommendations

[Continue for all junctions in route]
```

### 4. Real-Time Output
As driver approaches each junction, they receive:

```
⏰ APPROACHING JUNCTION (in 500 meters)

🚗 TURN: LEFT onto Main Street

🎬 VIDEO: "Main Street Walking Tour - Downtown" (87/100)
   - Shows street level views and landmarks
   - 10-minute street documentary available

🎵 MUSIC: "Urban Energy Mix" (85/100)
   - Captures bustling downtown atmosphere
   - Perfect for Main Street vibe

📖 HISTORY: "Main Street's Evolution" (92/100)
   - Built 1890s as commercial center
   - Historic buildings still standing

🏆 WINNER: History (92/100)
   "Best overall insight for this street"
```

---

## System Architecture for Junction-Based Processing

### Input Data Structure

```yaml
Route:
  total_time: "10 minutes"
  total_distance: "8.5 km"
  waypoints:
    - junction_1:
        address: "Main St & 5th Ave"
        coordinates: [40.7128, -74.0060]
        turn: "LEFT"
        distance_to_next: "500m"
    - junction_2:
        address: "Park Ave & 8th St"
        coordinates: [40.7131, -74.0060]
        turn: "RIGHT"
        distance_to_next: "1.2km"
    - junction_3:
        address: "Broadway & 10th St"
        coordinates: [40.7135, -74.0060]
        turn: "STRAIGHT"
        distance_to_next: "2.5km"
    [... more junctions ...]
```

### Processing Pipeline

```
Route Input
    ↓
Extract All Junctions
    ↓
For Each Junction in Sequence:
    ├─ Extract Junction Context
    │  ├─ Street names
    │  ├─ Intersection type (major/minor)
    │  ├─ Surrounding landmarks
    │  └─ Turn direction
    │
    ├─ Activate 3 Content Agents in Parallel
    │  ├─ Video Finder (500ms-2s)
    │  ├─ Music Finder (500ms-2s)
    │  └─ History Finder (1-3s)
    │
    ├─ Judge Agent Evaluates (500ms)
    │
    └─ Output Junction Recommendation
       ├─ Video recommendation
       ├─ Music recommendation
       ├─ History fact
       └─ Winner declaration

Repeat for All Junctions
    ↓
Generate Complete Route Report
```

---

## Agent Modifications for Junction-Based Processing

### Video Finder: Junction Video Discovery

**Input:** Junction details (street names, intersection, turn direction)

**Processing:**
1. Extract street intersection context
2. Search YouTube for:
   - "Main Street & 5th Ave walking tour"
   - "Downtown intersection street view"
   - "Street-level video of Main Street"
3. Filter for:
   - Street-level perspectives
   - Short clips (2-5 minutes)
   - Real-time traffic/street conditions
   - Recent uploads (within 1-2 months)

**Output:** Single best video for THIS SPECIFIC JUNCTION
- Video URL
- Duration
- Street view focus
- Relevance score (1-100)

**Scoring Criteria:**
- **Relevance (45%)**: Exact junction/street match
- **Quality (30%)**: Clear street-level view
- **Recency (15%)**: Recent upload (relevant current conditions)
- **Usefulness (10%)**: Practical navigation info

---

### Music Finder: Junction Atmosphere Music

**Input:** Junction details (street character, neighborhood vibe, turn type)

**Processing:**
1. Analyze street/intersection:
   - Is it busy commercial district? → Upbeat, energetic music
   - Is it quiet residential? → Calm, peaceful music
   - Is it scenic/park area? → Nature-inspired music
   - Is it historic? → Classical, period-appropriate music
2. Search for short songs/clips:
   - Perfect mood match for THIS street
   - 2-4 minute duration
   - Streaming available

**Output:** Single best song for THIS JUNCTION's atmosphere
- Song title and artist
- Duration
- Mood description
- Relevance score (1-100)

**Scoring Criteria:**
- **Relevance (40%)**: Street atmosphere match
- **Quality (25%)**: Artist reputation, production quality
- **Atmosphere (20%)**: Mood match to intersection type
- **Discoverability (15%)**: Available on Spotify

---

### History Finder: Junction-Specific Facts

**Input:** Junction details (street names, coordinates, neighborhood context)

**Processing:**
1. Research this SPECIFIC intersection:
   - When was each street named?
   - What historic events at this intersection?
   - Notable buildings nearby?
   - Any famous incidents or stories?
2. Verify facts for THIS junction only
3. Find 2-3 interesting, verified facts

**Output:** Single best fact/story for THIS JUNCTION
- Historical fact or narrative
- Time period
- Relevance to intersection
- Verification/source

**Scoring Criteria:**
- **Accuracy (40%)**: Verified, correct information
- **Relevance (30%)**: Specific to this junction
- **Engagement (20%)**: Interesting/engaging fact
- **Brevity (10%)**: Concise, quick-to-read (~100 words)

---

### Judge Agent: Quick Junction Evaluation

**Input:** 3 recommendations from agents (video, music, history)

**Processing:**
1. Quick evaluation of all three
2. Score each recommendation
3. Determine clear winner
4. Provide brief reasoning

**Output:** Quick judgment for driver
- Winner: [Agent name] with [score]/100
- Brief reason (1 sentence)
- Timestamp of evaluation

**Scoring Criteria:**
- Same as before but weighted for **speed**
- All evaluation done in < 500ms
- Clear winner declared
- Minimal text for quick reading while driving

---

## Example: Complete Route with Multiple Junctions

### Route: 10-minute drive through Downtown (8.5 km)

---

#### **JUNCTION 1: Main Street & 5th Avenue**
- **Turn:** LEFT
- **Distance to next:** 500m
- **ETA:** Next turn in ~4 minutes

```
🎬 VIDEO: "Downtown Main Street 2024 Street View" (88/100)
   - Real-time foot traffic and street activity
   - Shows intersection from multiple angles
   - 4-minute video

🎵 MUSIC: "Urban Pulse" (82/100)
   - Busy, energetic downtown vibe
   - Captures pedestrian activity

📖 HISTORY: "Main Street Built 1897, Historic Commercial Hub" (91/100)
   - "Main Street was established as the city's
     primary commercial district in 1897. The
     ornate Victorian buildings lining the street
     represent a crucial era of urban development."

🏆 WINNER: History Finder (91/100)
   Best historical context for this intersection
```

---

#### **JUNCTION 2: Park Avenue & 8th Street**
- **Turn:** RIGHT
- **Distance to next:** 1.2km
- **ETA:** Next turn in ~7 minutes

```
🎬 VIDEO: "Park Avenue Tree-Lined Street Walk" (79/100)
   - Shows tree-canopy and park entrance nearby
   - Quieter, residential feel

🎵 MUSIC: "Peaceful Urban Park Ambiance" (88/100)
   - Calm, tree-themed instrumental
   - Perfect for park entrance area

📖 HISTORY: "Central Park Adjacent, Designed 1920s" (85/100)
   - "Park Avenue marks the boundary of the
     city's famous Central Park, developed
     in the 1920s as a green space initiative."

🏆 WINNER: Music Finder (88/100)
   Best atmospheric match for park-adjacent street
```

---

#### **JUNCTION 3: Broadway & 10th Street**
- **Turn:** STRAIGHT
- **Distance to next:** 2.5km
- **ETA:** Next turn in ~11 minutes

```
🎬 VIDEO: "Broadway Theater District Street Activity" (93/100)
   - Shows theater marquees and street life
   - Captures iconic Broadway intersection
   - Recent upload with current conditions

🎵 MUSIC: "Broadway Show Tune - Theatrical Energy" (87/100)
   - Captures Broadway's cultural energy
   - Theater district vibes

📖 HISTORY: "Broadway Theater District Since 1920s" (86/100)
   - "Broadway's Theater District emerged in the
     1920s-30s as the city's entertainment hub,
     with iconic venues still operating today."

🏆 WINNER: Video Finder (93/100)
   Best captures active Broadway intersection atmosphere
```

---

## Key Implementation Differences

### Before (v1.0): Global System
```
Input: "Eiffel Tower, Paris"
Process: Comprehensive analysis
Output: 1 video, 1 song, 1 history for entire landmark
Time: 10-15 seconds total
```

### After (v2.0): Junction System
```
Input: Route [J1, J2, J3, J4, J5, J6, J7, J8, J9, J10]
Process: Per-junction analysis in sequence
Output: 3 items × 10 junctions = 30 recommendations
Time: ~500ms per junction × 10 = ~5 seconds total
  (running in parallel with navigation)
```

---

## Performance Specifications

| Metric | Requirement | Status |
|--------|------------|--------|
| **Per-Junction Time** | < 500ms | ✓ Achievable |
| **Total Route Time** | ~5 seconds (10 junctions × 500ms) | ✓ Real-time |
| **Video Quality** | Street-level, 2-5 min clips | ✓ Available |
| **Music Relevance** | Atmosphere match for street | ✓ Precise |
| **History Accuracy** | Verified facts per junction | ✓ Verified |
| **Simultaneity** | Process while driving | ✓ Non-blocking |

---

## Modified Skill Set for Junction Processing

### Video Finder Skills (Modified)
1. **Junction Context Extraction** - Extract intersection details
2. **Street-Level Video Discovery** - Find street-view videos
3. **Quick Relevance Scoring** - Fast relevance assessment
4. **API Web Fetching** - YouTube search API

### Music Finder Skills (Modified)
1. **Street Atmosphere Analysis** - Analyze intersection mood
2. **Short-Form Track Discovery** - Find 2-4 min songs
3. **Mood Matching** - Match to specific street vibe
4. **API Web Fetching** - Spotify search API

### History Finder Skills (Modified)
1. **Junction History Research** - Research THIS junction
2. **Fact Verification** - Verify facts about THIS spot
3. **Concise Storytelling** - Brief, punchy facts
4. **API Web Fetching** - Wikipedia/historical API

### Judge Skills (Modified)
1. **Quick Content Evaluation** - Fast assessment
2. **Speed-Optimized Scoring** - < 500ms evaluation
3. **Driver-Friendly Summary** - Minimal, clear output
4. **Real-Time Compilation** - Instant reports

---

## Use Cases

### 1. Tourist Road Trip
```
Route: San Francisco to LA (10-minute segments)
Each junction provides:
- Local landmark video
- Regional music vibe
- Historical fact about area
Result: Educational, entertaining drive
```

### 2. City Exploration
```
Route: Downtown walking/driving tour (10 min segments)
Each turn reveals:
- Street-level detail video
- Neighborhood atmosphere music
- Specific street/intersection history
Result: Immersive local experience
```

### 3. Historical Route
```
Route: Historic district tour (10-minute drive)
Each junction highlights:
- Period street scenes (if available)
- Era-appropriate music
- Historical events at THIS intersection
Result: Time-traveling tour
```

### 4. Urban Navigation
```
Route: Commute optimization (10-minute paths)
Each junction provides:
- Real-time street conditions
- Mood-matching commute music
- Quick local facts
Result: Engaging commute enhancement
```

---

## Benefits of Junction-Based Approach

✓ **Precision**: Content is specific to individual intersections
✓ **Real-Time**: Activates as driver approaches each turn
✓ **Engaging**: Constant stream of relevant content
✓ **Safe**: Information delivered just-in-time (not overwhelming)
✓ **Scalable**: Works for any length route (just more junctions)
✓ **Practical**: Supports actual navigation workflows
✓ **Interesting**: Every turn offers something new
✓ **Educational**: Learn about specific locations while traveling

---

## Technical Implementation

### Input: Google Maps Route
- API: Google Maps Directions API
- Provides: GPS coordinates, turn-by-turn instructions, distances
- Update: Real-time as driver progresses

### Processing: Parallel Junction Analysis
- For each upcoming junction:
  - Extract street names and coordinates
  - Spawn 3 agents in parallel
  - Compile results as they arrive
  - Judge evaluates immediately

### Output: Real-Time Recommendations
- Format: Push notifications or HUD display
- Timing: 30-60 seconds before approaching junction
- Content: Video preview, music snippet, history fact
- Judge: Winner + brief explanation

---

## Version Comparison

| Feature | v1.0 | v2.0 |
|---------|------|------|
| **Input Type** | City/address | Route waypoints |
| **Scope** | Entire location | Single junction |
| **Activation** | Manual | Automatic per turn |
| **Output** | 1 recommendation | 1 per junction |
| **Route Length** | N/A | 10-minute drive |
| **Precision** | City level | Intersection level |
| **Use Case** | Research | Navigation |
| **Engagement** | One-time | Continuous |

---

## Implementation Checklist

- [ ] Update agents for junction-based processing
- [ ] Modify skills for per-intersection analysis
- [ ] Optimize performance for < 500ms per junction
- [ ] Implement parallel processing
- [ ] Create junction input parser
- [ ] Add route waypoint handler
- [ ] Implement real-time scheduling
- [ ] Create driver-friendly output format
- [ ] Test with sample 10-minute routes
- [ ] Integrate with navigation APIs

---

## Conclusion

The Tour Guide System v2.0 shifts from **global address-based analysis** to **junction-by-junction turn-specific content delivery**. This enables:

- Real-time engagement while navigating
- Precise, location-specific recommendations
- Educational content at the right moment
- Safer, less overwhelming information flow
- Continuous entertainment throughout drive

Each junction activates all agents for maximum engagement, with the Judge determining the most relevant recommendation for that specific turn.

**Status:** Ready for implementation
**Target:** < 500ms per junction processing
**Scope:** 10-minute routes with unlimited junctions

---

**Tour Guide v2.0 - Turn-by-Turn Navigation Enhancement**
Created: November 21, 2025
Architecture: Junction-based, agent-driven, real-time
