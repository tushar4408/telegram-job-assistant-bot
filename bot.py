import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext
import os
TOKEN = os.environ.get("BOT_TOKEN") 
from dotenv import load_dotenv

load_dotenv()


# ================== CONFIG ==================

TOKEN = os.getenv("TELEGRAM_TOKEN")

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

# store user preferences
user_skill = {}

# ================== START COMMAND ==================

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Hi 👋\n\n"
        "I am your Job Alert Assistant Bot 🤖\n\n"
        "Use:\n"
        "/jobs python\n"
        "/jobs java\n"
        "/jobs data\n"
        "/jobs web\n\n"
        "If you don’t choose, I’ll show Python jobs by default 💥"
    )

# ================== JOBS COMMAND ==================

def jobs(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    # Step 1: Decide skill
    if context.args:
        skill = context.args[0].lower()
        user_skill[chat_id] = skill
    elif chat_id in user_skill:
        skill = user_skill[chat_id]
    else:
        skill = "python"

    allowed_skills = ["python", "java", "data", "web"]

    if skill not in allowed_skills:
        update.message.reply_text(
            "❌ Skill not supported.\n\n"
            "Use:\n"
            "/jobs python\n"
            "/jobs java\n"
            "/jobs data\n"
            "/jobs web"
        )
        return

    # Step 2: Skill → search keyword mapping
    search_keywords = {
        "python": "python developer",
        "java": "java developer",
        "data": "data analyst",
        "web": "web developer"
    }

    # Step 3: Fetch jobs from Adzuna API
    url = "https://api.adzuna.com/v1/api/jobs/in/search/1"

    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": 10,
        "what": search_keywords[skill]
    }

    response = requests.get(url, params=params)
    data = response.json()

    # Step 4: Send jobs
    update.message.reply_text(f"🔔 {skill.upper()} Job Openings:\n")

    for job in data.get("results", []):
        title = job.get("title", "Job Title")
        company = job.get("company", {}).get("display_name", "Company")
        link = job.get("redirect_url")

        keyboard = [
            [InlineKeyboardButton("✅ Apply Now", url=link)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = f"📌 {title}\n🏢 {company}"

        update.message.reply_text(text, reply_markup=reply_markup)

# ================== BOT SETUP ==================

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("jobs", jobs))

updater.start_polling()
updater.idle()
