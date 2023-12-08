import os.path
import time
import datetime
import pytz

import telebot
from telebot import types

separator = os.path.sep

with open(f"Tokens{separator}tokens.txt") as file:
    file_str = file.readlines()
    token_main = file_str[0].split()[1]

main_bot = telebot.TeleBot(token_main)

stations = ["Kosmonavtov_Avenue", "Uralmash", "Mashinostroiteley", "Uralskaya", "Dinamo", "Square_of_1905",
            "Geologicheskaya", "Chkalovskaya", "Botanicheskaya"]
stations_rus = ["Проспект космонавтов", "Уралмаш", "Машиностроителей", "Уральская", "Динамо", "Площадь 1905 года",
                "Геологическая", "Чкаловская", "Ботаническая"]

months = ["Января", "Февраля", "Марта", "Апреля", "Мая", "Июня", "Июля", "Августа", "Сентября", "Октября", "Ноября",
          "Декабря"]

global start_station
global finish_station
global edit_message_id


@main_bot.message_handler(commands=['start'])
def start_func(message):
    """
    Функция для обработки команды /start
    :param message: Получает message от декоратора.
    :return: None

    """
    global edit_message_id

    with open("BD" + separator + "users.txt", "r+", encoding="utf-8") as user_file:
        users = user_file.readlines()
        flag = False
        for line in users:
            if message.from_user.username in line:
                flag = True
                break

        city_p = pytz.timezone("Asia/Yekaterinburg")
        city_day = datetime.datetime.now().astimezone(city_p).strftime("%d")
        city_month = months[datetime.datetime.now().astimezone(city_p).month - 1]

        if not flag:
            user_file.write("@" + message.from_user.username + f" Зарегистрирован {city_day} {city_month}\n")

    marcup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    menu_button = types.KeyboardButton("Меню")
    marcup.row(menu_button)

    main_bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name} {message.from_user.last_name}!\n"
                                           f"Я бот, который будет помогать тебе быстро узнать ближайшие поезда для твоей "
                                           f"станции метро.\n"
                                           f"Приятного использования!", reply_markup=marcup)

    menu_func(message)
    return None


@main_bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    """
    Функция для обработки действий в кнопках меню.
    :param callback: Получает callback от декоратора.
    :return: None

    """
    global start_station
    global finish_station

    if callback.data in stations:
        start_station = callback.data
        marcup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton("Проспект космонавтов", callback_data="start")
        button2 = types.InlineKeyboardButton("Ботаническая", callback_data="finish")
        back_button = types.InlineKeyboardButton("<- Назад", callback_data="back")
        marcup.row(button1, button2)
        marcup.add(back_button)

        if start_station == "Kosmonavtov_Avenue":
            finish_station = "Ботаническая"
            send_schedule(callback.message)
        elif start_station == "Botanicheskaya":
            finish_station = "Проспект Космонавтов"
            send_schedule(callback.message)
        else:
            main_bot.edit_message_text("Выберите сторону, куда вы планируете ехать", callback.message.chat.id,
                                       callback.message.message_id, reply_markup=marcup)

    elif callback.data == "back":
        menu_func(callback.message)
    else:
        if callback.data == "start":
            finish_station = "Проспект Космонавтов"
        else:
            finish_station = "Ботаническая"
        send_schedule(callback.message)
        menu_func(callback.message)


@main_bot.message_handler()
def user_say_func(message):
    """
    Обработка сообщений пользователя.
    :param message: Получает message от декоратора.
    :return: None

    """

    if message.text.lower() == "меню":
        menu_func(message)


