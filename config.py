# ============================================================
#AUTHOR : MISTER STARK
# ============================================================

import os
from dotenv import load_dotenv

load_dotenv()

# Required configurations
API_ID = int(os.getenv("API_ID", 0000000)) #from www.telegram.org
API_HASH = os.getenv("API_HASH", "YOUR_API_HASH") #from www.telegram.org
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOU_BOT_TOKEN") #from #Botfather
MONGO_URI = os.getenv("MONGO_URI", "YOUR_MONGO_URO") # from mongo.db
DB_NAME = os.getenv("DB_NAME", "Cluster0")

OWNER_ID = int(os.getenv("OWNER_ID", 0000000))
BOT_USERNAME = os.getenv("BOT_USERNAME", "YOUR_BOT_USERNAME") # without @

SUPPORT_GROUP = os.getenv("SUPPORT_GROUP", "https://t.me/CarelessxWorld") #YOUR SUPPORT GROUP LINK
UPDATE_CHANNEL = os.getenv("UPDATE_CHANNEL", "https://t.me/+wQonHdyvZh5mZWM1") #YOUR UPDATE CHANELL LINK
START_IMAGE = os.getenv("START_IMAGE", "https://files.catbox.moe/v8vvxr.jpg") #YOUR START IMAGE LINK GENERATE FROM CATBOX


AI_API = os.getenv("AI_API", "") #groq api key 
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant") #groq ai model
PRIVACY_IMAGE = os.getenv("PRIVACY_IMAGE", "")
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", 0))
