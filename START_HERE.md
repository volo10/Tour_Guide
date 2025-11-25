# START HERE - Tour Guide Quick Reference

## For New Users: 3 Steps to Your First Tour

### Step 1: Get API Key
1. Go to https://console.cloud.google.com/
2. Enable "Directions API"
3. Create API Key
4. Copy it

### Step 2: Configure
Open `tour_guide/config.py` and paste your key:
```python
GOOGLE_MAPS_API_KEY = "paste_your_key_here"
```

### Step 3: Run Interactive Mode
```bash
python3 tour_guide_interactive.py
```

Answer the questions:
- Where are you starting from? **→** Type your source (e.g., "Tel Aviv")
- Where do you want to go? **→** Type your destination (e.g., "Jerusalem")
- Press Enter for all other questions (uses defaults)
- Type "yes" to start

**Done!** Your tour report will be displayed and saved to a JSON file.

---

## What You Get

```
============================================================
📊 SUMMARY:
   🎬 Video Wins:   6
   🎵 Music Wins:   0
   📖 History Wins: 16
   ⏱️  Processing:   105.46s
============================================================

📁 Results saved to: tour_TelAviv_to_Jerusalem_20251125_140530.json
```

Each junction along your route will have:
- 🎬 Video recommendation, OR
- 🎵 Music recommendation, OR
- 📖 History/story about that location

---

## Three Ways to Use Tour Guide

### 1. Interactive Mode ⭐ (EASIEST)
```bash
python3 tour_guide_interactive.py
```
Just answer questions. Perfect for beginners.

### 2. Pre-Made Demo (FASTEST)
```bash
python3 demo_technion_to_tau.py
```
Tests with Technion → Tel Aviv University route.

### 3. Python Code (MOST FLEXIBLE)
```python
from tour_guide import TourGuideAPI
api = TourGuideAPI()
result = api.get_tour("Start", "End")
```
Build your own apps with Tour Guide.

---

## Troubleshooting

**"API key not configured"**
→ Edit `tour_guide/config.py` and add your key

**"REQUEST_DENIED"**
→ Enable Directions API at https://console.cloud.google.com/

**Script hangs**
→ Normal! It's processing. Wait for it to finish (about 2 minutes for 20 junctions)

---

## Learn More

- **Interactive Mode Guide**: [INTERACTIVE_MODE.md](INTERACTIVE_MODE.md)
- **Complete Setup**: [GETTING_STARTED.md](GETTING_STARTED.md)
- **60-Second Setup**: [QUICK_SETUP.md](QUICK_SETUP.md)
- **Configuration**: [docs/CONFIGURATION.md](docs/CONFIGURATION.md)
- **Architecture**: [README.md](README.md)

---

## Quick Commands

```bash
# Run interactive mode
python3 tour_guide_interactive.py

# Run demo
python3 demo_technion_to_tau.py

# View results
cat tour_*.json | python3 -m json.tool

# Run tests
python3 -m pytest tests/ -v
```

---

**Ready? Run this now:**
```bash
python3 tour_guide_interactive.py
```

🚀 Enjoy your personalized tour guide!
