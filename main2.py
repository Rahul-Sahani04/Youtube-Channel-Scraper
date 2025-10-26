import yt_dlp
import csv
import sys
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

CHANNEL_URL = 'https://www.youtube.com/channel/UCh9nVJoWXmFb7sLApWGcLPQ/videos'
OUTPUT_FILE = 'channel_data.csv'
ERROR_FILE = 'failed_videos.txt'

# --- 1. Get a list of all video URLs first ---
print(f"Fetching video list from {CHANNEL_URL}...")
ydl_opts_list = {
    'quiet': True,
    'extract_flat': 'in_playlist', # Only get the video list, not details
    'ignoreerrors': True,
    # 'skip_download': True, # This is redundant with extract_flat
}

video_entries = []
try:
    with yt_dlp.YoutubeDL(ydl_opts_list) as ydl:
        info = ydl.extract_info(CHANNEL_URL, download=False)
        if 'entries' in info:
            video_entries = info['entries']
            print(f"Found {len(video_entries)} videos.")
        else:
            print("Error: Could not find video entries.")
            sys.exit(1)
except Exception as e:
    print(f"Fatal error fetching video list: {e}")
    sys.exit(1)

# --- 2. Process videos with multithreading ---
ydl_opts_video = {
    'quiet': True,
    'ignoreerrors': True,
}

# Define the CSV header
header = [
    'Video ID', 'Title', 'Channel', 'Upload Date', 'Views', 'Likes', 
    'Comments', 'Duration (min)', 'Has Subtitles?', 'Subtitle Languages', 
    'Highest Quality', 'URL'
]

# Thread-safe locks for file writing
csv_lock = threading.Lock()
error_lock = threading.Lock()

def process_video(entry):
    """Process a single video and return the row data or error info"""
    video_url = entry.get('url')
    if not video_url:
        return None, None
    
    try:
        # Each thread creates its own YoutubeDL instance (CRITICAL)
        with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
            video_info = ydl.extract_info(video_url, download=False)

        # --- Custom Data Formatting ---
        subtitles = video_info.get('subtitles', {})
        has_subs = "Yes" if subtitles else "No"
        sub_langs = ", ".join(subtitles.keys())
        
        # Convert duration from seconds to minutes (e.g., 1.5)
        duration_min = round(video_info.get('duration', 0) / 60, 2)

        # Return the formatted row data
        row = [
            video_info.get('id'),
            video_info.get('title'),
            video_info.get('channel'),
            video_info.get('upload_date'),
            video_info.get('view_count'),
            video_info.get('like_count'),
            video_info.get('comment_count'),
            duration_min,
            has_subs,
            sub_langs,
            video_info.get('resolution'),
            video_info.get('webpage_url')
        ]
        return row, None

    except Exception as e:
        return None, (video_url, str(e))

# Open files for writing
with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as csvfile, \
     open(ERROR_FILE, 'w', encoding='utf-8') as errfile:
    
    writer = csv.writer(csvfile)
    writer.writerow(header)

    # Adjust max_workers based on network speed and rate limiting
    # Start with 10; if you get errors, lower it. If not, try 15-20.
    max_workers = 10 
    print(f"Processing videos with {max_workers} threads...")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_entry = {executor.submit(process_video, entry): entry for entry in video_entries}
        
        # Process completed tasks with progress bar
        for future in tqdm(as_completed(future_to_entry), total=len(video_entries), desc="Processing videos"):
            row, error = future.result()
            
            if row:
                # Thread-safe CSV writing
                with csv_lock:
                    writer.writerow(row)
            elif error:
                # Thread-safe error logging
                video_url, error_msg = error
                with error_lock:
                    # *** REFINEMENT: Use tqdm.write() to avoid messing up the progress bar ***
                    tqdm.write(f"Failed to process {video_url}: {error_msg}")
                    errfile.write(f"{video_url}\n")

print(f"\nDone! Data saved to {OUTPUT_FILE}")
print(f"Failed videos (if any) logged in {ERROR_FILE}")