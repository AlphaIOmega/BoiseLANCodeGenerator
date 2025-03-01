🎮 Game Code Redeemer - Full README
📌 Project Overview

The Game Code Redeemer is a Flask + Discord bot application that allows users to redeem game codes securely via a Discord bot. Users enter their Discord username on the website, request a game, and receive the game code via a Discord DM. Users can also reject up to 3 games, after which the last rejected game code is automatically assigned to them.

📌 Features

✅ Game Code Redeemer Web App (HTML + Flask backend)

✅ Discord bot integration (Sends game codes via DM)

✅ User verification (Checks if the user is in the server)

✅ Reject up to 3 games (Then auto-assigns last rejected code)

✅ Game codes are hidden on the webpage (Sent via DM only)

✅ Tracks user attempts (Prevents multiple redemptions)

✅ Auto-refresh the page after redemption or reset


📌 Installation Instructions

1️⃣ Prerequisites

Install Python 3.8+
    
Install pip (Python package manager)
    
A Discord bot token (See setup below)
    
A Discord server where the bot will operate
    
An Excel file (games.xlsx) containing game data.
    

2️⃣ Install Required Dependencies

    pip install flask pandas discord.py asyncio


3️⃣ Setup the games.xlsx File

Create an Excel file named games.xlsx in the project folder with three columns:

Game Name	Game Code	Game Image Link

Game 1	ABC123	https://example.com/game1.jpg

Game 2	XYZ789	https://example.com/game2.jpg


📌 Ensure the first row contains headers exactly as shown above!


4️⃣ Configure Your Discord Bot

🔹 Step 1: Create a Discord Bot

Go to the Discord Developer Portal.
    
Click "New Application", name it, and go to "Bot" (left menu).
    
Click "Add Bot", then "Reset Token" and copy the token.
    

🔹 Step 2: Enable Bot Permissions
   
Under "Privileged Gateway Intents", enable:
        
✅ Presence Intent
       
✅ Server Members Intent
       
✅ Message Content Intent
    
Save changes.


🔹 Step 3: Invite the Bot to Your Server

 Go to OAuth2 > URL Generator.
    
Under Scopes, select:
    
 ✅ bot
        
 Under Bot Permissions, select:
    
✅ Send Messages
        
✅ Read Messages
        
✅ View Channels
        
Copy the generated URL and invite the bot to your server.
    

5️⃣ Configure app.py

Open app.py and update:

    DISCORD_BOT_TOKEN = "YOUR_DISCORD_BOT_TOKEN"

    DISCORD_GUILD_ID = 123456789012345678  # Replace with your actual Discord server ID


📌 Running the Application


1️⃣ Start the Flask App

    python app.py

🔹 Flask should now be running on http://127.0.0.1:5000/

2️⃣ How to Use

Open http://127.0.0.1:5000/ in your browser.
    
Enter your Discord username.
    
Click "Get New Game" to request a game.
    
The bot sends the game code via DM (not on the webpage).
    
If you don’t like the game, click "I Don’t Want This Game" (up to 3 times).
    
After 3 rejections, the last rejected game is automatically assigned.
    
To start over, click "New User".
    

📌 API Endpoints

🔹 /get_game (POST)

📌 Requests a new game.

Request Example:

    curl -X POST -d "discord_name=TestUser" http://127.0.0.1:5000/get_game

Response Example:

    {
        "name": "Game 1",
        "image": "https://example.com/game1.jpg",
        "discord_name": "TestUser"
    }

🔹 /accept_game (POST)

📌 Accepts the current game and sends the code via DM.

Request Example:

    curl -X POST -d "discord_name=TestUser" http://127.0.0.1:5000/accept_game

Response Example:

    {
        "success": "Game redeemed and sent to Discord!"
    }

🔹 /reject_game (POST)

📌 Rejects the current game (max 3 times).

Request Example:

    curl -X POST -d "discord_name=TestUser" http://127.0.0.1:5000/reject_game

Response Example:

    {
        "success": "Game rejected. You may request another game."
    }

🔹 /reset_user (POST)

📌 Resets the user so they can redeem another game.
Request Example:

    curl -X POST -d "discord_name=TestUser" http://127.0.0.1:5000/reset_user

Response Example:

    {
        "success": "User reset. They can now request a game again."
    }

📌 Troubleshooting

1️⃣ Flask Is Not Running

✅ Fix: Ensure you are in the correct directory and try:

    python app.py

2️⃣ Bot Is Not Sending DMs

✅ Fix: Ensure:

The bot is in your server.
You have enabled "Server Members Intent" in Discord Developer Portal.
The bot has permission to send DMs.

3️⃣ Game Codes Not Loading

✅ Fix:

Ensure games.xlsx exists in the project folder.
The first row should be:

| Game Name | Game Code | Game Image Link |

📌 License

📜 MIT License - Feel free to modify and improve this project!

📌 Contributors

👤 AlphaIOmega - Developer
