from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "8038871118:AAG78r6cvtCGn2sCmcTioECNxcRY0q_91Jc"

schede = ["Petto/Tricipiti", "Gambe", "Dorso/Bicipiti", "Full Body"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [[s] for s in schede]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "Ciao! Quale scheda vuoi fare oggi?",
        reply_markup=markup
    )

async def scelta_scheda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    scelta = update.message.text
    if scelta in schede:
        await update.message.reply_text(f"Ottima scelta! Iniziamo con: {scelta}")
    else:
        await update.message.reply_text("Per favore, scegli una delle schede elencate.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, scelta_scheda))
    print("Bot in esecuzione...")
    app.run_polling()

if __name__ == "__main__":
    main()