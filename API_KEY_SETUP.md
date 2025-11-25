# API Key Setup - Quick Start

Your Google Maps API key is now integrated into the Tour Guide system!

## ✅ What Changed

The API key is now stored in `tour_guide/config.py` alongside YouTube and Spotify keys:

```python
# tour_guide/config.py

GOOGLE_MAPS_API_KEY = "AIzaSyAgu_T79gjEJ2tVf5VLBSj7RjXByTDO7fo"
YOUTUBE_API_KEY = None  # Optional - for future video search
SPOTIFY_API_KEY = None  # Optional - for future music search
```

## 🚀 How to Use

### Before (Required API Key)

```python
# Had to pass API key every time
api = TourGuideAPI(google_maps_api_key="AIzaSyAgu_T79gjEJ2tVf5VLBSj7RjXByTDO7fo")
```

```bash
# Had to pass as argument
python3 demo_technion_to_tau.py AIzaSyAgu_T79gjEJ2tVf5VLBSj7RjXByTDO7fo
```

### After (Automatic)

```python
# API key automatically loaded from config.py
api = TourGuideAPI()
result = api.get_tour("Tel Aviv", "Jerusalem")
```

```bash
# No API key needed - uses config.py
python3 demo_technion_to_tau.py
```

## 📁 Files Modified

1. **`tour_guide/config.py`** (NEW)
   - Centralized configuration for all API keys
   - Default values for system settings

2. **`tour_guide/route_fetcher/google_maps_client.py`**
   - Now imports `get_google_maps_api_key()` from config
   - Falls back to config.py if no key provided

3. **`tour_guide/agent_orchestrator/agents.py`**
   - VideoAgent uses `get_youtube_api_key()`
   - MusicAgent uses `get_spotify_api_key()`

4. **`docs/CONFIGURATION.md`** (NEW)
   - Complete guide on API key setup
   - Security best practices
   - Troubleshooting

## 🔧 Configuration Priority

The system checks for API keys in this order:

1. **Direct parameter** (highest priority)
   ```python
   api = TourGuideAPI(google_maps_api_key="custom_key")
   ```

2. **Environment variable**
   ```bash
   export GOOGLE_MAPS_API_KEY="your_key"
   ```

3. **config.py** (lowest priority)
   ```python
   # tour_guide/config.py
   GOOGLE_MAPS_API_KEY = "default_key"
   ```

## 🎯 Quick Examples

### Example 1: Simple Usage

```python
from tour_guide import TourGuideAPI

# Key loaded automatically from config.py
api = TourGuideAPI()
result = api.get_tour("Technion", "Tel Aviv University")
print(f"Processed {result.total_junctions} junctions")
```

### Example 2: Override Config

```python
from tour_guide import TourGuideAPI

# Use different key for this instance
api = TourGuideAPI(google_maps_api_key="special_key")
result = api.get_tour("Haifa", "Jerusalem")
```

### Example 3: Check Configuration

```python
from tour_guide import config

print(f"Current API Key: {config.GOOGLE_MAPS_API_KEY[:20]}...")
print(f"Junction Interval: {config.DEFAULT_JUNCTION_INTERVAL}s")
```

## 🔒 Security Notes

### For Development
- Your API key is already in `config.py` - ready to use!
- Perfect for testing and development

### For Production
- Use environment variables instead:
  ```bash
  export GOOGLE_MAPS_API_KEY="production_key"
  ```
- Or add `tour_guide/config.py` to `.gitignore`

### If Sharing Code
- Create `config.example.py` with placeholder values
- Add real `config.py` to `.gitignore`
- Never commit API keys to public repositories

## 📚 Documentation

- **Full Configuration Guide**: `docs/CONFIGURATION.md`
- **Logging Guide**: `docs/LOGGING.md`
- **Main README**: `README.md`

## ✨ Benefits

1. **No more typing API keys** - Set once, use everywhere
2. **Consistent with other agents** - YouTube and Spotify use same pattern
3. **Easy to override** - Can still pass custom keys when needed
4. **Centralized configuration** - All settings in one place

## 🧪 Test It

Run the demo without any arguments:

```bash
python3 demo_technion_to_tau.py
```

Output:
```
Using API key from tour_guide/config.py
Setting up debug logging...
...
Route fetched successfully: 22 junctions, 90.3 km, 1 hour 4 mins
```

Success! The API key is automatically loaded from config.py.
