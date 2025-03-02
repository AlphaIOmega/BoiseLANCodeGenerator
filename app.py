import os
import json
import discord
import pandas as pd
import random
import asyncio
import threading
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder="templates", static_folder="static")

# Discord Bot Setup
DISCORD_BOT_TOKEN = "INSERT TOKEN HERE"
DISCORD_GUILD_ID = 1234567890987654321  # Replace with your actual Discord server ID

# Storage Files
SHOWN_GAMES_FILE = "shown_games.json"
USER_ATTEMPTS_FILE = "user_attempts.json"
SYNOPSIS_CACHE_FILE = "synopsis_cache.json"
IMAGE_CACHE_FILE = "image_cache.json"

# Initialize Discord Client
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

async def check_user_in_server(username):
    """Check if a user exists in the Discord server."""
    await client.wait_until_ready()
    guild = discord.utils.get(client.guilds, id=DISCORD_GUILD_ID)
    return guild.get_member_named(username.lower()) is not None

async def send_discord_dm(username, message):
    """Send a DM to a user in the Discord server."""
    await client.wait_until_ready()
    guild = discord.utils.get(client.guilds, id=DISCORD_GUILD_ID)
    member = guild.get_member_named(username.lower())

    if not member:
        print(f"❌ Error: User {username} not found in the server.")
        return "User Not Found"

    try:
        await member.send(message)
        print(f"📨 DM sent to {username}")
        return "Success"
    except discord.Forbidden:
        print(f"❌ Error: Cannot send DM to {username} (DMs disabled).")
        return "DMs Disabled"
    except discord.HTTPException as e:
        print(f"❌ Discord API Error: {e}")
        return "API Error"

# Load Excel File
try:
    df = pd.read_excel("games.xlsx", header=None)
    df.columns = ["Game Name", "Game Code", "Game Image Link"]
    if df.empty:
        print("Warning: games.xlsx is empty!")
except Exception as e:
    print(f"Error loading games.xlsx: {e}")
    df = None  

# Load Stored Data
def load_json(filename):
    if os.path.exists(filename):
        with open(filename, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}
    return {}

def save_json(filename, data):
    """Save JSON data safely."""
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

# Load Cached Synopses & Images
synopsis_cache = load_json(SYNOPSIS_CACHE_FILE)
image_cache = load_json(IMAGE_CACHE_FILE)
shown_games = load_json(SHOWN_GAMES_FILE)
user_attempts = load_json(USER_ATTEMPTS_FILE)

# ✅ Fetch Steam Synopsis with Local Cache
def get_steam_synopsis(game_name):
    """Retrieve cached synopsis or fetch from Steam."""
    if game_name in synopsis_cache:
        return synopsis_cache[game_name]

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

        result_text = synopsis.text.strip() if synopsis else "No synopsis available."
        synopsis_cache[game_name] = result_text  # Save to cache
        save_json(SYNOPSIS_CACHE_FILE, synopsis_cache)

        return result_text
    except Exception as e:
        print(f"Error fetching Steam synopsis: {e}")
        return "No synopsis available."

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/get_games', methods=["POST"])
def get_games():
    try:
        discord_name = request.form.get("discord_name").strip().lower()

        if not discord_name:
            return jsonify({"error": "Please enter a Discord username before requesting games."}), 400

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        user_exists = loop.run_until_complete(check_user_in_server(discord_name))

        if not user_exists:
            return jsonify({"error": f"User '{discord_name}' not found in the server."}), 400

        if discord_name in user_attempts and user_attempts[discord_name].get("redeemed", False):
            return jsonify({"error": "You have already redeemed games and cannot request more."}), 400

        redeemed_codes = set(shown_games.get("codes", []))
        available_games = df[~df["Game Code"].isin(redeemed_codes)]

        if available_games.empty:
            return jsonify({"error": "No more available games."}), 400

        games = available_games.sample(n=min(6, len(available_games)))

        game_list = []
        for _, row in games.iterrows():
            game_name = str(row["Game Name"])
            game_code = str(row["Game Code"])

            cached_image_path = image_cache.get(game_name)

            if cached_image_path:
                image_path = cached_image_path
            else:
                image_path = str(row["Game Image Link"])

            synopsis = get_steam_synopsis(game_name)
            game_list.append({
                "name": game_name,
                "image": image_path,
                "code": game_code,
                "synopsis": synopsis
            })

        return jsonify({"games": game_list})

    except Exception as e:
        print(f"❌ Error in /get_games: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

@app.route('/accept_games', methods=["POST"])
def accept_games():
    try:
        discord_name = request.form.get("discord_name")
        selected_games = request.form.get("games")

        if not discord_name or not selected_games:
            return jsonify({"error": "Invalid request. Discord name and game selection are required."}), 400

        selected_games = selected_games.split(",")

        if len(selected_games) > 2:
            return jsonify({"error": "You can only select up to 2 games."}), 400

        shown_games.setdefault("codes", []).extend(selected_games)
        save_json(SHOWN_GAMES_FILE, shown_games)

        user_attempts[discord_name] = {"redeemed": True}
        save_json(USER_ATTEMPTS_FILE, user_attempts)

        message = "🎮 **You have redeemed the following games:**\n" + "\n".join(
            [f"🔢 **{game}**" for game in selected_games]
        )

        future = asyncio.run_coroutine_threadsafe(send_discord_dm(discord_name, message), client.loop)
        result = future.result()

        if result == "User Not Found":
            return jsonify({"error": f"User '{discord_name}' not found in the server."}), 400

        return jsonify({"success": "Games redeemed and sent to Discord!"})

    except Exception as e:
        print(f"❌ Error in /accept_games: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

if __name__ == "__main__":
    discord_thread = threading.Thread(target=lambda: asyncio.run(client.start(DISCORD_BOT_TOKEN)), daemon=True)
    discord_thread.start()
    app.run(debug=True)