def send_schedule(message):
    """
    Отправляет сообщение с расписанием, которое имеет следующий формат:

    `Сегодня [Число Месяц], [ДЕНЬ НЕДЕЛИ]`
    `Текущее точное время [Часы:Минуты]`

    `Расписание ближайших поездов в Рабочие дни со станции [Начальная станция] в сторону станции [Финальная станция]:`
        `1. [Часы:Минуты] - осталось [Минут до поезда] минут`
        `2. [Часы:Минуты] - осталось [Минут до поезда] минут`
        `3. [Часы:Минуты] - осталось [Минут до поезда] минут`

    `Расписание ближайших поездов в Выходные дни со станции [Начальная станция] в сторону станции [Финальная станция]:`
        `1. [Часы:Минуты] - осталось [Минут до поезда] минут`
        `2. [Часы:Минуты] - осталось [Минут до поезда] минут`
        `3. [Часы:Минуты] - осталось [Минут до поезда] минут`
    :param message: Необходимо передать сообщение, из которого было вызвано действие с меню.
    :return: None

    """
    try:
        global edit_message_id
        global start_station
        global finish_station

        with open(f"BD{separator}" + f"{start_station}.txt", encoding="utf-8") as file:
            hours = int(datetime.datetime.now(pytz.utc).strftime("%H")) + 5
            if hours >= 25:
                hours -= 24
            minutes = int(datetime.datetime.now().strftime("%M"))
            now_time = hours * 60 + minutes

            if hours >= 24:
                hours -= 24
            if hours < 10:
                hours = "0" + str(hours)
            if minutes < 10:
                minutes = "0" + str(minutes)

            bot_message = "🤔"

            edit_message_id = message.message_id + 1
            main_bot.edit_message_text(bot_message, message.chat.id, edit_message_id)
            time.sleep(1)

            week_day = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

            city_p = pytz.timezone("Asia/Yekaterinburg")
            city_day = datetime.datetime.now().astimezone(city_p).strftime("%d")
            city_month = months[datetime.datetime.now().astimezone(city_p).month - 1]
            city_week_day = week_day[datetime.datetime.today().astimezone(city_p).weekday()]

            bot_message = f"Сегодня {city_day} {city_month}, <b>{city_week_day.upper()}</b>\nТекущее точное время {hours}:{minutes}\n"

            my_file = file.readlines()

            for i in range(len(my_file)):
                if finish_station in my_file[i]:
                    trains_time = my_file[i + 1].split()
                    count_trains = 0
                    for k in range(len(trains_time)):
                        if int(trains_time[k]) > now_time:
                            train_hour = int(trains_time[k]) // 60
                            train_minutes = int(trains_time[k]) % 60

                            if train_hour >= 24:
                                train_hour -= 24

                            if train_hour < 10:
                                train_hour = "0" + str(train_hour)
                            if train_minutes < 10:
                                train_minutes = "0" + str(train_minutes)

                            if count_trains == 0:
                                if (city_week_day == "Суббота") or (city_week_day == "Воскресенье"):
                                    if my_file[i].split()[0] == "Выходные":
                                        bot_message += f"<b>\nРасписание ближайших поездов в <i>{my_file[i].split()[0].upper()} {my_file[i].split()[1].upper()}</i> со станции {stations_rus[stations.index(start_station)]} в сторону станции {finish_station}:</b>\n"
                                    else:
                                        bot_message += f"\nРасписание ближайших поездов в {my_file[i].split()[0]} {my_file[i].split()[1]} со станции {stations_rus[stations.index(start_station)]} в сторону станции {finish_station}:\n"
                                else:
                                    if my_file[i].split()[0] == "Рабочие":
                                        bot_message += f"<b>\nРасписание ближайших поездов в <i>{my_file[i].split()[0].upper()} {my_file[i].split()[1].upper()}</i> со станции {stations_rus[stations.index(start_station)]} в сторону станции {finish_station}:</b>\n"
                                    else:
                                        bot_message += f"\nРасписание ближайших поездов в {my_file[i].split()[0]} {my_file[i].split()[1]} со станции {stations_rus[stations.index(start_station)]} в сторону станции {finish_station}:\n"

                            count_trains += 1

                            if (city_week_day == "Суббота") or (city_week_day == "Воскресенье"):
                                if my_file[i].split()[0] == "Выходные":
                                    bot_message += f"   <b>{count_trains}. В {train_hour}:{train_minutes} - осталось {int(trains_time[k]) - now_time} минут(ы)</b>\n"
                                else:
                                    bot_message += f"   {count_trains}. В {train_hour}:{train_minutes} - осталось {int(trains_time[k]) - now_time} минут(ы)\n"
                            else:
                                if my_file[i].split()[0] == "Рабочие":
                                    bot_message += f"   <b>{count_trains}. В {train_hour}:{train_minutes} - осталось {int(trains_time[k]) - now_time} минут(ы)</b>\n"
                                else:
                                    bot_message += f"   {count_trains}. В {train_hour}:{train_minutes} - осталось {int(trains_time[k]) - now_time} минут(ы)\n"

                            if count_trains == 3:
                                break

            main_bot.edit_message_text(bot_message, message.chat.id, edit_message_id, parse_mode="html")

    except telebot.apihelper.ApiTelegramException:
        pass


def menu_func(message):
    """
    Создание или изменение меню.
    :param message: Необходимо передать сообщение, из которого было вызвано действие с меню.
    :return: None

    """
    global edit_message_id

    marcup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("Проспект космонавтов", callback_data="Kosmonavtov_Avenue")
    button2 = types.InlineKeyboardButton("Уралмаш", callback_data="Uralmash")
    button3 = types.InlineKeyboardButton("Машиностроителей", callback_data="Mashinostroiteley")
    button4 = types.InlineKeyboardButton("Уральская", callback_data="Uralskaya")
    button5 = types.InlineKeyboardButton("Динамо", callback_data="Dinamo")
    button6 = types.InlineKeyboardButton("Площадь 1905 года", callback_data="Square_of_1905")
    button7 = types.InlineKeyboardButton("Геологическая", callback_data="Geologicheskaya")
    button8 = types.InlineKeyboardButton("Чкаловская", callback_data="Chkalovskaya")
    button9 = types.InlineKeyboardButton("Ботаническая", callback_data="Botanicheskaya")

    marcup.row(button1, button2, button3)
    marcup.row(button4, button5, button6)
    marcup.row(button7, button8, button9)
    try:
        main_bot.edit_message_text("Выберите станцию с которой планируете ехать:", message.chat.id,
                                   message.message_id, reply_markup=marcup)
    except telebot.apihelper.ApiTelegramException:
        main_bot.send_message(message.chat.id, "Выберите станцию с которой планируете ехать", reply_markup=marcup)
        main_bot.send_message(message.chat.id, "👋")
        edit_message_id = message.message_id + 2


if __name__ == '__main__':
    print("Bot started!")
    main_bot.infinity_polling()
