from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ConversationHandler, ContextTypes
)

import os

NOM, PRENOM, ADRESSE, WHATSAPP, PRODUIT, PCS_PHOTO = range(6)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bienvenue dans l’espace d’achat !\n"
        "Paiement uniquement par recharge PCS. Appuyez sur Entrée pour continuer."
    )
    return NOM

async def get_nom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["nom"] = update.message.text
    await update.message.reply_text("Entrez votre prénom :")
    return PRENOM

async def get_prenom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["prenom"] = update.message.text
    await update.message.reply_text("Entrez votre adresse de livraison :")
    return ADRESSE

async def get_adresse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["adresse"] = update.message.text
    await update.message.reply_text("Entrez votre numéro WhatsApp :")
    return WHATSAPP

async def get_whatsapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["whatsapp"] = update.message.text
    await update.message.reply_text("Quel est l'ID du produit ? (voir message épinglé)")
    return PRODUIT

async def get_produit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["produit_id"] = update.message.text
    await update.message.reply_text("Envoyez les photos des recharges PCS neuves.")
    return PCS_PHOTO

async def get_pcs_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        context.user_data.setdefault("pcs_photos", []).append(update.message.photo[-1].file_id)
        await update.message.reply_text("Photo enregistrée. Tapez /valider quand vous avez terminé.")
        return PCS_PHOTO
    else:
        await update.message.reply_text("Veuillez envoyer une photo.")
        return PCS_PHOTO

async def valider(update: Update, context: ContextTypes.DEFAULT_TYPE):
    infos = context.user_data
    summary = (
        f"Commande reçue :\n"
        f"👤 {infos['prenom']} {infos['nom']}\n"
        f"📍 {infos['adresse']}\n"
        f"📱 WhatsApp : {infos['whatsapp']}\n"
        f"🛍️ Produit ID : {infos['produit_id']}\n"
        f"📸 Photos PCS : {len(infos.get('pcs_photos', []))} reçues"
    )
    await update.message.reply_text(summary)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Commande annulée.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

if __name__ == '__main__':
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NOM: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_nom)],
            PRENOM: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_prenom)],
            ADRESSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_adresse)],
            WHATSAPP: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_whatsapp)],
            PRODUIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_produit)],
            PCS_PHOTO: [
                MessageHandler(filters.PHOTO, get_pcs_photo),
                CommandHandler("valider", valider)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()
