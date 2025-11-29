# How to Get API Keys for Tour Guide

This guide explains how to obtain the required API keys to run the Tour Guide application.

## Required API Keys

| Service | Purpose | Cost |
|---------|---------|------|
| Google Maps Directions API | Route fetching | Free tier: $200/month credit |
| YouTube Data API v3 | Video discovery | Free: 10,000 units/day |
| Spotify Web API | Music discovery | Free: unlimited |

---

## 1. Google Maps API Key (Directions API)

### Steps:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)

2. **Create a new project** (or select an existing one)
   - Click the project dropdown at the top
   - Click "New Project"
   - Enter a name (e.g., "Tour Guide App")
   - Click "Create"

3. **Enable the Directions API**
   - Go to **APIs & Services** → **Library**
   - Search for "Directions API"
   - Click on it and click **Enable**

4. **Create an API Key**
   - Go to **APIs & Services** → **Credentials**
   - Click **Create Credentials** → **API Key**
   - Copy the generated key

5. **(Optional) Restrict the API Key**
   - Click on the API key to edit it
   - Under "API restrictions", select "Restrict key"
   - Select "Directions API"
   - Click "Save"

### Pricing:
- Free tier includes **$200/month credit** (~40,000 direction requests)
- No credit card required for free tier usage

---

## 2. YouTube API Key (YouTube Data API v3)

### Steps:

1. Go to [Google Cloud Console](https://console.cloud.google.com/) (use the same project as Google Maps)

2. **Enable the YouTube Data API v3**
   - Go to **APIs & Services** → **Library**
   - Search for "YouTube Data API v3"
   - Click on it and click **Enable**

3. **Create an API Key** (or reuse the Google Maps key)
   - Go to **APIs & Services** → **Credentials**
   - Click **Create Credentials** → **API Key**
   - Copy the generated key

4. **(Optional) Restrict the API Key**
   - Click on the API key to edit it
   - Under "API restrictions", add "YouTube Data API v3"

### Quota:
- Free: **10,000 units per day**
- Search requests cost 100 units each (~100 searches/day)

---

## 3. Spotify API Credentials

### Steps:

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)

2. **Log in** with your Spotify account
   - A free Spotify account works fine
   - Create one at [spotify.com](https://www.spotify.com/) if needed

3. **Create an App**
   - Click **Create App**
   - Fill in the form:
     - **App name:** Tour Guide
     - **App description:** Tour guide application for route recommendations
     - **Redirect URI:** `http://localhost:8888/callback`
   - Check the Terms of Service agreement
   - Click **Create**

4. **Get your credentials**
   - Click on your newly created app
   - Click **Settings**
   - Copy the **Client ID**
   - Click "View client secret" and copy the **Client Secret**

### Pricing:
- **Completely free** - no usage limits for the Search API
- No credit card required

---

## Setting Up Environment Variables

### Option 1: Command Line (Temporary)

#### Windows (Command Prompt)
```cmd
set GOOGLE_MAPS_API_KEY=your_google_key_here
set YOUTUBE_API_KEY=your_youtube_key_here
set SPOTIFY_CLIENT_ID=your_spotify_client_id
set SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
```

#### Windows (PowerShell)
```powershell
$env:GOOGLE_MAPS_API_KEY="your_google_key_here"
$env:YOUTUBE_API_KEY="your_youtube_key_here"
$env:SPOTIFY_CLIENT_ID="your_spotify_client_id"
$env:SPOTIFY_CLIENT_SECRET="your_spotify_client_secret"
```

#### Linux / macOS
```bash
export GOOGLE_MAPS_API_KEY="your_google_key_here"
export YOUTUBE_API_KEY="your_youtube_key_here"
export SPOTIFY_CLIENT_ID="your_spotify_client_id"
export SPOTIFY_CLIENT_SECRET="your_spotify_client_secret"
```

### Option 2: Using a `.env` File (Recommended)

1. **Install python-dotenv**
   ```bash
   pip install python-dotenv
   ```

2. **Create a `.env` file** in the project root directory:
   ```
   GOOGLE_MAPS_API_KEY=your_google_key_here
   YOUTUBE_API_KEY=your_youtube_key_here
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   ```

3. **Load the environment variables** in your code:
   ```python
   from dotenv import load_dotenv
   load_dotenv()

   # Now you can use the Tour Guide API
   from tour_guide import TourGuideAPI
   api = TourGuideAPI()
   ```

> **Security Note:** Never commit your `.env` file to version control. Add `.env` to your `.gitignore` file.

### Option 3: System Environment Variables (Permanent)

#### Windows
1. Press `Win + R`, type `sysdm.cpl`, press Enter
2. Go to **Advanced** tab → **Environment Variables**
3. Under "User variables", click **New** for each key
4. Add the variable name and value
5. Click OK and restart your terminal

#### Linux / macOS
Add to your `~/.bashrc` or `~/.zshrc`:
```bash
export GOOGLE_MAPS_API_KEY="your_google_key_here"
export YOUTUBE_API_KEY="your_youtube_key_here"
export SPOTIFY_CLIENT_ID="your_spotify_client_id"
export SPOTIFY_CLIENT_SECRET="your_spotify_client_secret"
```
Then run `source ~/.bashrc` or restart your terminal.

---

## Verifying Your Setup

### Quick Validation

```python
from tour_guide.config import validate_api_keys

result = validate_api_keys()
if result['valid']:
    print("All API keys are configured!")
else:
    print(f"Missing keys: {result['missing']}")
```

### Full Test

```python
from tour_guide import TourGuideAPI

api = TourGuideAPI(junction_interval_seconds=2.0)
result = api.get_tour("Tel Aviv", "Jerusalem", verbose=True)

if result.success:
    result.print_winners()
else:
    print(f"Error: {result.error}")
```

### Command Line Test

```bash
python -m tour_guide
```

---

## Troubleshooting

### "Google Maps API key not provided"
- Ensure `GOOGLE_MAPS_API_KEY` environment variable is set
- Check that the key is correct (no extra spaces)
- Verify the Directions API is enabled in Google Cloud Console

### "YouTube API error"
- Check that `YOUTUBE_API_KEY` is set correctly
- Verify the YouTube Data API v3 is enabled
- Check your daily quota in Google Cloud Console

### "Spotify authentication error"
- Ensure both `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` are set
- Check that the credentials match those in your Spotify Developer Dashboard
- Verify your app is not in "Development mode" restrictions

### API Key Restrictions
If you've restricted your API keys and they're not working:
- Go to Google Cloud Console → Credentials
- Edit your API key
- Ensure the correct APIs are allowed
- Check IP/referrer restrictions aren't blocking your requests

---

## Cost Summary

| API | Free Tier | Typical Usage |
|-----|-----------|---------------|
| Google Maps Directions | $200/month credit | ~40,000 requests |
| YouTube Data API | 10,000 units/day | ~100 searches/day |
| Spotify Web API | Unlimited | No limits |

For a typical tour guide session (10 junctions), you'll use:
- 1 Google Maps request
- ~10 YouTube searches
- ~10 Spotify searches
- ~10 Wikipedia requests (free, no key needed)

**Bottom line:** The free tiers are more than sufficient for development and moderate usage.

---

## Next Steps

Once your API keys are configured:

1. Run the demo: `python demo_technion_to_tau.py`
2. Try interactive mode: `python tour_guide_interactive.py`
3. Read the [User Guide](USER_GUIDE.md) for more features
