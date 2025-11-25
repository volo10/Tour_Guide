# Tour Guide - Interactive Mode

The easiest way to use Tour Guide! Just answer a few questions and get your tour report.

## Quick Start

```bash
python3 tour_guide_interactive.py
```

That's it! The script will guide you through the rest.

## What It Does

The interactive script will ask you:

1. **Where are you starting from?** (e.g., Tel Aviv, Technion)
2. **Where do you want to go?** (e.g., Jerusalem, Haifa)
3. **Settings** (optional - just press Enter to use defaults)
4. **Confirm** and start processing

Then it:
- Fetches your route from Google Maps
- Processes each junction with Video/Music/History agents
- Shows you the winners for each junction
- Saves results to a JSON file

## Example Session

```
============================================================
🚗 TOUR GUIDE - Interactive Mode
============================================================

Generate personalized tour recommendations for your route!
The system will find videos, music, and historical facts
for each junction along your journey.

✅ API Key configured: AIzaSyAgu_T79gjEJ2tV...

------------------------------------------------------------
📍 Enter Your Route
------------------------------------------------------------

🏁 Where are you starting from? (e.g., Tel Aviv, Technion, etc.)
> Technion

🎯 Where do you want to go? (e.g., Jerusalem, Ben Gurion Airport, etc.)
> Tel Aviv University

------------------------------------------------------------
⚙️  Settings (optional)
------------------------------------------------------------

⏱️  Junction processing interval:
   How many seconds between processing each junction?
   (Default: 5 seconds)
> 5

📢 Show progress while processing?
   (yes/no, default: yes)
> yes

📝 Save detailed debug logs?
   (yes/no, default: no)
> no

============================================================
📋 Route Summary
============================================================
  🏁 From: Technion
  🎯 To:   Tel Aviv University
  ⏱️  Interval: 5 seconds per junction
============================================================

✅ Start processing? (yes/no) > yes

============================================================
🚀 Processing Route...
============================================================

🗺️  Fetching route from Google Maps...

🚗 Processing route: Technion → Tel Aviv University
⏱️  Tempo: 5.0s per junction
----------------------------------------
  📖 Junction 1: Local Stories from Derech Ya'akov Dori
  🎬 Junction 2: Derech Ya'akov Dori Street Walking Tour
  📖 Junction 3: The History of Malal St
  ...

[Results display]

============================================================
🚗 TOUR GUIDE RESULTS
============================================================
Route: Technion → Tel Aviv University
...

📁 Results saved to: tour_Technion_to_Tel_Aviv_University_20251125_140530.json

============================================================
🔄 Process another route? (yes/no) > no

============================================================
👋 Thank you for using Tour Guide!
============================================================
```

## Features

### Smart Filename
Results are saved with descriptive filenames:
```
tour_Technion_to_Tel_Aviv_University_20251125_140530.json
```

Format: `tour_[source]_to_[destination]_[timestamp].json`

### Optional Debug Logging
If you enable debug logs, you get detailed execution logs:
```
tour_20251125_140530.log
```

You can filter by junction ID:
```bash
cat tour_20251125_140530.log | grep '[JID-5]'
```

### Multiple Routes
Process multiple routes in one session:
- Answer "yes" to "Process another route?"
- Enter new source and destination
- Keeps going until you say "no"

### Error Handling
If something goes wrong, the script:
- Shows a clear error message
- Suggests solutions
- Lets you try again or exit

## Settings Explained

### Junction Processing Interval
**Question:** "How many seconds between processing each junction?"

- **Default:** 5 seconds
- **What it means:** Time delay between starting to process each junction
- **Example:** With 20 junctions at 5 seconds each = ~100 seconds total
- **Tip:** Use 3-5 seconds for normal speed, 1-2 for faster (less realistic tempo)

### Show Progress
**Question:** "Show progress while processing?"

- **Default:** Yes
- **What it shows:** Real-time updates as each junction is processed
- **Example:**
  ```
  📖 Junction 1: Local Stories from Derech Ya'akov Dori
  🎬 Junction 2: Walking Tour Video
  ```

### Debug Logging
**Question:** "Save detailed debug logs?"

- **Default:** No
- **What it saves:** Detailed logs with timestamps and junction ID tracking
- **Use when:** You want to debug or understand system behavior
- **File:** Creates `tour_YYYYMMDD_HHMMSS.log`

## Usage Tips

### Quick Test (Use All Defaults)
Just press Enter for all settings questions:
```
> [Enter]  # Use default interval
> [Enter]  # Yes to progress
> [Enter]  # No to debug logs
> [Enter]  # Yes to start
```

### Common Routes (Israel)
```
Technion → Tel Aviv University
Tel Aviv Central Station → Ben Gurion Airport
Haifa → Jerusalem
Tel Aviv → Eilat
Herzliya → Netanya
```

### International Examples
```
New York, NY → Boston, MA
London, UK → Manchester, UK
Paris, France → Lyon, France
```

### View Results
```bash
# View JSON (formatted)
python3 -m json.tool tour_Technion_to_Tel_Aviv_University_*.json

# View JSON (raw)
cat tour_Technion_to_Tel_Aviv_University_*.json

# Extract just the summary
cat tour_*.json | python3 -m json.tool | grep -A 5 "summary"

# Count total junctions
cat tour_*.json | python3 -m json.tool | grep "total_junctions"
```

## Troubleshooting

### "API key not configured"
**Solution:** Set your Google Maps API key in `tour_guide/config.py`:
```python
GOOGLE_MAPS_API_KEY = "your_key_here"
```

### "Route not found"
**Solution:** Check that both addresses are valid. Try:
- Adding country name (e.g., "Tel Aviv, Israel")
- Using more specific addresses (e.g., "Tel Aviv Central Station")
- Checking spelling

### Script hangs during processing
**Cause:** Normal - it's processing junctions with the interval you specified
**Wait time:** Number of junctions × interval (e.g., 20 junctions × 5 seconds = 100 seconds)

### Want to cancel mid-process
**Solution:** Press `Ctrl+C` to interrupt
- Script will stop gracefully
- Ask if you want to try another route

## Comparison with Other Methods

### Interactive Script (This)
✅ **Easiest** - Just answer questions
✅ **Best for:** First-time users, testing different routes
✅ **No coding needed**

```bash
python3 tour_guide_interactive.py
```

### Pre-made Demo
✅ **Fast** - No questions
❌ **Fixed route** - Technion to Tel Aviv University only
✅ **Best for:** Quick test of the system

```bash
python3 demo_technion_to_tau.py
```

### Python API
✅ **Most flexible** - Full control
❌ **Requires coding**
✅ **Best for:** Integration, automation, custom features

```python
from tour_guide import TourGuideAPI
api = TourGuideAPI()
result = api.get_tour("Start", "End")
```

## Next Steps

After using interactive mode:

1. **View your results** - Open the JSON file
2. **Try different routes** - Run again with new locations
3. **Enable debug logs** - See how the system works internally
4. **Learn the API** - Use Tour Guide in your own code (see [GETTING_STARTED.md](GETTING_STARTED.md))

## Summary

**For new users, this is the recommended way to use Tour Guide:**

1. Set API key in `tour_guide/config.py` (one time)
2. Run `python3 tour_guide_interactive.py`
3. Answer the questions
4. Get your personalized tour report!

Simple, fast, and user-friendly! 🚀
