from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import json
import time

TOKEN = "7508729989:AAEHffL9PBuOzvdD7dKTzYh8pPpHFX7nE4c"
ADMIN_ID = 5471744417
CHANNELS = ["@kyrgyzkino_kg", "@alga_kgz", "@bishkek_24", "@joldokgz"]
DATABASE = "films.json"

def load_films():
    try:
        with open(DATABASE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_films(films):
    with open(DATABASE, "w") as f:
        json.dump(films, f, indent=4)

USER_LANGUAGE = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    USER_LANGUAGE[user_id] = "ky"

    if not await check_subscription(update, context):
        await update.message.reply_text("Ботту колдонуу үчүн төмөнкү каналдарга кошул:\n" + "\n".join(CHANNELS) + "\nКошулгандан кийин /start деп жаз.")
        return

    await update.message.reply_text("Салам! Кино кодун жаз (мисалы, K1234).\nЭгер түшүнбөсөң, жооп бер, орусчага өтөм.")

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    for channel in CHANNELS:
        try:
            member = await context.bot.get_chat_member(channel, user.id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await check_subscription(update, context):
        if USER_LANGUAGE.get(user_id, "ky") == "ky":
            await update.message.reply_text("Каналдарга кошул!\n" + "\n".join(CHANNELS))
        else:
            await update.message.reply_text("Подпишись на каналы!\n" + "\n".join(CHANNELS))
        return

    code = update.message.text.strip()
    films = load_films()

    if code in films:
        await update.message.reply_video(video=films[code]["file_id"], caption=films[code]["title"])
    else:
        if USER_LANGUAGE.get(user_id, "ky") == "ky":
            await update.message.reply_text("Мындай код жок! Башка код жаз.")
        else:
            await update.message.reply_text("Такой код не найден! Попробуй другой.")

async def switch_to_russian(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    USER_LANGUAGE[user_id] = "ru"
    await update.message.reply_text("Хорошо, теперь я на русском! Напиши код фильма (например, K1234).")

async def add_film(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Сен админ эмессиң!")
        return

    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Колдонуу: /add_film <код> <аталыш>")
        return

    code, title = args[0], " ".join(args[1:])
    films = load_films()
    films[code] = {"title": title, "file_id": None}
    save_films(films)
    context.user_data['current_code'] = code
    await update.message.reply_text(f"Кино кошулду: {code} - {title}\nЭми MP4 файл жөнөт, мен file_id алам.")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Сен админ эмессиң!")
        return

    video = update.message.video
    if not video:
        await update.message.reply_text("MP4 файл жөнөт!")
        return

    code = context.user_data.get('current_code')
    if code:
        films = load_films()
        films[code]["file_id"] = video.file_id
        save_films(films)
        await update.message.reply_text(f"Видео {code} код менен сакталды!")
        del context.user_data['current_code']
    else:
        await update.message.reply_text("Алгач /add_film <код> <аталыш> менен фильмди кошуңуз!")

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ru", switch_to_russian))
    application.add_handler(CommandHandler("add_film", add_film))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    application.add_handler(MessageHandler(filters.Regex("(?i)^(оруске|русский|на русском)$"), switch_to_russian))

    application.run_polling()

if __name__ == "__main__":
    main()
