from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import json
import time

# Бот токени (сеники)
TOKEN = "7508729989:AAEHffL9PBuOzvdD7dKTzYh8pPpHFX7nE4c"

# Админ ID (сеники)
ADMIN_ID = 5471744417

# Каналдардын тизмеси
CHANNELS = ["@kyrgyzkino_kg", "@alga_kgz", "@bishkek_24", "@joldokgz"]

# Кино маалыматтарын сактоо үчүн JSON файл
DATABASE = "films.json"

# Баштапкы маалымат базасы
def load_films():
    try:
        with open(DATABASE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_films(films):
    with open(DATABASE, "w") as f:
        json.dump(films, f, indent=4)

# Колдонуучунун тилин сактоо
USER_LANGUAGE = {}

# Баштоо командасы
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    # Тилди аныктоо
    USER_LANGUAGE[user_id] = "ky"  # Башында кыргызча

    # Каналга кошулганын текшерүү
    if not await check_subscription(update, context):
        await update.message.reply_text(
            "Ботту колдонуу үчүн төмөнкү каналдарга кошул:\n" +
            "\n".join(CHANNELS) +
            "\nКошулгандан кийин /start деп жаз."
        )
        return

    await update.message.reply_text(
        "Салам! Кино кодун жаз (мисалы, K1234).\nЭгер түшүнбөсөң, жооп бер, орусчага өтөм."
    )

# Каналга кошулганын текшерүү
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

# Код менен кино жөнөтүү
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

# Тилди өзгөртүү (орусчага)
async def switch_to_russian(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    USER_LANGUAGE[user_id] = "ru"
    await update.message.reply_text("Хорошо, теперь я на русском! Напиши код фильма (например, K1234).")

# Админ командалары
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
    films[code] = {"title": title, "file_id": None}  # file_id кийин кошобуз
    save_films(films)
    await update.message.reply_text(f"Кино кошулду: {code} - {title}\nЭми MP4 файл жөнөт, мен file_id алам.")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Сен админ эмессиң!")
        return

    video = update.message.video
    if not video:
        await update.message.reply_text("MP4 файл жөнөт!")
        return

    file_id = video.file_id
    await update.message.reply_text(f"Видео кабыл алынды! Кодду жаз (мисалы, K1234), бул видео менен байланыштырам.")
    context.user_data["pending_file_id"] = file_id

async def link_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Сен админ эмессиң!")
        return

    code = update.message.text.strip()
    file_id = context.user_data.get("pending_file_id")
    if not file_id:
        await update.message.reply_text("Алгач MP4 файл жөнөт!")
        return

    films = load_films()
    if code in films:
        films[code]["file_id"] = file_id
        save_films(films)
        await update.message.reply_text(f"Видео {code} коду менен байланыштырылды!")
        context.user_data.pop("pending_file_id", None)
    else:
        await update.message.reply_text("Мындай код жок! /add_film менен код кош.")

async def list_films(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Сен админ эмессиң!")
        return

    films = load_films()
    if not films:
        await update.message.reply_text("Кино жок.")
        return

    response = "\n".join([f"{code}: {info['title']}" for code, info in films.items()])
    await update.message.reply_text(response)

async def delete_film(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Сен админ эмессиң!")
        return

    if not context.args:
        await update.message.reply_text("Колдонуу: /delete_film <код>")
        return

    code = context.args[0]
    films = load_films()
    if code in films:
        del films[code]
        save_films(films)
        await update.message.reply_text(f"Кино өчүрүлдү: {code}")
    else:
        await update.message.reply_text("Мындай код жок!")

# Негизги функция
def main():
    app = Application.builder().token(TOKEN).build()

    # Командалар
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add_film", add_film))
    app.add_handler(CommandHandler("list_films", list_films))
    app.add_handler(CommandHandler("delete_film", delete_film))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code))
    app.add_handler(MessageHandler(filters.Regex("^(?i)(оруске|русский|на русском)$"), switch_to_russian))

    # Ботту иштетүү
    app.run_polling()

if __name__ == "__main__":
    main()

