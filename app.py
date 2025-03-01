import os
import json
import discord
import pandas as pd
import random
import asyncio
import threading
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Discord Bot Setup
DISCORD_BOT_TOKEN = "ITSASECRETSSSHHHHHH"
DISCORD_GUILD_ID = 123456789  # Replace with your Discord server ID

# Storage Files
SHOWN_GAMES_FILE = "shown_games.json"
USER_ATTEMPTS_FILE = "user_attempts.json"

# Initialize Discord Client
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

async def check_user_in_server(username):
    """Check if a user exists in the Discord server."""
    await client.wait_until_ready()
    guild = discord.utils.get(client.guilds, id=DISCORD_GUILD_ID)
    return guild.get_member_named(username) is not None

async def send_discord_dm(username, message):
    """Send a DM to a user in the Discord server."""
    await client.wait_until_ready()
    guild = discord.utils.get(client.guilds, id=DISCORD_GUILD_ID)
    member = guild.get_member_named(username)

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

# Save Data to JSON
def save_json(filename, data):
    with open(filename, "w") as file:
        json.dump(data, file)

# Load Stored Data
shown_games = load_json(SHOWN_GAMES_FILE)
user_attempts = load_json(USER_ATTEMPTS_FILE)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/get_game', methods=["POST"])
def get_game():
    try:
        discord_name = request.form.get("discord_name")

        if not discord_name:
            print("❌ Error: Missing Discord name in request.")
            return jsonify({"error": "Please enter a Discord name before requesting a game."}), 400

        # Check if user exists in the Discord server
        future = asyncio.run_coroutine_threadsafe(check_user_in_server(discord_name), bot_loop)
        user_exists = future.result()

        if not user_exists:
            print(f"❌ Error: User '{discord_name}' not found in server.")
            return jsonify({"error": f"User '{discord_name}' not found in the server. Please check your username and try again."}), 400

        # Ensure user_attempts entry exists
        if discord_name not in user_attempts:
            user_attempts[discord_name] = {"attempts": 0, "redeemed": False, "last_rejected_game": None}

        attempts = user_attempts[discord_name]

        if attempts["attempts"] >= 3:
            last_game = attempts.get("last_rejected_game")
            if last_game:
                print(f"✅ User {discord_name} reached max rejections. Auto-sending last rejected game.")

                # Send last rejected game via DM
                future = asyncio.run_coroutine_threadsafe(
                    send_discord_dm(discord_name, f"🎮 **You have reached max rejections!**\n🔢 **Game Code:** `{last_game}`"),
                    bot_loop
                )
                future.result()

                # Mark user as redeemed and prevent further requests
                user_attempts[discord_name]["redeemed"] = True
                save_json(USER_ATTEMPTS_FILE, user_attempts)

                return jsonify({"error": "You have reached the maximum of 3 rejections. The last rejected game code has been sent to your Discord DM."}), 400
            else:
                return jsonify({"error": "You have reached the maximum of 3 rejections, but no previous game was stored."}), 400

        shown_game_codes = shown_games.get("codes", [])
        available_games = df[~df["Game Code"].isin(shown_game_codes)]
        if available_games.empty:
            return jsonify({"error": "All games have been displayed. No more games available."}), 400

        # Select a random game
        game = available_games.sample(n=1).iloc[0]

        # Save user's attempt and store game code
        user_attempts[discord_name]["current_game_code"] = str(game["Game Code"])
        save_json(USER_ATTEMPTS_FILE, user_attempts)

        return jsonify({
            "name": str(game["Game Name"]),
            "image": str(game["Game Image Link"]),
            "discord_name": discord_name
        })

    except Exception as e:
        print(f"❌ Error in /get_game: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

@app.route('/reset_user', methods=["POST"])
def reset_user():
    try:
        discord_name = request.form.get("discord_name")

        if not discord_name:
            print("❌ Error: No Discord name provided for reset.")
            return jsonify({"error": "Invalid request. Please enter a Discord name."}), 400

        if discord_name in user_attempts:
            del user_attempts[discord_name]
            save_json(USER_ATTEMPTS_FILE, user_attempts)
            print(f"✅ User {discord_name} has been reset.")
            return jsonify({"success": "User reset. They can now request a game again."})
        else:
            print(f"❌ Error: User {discord_name} not found in records.")
            return jsonify({"error": "User not found. No reset needed."}), 400

    except Exception as e:
        print(f"❌ Error in /reset_user: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

@app.route('/accept_game', methods=["POST"])
def accept_game():
    try:
        discord_name = request.form.get("discord_name")

        if not discord_name:
            print("❌ Error: Missing Discord name.")
            return jsonify({"error": "Invalid request. Discord name is required."}), 400

        if discord_name not in user_attempts or "current_game_code" not in user_attempts[discord_name]:
            print(f"❌ Error: No game stored for {discord_name}.")
            return jsonify({"error": "No game to accept. Please request a new game first."}), 400

        game_code = user_attempts[discord_name]["current_game_code"]

        # Store the game as redeemed
        shown_games.setdefault("codes", []).append(game_code)
        save_json(SHOWN_GAMES_FILE, shown_games)

        # Mark user as redeemed
        user_attempts[discord_name] = {"attempts": 3, "redeemed": True}
        save_json(USER_ATTEMPTS_FILE, user_attempts)

        # Debugging log
        print(f"✅ Game accepted by {discord_name}. Sending DM...")

        # Send the DM using the bot's event loop
        future = asyncio.run_coroutine_threadsafe(
            send_discord_dm(discord_name, f"🎮 **You have redeemed a game!**\n🔢 **Game Code:** `{game_code}`"),
            bot_loop
        )
        result = future.result()

        if result == "User Not Found":
            return jsonify({"error": f"User '{discord_name}' not found in the server. Please check your username and try again."}), 400

        return jsonify({"success": "Game redeemed and sent to Discord!"})

    except Exception as e:
        print(f"❌ Error in /accept_game: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

@app.route('/reject_game', methods=["POST"])
def reject_game():
    try:
        discord_name = request.form.get("discord_name")

        if not discord_name:
            print("❌ Error: No Discord name provided for rejection.")
            return jsonify({"error": "Invalid request. Please enter a Discord name."}), 400

        if discord_name not in user_attempts or "current_game_code" not in user_attempts[discord_name]:
            return jsonify({"error": "No game to reject. Please request a new game first."}), 400

        attempts = user_attempts[discord_name]

        if attempts["attempts"] >= 3:
            return jsonify({"error": "You have already rejected 3 games."}), 400

        # Store the last rejected game code
        attempts["last_rejected_game"] = user_attempts[discord_name]["current_game_code"]
        attempts["attempts"] += 1
        user_attempts[discord_name] = attempts
        save_json(USER_ATTEMPTS_FILE, user_attempts)

        print(f"✅ {discord_name} rejected a game. Total rejections: {attempts['attempts']}")

        return jsonify({"success": "Game rejected. You may request another game."})

    except Exception as e:
        print(f"❌ Error in /reject_game: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

def run_bot():
    global bot_loop
    bot_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(bot_loop)
    bot_loop.run_until_complete(client.start(DISCORD_BOT_TOKEN))

if __name__ == "__main__":
    discord_thread = threading.Thread(target=run_bot, daemon=True)
    discord_thread.start()
    app.run(debug=True)
