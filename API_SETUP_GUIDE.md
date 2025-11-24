---
name: API Setup Guide
description: Step-by-step guide to get YouTube and Spotify API credentials
version: 1.0
---

# 🔑 API Setup Guide - YouTube & Spotify

This guide shows you how to get API keys for YouTube and Spotify so we can fetch real videos and songs.

---

## Part 1: YouTube API Setup

### Step 1: Go to Google Cloud Console
1. Visit: **https://console.cloud.google.com/**
2. Sign in with your Google account (create one if needed)
3. Click on the project dropdown at the top

### Step 2: Create a New Project
1. Click **"Select a Project"** at the top
2. Click **"NEW PROJECT"**
3. Enter project name: `Tour-Guide-System`
4. Click **"CREATE"**
5. Wait for project to be created (takes ~1 minute)

### Step 3: Enable YouTube Data API
1. In the left sidebar, click **"APIs & Services"**
2. Click **"Library"**
3. Search for: **"YouTube Data API v3"**
4. Click on it
5. Click **"ENABLE"**

### Step 4: Create Credentials
1. Go back to **"APIs & Services"** → **"Credentials"**
2. Click **"+ CREATE CREDENTIALS"** at the top
3. Choose: **"API Key"**
4. A key will appear - **COPY IT** (you'll need this)
5. Click **"Restrict Key"** to add restrictions (optional)

### Step 5: Save Your YouTube API Key
```
YOUTUBE_API_KEY = "your_key_here"
```

**Keep this key safe!** You'll use it in the Python script.

---

## Part 2: Spotify API Setup

### Step 1: Go to Spotify Developer Dashboard
1. Visit: **https://developer.spotify.com/dashboard**
2. Click **"Log In"** (or create Spotify account if needed)
3. Accept terms and create account if first time

### Step 2: Create an Application
1. Click **"Create an App"** button
2. Name your app: `Tour-Guide-System`
3. Check the terms checkbox
4. Click **"Create"**

### Step 3: Get Your Credentials
You'll see:
- **Client ID**
- **Client Secret**

**COPY BOTH** (you'll need these)

### Step 4: Save Your Spotify Credentials
```
SPOTIFY_CLIENT_ID = "your_client_id_here"
SPOTIFY_CLIENT_SECRET = "your_client_secret_here"
```

**Keep these secret!** Never share them publicly.

---

## Step 3: Test Your Keys

Once you have all three:
1. YouTube API Key
2. Spotify Client ID
3. Spotify Client Secret

You'll use them in the Python script we're about to create.

---

## Common Issues

### YouTube API Key Issues
**Problem:** "quotaExceeded"
- **Solution:** You have a free quota. Don't worry, it resets daily.

**Problem:** "invalid API key"
- **Solution:** Make sure you copied the key correctly. Check for spaces or typos.

### Spotify Issues
**Problem:** "invalid credentials"
- **Solution:** Make sure Client ID and Secret are correct and not swapped.

**Problem:** "unauthorized"
- **Solution:** Make sure you're using Base64 encoding (the script does this).

---

## Security Notes

⚠️ **Important:**
- Never commit your API keys to Git
- Never share your Spotify Client Secret
- Create a `.env` file to store keys locally
- The script will use environment variables for safety

---

## What's Next

Once you have your API keys:

1. Create a file: `~/.tour_guide_env`
2. Add your keys:
   ```
   YOUTUBE_API_KEY=your_youtube_key_here
   SPOTIFY_CLIENT_ID=your_spotify_id_here
   SPOTIFY_CLIENT_SECRET=your_spotify_secret_here
   ```

3. We'll create a Python script that uses these keys
4. Script will fetch real videos and songs for the Ramat Hasharon → Tel Aviv route
5. You'll get actual clickable links!

---

## Timeline

- **YouTube Setup:** 5 minutes
- **Spotify Setup:** 5 minutes
- **Total:** 10 minutes to have all keys ready

Then the Python script will handle the rest automatically! 🚀

---

## Questions?

If you get stuck:
1. YouTube: Check https://developers.google.com/youtube/v3
2. Spotify: Check https://developer.spotify.com/documentation/web-api

But the steps above should be all you need!

---

**Ready?** Once you have your 3 credentials, let me know and I'll create the working Python script! 🎬🎵
