# YouTube Channel Scraper

A Python script to scrape metadata from YouTube channels using `yt-dlp` and `pandas`. This tool extracts video details such as titles, views, likes, comments, durations, and more.

## Features

- Extract video metadata from a YouTube channel.
- Support for multiple videos with multithreading (in `main2.py`).
- Output data to CSV format.
- Log failed video extractions.

## Requirements

Install the dependencies using:

```bash
pip install -r requirements.txt
```

Dependencies:
- `yt-dlp`: For downloading video information.
- `pandas`: For data manipulation (used in `main.py`).
- `tqdm`: For progress bars (used in `main2.py`).
- Other standard libraries: `csv`, `threading`, `concurrent.futures`.

## Usage

### main.py
Basic scraper that extracts metadata for videos in a channel and displays the top results.

```bash
python main.py
```

This script uses a hardcoded channel URL and prints the DataFrame to console.

### main2.py
Advanced scraper with multithreading for processing multiple videos efficiently.

```bash
python main2.py
```

This script:
- Fetches the list of videos from the channel.
- Processes them in parallel using threads.
- Saves the data to `channel_data.csv`.
- Logs any failed extractions to `failed_videos.txt`.

## Configuration

- Update the `CHANNEL_URL` in the scripts to target a different channel.
- Adjust `max_workers` in `main2.py` for threading (default: 10).

## Output

- `channel_data.csv`: Contains the scraped video metadata.
- `failed_videos.txt`: List of URLs that failed to process.

## Notes

- Ensure you comply with YouTube's Terms of Service.
- Rate limiting may apply; adjust thread counts if needed.
- Data files are tracked in Git; exclude them in `.gitignore` if they contain sensitive data.

## License

MIT License. See LICENSE file for details.