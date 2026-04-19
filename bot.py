import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

from games import worker_game

load_dotenv()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # C'est ici que tu peux lister tes différents jeux
    message = (
        "👋 Bienvenue sur le bot multi-jeux !\n\n"
        "🎮 Jeux disponibles :\n"
        "- Tape /worker ou 'worker' pour lancer le jeu de l'ouvrier 🛵🍔\n\n"
        "*(Ajoute tes autres jeux ici)*"
    )
    await update.message.reply_text(message)

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    
    # Routeur de jeux basé sur le nom
    if text == "worker":
        await worker_game.start_worker_game(update, context)
    else:
        # Message par défaut si le jeu n'est pas reconnu
        await update.message.reply_text("Jeu inconnu. Tape /start pour voir la liste des jeux.")

def main():
    
    token = os.getenv("TELEGRAM_TOKEN")
    if not token or token == "ton_token_ici":
        print("Erreur: TELEGRAM_TOKEN introuvable. Configure le dans .env")
        return

    application = Application.builder().token(token).build()

    # Routeur de commandes générales
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("worker", worker_game.start_worker_game))
    
    # Routeur basé sur le texte exact (pour lancer les jeux par leur nom)
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), text_handler))
    
    # Redirige les CallbackQueries (clics sur les boutons inlines) vers les gestionnaires appropriés
    # worker_game a son propre routeur de callback basé sur un préfixe
    application.add_handler(CallbackQueryHandler(worker_game.handle_callback, pattern='^worker_'))

    print("Le bot est démarré et écoute !")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
