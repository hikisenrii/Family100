import logging
import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv
from questions import get_random_question, check_answer

# Load environment variables
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

app = Client("super_family_100_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

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

@app.on_message(filters.command("start") & (filters.private | filters.group))
async def start(client, message):
    user_fullname = message.from_user.first_name
    chat_id = message.chat.id
    if message.chat.type in ["group", "supergroup"]:
        logger.info(f"Bot joined a group: {message.chat.title} ({chat_id})")
    else:
        logger.info(f"User started bot: {user_fullname} ({message.from_user.id})")

    keyboard = [
        [InlineKeyboardButton("Support", url="https://t.me/+bRlP2S66_g45MTFl")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text(
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

@app.on_message(filters.command("help") & (filters.private | filters.group))
async def bantuan(client, message):
    await message.reply_text(
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

@app.on_message(filters.command("play") & (filters.private | filters.group))
async def play(client, message):
    if message.from_user.id in blacklisted_users or message.chat.id in blacklisted_groups:
        await message.reply_text("Anda atau grup ini telah diblokir dari permainan.")
        return

    question, answers = get_random_question()
    client.current_question = question
    client.correct_answers = ["_" * len(ans) for ans, _ in answers]
    client.all_answers = answers
    formatted_question = format_question(question, client.correct_answers)
    await message.reply_text(formatted_question)

@app.on_message(filters.text & ~filters.command & (filters.group | filters.private))
async def handle_answer(client, message):
    if not hasattr(client, 'current_question'):
        return

    user_answer = message.text.strip()
    question = client.current_question
    correct_answers = client.correct_answers
    all_answers = client.all_answers

    logger.debug(f"User answer: {user_answer}")
    logger.debug(f"Current question: {question}")
    logger.debug(f"Correct answers so far: {correct_answers}")

    index, points = check_answer(question, user_answer)
    logger.debug(f"Index of the correct answer: {index}, Points: {points}")
    
    if index != -1:
        correct_answers[index] = all_answers[index][0]
        formatted_question = update_question_format(question, correct_answers)
        
        await message.reply_text(f"Jawaban benar! Poin: {points}\n{formatted_question}")

        user_name = message.from_user.username
        if user_name not in user_scores:
            user_scores[user_name] = 0
        user_scores[user_name] += points

        chat_id = message.chat.id
        if chat_id not in group_scores:
            group_scores[chat_id] = {}
        if user_name not in group_scores[chat_id]:
            group_scores[chat_id][user_name] = 0
        group_scores[chat_id][user_name] += points

        del client.current_question
        del client.correct_answers
        del client.all_answers

@app.on_message(filters.command("nyerah") & (filters.private | filters.group))
async def nyerah(client, message):
    await message.reply_text("Anda telah menyerah dari game.")

@app.on_message(filters.command("next") & (filters.private | filters.group))
async def next(client, message):
    question, answers = get_random_question()
    client.current_question = question
    client.correct_answers = ["_" * len(ans) for ans, _ in answers]
    client.all_answers = answers
    formatted_question = format_question(question, client.correct_answers)
    await message.reply_text(formatted_question)

@app.on_message(filters.command("stats") & (filters.private | filters.group))
async def stats(client, message):
    user_name = message.from_user.username
    user_id = message.from_user.id
    user_score = user_scores.get(user_name, 0)
    
    global_rank = len(user_scores)

    stats_message = (
        f"Your Game Stats\n"
        f"🆔 ID: {user_id}\n"
        f"🏅 Name: {user_name}\n"
        f"🌐 Score: {user_score}\n"
    )
    await message.reply_text(stats_message)

@app.on_message(filters.command("top") & (filters.private | filters.group))
async def top(client, message):
    top_players = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)
    formatted_top_players = [
        f"{i + 1}. {'🥇' if i == 0 else '🥈' if i == 1 else '🥉' if i == 2 else '🏅'} {player} - {score}"
        for i, (player, score) in enumerate(top_players[:10])
    ]
    await message.reply_text("Top Player Global:\n" + "\n".join(formatted_top_players))

@app.on_message(filters.command("topgrup") & (filters.private | filters.group))
async def topgrup(client, message):
    chat_id = message.chat.id
    if chat_id not in group_scores:
        group_scores[chat_id] = {}
    
    top_group_players = sorted(group_scores[chat_id].items(), key=lambda x: x[1], reverse=True)
    formatted_top_group_players = [
        f"{i + 1}. {'🥇' if i == 0 else '🥈' if i == 1 else '🥉' if i == 2 else '🏅'} {player} - {score}"
        for i, (player, score) in enumerate(top_group_players[:10])
    ]
    await message.reply_text("Top Player Grup:\n" + "\n".join(formatted_top_group_players))

@app.on_message(filters.command("peraturan") & (filters.private | filters.group))
async def peraturan(client, message):
    await message.reply_text(
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

@app.on_message(filters.command("blacklist") & filters.user(OWNER_ID))
async def blacklist(client, message):
    args = message.command
    if len(args) < 2:
        await message.reply_text("Penggunaan: /blacklist [user_id/grup_id]")
        return

    try:
        target_id = int(args[1])
        if target_id < 0:
            blacklisted_groups.add(target_id)
            await message.reply_text(f"Grup {target_id} telah diblacklist.")
            logger.info(f"Group {target_id} blacklisted by {message.from_user.username}.")
        else:
            blacklisted_users.add(target_id)
            await message.reply_text(f"User {target_id} telah diblacklist.")
            logger.info(f"User {target_id} blacklisted by {message.from_user.username}.")
    except ValueError:
        await message.reply_text("ID harus berupa angka.")

@app.on_message(filters.command("whitelist") & filters.user(OWNER_ID))
async def whitelist(client, message):
    args = message.command
    if len(args) < 2:
        await message.reply_text("Penggunaan: /whitelist [user_id/grup_id]")
        return

    try:
        target_id = int(args[1])
        if target_id < 0:
            blacklisted_groups.discard(target_id)
            await message.reply_text(f"Grup {target_id} telah dihapus dari blacklist.")
            logger.info(f"Group {target_id} removed from blacklist by {message.from_user.username}.")
        else:
            blacklisted_users.discard(target_id)
            await message.reply_text(f"User {target_id} telah dihapus dari blacklist.")
            logger.info(f"User {target_id} removed from blacklist by {message.from_user.username}.")
    except ValueError:
        await message.reply_text("ID harus berupa angka.")

app.run()
