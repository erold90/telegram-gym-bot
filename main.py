import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes
)

# TOKEN del bot Telegram
TOKEN = os.getenv("TOKEN") or "8038871118:AAG78r6cvtCGn2sCmcTioECNxcRY0q_91Jc"

# === UTILS ===

def get_emoji(muscle):
    mapping = {
        "Petto": "🏋️",
        "Gambe": "🦵",
        "Spalle": "🏋️‍♂️",
        "Schiena": "🧗",
        "Bicipiti": "💪",
        "Tricipiti": "🏋️‍♀️"
    }
    return mapping.get(muscle, "")

# === DATA: scheda di allenamento ===

workout_plan = [
    {
        "muscle": "Petto",
        "exercise": "Panca Piana",
        "description": "Sdraiati su una panca, abbassa il bilanciere al petto e spingi su in modo controllato.",
        "test": "3x10 con 70% del massimale"
    },
    {
        "muscle": "Gambe",
        "exercise": "Squat",
        "description": "Scendi sotto il parallelo, risali spingendo con i talloni, schiena dritta.",
        "test": "4x8 carico progressivo"
    },
    {
        "muscle": "Spalle",
        "exercise": "Military Press",
        "description": "Spingi il bilanciere sopra la testa, mantieni il core contratto.",
        "test": "3x10"
    },
    {
        "muscle": "Schiena",
        "exercise": "Trazioni",
        "description": "Prendi la sbarra in presa prona, tira su il petto fino a superare il mento.",
        "test": "3x8 corpo libero o zavorra"
    },
    {
        "muscle": "Bicipiti",
        "exercise": "Curl con bilanciere",
        "description": "In piedi, esegui il curl senza oscillare il busto.",
        "test": "3x12"
    },
    {
        "muscle": "Tricipiti",
        "exercise": "French Press",
        "description": "Sdraiato, porta il bilanciere verso la fronte piegando solo i gomiti.",
        "test": "3x10"
    }
]

# === HANDLERS ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Inizia Allenamento", callback_data="start_workout")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Ciao atleta! Sei pronto per una sessione full body da vero leone?\n\nPremi il bottone qui sotto!",
        reply_markup=reply_markup
    )

async def handle_workout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text("**Riscaldamento Attivazione Muscolare**:\n\n"
        "- Jumping Jacks x 30 sec\n"
        "- Squat a corpo libero x 15\n"
        "- Circonduzioni braccia x 20\n"
        "- Affondi x 10/gamba\n\nPartiamo tra 10 secondi!")
    await asyncio.sleep(10)

    for ex in workout_plan:
        msg = f"**{ex['muscle']}** - {ex['exercise']} {get_emoji(ex['muscle'])}\n"
        msg += f"{ex['description']}\n\n*Serie consigliata:* {ex['test']}"
        await query.message.reply_text(msg, parse_mode='Markdown')

        # Countdown di riposo 60 sec
        await rest_timer(query, 60)

    await query.message.reply_text("**Allenamento Completato!**\nOttimo lavoro! Ci si rivede alla prossima sessione!")

async def rest_timer(query, seconds):
    msg = await query.message.reply_text(f"⏱ Riposo: {seconds} sec")
    for t in range(seconds, 0, -1):
        await asyncio.sleep(1)
        try:
            await msg.edit_text(f"⏱ Riposo: {t} sec")
        except:
            break

# === MAIN ===

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_workout, pattern="^start_workout$"))

    print("Bot avviato…")
    app.run_polling()

if __name__ == "__main__":
    main()