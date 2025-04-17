import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
)

TOKEN = "8038871118:AAG78r6cvtCGn2sCmcTioECNxcRY0q_91Jc"
SCELTA_GIORNO, ALLENAMENTO = range(2)

schede_settimanali = {
    "Lunedì": [
        {"nome": "Chest press (warm-up)", "serie": 1, "ripetizioni": 15, "warmup": True},
        {"nome": "Panca piana", "serie": 4, "ripetizioni": 8},
        {"nome": "Curl con bilanciere", "serie": 4, "ripetizioni": 10}
    ],
    "Venerdì": [
        {"nome": "Squat corpo libero (warm-up)", "serie": 1, "ripetizioni": 15, "warmup": True},
        {"nome": "Squat", "serie": 4, "ripetizioni": 8}
    ]
}

user_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(g, callback_data=g)] for g in schede_settimanali]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Ciao! Scegli il giorno:", reply_markup=markup)
    return SCELTA_GIORNO

async def scegli_giorno(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    giorno = query.data
    user_id = query.from_user.id
    user_sessions[user_id] = {
        "giorno": giorno,
        "esercizi": schede_settimanali[giorno],
        "indice_esercizio": 0,
        "indice_serie": 0,
        "log": []
    }
    await mostra_esercizio(update, context)
    return ALLENAMENTO

async def mostra_esercizio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    sessione = user_sessions[user_id]
    esercizio = sessione["esercizi"][sessione["indice_esercizio"]]
    serie_corrente = sessione["indice_serie"] + 1

    testo = (
        f"{'🟡 Riscaldamento\n' if esercizio.get('warmup') else ''}"
        f"Esercizio: {esercizio['nome']}\n"
        f"Serie {serie_corrente}/{esercizio['serie']} - {esercizio['ripetizioni']} ripetizioni"
    )
    keyboard = [[InlineKeyboardButton("✅ Serie completata", callback_data="serie_completata")]]
    markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=testo, reply_markup=markup)

async def serie_completata(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    s = user_sessions[user_id]
    esercizio = s["esercizi"][s["indice_esercizio"]]
    s["log"].append(f"{esercizio['nome']} - Serie {s['indice_serie']+1}/{esercizio['serie']} completata")
    s["indice_serie"] += 1

    if s["indice_serie"] < esercizio["serie"]:
        await timer_recupero(update)
        await mostra_esercizio(update, context)
    else:
        s["indice_esercizio"] += 1
        s["indice_serie"] = 0
        if s["indice_esercizio"] < len(s["esercizi"]):
            await timer_recupero(update)
            await mostra_esercizio(update, context)
        else:
            await mostra_riepilogo(update, context)
            return ConversationHandler.END
    return ALLENAMENTO

async def timer_recupero(update: Update):
    query = update.callback_query
    msg = await query.edit_message_text("Recupero: 60s rimanenti...")
    await asyncio.sleep(15)
    await msg.edit_text("Recupero: 45s rimanenti...")
    await asyncio.sleep(15)
    await msg.edit_text("Recupero: 30s rimanenti...")
    await asyncio.sleep(15)
    await msg.edit_text("Recupero: 15s rimanenti...")
    await asyncio.sleep(5)
    await msg.edit_text("Recupero: 10s rimanenti... (preparati)")
    await asyncio.sleep(10)
    await msg.edit_text("Recupero completato! Passiamo avanti...")

async def mostra_riepilogo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    s = user_sessions[user_id]
    log = "\n".join(s["log"])
    testo = f"Allenamento completato ({s['giorno']})!\n\n{log}"
    await update.callback_query.edit_message_text(text=testo)

    with open("log.txt", "a") as f:
        f.write(f"Giorno: {s['giorno']}\n{log}\n\n")

    user_sessions.pop(user_id, None)

async def annulla(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_sessions.pop(update.message.from_user.id, None)
    await update.message.reply_text("Allenamento annullato.")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SCELTA_GIORNO: [CallbackQueryHandler(scegli_giorno)],
            ALLENAMENTO: [CallbackQueryHandler(serie_completata, pattern="^serie_completata$")]
        },
        fallbacks=[CommandHandler("annulla", annulla)],
    )
    app.add_handler(conv_handler)
    print("Bot in esecuzione...")
    app.run_polling()

if __name__ == "__main__":
    main()