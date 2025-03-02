
# Boise LAN Free Games

BoiseLANCodeGenerator is a Flask-based web application designed for Boise LAN event participants. It allows users to enter their Discord name and receive a selection of six games, each with an image, title, and synopsis. Users can then select one or two games, which are sent to them via the Discord API. The application verifies whether the user is part of the specified Discord server before proceeding. Once the game selection is completed, the page refreshes to ensure privacy for the next user.

This project includes web scraping tools that collect and cache game images and synopsis data from external sources, which are later used for the web app.


## Features

- Game Scraping & Caching: Uses scrapers in the Scrapers folder to fetch and locally store game images and synopsis data.

- Flask Web Application: Provides a simple interface for users to interact with.

- Discord API Integration: Verifies users and sends game selections directly via Discord.

- Privacy Protection: Refreshes the page after each submission.

- Pre-cached Data: Ensures a smooth user experience by storing game data locally.


## Installation

Prerequisites

Ensure you have the following installed on your system:

    Python (>= 3.8)
    Pip (Python package manager)
    Virtual environment (recommended)
    A Discord bot token (for API integration)
    Necessary Python dependencies

Setup Instructions

Clone the Repository

    git clone https://github.com/AlphaIOmega/BoiseLANCodeGenerator.git
    cd BoiseLANCodeGenerator

Install Dependencies

    pip install -r requirements.txt

Modify app.py with your Discord bot token and Server ID:

    DISCORD_BOT_TOKEN=your_discord_bot_token
    DISCORD_GUILD_ID=your_guild_id

Run the Scrapers

    python Scrapers/image_scraper.py
    python Scrapers/synopsis_scraper.py

Start the Flask Application

    python app.py

Access the Web App Open your browser and go to:

    http://127.0.0.1:5000/


## Usage/Examples

    Enter Your Discord Username
        Input your Discord name in the web interface.

    View Game Suggestions
        The app will display six games, each with an image, title, and synopsis.

    Select One or Two Games
        Choose one or two games from the selection.

    Verify Discord Membership
        The app checks if you belong to the specified Discord server.

    Receive a Discord Message
        If valid, your selected games will be sent to you via Discord.

    Page Refresh for Privacy
        The app automatically refreshes the page after submission.


## Project Structure


    BoiseLANCodeGenerator/
        Scrapers/               # Contains scrapers for collecting game data
    
            image_scraper.py    # Scrapes and caches game images
            synopsis_scraper.py # Scrapes and caches game synopsis data

        static/                 # Stores static files (images, CSS, etc.)

        templates/              # HTML templates for the web app
            index.html          # Main user interface

        app.py                  # Flask application logic
        discord_api.py          # Handles Discord API integration
        requirements.txt        # Python dependencies
        README.md               # Documentation (this file)



## Dependencies

    Flask
    Requests
    BeautifulSoup (for web scraping)
    Discord API (via discord.py)
    Pandas (for data management)

To install all dependencies:

    pip install -r requirements.txt


## Discord Bot Setup

    Step 1: Create a Discord Bot
        - Go to the Discord Developer Portal.
        - Click "New Application", name it, and go to "Bot" (left menu).
        - Click "Add Bot", then "Reset Token" and copy the token.

    Step 2: Enable Bot Permissions
        - Under "Privileged Gateway Intents", enable:
            - Presence Intent
            - Server Members Intent
            - Message Content Intent
        - Save changes.

    Step 3: Invite the Bot to Your Server
        - Go to OAuth2 > URL Generator.
        - Under Scopes, select:
            - bot
        - Under Bot Permissions, select:
            - Send Messages
            - Read Messages
            - View Channels
            - Copy the generated URL and invite the bot to your server.



## Authors

- ChatGPT


## Contributing

AlphaIOmega
