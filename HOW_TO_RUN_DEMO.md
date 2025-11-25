# How to Run the Tour Guide Demo

This document explains what `demo_technion_to_tau.py` is and how to use it.

## What is demo_technion_to_tau.py?

`demo_technion_to_tau.py` is a **ready-to-run demonstration script** that:
- Fetches a real route from Technion (Haifa) to Tel Aviv University
- Processes 22 junctions along the route
- Shows the Tour Guide system in action with logging
- Saves results to JSON and log files

**Location:** The file is in the root directory of the Tour Guide project.

## What Users Need to Do

### 1. The Demo File Already Exists

✅ **You don't need to create it** - it's already in the project!

```bash
# Check that it exists
ls demo_technion_to_tau.py
```

### 2. Set Up API Key (One-Time)

**Option A: Edit config.py (Recommended)**

Open `tour_guide/config.py` and add your Google Maps API key:

```python
# tour_guide/config.py
GOOGLE_MAPS_API_KEY = "AIzaSyAgu_T79gjEJ2tVf5VLBSj7RjXByTDO7fo"
```

**Option B: Use Environment Variable**

```bash
export GOOGLE_MAPS_API_KEY="your_key_here"
```

### 3. Run the Demo

```bash
python3 demo_technion_to_tau.py
```

**That's it!** No arguments needed - the API key is loaded automatically.

## Different Ways to Run

### Method 1: Using config.py (Easiest)

Set key once in `tour_guide/config.py`, then just run:

```bash
python3 demo_technion_to_tau.py
```

Output:
```
Using API key from tour_guide/config.py
```

### Method 2: Environment Variable

```bash
export GOOGLE_MAPS_API_KEY="your_key"
python3 demo_technion_to_tau.py
```

Output:
```
Using API key from GOOGLE_MAPS_API_KEY environment variable
```

### Method 3: Command Line Argument

```bash
python3 demo_technion_to_tau.py YOUR_API_KEY_HERE
```

Output:
```
Using API key from command line argument
```

## What Happens When You Run It?

```
Using API key from tour_guide/config.py
Setting up debug logging...

============================================================
TOUR GUIDE DEMO: Technion → Tel Aviv University
============================================================

This will:
  1. Fetch route from Google Maps
  2. Process each junction with Video/Music/History agents
  3. Have Judge pick winner for each junction
  4. Show junction ID tracking in logs

============================================================

🚗 Processing route: Technion → Tel Aviv University
⏱️  Tempo: 5.0s per junction
----------------------------------------

[Processing happens - shows winners for each junction]

  📖 Junction 1: Local Stories from Derech Ya'akov Dori
  🎬 Junction 2: Derech Ya'akov Dori Street Walking Tour
  📖 Junction 3: The History of Malal St
  ...

[After processing all junctions]

============================================================
🚗 TOUR GUIDE RESULTS
============================================================
Route: Technion → Tel Aviv University
Distance: N/A | Duration: N/A
============================================================

📍 WINNERS PER JUNCTION:

  1. Derech Ya'akov Dori
     Turn: STRAIGHT
     📖 HISTORY: Local Stories from Derech Ya'akov Dori
     Score: 81/100
     URL: https://wikipedia.org/wiki/Derech_Ya'akov_Dori

  [... 20 more junctions ...]

============================================================
📊 SUMMARY:
   🎬 Video Wins:   6
   🎵 Music Wins:   0
   📖 History Wins: 16
   ⏱️  Processing:   105.46s
============================================================

✅ Results saved to: technion_to_tau_results.json

📁 FILES CREATED:
   - technion_to_tau_results.json (Final report in JSON format)
   - technion_to_tau_debug.log (Debug logs with junction tracking)

💡 TIPS:
   View specific junction logs:
     cat technion_to_tau_debug.log | grep '[JID-3]'
   View final report:
     cat technion_to_tau_results.json
```

## Output Files Created

After running, you'll have:

### 1. technion_to_tau_results.json

