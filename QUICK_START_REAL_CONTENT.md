# 🚀 Quick Start - Real Content Fetcher

## Overview

This guide shows you how to **fetch REAL videos from YouTube and REAL songs from Spotify** for the Ramat Hasharon → Tel Aviv route.

**Total Time:** ~15 minutes (10 min setup + 5 min fetching)

---

## Step 1: Get Your API Keys (10 minutes)

### 📺 YouTube API Key
1. Go to: **https://console.cloud.google.com/**
2. Create new project: `Tour-Guide-System`
3. Search for: **"YouTube Data API v3"** → Enable it
4. Go to: **Credentials** → **+ Create Credentials** → **API Key**
5. **COPY YOUR KEY** ✓

### 🎵 Spotify Credentials
1. Go to: **https://developer.spotify.com/dashboard**
2. Create new app: `Tour-Guide-System`
3. You'll get:
   - **Client ID**
   - **Client Secret**
4. **COPY BOTH** ✓

**Detailed guide:** See `API_SETUP_GUIDE.md`

---

## Step 2: Set Your Credentials

Choose ONE method:

### Method A: Environment Variables (Recommended)
```bash
# In your terminal, set these:
export YOUTUBE_API_KEY='your_youtube_key_here'
export SPOTIFY_CLIENT_ID='your_spotify_id_here'
export SPOTIFY_CLIENT_SECRET='your_spotify_secret_here'
```

### Method B: Create .env File
```bash
# Create file: ~/.tour_guide_env
cat > ~/.tour_guide_env << 'EOF'
export YOUTUBE_API_KEY='your_youtube_key_here'
export SPOTIFY_CLIENT_ID='your_spotify_id_here'
export SPOTIFY_CLIENT_SECRET='your_spotify_secret_here'
EOF

# Load it:
source ~/.tour_guide_env
```

### Method C: Manual Entry When Running
```bash
# Just run the script and enter keys when prompted
python3 fetch_real_content.py
```

---

## Step 3: Run the Content Fetcher

### Option A: Use the Shell Script (Easiest)
```bash
cd /Users/bvolovelsky/Desktop/LLM/Tour_Guide/scripts
chmod +x run_real_content_fetch.sh
./run_real_content_fetch.sh
```

### Option B: Run Python Directly
```bash
cd /Users/bvolovelsky/Desktop/LLM/Tour_Guide/scripts
python3 fetch_real_content.py
```

---

## Step 4: View Your Results

The script will:
1. Search YouTube for videos for each junction ✓
2. Search Spotify for songs for each junction ✓
3. Display results in terminal with **clickable links** ✓
4. Save all results to: `tour_guide_real_results.json` ✓

### Results File
```bash
# View the JSON results:
cat tour_guide_real_results.json | python3 -m json.tool

# Or view in any text editor
```

---

## Example Output

When you run the script, you'll see:

```
============================================================
🚗 Tour Guide Real Content Fetcher
============================================================

✓ Spotify authenticated successfully

============================================================
📍 JUNCTION 1: Hasadot → Highway 5
============================================================

🎬 Searching YouTube for: Highway 5 Ramat Hasharon Tel Aviv drive

✓ Top YouTube Videos:
  1. Highway 5 Drive - Ramat Hasharon to Tel Aviv
     Channel: Israeli Travel Vlogs
     URL: https://www.youtube.com/watch?v=XXXXX

  2. Israel Highway 5 Traffic Conditions
     Channel: Israeli Traffic Cam
     URL: https://www.youtube.com/watch?v=YYYYY

🎵 Searching Spotify for: Israeli highway driving music

✓ Top Spotify Tracks:
  1. Urban Drive
     Artist: Israeli Electronic Artist
     Popularity: 65/100
     URL: https://open.spotify.com/track/ZZZZZ

  2. Modern Highway
     Artist: Contemporary Israeli
     Popularity: 58/100
     URL: https://open.spotify.com/track/WWWWW

[... and so on for all 6 junctions ...]

✓ Complete route results saved to: tour_guide_real_results.json
Tour Guide Real Content Fetching Complete!
```

---

## Troubleshooting

### ❌ "YouTube API key invalid"
- Check you copied the key correctly (no spaces)
- Make sure YouTube Data API v3 is **enabled** in Google Cloud

### ❌ "Spotify authentication failed"
- Verify Client ID and Secret are correct
- Check they're not swapped
- Make sure you're using the right Spotify app credentials

### ❌ "No results found"
- That's OK! Not all junctions may have videos/songs
- The script finds what's available
- Even one result per junction is useful

### ❌ "quota exceeded"
- YouTube has a free quota (resets daily)
- Wait 24 hours or upgrade to paid plan
- Spotify has generous limits (no issue)

---

## What You Get

### For Each Junction:

**YouTube Videos:**
- ✅ Direct clickable URL
- ✅ Video title
- ✅ Channel name
- ✅ Thumbnail URL
- ✅ Full video ID

**Spotify Songs:**
- ✅ Direct clickable URL
- ✅ Song title
- ✅ Artist name(s)
- ✅ Album name
- ✅ Popularity score (0-100)
- ✅ Duration
- ✅ Preview URL (listen for free!)

---

## Next Steps

### After Getting Real Links:

1. **Use in App**
   - Display video previews
   - Play song previews
   - Let driver click through

2. **Integrate with Navigation**
   - Show during actual drive
   - Update 30-60 seconds before junction
   - Automatically fetch for upcoming turns

3. **Enhance Results**
   - Add more search filters
   - Rate which content drivers liked
   - Learn driver preferences

---

## Tips

💡 **Tips for Best Results:**

1. **Fresh API Keys:** Newly created keys work best
2. **Search Terms Matter:** The script uses good defaults, but you can modify for different search terms
3. **Periodic Updates:** Run monthly to get fresh content recommendations
4. **Cache Results:** Save the JSON to reuse without hitting APIs again
5. **Spotify Preview:** Many songs have 30-second previews you can play!

---

## Example Command-Line Usage

```bash
# Navigate to scripts directory
cd /Users/bvolovelsky/Desktop/LLM/Tour_Guide/scripts

# Set credentials (one time)
export YOUTUBE_API_KEY='AIzaSy...'
export SPOTIFY_CLIENT_ID='a1b2c3...'
export SPOTIFY_CLIENT_SECRET='x9y8z7...'

# Run the fetcher
python3 fetch_real_content.py

# View results
cat tour_guide_real_results.json | python3 -m json.tool
```

---

## Questions?

- **API Key Issues?** → See `API_SETUP_GUIDE.md`
- **Script Issues?** → Check Python 3.6+ and `requests` package installed
- **No Results?** → Try different search terms or verify API keys

---

## Timeline

| Step | Time | Action |
|------|------|--------|
| 1 | 5 min | Get YouTube API Key |
| 2 | 5 min | Get Spotify Credentials |
| 3 | 2 min | Set Environment Variables |
| 4 | 2 min | Run Script |
| 5 | 1 min | View Results |
| **Total** | **15 min** | **Real Video & Song Links** ✓ |

---

**Ready?** Let's get real content! 🎬🎵

Next step: Get your API keys and come back with them! 👉
