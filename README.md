*Disclaimer: This tool is for personal archival only. It is not intended to spam or burden Tenor servers.*

Toast: Discord bot for auto-uploading Tenor gifs to Discord CDN to save favorited gifs.

Requirements:
A Discord Application
Python
Pip

Clone the repository and run following command. Preferably in a venv.
`pip install -r requirements.txt`

Put your user ID (to send the initial bot message via /say) and your Discord app token in a `.env` file in the following format
DISCORD_TOKEN="123456789abcdefg"
MOD="123456789"

Run `bot.py` and send a message with the /say command. 

When replied with a Tenor gif, Toast will upload the gif onto Discord servers and send it in the same channel.
