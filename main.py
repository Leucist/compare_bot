import telebot
import config
import json
import random

from telebot.apihelper import ApiException
from telebot import types

bot = telebot.TeleBot(config.TOKEN)

amount = 4
adm_functions = ['Рассылка', 'Отправить сообщение-вопрос', 'Просмотреть БД']
admin_id = "id (int)"


@bot.message_handler(commands=['start'])
def start(message):
    markup = back_markup()
    personalise(message)
    bot.send_message(message.chat.id,
                     "Привет, {0.first_name}!\nЯ - <b>{1.first_name}</b>, чат-бот, который создан для формирования рейтинга на основе попарного сравнения фото.".format(
                         message.from_user, bot.get_me()), parse_mode='html', reply_markup=markup)


def personalise(message):
    with open("userbase.json", "r", encoding="UTF-8") as database:
        data = json.loads(database.read())
        if str(message.from_user.id) not in data:
            user_list = {}
            for i in range(amount):
                user_list[str(i)] = []
            data[message.from_user.id] = user_list
            write_database(data, "userbase.json")


@bot.message_handler(commands=['admin'])
def admin(message):
    if message.from_user.id == admin_id:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for function in adm_functions:
            item = types.KeyboardButton(function)
            markup.add(item)
        item = types.KeyboardButton("Назад ➤")
        markup.add(item)
        sent = bot.send_message(admin_id, "Что бы Вы хотели сделать?", reply_markup=markup)
        bot.register_next_step_handler(sent, admin_after)
    else:
        bot.send_message(message.chat.id, "У Вас недостаточно прав для использования этой функции.")


def admin_after(message):
    markup = back_markup()
    if message.from_user.id == admin_id:
        if message.text == "Рассылка":
            sent = bot.send_message(message.chat.id, "Какое сообщение Вы хотите разослать?")
            bot.register_next_step_handler(sent, mailing)
        elif message.text == "Просмотреть БД":
            show_database()
        elif message.text == "Отправить сообщение-вопрос":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("Всем")
            item2 = types.KeyboardButton("Выбрать пользователя")
            markup.add(item1, item2)
            sent = bot.send_message(message.chat.id,
                                    "Разослать опрос всем пользователям или выбрать конкретного пользователя?",
                                    reply_markup=markup)
            bot.register_next_step_handler(sent, admin_after)
        elif message.text.lower() == 'всем':
            sent = bot.send_message(message.chat.id, "Опрос на какую тему Вы хотите провести?", reply_markup=None)
            bot.register_next_step_handler(sent, mailing, arguments=True)
        elif message.text == 'Выбрать пользователя':
            sent = bot.send_message(message.chat.id, "Выберите желаемого пользователя и отправьте его id",
                                    reply_markup=None)
            bot.register_next_step_handler(sent, q_user)
        elif message.text == "Назад ➤":
            bot.send_message(message.chat.id, "Принято.", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "У Вас недостаточно прав для использования этой функции.",
                         reply_markup=markup)


@bot.message_handler(content_types=['text'])
def chat(message):
    if message.chat.type == 'private':
        if message.text == "Сравнить":
            compare(message)
        elif message.text == "Просмотреть рейтинг":
            show_rating(message)
        else:
            markup = back_markup()
            bot.send_message(message.chat.id, "Неопознанная команда...\nЯ лишь бот, имитация жизни!")
            ph1 = open("photos/pik4.jpg", "rb")
            bot.send_photo(message.chat.id, ph1, caption="Лучше выбери одну из кнопок:", reply_markup=markup)


def show_rating(message):
    result = ""
    list_m = []
    with open("models.json", "r", encoding="UTF-8") as database:
        data = json.loads(database.read())
        for model_id in data:
            list_m.append(data[model_id]["rating"])
        list_m = sorted(list_m, reverse=True)
        for i in range(amount):
            for model_id in data:
                model = data[model_id]
                if model["rating"] == list_m[i]:
                    result += str(i + 1) + ". " + model["name"] + " " + model["surname"] + ". Рейтинг: " + str(
                        model["rating"]) + ";\n"
    bot.send_message(message.chat.id, result)


