import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

TOKEN = "8038871118:AAG78r6cvtCGn2sCmcTioECNxcRY0q_91Jc"

# Scheda full body ipertrofica
workout_plan = [
    {
        "muscle": "Petto",
        "exercise": "Panca Piana con Bilanciere",
        "description": "Sdraiati su una panca, piedi a terra, abbassa il bilanciere al petto e spingi su in maniera controllata.",
        "test": "3x8-12 con 60-75% del massimale"
    },
    {
        "muscle": "Schiena",
        "exercise": "Trazioni alla Sbarra",
        "description": "Impugnatura prona, tira il corpo verso l’alto fino a superare il mento, controlla la discesa.",
        "test": "3x6-10 (aggiungi zavorra se sei avanzato)"
    },
    {
        "muscle": "Gambe",
        "exercise": "Squat con Bilanciere",
        "description": "Scendi sotto il parallelo mantenendo il core contratto, risali spingendo con i talloni.",
        "test": "4x8-12 con carico progressivo"
    },
    {
        "muscle": "Spalle",
        "exercise": "Military Press",
        "description": "Spingi il bilanciere sopra la testa da in piedi, mantieni il busto fermo.",
        "test": "3x8-10"
    },
    {
        "muscle": "Bicipiti",
        "exercise": "Curl con Bilanciere",
        "description": "Piedi larghi come le spalle, porta il bilanciere al petto senza oscillare.",
        "test": "3x10-12"
    },
    {
        "muscle": "Tricipiti",
        "exercise": "French Press",
        "description": "Sdraiati, braccia perpendicolari, piega i gomiti portando il bilanciere verso la fronte.",
        "test": "3x10-12"
    }
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Inizia Allenamento Full Body", callback_data="start_workout")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Ciao atleta! Sei pronto per la tua sessione di ipertrofia? **3x a settimana**! Spingiamo forte!", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "start_workout":
        await query.edit_message_text("**Riscaldamento in corso…**\n\n- Jumping jacks x 1 min\n- Squat a corpo libero x 15\n- Circonduzioni braccia x 30 sec\n- Affondi camminati x 10 per gamba\n\nTra 10 secondi si parte!")
        await asyncio.sleep(10)

        for idx, exercise in enumerate(workout_plan):
            msg = f"**{exercise['muscle']}** - {exercise['exercise']} {muscle_emoji(exercise['muscle'])}\n"
            msg += f"{exercise['description']}\n\n{exercise['test']}"
            await query.message.reply_text(msg, parse_mode='Markdown')
            await rest_timer(query, 60)

        await query.message.reply_text("Allenamento completato! Ottimo lavoro! **Recupera e preparati per la prossima sessione.**")

async def rest_timer(query, seconds):
    msg = await query.message.reply_text("Riposo: {} sec".format(seconds))
    for remaining in range(seconds, 0, -1):
        await asyncio.sleep(1)
        try:
            await msg.edit_text("Riposo: {} sec".format(remaining))
        except:
            break

def muscle_emoji(muscle):
    emoji_map = {
        "Petto": "🏋️",
        "Schiena": "🧗",
        "Gambe": "🦵",
        "Spalle": "🏋️‍♂️",
        "Bicipiti": "💪",
        "Tricipiti": "🏋️‍♀️"
    }
    return emoji_map.get(muscle, "")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Bot avviato...")
    app.run_polling()