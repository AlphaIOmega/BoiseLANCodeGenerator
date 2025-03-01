🚀 Step-by-Step Guide: Setting Up a Discord Bot for Your Server

Follow these steps to create a Discord bot, add it to your server, and obtain the bot token required for your Python app.
🔹 Step 1: Create a New Discord Bot

    Go to the Discord Developer Portal:
    👉 https://discord.com/developers/applications

    Create a New Application
        Click "New Application" (top-right).
        Give it a name (e.g., GameCodeBot).
        Click "Create".

    Go to the "Bot" Section
        On the left sidebar, click "Bot".
        Click "Add Bot".
        Click "Yes, do it!" to confirm.

    Set Bot Username & Avatar (Optional)
        You can change the bot's name and upload an avatar here.

🔹 Step 2: Get the Bot Token

    Under the "Bot" tab, scroll down to "Token".
    Click "Reset Token" → "Copy".
    Save this bot token somewhere safe (you'll use it in app.py).

🔹 Step 3: Enable Permissions for the Bot

    In the "Bot" tab, scroll down to "Privileged Gateway Intents".
    Enable:
        ✅ "Presence Intent"
        ✅ "Server Members Intent"
        ✅ "Message Content Intent"
    Click Save Changes.

🔹 Step 4: Generate an Invite Link for Your Bot

    Go to OAuth2 → "URL Generator" (left menu).
    Under SCOPES, select:
        ✅ bot
    Under BOT PERMISSIONS, select:
        ✅ "Send Messages"
        ✅ "Read Messages"
        ✅ "View Channels"
    Copy the generated URL (bottom of the page).
    Open the URL in a new tab and add the bot to your Discord server.

🔹 Step 5: Get Your Discord Server & Channel ID
1. Enable Developer Mode

    Open Discord.
    Go to User Settings → Advanced.
    Enable Developer Mode.

2. Get Your Server ID

    Right-click your server name (in Discord's left panel).
    Click "Copy ID".
    Save it as DISCORD_GUILD_ID.

3. Get Your Channel ID (Optional, If Sending to a Specific Channel)

    Right-click the text channel where the bot should send messages.
    Click "Copy ID".
    Save it as DISCORD_CHANNEL_ID.

🔹 Step 6: Add Your Bot Token & Server ID to app.py

Once you've created and added the bot, update your app.py with the bot token and server ID:

DISCORD_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
DISCORD_GUILD_ID = 123456789012345678  # Replace with your actual Server ID
DISCORD_CHANNEL_ID = 123456789012345678  # (Optional) Replace with your actual Channel ID
