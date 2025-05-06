import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

# Токен
TOKEN = "7508729989:AAEHffL9PBuOzvdD7dKTzYh8pPpHFX7nE4c"

# Глобальные переменные
language = "ky"  # По умолчанию кыргызча
admin_id =  5471744417 # Замените на свой Telegram ID админа
films = {}  # Словарь для фильмов: {code: title}
info = "Бул боттун маалыматы / Информация о боте"  # Информация по умолчанию
channels = []  # Список каналов

# Меню панели
def get_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("Кыргызча", callback_data="lang_ky"),
         InlineKeyboardButton("Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("Кино кошуу", callback_data="add_film"),
         InlineKeyboardButton("Кино өчүрүү", callback_data="delete_film")],
        [InlineKeyboardButton("Маалымат кошуу", callback_data="set_info"),
         InlineKeyboardButton("Маалымат өзгөртүү", callback_data="edit_info"),
         InlineKeyboardButton("Маалымат өчүрүү", callback_data="delete_info")],
        [InlineKeyboardButton("Канал кошуу", callback_data="add_channel"),
         InlineKeyboardButton("Канал өзгөртүү", callback_data="edit_channel"),
         InlineKeyboardButton("Канал өчүрүү", callback_data="delete_channel")],
        [InlineKeyboardButton("Жардам / Помощь", callback_data="help")]
    ]
    return InlineKeyboardMarkup(keyboard)

# /start командасы
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    await update.message.reply_text(
        f"Салам, {user.first_name}! Мен Кinolorkg ботаң! Тилди тандаңыз / Привет, {user.first_name}! Я бот Kinolorkg! Выберите язык:",
        reply_markup=get_menu_keyboard()
    )

