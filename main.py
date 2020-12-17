import telebot
import config
import json
import random

from telebot import types

bot = telebot.TeleBot(config.TOKEN)

adm_functions = ['Рассылка', 'Провести опрос', 'Просмотреть БД']
amount = 4


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Сравнить")
    item2 = types.KeyboardButton("Просмотреть рейтинг")
    # item3 = types.KeyboardButton("Пожаловаться")
    markup.add(item1, item2)
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


# @bot.message_handler(commands=['admin'])
# def admin(message):
#     if message.from_user.id == 1064282294:
#         markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#         for function in adm_functions:
#             item = types.KeyboardButton(function)
#             markup.add(item)
#         item = types.KeyboardButton("Назад ➤")
#         markup.add(item)
#         sent = bot.send_message(message.chat.id, "Что бы Вы хотели сделать?", reply_markup=markup)
#         bot.register_next_step_handler(sent, admin_after)
#     else:
#         bot.send_message(message.chat.id, "У Вас недостаточно прав для использования этой функции.")
#
#
# def admin_after(message):
#     markup = back_markup()
#     if message.from_user.id == 1064282294:
#         if message.text == "Рассылка":
#             sent = bot.send_message(message.chat.id, "Какое сообщение Вы хотите разослать?")
#             bot.register_next_step_handler(sent, mailing)
#         elif message.text == "Просмотреть БД":
#             Person(message).show_database()
#         elif message.text == 'Провести опрос':
#             sent = bot.send_message(message.chat.id, "Опрос на какую тему Вы хотите провести?")
#             bot.register_next_step_handler(sent, mailing, arguments=True)
#         elif message.text == "Назад ➤":
#             bot.send_message(message.chat.id, "Принято.", reply_markup=markup)
#     else:
#         bot.send_message(message.chat.id, "У Вас недостаточно прав для использования этой функции.",
#                          reply_markup=markup)


@bot.message_handler(content_types=['text'])
def chat(message):
    if message.chat.type == 'private':
        if message.text == "Сравнить":
            compare(message)
        elif message.text == "Просмотреть рейтинг":
            show_rating(message)
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("Сравнить")
            item2 = types.KeyboardButton("Просмотреть рейтинг")
            markup.add(item1, item2)
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
        int1_prev = int1
        int1, int2 = check(data, message.from_user.id, int1, int1_prev)
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


def check(data, user_id, int1, int1_prev, crutch=None):
    if int1 == int1_prev and crutch is not None:
        return None
    int2 = 0
    if int1 == int2:
        # if int2 == amount-1:
        #     int2 = 0
        int2 += 1
    user_id = str(user_id)
    for i in data[user_id][str(int1)]:
        if int2 == i or int1 == int2:
            if int2 == amount - 1:
                if int1 == amount - 1:
                    int1 = 0
                    crutch = True
                int1, int2 = check(data, user_id, int1 + 1, int1_prev, crutch)
                break
            int2 += 1
    if int1 == int2:
        int1 = None
    return int1, int2


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
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Сравнить")
    item2 = types.KeyboardButton("Просмотреть рейтинг")
    markup.add(item1, item2)
    bot.send_message(message.chat.id, "Принято.", reply_markup=markup)


def write_database(data, filename):
    with open(filename, "w", encoding="UTF-8") as database:
        json.dump(data, database, indent=1, ensure_ascii=False, separators=(',', ':'))


bot.polling(none_stop=True)
