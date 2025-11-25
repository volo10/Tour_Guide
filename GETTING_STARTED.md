# Getting Started with Tour Guide

This guide will walk you through setting up and running the Tour Guide demo from scratch.

## Prerequisites

- Python 3.8 or higher
- Google Maps API key (free tier works fine)

## Step 1: Install Python Dependencies

```bash
# Navigate to the Tour_Guide directory
cd /path/to/Tour_Guide

# Install required packages
pip3 install certifi
```

## Step 2: Get a Google Maps API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
3. Enable the **Directions API**:
   - Go to "APIs & Services" → "Library"
   - Search for "Directions API"
   - Click "Enable"
4. Create an API key:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "API Key"
   - Copy your API key (looks like: `AIzaSyAgu_T79gjEJ2tVf5VLBSj7RjXByTDO7fo`)

## Step 3: Configure Your API Key

**Option A: Edit config.py (Easiest)**

Open `tour_guide/config.py` and paste your API key:

```python
# tour_guide/config.py

GOOGLE_MAPS_API_KEY = "YOUR_API_KEY_HERE"  # Replace with your actual key
```

**Option B: Use Environment Variable**

```bash
export GOOGLE_MAPS_API_KEY="YOUR_API_KEY_HERE"
```

## Step 4: Run the Demo

The demo script `demo_technion_to_tau.py` is already in the project root.

### Method 1: Using config.py (Recommended)

If you set the key in `config.py`:

```bash
python3 demo_technion_to_tau.py
```

### Method 2: Using Environment Variable

```bash
export GOOGLE_MAPS_API_KEY="your_key"
python3 demo_technion_to_tau.py
```

### Method 3: Pass Key as Argument

```bash
python3 demo_technion_to_tau.py YOUR_API_KEY_HERE
```

## What the Demo Does

The demo will:

1. **Fetch route** from Technion (Haifa) to Tel Aviv University via Google Maps
2. **Process 22 junctions** along the route
3. **Run 3 agents per junction** (Video, Music, History) in parallel
4. **Judge picks winner** for each junction
5. **Save results** to JSON file
6. **Generate debug logs** with junction ID tracking

## Expected Output

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
  📖 Junction 1: Local Stories from Derech Ya'akov Dori
  📖 Junction 2: Local Stories from Derech Ya'akov Dori
  🎬 Junction 3: Malal St Street Walking Tour
  ...

============================================================
📊 SUMMARY:
   🎬 Video Wins:   6
   🎵 Music Wins:   0
   📖 History Wins: 16
   ⏱️  Processing:   105.46s
============================================================
```

## Output Files

After running, you'll find:

1. **`technion_to_tau_results.json`** - Complete results in JSON format
   ```bash
   cat technion_to_tau_results.json
   ```

2. **`technion_to_tau_debug.log`** - Detailed debug logs with junction tracking
   ```bash
   # View logs for specific junction
   cat technion_to_tau_debug.log | grep '[JID-5]'
   ```

## Creating Your Own Demo

To create a demo for different locations:

### Option 1: Copy and Modify

```bash
# Copy the existing demo
cp demo_technion_to_tau.py my_demo.py

# Edit my_demo.py and change:
source="Your Start Location"
destination="Your End Location"
```

### Option 2: Write from Scratch

Create a new file `my_demo.py`:

```python
#!/usr/bin/env python3
from tour_guide import TourGuideAPI, setup_debug_logging

# Enable logging
setup_debug_logging(log_file="my_demo_debug.log")

# Create API (uses key from config.py automatically)
api = TourGuideAPI(junction_interval_seconds=5.0)

# Run tour
result = api.get_tour(
    source="Tel Aviv",
    destination="Haifa",
    verbose=True
)

# Print results
result.print_winners()

# Save to JSON
with open("my_demo_results.json", "w") as f:
    f.write(result.to_json())

print(f"Done! Processed {result.total_junctions} junctions")
```

Make it executable and run:

```bash
chmod +x my_demo.py
python3 my_demo.py
```

## Using Tour Guide in Your Code

### Simple Example

```python
from tour_guide import TourGuideAPI

# API key loaded from config.py
api = TourGuideAPI()

# Get tour recommendations
result = api.get_tour("Start Address", "End Address")

# Access results
print(f"Total junctions: {result.total_junctions}")
print(f"Video wins: {result.video_wins}")
print(f"Music wins: {result.music_wins}")
print(f"History wins: {result.history_wins}")

# Iterate through winners
for winner in result.winners:
    print(f"{winner.junction_number}. {winner.winner_type}: {winner.winner_title}")
```

### Advanced Example with Logging

```python
from tour_guide import TourGuideAPI, setup_debug_logging

# Enable detailed logging
setup_debug_logging("my_tour.log")

# Create API with custom settings
api = TourGuideAPI(
    junction_interval_seconds=3.0,  # Process faster
    google_maps_api_key="custom_key"  # Optional override
)

# Get tour with progress output
result = api.get_tour(
    source="Start",
    destination="End",
    verbose=True  # Show progress in terminal
)

# Print formatted output
result.print_winners()

# Access specific winner details
for winner in result.winners:
    print(f"""
    Junction {winner.junction_number}: {winner.junction_address}
    Turn: {winner.turn_direction}
    Winner: {winner.winner_type}
    Title: {winner.winner_title}
    Score: {winner.score:.0f}/100
    URL: {winner.winner_url}
    """)
```

## Troubleshooting

### Error: "Google Maps API key not provided"

**Solution:** Set your API key in one of three ways:
1. Edit `tour_guide/config.py`
2. Set environment variable: `export GOOGLE_MAPS_API_KEY="your_key"`
3. Pass as parameter: `TourGuideAPI(google_maps_api_key="your_key")`

### Error: "REQUEST_DENIED"

**Solution:**
1. Make sure Directions API is enabled in Google Cloud Console
2. Check that billing is enabled for your project
3. Verify your API key is correct

### Error: "SSL: CERTIFICATE_VERIFY_FAILED"

**Solution:** Install certifi:
```bash
pip3 install --upgrade certifi
```

### Demo runs but shows 0 junctions

**Solution:**
1. Check that your API key is valid
2. Verify the source and destination addresses are valid
3. Check the logs: `cat technion_to_tau_debug.log`

## Next Steps

- Read the [Configuration Guide](docs/CONFIGURATION.md) for advanced setup
- Read the [Logging Guide](docs/LOGGING.md) to understand the logs
- Read the [README](README.md) for architecture details
- Run tests: `python3 -m pytest tests/`

## Quick Reference

```bash
# Run demo (uses config.py)
python3 demo_technion_to_tau.py

# Run demo with custom key
python3 demo_technion_to_tau.py YOUR_API_KEY

# Run with environment variable
export GOOGLE_MAPS_API_KEY="your_key"
python3 demo_technion_to_tau.py

# View results
cat technion_to_tau_results.json

# View logs
cat technion_to_tau_debug.log

# Filter logs by junction
cat technion_to_tau_debug.log | grep '[JID-5]'

# Run tests
python3 -m pytest tests/ -v
```

## Need Help?

- Check [docs/CONFIGURATION.md](docs/CONFIGURATION.md) for API key setup
- Check [docs/LOGGING.md](docs/LOGGING.md) for understanding logs
- Check [README.md](README.md) for system architecture
- Check [API_KEY_SETUP.md](API_KEY_SETUP.md) for quick API key reference
