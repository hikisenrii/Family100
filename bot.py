import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from questions import get_random_question, check_answer
from config import TOKEN, OWNER_ID, API_ID, API_HASH

# Load environment variables if running locally
if os.getenv('ENV') != 'HEROKU':
    from dotenv import load_dotenv
    load_dotenv()

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Data untuk menyimpan skor pengguna dan grup
user_scores = {}
group_scores = {}
blacklisted_users = set()
blacklisted_groups = set()

async def start(update: Update, context: CallbackContext) -> None:
    user_fullname = update.message.from_user.full_name
    chat_id = update.message.chat.id
    if update.message.chat.type in ["group", "supergroup"]:
        logger.info(f"Bot joined a group: {update.message.chat.title} ({chat_id})")
    else:
        logger.info(f"User started bot: {user_fullname} ({update.message.from_user.id})")

    keyboard = [
        [InlineKeyboardButton("Support", url="https://t.me/+bRlP2S66_g45MTFl")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"Halo {user_fullname}, ayo kita main Super Family 100.\n"
        "/play : mulai game\n"
        "/nyerah : menyerah dari game\n"
        "/next : Pertanyaan berikutnya\n"
        "/help : membuka pesan bantuan\n"
        "/stats : melihat statistik kamu\n"
        "/top : lihat top skor global\n"
        "/topgrup : lihat top skor grup\n"
        "/peraturan : aturan bermain\n",
        reply_markup=reply_markup
    )

async def bantuan(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "/play : mulai game\n"
        "/nyerah : menyerah dari game\n"
        "/next : Pertanyaan berikutnya\n"
        "/help : membuka pesan bantuan\n"
        "/stats : melihat statistik kamu\n"
        "/top : lihat top skor global\n"
        "/topgrup : lihat top skor grup\n"
        "/peraturan : aturan bermain\n"
    )

def format_question(question, correct_answers):
    answer_lines = [f"{i+1}. {answer}" for i, answer in enumerate(correct_answers)]
    return f"{question}\n" + "\n".join(answer_lines)

def update_question_format(question, correct_answers):
    return format_question(question, correct_answers)

async def play(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id in blacklisted_users or update.message.chat.id in blacklisted_groups:
        await update.message.reply_text("Anda atau grup ini telah diblokir dari permainan.")
        return

    question, answers = get_random_question()
    context.chat_data['current_question'] = question
    context.chat_data['correct_answers'] = ["_" * len(ans) for ans, _ in answers]
    context.chat_data['all_answers'] = answers
    formatted_question = format_question(question, context.chat_data['correct_answers'])
    await update.message.reply_text(formatted_question)

async def handle_answer(update: Update, context: CallbackContext) -> None:
    if 'current_question' not in context.chat_data:
        return

    user_answer = update.message.text.strip()
    question = context.chat_data['current_question']
    all_answers = context.chat_data['all_answers']
    correct_answers = context.chat_data['correct_answers']
    
    logger.debug(f"User answer: {user_answer}")
    logger.debug(f"Current question: {question}")
    logger.debug(f"All answers: {all_answers}")
    logger.debug(f"Correct answers so far: {correct_answers}")

    index, points = check_answer(question, user_answer)
    logger.debug(f"Index of the correct answer: {index}, Points: {points}")
    
    if index != -1:
        correct_answers[index] = all_answers[index][0]
        formatted_question = update_question_format(question, correct_answers)
        
        await update.message.reply_text(f"Jawaban benar! Poin: {points}\n{formatted_question}")

        user_name = update.message.from_user.username
        if user_name not in user_scores:
            user_scores[user_name] = 0
        user_scores[user_name] += points

        chat_id = update.message.chat.id
        if chat_id not in group_scores:
            group_scores[chat_id] = {}
        if user_name not in group_scores[chat_id]:
            group_scores[chat_id][user_name] = 0
        group_scores[chat_id][user_name] += points

        context.chat_data['current_question'] = None
        context.chat_data['all_answers'] = None
        context.chat_data['correct_answers'] = None

async def nyerah(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Anda telah menyerah dari game.")

async def next(update: Update, context: CallbackContext) -> None:
    question, answers = get_random_question()
    context.chat_data['current_question'] = question
    context.chat_data['correct_answers'] = ["_" * len(ans) for ans, _ in answers]
    context.chat_data['all_answers'] = answers
    formatted_question = format_question(question, context.chat_data['correct_answers'])
    await update.message.reply_text(formatted_question)

async def stats(update: Update, context: CallbackContext) -> None:
    user_name = update.message.from_user.username
    user_id = update.message.from_user.id
    user_score = user_scores.get(user_name, 0)
    
    global_rank = len(user_scores)

    stats_message = (
        f"Your Game Stats\n"
        f"🆔 ID: {user_id}\n"
        f"🏅 Name: {user_name}\n"
        f"🌐 Score: {user_score}\n"
    )
    await update.message.reply_text(stats_message)

async def top(update: Update, context: CallbackContext) -> None:
    top_players = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)
    formatted_top_players = [
        f"{i + 1}. {'🥇' if i == 0 else '🥈' if i == 1 else '🥉' if i == 2 else '🏅'} {player} - {score}"
        for i, (player, score) in enumerate(top_players[:10])
    ]
    await update.message.reply_text("Top Player Global:\n" + "\n".join(formatted_top_players))

async def topgrup(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat.id
    if chat_id not in group_scores:
        group_scores[chat_id] = {}
    
    top_group_players = sorted(group_scores[chat_id].items(), key=lambda x: x[1], reverse=True)
    formatted_top_group_players = [
        f"{i + 1}. {'🥇' if i == 0 else '🥈' if i == 1 else '🥉' if i == 2 else '🏅'} {player} - {score}"
        for i, (player, score) in enumerate(top_group_players[:10])
    ]
    await update.message.reply_text("Top Player Grup:\n" + "\n".join(formatted_top_group_players))

async def peraturan(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "<b>Peraturan bermain adalah:</b>\n\n"
        "1. Mulai permainan dengan mengetik /play.\n"
        "2. Anda akan diberikan pertanyaan dan harus menjawabnya.\n"
        "3. Gunakan /nyerah untuk menyerah dari permainan.\n"
        "4. Gunakan /next untuk mendapatkan pertanyaan berikutnya.\n"
        "5. Gunakan /stats untuk melihat statistik Anda.\n"
        "6. Gunakan /top untuk melihat top skor global.\n"
        "7. Gunakan /topgrup untuk melihat top skor grup.\n"
        "8. Gunakan /help untuk melihat daftar perintah.\n\n",
        parse_mode='HTML'
    )

async def blacklist(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id != OWNER_ID:
        await update.message.reply_text("Anda tidak memiliki izin untuk menggunakan perintah ini.")
        return

    args = context.args
    if not args:
        await update.message.reply_text("Penggunaan: /blacklist [user_id/grup_id]")
        return

    try:
        target_id = int(args[0])
        if target_id < 0:
            blacklisted_groups.add(target_id)
            await update.message.reply_text(f"Grup {target_id} telah diblacklist.")
            logger.info(f"Group {target_id} blacklisted by {update.message.from_user.username}.")
        else:
            blacklisted_users.add(target_id)
            await update.message.reply_text(f"User {target_id} telah diblacklist.")
            logger.info(f"User {target_id} blacklisted by {update.message.from_user.username}.")
    except ValueError:
        await update.message.reply_text("ID harus berupa angka.")

async def whitelist(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id != OWNER_ID:
        await update.message.reply_text("Anda tidak memiliki izin untuk menggunakan perintah ini.")
        return

    args = context.args
    if not args:
        await update.message.reply_text("Penggunaan: /whitelist [user_id/grup_id]")
        return

    try:
        target_id = int(args[0])
        if target_id < 0:
            blacklisted_groups.discard(target_id)
            await update.message.reply_text(f"Grup {target_id} telah dihapus dari blacklist.")
            logger.info(f"Group {target_id} removed from blacklist by {update.message.from_user.username}.")
        else:
            blacklisted_users.discard(target_id)
            await update.message.reply_text(f"User {target_id} telah dihapus dari blacklist.")
            logger.info(f"User {target_id} removed from blacklist by {update.message.from_user.username}.")
    except ValueError:
        await update.message.reply_text("ID harus berupa angka.")

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", bantuan))
    application.add_handler(CommandHandler("play", play))
    application.add_handler(CommandHandler("nyerah", nyerah))
    application.add_handler(CommandHandler("next", next))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("top", top))
    application.add_handler(CommandHandler("topgrup", topgrup))
    application.add_handler(CommandHandler("peraturan", peraturan))
    application.add_handler(CommandHandler("blacklist", blacklist))
    application.add_handler(CommandHandler("whitelist", whitelist))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))

    application.run_polling()

if __name__ == "__main__":
    main()
