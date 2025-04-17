from telegram.ext import ApplicationBuilder
from handlers.start import start_handler
from handlers.workout import workout_handler

import os

TOKEN = os.getenv("TOKEN") or "8038871118:AAG78r6cvtCGn2sCmcTioECNxcRY0q_91Jc"

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(start_handler)
    app.add_handler(workout_handler)

    print("Bot avviato...")
    app.run_polling()

if __name__ == "__main__":
    main()