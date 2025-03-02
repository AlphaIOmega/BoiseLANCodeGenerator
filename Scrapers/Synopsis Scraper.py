import pandas as pd
import json
import requests
from bs4 import BeautifulSoup

SYNOPSIS_CACHE_FILE = "synopsis_cache.json"

def save_json(filename, data):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

def get_steam_synopsis(game_name):
    search_url = f"https://store.steampowered.com/search/?term={game_name.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        search_page = requests.get(search_url, headers=headers, timeout=5)
        soup = BeautifulSoup(search_page.text, "html.parser")

        result = soup.find("a", class_="search_result_row")
        if not result:
            return "No synopsis found."

        game_url = result["href"]
        game_page = requests.get(game_url, headers=headers, timeout=5)
        game_soup = BeautifulSoup(game_page.text, "html.parser")
        synopsis = game_soup.find("div", class_="game_description_snippet")

        return synopsis.text.strip() if synopsis else "No synopsis available."
    except:
        return "No synopsis available."

df = pd.read_excel("games.xlsx", header=None, names=["Game Name", "Game Code", "Game Image"])
synopsis_cache = {}

for game_name in df["Game Name"]:
    synopsis_cache[game_name] = get_steam_synopsis(game_name)

save_json(SYNOPSIS_CACHE_FILE, synopsis_cache)
print("✅ Synopses saved to synopsis_cache.json")
