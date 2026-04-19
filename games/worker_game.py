import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import BadRequest

# In-memory storage
MEMORY_DB = {}

def get_user(user_id):
    if user_id not in MEMORY_DB:
        MEMORY_DB[user_id] = {"health": 100, "food": 0}
    user = MEMORY_DB[user_id]
    return user["health"], user["food"]

def update_user(user_id, health, food):
    MEMORY_DB[user_id] = {"health": health, "food": food}

def get_worker_keyboard():
    keyboard = [
        [InlineKeyboardButton("🛵 Aller au frigo (Jeu 1)", callback_data="worker_fridge")],
        [InlineKeyboardButton("🍔 Nourrir l'ouvrier (Jeu 2)", callback_data="worker_feed")],
        [InlineKeyboardButton("📊 Statut", callback_data="worker_status")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start_worker_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    health, food = get_user(user_id)
    
    text = (
        "👨‍🔧 **Jeu de l'Ouvrier en Moto**\n\n"
        f"❤️ Santé : {health}/100\n"
        f"🍔 Nourriture : {food}\n\n"
        "Choisis une action :"
    )
    
    if update.message:
        await update.message.reply_text(text, reply_markup=get_worker_keyboard(), parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.message.reply_text(text, reply_markup=get_worker_keyboard(), parse_mode="Markdown")

async def test_worker_death(update: Update, health: int, user_id: int):
    if health <= 0:
        # Reset user
        update_user(user_id, 100, 0)
        await update.callback_query.message.reply_text(
            "☠️ **Oh non ! Ton ouvrier est mort d'épuisement...**\n\n"
            "Tout est réinitialisé. Un nouvel ouvrier est embauché.",
            parse_mode="Markdown"
        )
        return True
    return False

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer() # Ack the click
    except BadRequest as e:
        if "Query is too old" not in str(e):
            raise e
    
    user_id = update.effective_user.id
    action = query.data
    
    health, food = get_user(user_id)
    
    if action == "worker_status":
        await query.edit_message_text(
            f"📊 **Statut Actuel**\n\n❤️ Santé : {health}/100\n🍔 Nourriture : {food}",
            reply_markup=get_worker_keyboard(),
            parse_mode="Markdown"
        )
        return

    if await test_worker_death(update, health, user_id):
        # Already handled death message, return to menu
        await start_worker_game(update, context)
        return

    if action == "worker_fridge":
        # Cost of going to fridge
        new_health = health - 10
        
        if await test_worker_death(update, new_health, user_id):
            await start_worker_game(update, context)
            return

        # 50% chance to win
        success = random.choice([True, False])
        
        if success:
            new_food = food + 1
            update_user(user_id, new_health, new_food)
            msg = f"🎉 **Succès !** L'ouvrier est revenu en moto avec de la nourriture !\n\n❤️ Santé : {new_health}/100\n🍔 Nourriture : {new_food}"
        else:
            update_user(user_id, new_health, food)
            msg = f"❌ **Échec !** Le frigo était vide ou la moto est tombée en panne...\n\n❤️ Santé : {new_health}/100\n🍔 Nourriture : {food}"
            
        await query.edit_message_text(msg, reply_markup=get_worker_keyboard(), parse_mode="Markdown")
        
    elif action == "worker_feed":
        if food >= 1:
            new_food = food - 1
            new_health = min(100, health + 30)
            update_user(user_id, new_health, new_food)
            msg = f"💪 **Miam !** L'ouvrier a mangé et repris des forces !\n\n❤️ Santé : {new_health}/100\n🍔 Nourriture : {new_food}"
            await query.edit_message_text(msg, reply_markup=get_worker_keyboard(), parse_mode="Markdown")
        else:
            msg = "⚠️ **Tu n'as pas de nourriture !**\n\nVa au frigo (Jeu 1) pour en chercher."
            await query.edit_message_text(msg, reply_markup=get_worker_keyboard(), parse_mode="Markdown")
