import yt_dlp
import pandas as pd

# YouTube channel URL
CHANNEL_URL = "https://www.youtube.com/channel/UCh9nVJoWXmFb7sLApWGcLPQ/videos"

# yt-dlp options
ydl_opts = {
    "extract_flat": False,         # Extract full metadata (not just playlist info)
    "skip_download": True,         # Don't download videos
    "quiet": True,                 # Suppress console noise
    "ignoreerrors": True,          # Skip videos that error out
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(CHANNEL_URL, download=False)

# If the channel URL gives a playlist-like structure
videos = info.get("entries", [info])

# Extract required fields
data = []
for v in videos:
    if not v:
        continue
    data.append({
        "Video ID": v.get("id"),
        "Title": v.get("title"),
        "Channel": v.get("channel"),
        "Upload Date": v.get("upload_date"),
        "Views": v.get("view_count"),
        "Likes": v.get("like_count"),
        "Comments": v.get("comment_count"),
        "Duration (min)": round((v.get("duration") or 0) / 60, 2),
        "Has Subtitles": bool(v.get("subtitles")),
        "Subtitle Languages": list(v.get("subtitles", {}).keys()) if v.get("subtitles") else None,
        "Highest Quality": f"{v.get('height', '')}p" if v.get("height") else None,
        "URL": v.get("webpage_url"),
    })

# Convert to DataFrame
df = pd.DataFrame(data)

# Sort by upload date (descending)
df.sort_values(by="Upload Date", ascending=False, inplace=True)

print(df.head())