def compare(message):
    with open("userbase.json", "r", encoding="UTF-8") as database:
        data = json.loads(database.read())
        try:
            couple_list = data[str(message.from_user.id)]
            del couple_list
        except KeyError:
            personalise(message)
            compare(message)
            return 0
        int1 = random.randint(0, amount - 1)
        int2 = random.randint(0, amount - 1)
        if int1 == int2:
            if int2 == amount - 1:
                int2 = 0
            else:
                int2 += 1
        int1_prev = int1
        int2_prev = int2
        int1, int2 = check(data, message.from_user.id, int1, int1_prev, int2, int2_prev)
        if int1 is None:
            achievement = open("photos/achievement.jpg", "rb")
            bot.send_message(message.chat.id, "[ошибка] Вы оценили всех. Серьезно, всех!")
            bot.send_photo(message.chat.id, achievement, caption="Лови ачивку :Р")
            return 0
        data[str(message.from_user.id)][str(int1)].append(int2)
        data[str(message.from_user.id)][str(int1)].sort()  # мб лучше sorted([...])
        data[str(message.from_user.id)][str(int2)].append(int1)
        data[str(message.from_user.id)][str(int2)].sort()  # ________^
        write_database(data, "userbase.json")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("1")
        item2 = types.KeyboardButton("2")
        markup.add(item1, item2)
        ph1 = open("photos/" + str(int1) + ".jpg", "rb")
        ph2 = open("photos/" + str(int2) + ".jpg", "rb")
        photos = [types.InputMediaPhoto(ph1),
                  types.InputMediaPhoto(ph2)]
        bot.send_media_group(message.chat.id, photos)
        sent = bot.send_message(message.chat.id, "Какую ты считаешь более привлекательной?", reply_markup=markup)
        bot.register_next_step_handler(sent, choose, [int1, int2])


def check(data, user_id, int1, int1_prev, int2, int2_prev, crutch=None):
    if int1 == int2:
        if int2 == amount - 1:
            int2 = 0
        else:
            int2 += 1

    user_id = str(user_id)
    repeated = ch_a(data[user_id], int1, int2)
    while not repeated:
        if int1 == int1_prev and int2 == int2_prev and crutch is not None:
            int1 = None
            return int1, int2

        if int2 == amount - 1:
            if int1 == amount - 1:
                int1 = 0
                crutch = True
            int1 += 1
            int2 = 0
            repeated = ch_a(data[user_id], int1, int2)
            continue
        int2 += 1
        if int1 == int2:
            continue
        repeated = ch_a(data[user_id], int1, int2)
    return int1, int2


def ch_a(data, int1, int2):
    for i in data[str(int1)]:
        if int2 == i:
            return False
    return True


def choose(message, couple):
    K = 16
    if message.text == "1":
        Sa = 1
        Sb = 0
    elif message.text == "2":
        Sa = 0
        Sb = 1
    else:
        bot.send_message(message.chat.id, "Неверный формат ответа")
        sent = bot.send_message(message.chat.id, "Попробуй еще раз. Какую ты считаешь более привлекательной? ['1'/'2']")
        bot.register_next_step_handler(sent, choose, couple)
        return 0
    with open("models.json", "r", encoding="UTF-8") as database:
        data = json.loads(database.read())
        Ra = data[str(couple[0])]["rating"]
        Rb = data[str(couple[1])]["rating"]

        Ea = 1 / (1 + pow(10, (Rb - Ra) / 400))
        Ra_n = Ra + K * (Sa - Ea)
        Eb = 1 / (1 + pow(10, (Ra - Rb) / 400))
        Rb_n = Rb + K * (Sb - Eb)

        data[str(couple[0])]["rating"] = Ra_n
        data[str(couple[1])]["rating"] = Rb_n

        write_database(data, "models.json")
    markup = back_markup()
    bot.send_message(message.chat.id, "Принято.", reply_markup=markup)


def back_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Сравнить")
    item2 = types.KeyboardButton("Просмотреть рейтинг")
    # item3 = types.KeyboardButton("Пожаловаться")
    markup.add(item1, item2)
    return markup


def write_database(data, filename):
    with open(filename, "w", encoding="UTF-8") as database:
        json.dump(data, database, indent=1, ensure_ascii=False, separators=(',', ':'))