# Callback query handler для меню
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    global language, info, channels
    if query.data == "lang_ky":
        language = "ky"
        await query.edit_message_text("Тил кыргызчага алмаштырылды! / Язык изменён на кыргызский!", reply_markup=get_menu_keyboard())
    elif query.data == "lang_ru":
        language = "ru"
        await query.edit_message_text("Язык изменён на русский! / Тил орусчага алмаштырылды!", reply_markup=get_menu_keyboard())
    elif query.data == "help":
        await query.edit_message_text("Жардам: /start - баштоо, /add_film - фильм кошуу. Админ болсоңуз, @BotFather'га жазыңыз. / Помощь: /start - начать, /add_film - добавить фильм. Если админ, пишите в @BotFather.", reply_markup=get_menu_keyboard())
    elif query.data == "add_film":
        if update.effective_user.id == admin_id:
            await query.edit_message_text("MP4 файл жөнөтүңүз жана /add_film K1234 \"Аты\" деп жазыңыз. / Отправьте MP4 файл и напишите /add_film K1234 \"Название\".", reply_markup=get_menu_keyboard())
        else:
            await query.edit_message_text("Сиз администратор эмессиз! / Вы не администратор!", reply_markup=get_menu_keyboard())
    elif query.data == "delete_film":
        if update.effective_user.id == admin_id:
            if films:
                await query.edit_message_text(f"Кино тизмеси / Список фильмов:\n{films}\nКодду жазыңыз (мисалы, /delete_film K1234)", reply_markup=get_menu_keyboard())
            else:
                await query.edit_message_text("Кино тизмеси бош / Список фильмов пуст", reply_markup=get_menu_keyboard())
        else:
            await query.edit_message_text("Сиз администратор эмессиз! / Вы не администратор!", reply_markup=get_menu_keyboard())
    elif query.data == "set_info":
        if update.effective_user.id == admin_id:
            await query.edit_message_text("Жаңы маалыматты жазыңыз (мисалы, /set_info Бул жаңы маалымат) / Напишите новую информацию (например, /set_info Это новая информация)", reply_markup=get_menu_keyboard())
        else:
            await query.edit_message_text("Сиз администратор эмессиз! / Вы не администратор!", reply_markup=get_menu_keyboard())
    elif query.data == "edit_info":
        if update.effective_user.id == admin_id:
            await query.edit_message_text(f"Учурдагы маалымат / Текущая информация:\n{info}\nЖаңы маалыматты жазыңыз (мисалы, /set_info Жаңы текст) / Напишите новую информацию (например, /set_info Новый текст)", reply_markup=get_menu_keyboard())
        else:
            await query.edit_message_text("Сиз администратор эмессиз! / Вы не администратор!", reply_markup=get_menu_keyboard())
    elif query.data == "delete_info":
        if update.effective_user.id == admin_id:
            info = "Маалымат өчүрүлдү / Информация удалена"
            await query.edit_message_text("Маалымат өчүрүлдү / Информация удалена", reply_markup=get_menu_keyboard())
        else:
            await query.edit_message_text("Сиз администратор эмессиз! / Вы не администратор!", reply_markup=get_menu_keyboard())
    elif query.data == "add_channel":
        if update.effective_user.id == admin_id:
            await query.edit_message_text("Канал шилтемесин жазыңыз (мисалы, /add_channel @channelname) / Напишите ссылку на канал (например, /add_channel @channelname)", reply_markup=get_menu_keyboard())
        else:
            await query.edit_message_text("Сиз администратор эмессиз! / Вы не администратор!", reply_markup=get_menu_keyboard())
    elif query.data == "edit_channel":
        if update.effective_user.id == admin_id:
            if channels:
                await query.edit_message_text(f"Каналдар тизмеси / Список каналов:\n{channels}\nӨзгөртүү үчүн: /edit_channel @old_channel @new_channel", reply_markup=get_menu_keyboard())
            else:
                await query.edit_message_text("Каналдар тизмеси бош / Список каналов пуст", reply_markup=get_menu_keyboard())
        else:
            await query.edit_message_text("Сиз администратор эмессиз! / Вы не администратор!", reply_markup=get_menu_keyboard())
    elif query.data == "delete_channel":
        if update.effective_user.id == admin_id:
            if channels:
                await query.edit_message_text(f"Каналдар тизмеси / Список каналов:\n{channels}\nӨчүрүү үчүн: /delete_channel @channelname", reply_markup=get_menu_keyboard())
            else:
                await query.edit_message_text("Каналдар тизмеси бош / Список каналов пуст", reply_markup=get_menu_keyboard())
        else:
            await query.edit_message_text("Сиз администратор эмессиз! / Вы не администратор!", reply_markup=get_menu_keyboard())

