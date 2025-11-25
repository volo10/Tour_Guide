# Tour Guide - Quick Setup (60 seconds)

Get Tour Guide running in under a minute!

## Step 1: Get Google Maps API Key (30 seconds)

1. Visit https://console.cloud.google.com/
2. Enable **Directions API**
3. Create **API Key**
4. Copy the key (looks like: `AIzaSyA...`)

## Step 2: Configure API Key (15 seconds)

Open `tour_guide/config.py` and paste your key:

```python
GOOGLE_MAPS_API_KEY = "YOUR_KEY_HERE"  # ← Paste here
```

Save the file.

## Step 3: Install Dependencies (10 seconds)

```bash
pip3 install certifi
```

## Step 4: Run Demo (5 seconds)

```bash
python3 demo_technion_to_tau.py
```

**Done!** 🎉

---

## What You'll See

```
Using API key from tour_guide/config.py
Setting up debug logging...

============================================================
TOUR GUIDE DEMO: Technion → Tel Aviv University
============================================================

🚗 Processing route: Technion → Tel Aviv University
⏱️  Tempo: 5.0s per junction
----------------------------------------
  📖 Junction 1: Local Stories from Derech Ya'akov Dori
  📖 Junction 2: Local Stories from Derech Ya'akov Dori
  🎬 Junction 3: Malal St Street Walking Tour
  📖 Junction 4: Local Stories from Natan Komoi St
  ...

============================================================
📊 SUMMARY:
   🎬 Video Wins:   6
   🎵 Music Wins:   0
   📖 History Wins: 16
   ⏱️  Processing:   105.46s
============================================================

✅ Results saved to: technion_to_tau_results.json
```

## Output Files

- **`technion_to_tau_results.json`** - Complete results
- **`technion_to_tau_debug.log`** - Detailed logs with junction tracking

## Use in Your Code

```python
from tour_guide import TourGuideAPI

api = TourGuideAPI()  # Key loaded automatically!
result = api.get_tour("Start", "End")

print(f"Processed {result.total_junctions} junctions")
print(f"Winners: {result.video_wins} video, {result.history_wins} history")
```

## Need More Help?

- 📖 **Complete Guide**: [GETTING_STARTED.md](GETTING_STARTED.md)
- ⚙️ **Configuration**: [docs/CONFIGURATION.md](docs/CONFIGURATION.md)
- 📝 **Logging**: [docs/LOGGING.md](docs/LOGGING.md)
- 🏗️ **Architecture**: [README.md](README.md)

---

**That's it!** Your Tour Guide system is ready to use. 🚀
