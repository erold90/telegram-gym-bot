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
SCELTA_AZIONE, SCELTA_GIORNO, ALLENAMENTO = range(3)

schede_settimanali = {
    "Lunedì": [
        {"nome": "Chest press (warm-up)", "serie": 1, "ripetizioni": 15, "warmup": True, "recupero": 45},
        {"nome": "Panca piana", "serie": 4, "ripetizioni": 8, "recupero": 90},
        {"nome": "Curl con bilanciere", "serie": 4, "ripetizioni": 10, "recupero": 60}
    ],
    "Venerdì": [
        {"nome": "Squat corpo libero (warm-up)", "serie": 1, "ripetizioni": 15, "warmup": True, "recupero": 45},
        {"nome": "Squat", "serie": 4, "ripetizioni": 8, "recupero": 120}
    ]
}

user_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🏋️ Allenamento", callback_data="allenamento")],
        [InlineKeyboardButton("📄 Log allenamenti", callback_data="log")],
        [InlineKeyboardButton("ℹ️ Info", callback_data="info")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Benvenuto! Cosa vuoi fare?", reply_markup=markup)
    return SCELTA_AZIONE

async def menu_principale(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    scelta = query.data
    if scelta == "allenamento":
        keyboard = [[InlineKeyboardButton(g, callback_data=g)] for g in schede_settimanali]
        markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Scegli il giorno:", reply_markup=markup)
        return SCELTA_GIORNO
    elif scelta == "log":
        try:
            with open("log.txt", "r") as f:
                testo = f.read() or "Nessun allenamento registrato."
        except:
            testo = "Nessun log disponibile."
        await query.edit_message_text(testo[-4000:])  # Telegram max 4096 chars
    elif scelta == "info":
        await query.edit_message_text("Questo bot ti guida nel tuo allenamento ipertrofico in palestra.")
    return ConversationHandler.END

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
    await query.edit_message_text(text= testo, reply_markup=markup)

async def serie_completata(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    s = user_sessions[user_id]
    esercizio = s["esercizi"][s["indice_esercizio"]]
    s["log"].append(f"{esercizio['nome']} - Serie {s['indice_serie']+1}/{esercizio['serie']} completata")
    s["indice_serie"] += 1

    if s["indice_serie"] < esercizio["serie"]:
        await timer_recupero(update, esercizio.get("recupero", 60))
        await mostra_esercizio(update, context)
    else:
        s["indice_esercizio"] += 1
        s["indice_serie"] = 0
        if s["indice_esercizio"] < len(s["esercizi"]):
            await timer_recupero(update, esercizio.get("recupero", 60))
            await mostra_esercizio(update, context)
        else:
            await mostra_riepilogo(update, context)
            return ConversationHandler.END
    return ALLENAMENTO

async def timer_recupero(update: Update, durata: int):
    query = update.callback_query
    step = durata // 6
    barra = ""
    msg = await query.edit_message_text("Recupero: in corso...\n[          ]")
    for i in range(1, 7):
        await asyncio.sleep(step)
        barra = "#" * i + " " * (10 - i)
        testo = f"Recupero: {durata - (i * step)}s rimanenti\n[{barra}]"
        if durata - (i * step) <= 10:
            testo += " (preparati)"
        await msg.edit_text(testo)
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
            SCELTA_AZIONE: [CallbackQueryHandler(menu_principale)],
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