# Фильм кошуу
async def add_film(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != admin_id:
        await update.message.reply_text("Сиз администратор эмессиз! / Вы не администратор!")
        return

    if update.message.document and update.message.text:
        try:
            command, code, title = update.message.text.split(maxsplit=2)
            if command == "/add_film":
                file = await update.message.document.get_file()
                file_path = file.file_path
                films[code] = title
                await update.message.reply_text(f"{language_dict[language]['film_added']} {code} - {title}", reply_markup=get_menu_keyboard())
        except ValueError:
            await update.message.reply_text(f"{language_dict[language]['invalid_format']}", reply_markup=get_menu_keyboard())

# Фильм өчүрүү
async def delete_film(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != admin_id:
        await update.message.reply_text("Сиз администратор эмессиз! / Вы не администратор!")
        return

    try:
        command, code = update.message.text.split()
        if command == "/delete_film" and code in films:
            del films[code]
            await update.message.reply_text(f"Кино өчүрүлдү: {code} / Фильм удалён: {code}", reply_markup=get_menu_keyboard())
        else:
            await update.message.reply_text("Мындай код табылган жок / Код не найден", reply_markup=get_menu_keyboard())
    except ValueError:
        await update.message.reply_text("Формат туура эмес! /delete_film K1234 деп жазыңыз / Неверный формат! Напишите /delete_film K1234", reply_markup=get_menu_keyboard())

# Маалымат кошуу/өзгөртүү
async def set_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != admin_id:
        await update.message.reply_text("Сиз администратор эмессиз! / Вы не администратор!")
        return

    try:
        command, *new_info = update.message.text.split(maxsplit=1)
        if command == "/set_info" and new_info:
            global info
            info = new_info[0]
            await update.message.reply_text("Маалымат кошулду / Информация добавлена", reply_markup=get_menu_keyboard())
        else:
            await update.message.reply_text("Формат туура эмес! /set_info Текст деп жазыңыз / Неверный формат! Напишите /set_info Текст", reply_markup=get_menu_keyboard())
    except:
        await update.message.reply_text("Маалыматты жазыңыз / Напишите информацию", reply_markup=get_menu_keyboard())

# Канал кошуу
async def add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != admin_id:
        await update.message.reply_text("Сиз администратор эмессиз! / Вы не администратор!")
        return

    try:
        command, channel = update.message.text.split()
        if command == "/add_channel":
            channels.append(channel)
            await update.message.reply_text(f"Канал кошулду: {channel} / Канал добавлен: {channel}", reply_markup=get_menu_keyboard())
    except ValueError:
        await update.message.reply_text("Формат туура эмес! /add_channel @channelname деп жазыңыз / Неверный формат! Напишите /add_channel @channelname", reply_markup=get_menu_keyboard())

# Канал өзгөртүү
async def edit_channel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != admin_id:
        await update.message.reply_text("Сиз администратор эмессиз! / Вы не администратор!")
        return

    try:
        command, old_channel, new_channel = update.message.text.split()
        if command == "/edit_channel" and old_channel in channels:
            index = channels.index(old_channel)
            channels[index] = new_channel
            await update.message.reply_text(f"Канал өзгөртүлдү: {old_channel} -> {new_channel} / Канал изменён: {old_channel} -> {new_channel}", reply_markup=get_menu_keyboard())
        else:
            await update.message.reply_text("Мындай канал табылган жок / Канал не найден", reply_markup=get_menu_keyboard())
    except ValueError:
        await update.message.reply_text("Формат туура эмес! /edit_channel @old_channel @new_channel деп жазыңыз / Неверный формат! Напишите /edit_channel @old_channel @new_channel", reply_markup=get_menu_keyboard())

# Канал өчүрүү
async def delete_channel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != admin_id:
        await update.message.reply_text("Сиз администратор эмессиз! / Вы не администратор!")
        return

    try:
        command, channel = update.message.text.split()
        if command == "/delete_channel" and channel in channels:
            channels.remove(channel)
            await update.message.reply_text(f"Канал өчүрүлдү: {channel} / Канал удалён: {channel}", reply_markup=get_menu_keyboard())
        else:
            await update.message.reply_text("Мындай канал табылган жок / Канал не найден", reply_markup=get_menu_keyboard())
    except ValueError:
        await update.message.reply_text("Формат туура эмес! /delete_channel @channelname деп жазыңыз / Неверный формат! Напишите /delete_channel @channelname", reply_markup=get_menu_keyboard())

# Язык словарь
language_dict = {
    "ky": {"film_added": "Фильм кошулду:", "invalid_format": "Формат туура эмес! /add_film K1234 \"Аты\" деп жазыңыз."},
    "ru": {"film_added": "Фильм добавлен:", "invalid_format": "Неверный формат! Напишите /add_film K1234 \"Название\"."}
}

# Error handler
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"Update {update} caused error {context.error}")

# Main функция
def main() -> None:
    application = Application.builder().token(TOKEN).build()

    # Команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add_film", add_film))
    application.add_handler(CommandHandler("delete_film", delete_film))
    application.add_handler(CommandHandler("set_info", set_info))
    application.add_handler(CommandHandler("add_channel", add_channel))
    application.add_handler(CommandHandler("edit_channel", edit_channel))
    application.add_handler(CommandHandler("delete_channel", delete_channel))

    # Callback query
    application.add_handler(CallbackQueryHandler(button))

    # Error handler
    application.add_error_handler(error)

    # Поллинг
    application.run_polling(timeout=30, read_timeout=30, connect_timeout=30)

if __name__ == "__main__":
    main()