def show_database():
    filename = "filename"  # чисто на всякий~
    try:
        filename = "userbase.json"
        with open(filename, "r", encoding="UTF-8") as database_file:
            bot.send_document(admin_id, database_file)
        filename = "models.json"
        with open(filename, "r", encoding="UTF-8") as database_file:
            bot.send_document(admin_id, database_file)
    except FileNotFoundError:
        bot.send_message(admin_id, '[Ошибка] Файл БД "' + filename + '"не найден.', reply_markup=None)


def q_user(message):
    try:
        user_id = int(message.text.strip())
    except ValueError:
        markup = back_markup()
        bot.send_message(admin_id,
                         "Ошибка: Неверный формат id.\nПроверьте правильность введенных данных и попробуйте снова.",
                         reply_markup=markup)
        return 1
    else:
        sent = bot.send_message(admin_id, "Какой вопрос Вы хотели бы задать?\n(Отправьте его следующим сообщением)")
        bot.register_next_step_handler(sent, mailing, arguments=True, user_id=user_id)


def mailing(message, arguments=None, user_id=None):
    markup = back_markup()
    with open("userbase.json", "r", encoding="UTF-8") as database:
        data = json.loads(database.read())
        if arguments:
            if user_id is not None:
                try:
                    sent = bot.send_message(user_id, message.text, reply_markup=markup)
                    bot.register_next_step_handler(sent, feedback, message.text)
                except ApiException:
                    bot.send_message(admin_id,
                                     "Вопрос не был отправлен, т.к. пользователь заблокировал бота или отправка сообщений ему невозможна.",
                                     reply_markup=markup)
                finally:
                    return 0
            for u_id in data:
                try:
                    if int(u_id) != message.from_user.id:
                        sent = bot.send_message(u_id, message.text, reply_markup=markup)
                        bot.register_next_step_handler(sent, feedback, message.text)
                    else:
                        bot.send_message(message.chat.id, "Принято.", reply_markup=markup)
                except ApiException:
                    continue
                else:
                    continue
            return 0
        if message.content_type == 'text':
            for u_id in data:
                try:
                    if int(u_id) != message.from_user.id:
                        bot.send_message(u_id, message.text, reply_markup=markup)
                    else:
                        bot.send_message(message.chat.id, "Принято.", reply_markup=markup)
                except ApiException:
                    continue
                else:
                    continue
            bot.send_message(message.chat.id, "Разослано.", reply_markup=markup)
        elif message.content_type == 'photo':
            raw = message.photo[2].file_id
            name = "mailing.jpg"
            file_info = bot.get_file(raw)
            downloaded_file = bot.download_file(file_info.file_path)
            with open(name, "wb") as photo:
                photo.write(downloaded_file)
            for u_id in data:
                photo = open(name, "rb")
                try:
                    if int(u_id) != message.from_user.id:
                        bot.send_photo(u_id, photo, reply_markup=markup)
                    else:
                        bot.send_message(message.chat.id, "Принято.", reply_markup=markup)
                except ApiException:
                    photo.close()
                    continue
                else:
                    photo.close()
                    continue
            bot.send_message(message.chat.id, "Разослано.", reply_markup=markup)
        elif message.content_type == 'document':
            raw = message.document.file_id
            name = "mailing" + message.document.file_name[-4:]
            file_info = bot.get_file(raw)
            downloaded_file = bot.download_file(file_info.file_path)
            with open(name, "wb") as document:
                document.write(downloaded_file)
            for u_id in data:
                document = open(name, "rb")
                try:
                    if int(u_id) != message.from_user.id:
                        bot.send_document(u_id, document, reply_markup=markup)
                    else:
                        bot.send_message(message.chat.id, "Принято.", reply_markup=markup)
                except ApiException:
                    document.close()
                    continue
                else:
                    document.close()
                    continue
            bot.send_message(message.chat.id, "Разослано.", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Неподдерживаемый тип сообщения", reply_markup=markup)


def feedback(message, question):
    bot.send_message(admin_id,
                     'Ответ на Ваш вопрос "' + question + '" — "' + message.text + '" от:\n(id) ' + str(
                         message.from_user.id) + ',\n(name) '
                     + str(message.from_user.first_name))
    bot.send_message(message.chat.id, "Принято.\nБлагодарим за ответ!)")


bot.polling(none_stop=True)
