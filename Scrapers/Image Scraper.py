import os
import json
import pandas as pd
import requests
import re
from datetime import datetime

IMAGE_CACHE_DIR = "static/cached_images"  # Ensure images are stored here
IMAGE_CACHE_FILE = "image_cache.json"
ERROR_LOG_FILE = "image_download_errors.log"

# Ensure the image cache directory exists
os.makedirs(IMAGE_CACHE_DIR, exist_ok=True)

def sanitize_filename(game_name):
    """Sanitize game name to create a valid filename."""
    return re.sub(r'[<>:"/\\|?*]', '', game_name).replace(' ', '_') + ".jpg"

def save_json(filename, data):
    """Save JSON data safely."""
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

def log_error(message):
    """Log errors to a file with a timestamp."""
    with open(ERROR_LOG_FILE, "a") as log_file:
        log_file.write(f"{datetime.now()} - {message}\n")

def download_image(game_name, image_url):
    """Download an image from the given URL and save it locally."""
    try:
        filename = sanitize_filename(game_name)
        local_path = os.path.join(IMAGE_CACHE_DIR, filename).replace("\\", "/")  # Standardize path

        print(f"⬇️ Downloading: {game_name} from {image_url}...")

        response = requests.get(image_url, stream=True, timeout=10)

        if response.status_code == 200:
            with open(local_path, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            print(f"✅ Saved: {local_path}")
            return f"/static/cached_images/{filename}"  # Path Flask will use
        else:
            error_message = f"⚠️ Failed to download {image_url} (Status: {response.status_code})"
            print(error_message)
            log_error(f"{game_name}: {error_message}")
            return None
    except Exception as e:
        error_message = f"⚠️ Error downloading {image_url}: {e}"
        print(error_message)
        log_error(f"{game_name}: {error_message}")
        return None

# Load game data from Excel
df = pd.read_excel("games.xlsx", header=None, names=["Game Name", "Game Code", "Image URL"])

# Load existing image cache
if os.path.exists(IMAGE_CACHE_FILE):
    with open(IMAGE_CACHE_FILE, "r") as file:
        image_cache = json.load(file)
else:
    image_cache = {}

# Clear the error log at the start
open(ERROR_LOG_FILE, "w").close()

# Download and cache images
for _, row in df.iterrows():
    game_name = row["Game Name"]
    image_url = row["Image URL"]

    # Skip if already cached and file exists
    if game_name in image_cache and os.path.exists(IMAGE_CACHE_DIR + "/" + os.path.basename(image_cache[game_name])):
        print(f"🔄 Skipping (Already Cached): {game_name}")
        continue

    local_path = download_image(game_name, image_url)
    if local_path:
        image_cache[game_name] = local_path

# Save the updated cache
save_json(IMAGE_CACHE_FILE, image_cache)

print("\n✅ All images cached successfully!")
print(f"📂 Error log saved to {ERROR_LOG_FILE} (Check for any issues)")