Complete results in JSON format:

```json
{
  "source": "Haifa, 3200003, Israel",
  "destination": "Chaim Levanon St 55, Tel Aviv-Yafo, 6997801, Israel",
  "total_junctions": 22,
  "winners": [
    {
      "junction_number": 1,
      "junction_address": "Derech Ya'akov Dori",
      "turn_direction": "STRAIGHT",
      "winner_type": "history",
      "winner_title": "Local Stories from Derech Ya'akov Dori",
      "score": 81.01
    },
    ...
  ],
  "summary": {
    "video_wins": 6,
    "music_wins": 0,
    "history_wins": 16
  }
}
```

### 2. technion_to_tau_debug.log

Detailed logs with junction ID tracking:

```
2025-11-25 13:48:51,352 - tour_guide.route_fetcher.route_fetcher - INFO - Route fetched successfully: 22 junctions, 90.3 km, 1 hour 4 mins
2025-11-25 13:48:51,352 - tour_guide.junction_orchestrator.orchestrator - INFO - [JID-1] Dispatching junction 1/22: Derech Ya'akov Dori (STRAIGHT)
2025-11-25 13:48:51,353 - tour_guide.agent_orchestrator.junction_processor - INFO - [JID-1] Processing junction: Derech Ya'akov Dori
2025-11-25 13:48:51,522 - tour_guide.agent_orchestrator.junction_processor - INFO - [JID-1] history completed: 'Local Stories from Derech Ya'akov Dori' (relevance: 94.8, quality: 94.7)
2025-11-25 13:48:51,658 - tour_guide.agent_orchestrator.junction_processor - INFO - [JID-1] Judge selected: history
```

## Creating Your Own Demo

### Copy and Modify

```bash
# Copy the demo
cp demo_technion_to_tau.py my_custom_demo.py

# Edit my_custom_demo.py
nano my_custom_demo.py
```

Change these lines:

```python
# Change from:
source="Technion",
destination="Tel Aviv University",

# To your locations:
source="Tel Aviv Central Station",
destination="Jaffa Port",
```

Run your custom demo:

```bash
python3 my_custom_demo.py
```

### Create Simple Demo from Scratch

Create `simple_demo.py`:

```python
from tour_guide import TourGuideAPI

# API key loaded from config.py automatically
api = TourGuideAPI()

# Get tour
result = api.get_tour("Start Address", "End Address", verbose=True)

# Print results
print(f"\nProcessed {result.total_junctions} junctions")
print(f"Video: {result.video_wins}, Music: {result.music_wins}, History: {result.history_wins}")
```

Run it:

```bash
python3 simple_demo.py
```

## Troubleshooting

### "No such file or directory: demo_technion_to_tau.py"

**Solution:** You're not in the Tour_Guide directory.

```bash
cd /path/to/Tour_Guide
python3 demo_technion_to_tau.py
```

### "Google Maps API key not provided"

**Solution:** Set your API key in `tour_guide/config.py` or as environment variable.

```bash
# Option 1: Edit tour_guide/config.py
nano tour_guide/config.py

# Option 2: Set env var
export GOOGLE_MAPS_API_KEY="your_key"
```

### "command not found: python3"

**Solution:** Use `python` instead:

```bash
python demo_technion_to_tau.py
```

## Summary

**To run the demo:**

1. **One-time setup:** Put API key in `tour_guide/config.py`
2. **Run:** `python3 demo_technion_to_tau.py`
3. **View results:** `cat technion_to_tau_results.json`

**The demo file already exists in your project - no need to create it!**

## Documentation

- **Complete Setup Guide**: [GETTING_STARTED.md](GETTING_STARTED.md)
- **60-Second Setup**: [QUICK_SETUP.md](QUICK_SETUP.md)
- **API Configuration**: [docs/CONFIGURATION.md](docs/CONFIGURATION.md)
- **Understanding Logs**: [docs/LOGGING.md](docs/LOGGING.md)
