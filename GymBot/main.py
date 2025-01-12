import telebot
import time
from telebot import types
from GymBot.privacy import TOKEN
from GymBot.buttons import *
from GymBot.messages import *

bot = telebot.TeleBot(TOKEN)


user_test_progress = {}


def generate_markup(buttons, include_back=True):
    markup = types.InlineKeyboardMarkup()
    for text, callback in buttons.items():
        btn = types.InlineKeyboardButton(text=text, callback_data=callback)
        markup.add(btn)
    if include_back:
        back_button = types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back", replay_markup=markup)
        markup.add(back_button)
    return markup


@bot.message_handler(commands=["start"])
def start(message):
    bot.set_my_commands([
        types.BotCommand("start", "Начать"),
    ])
    markup = types.InlineKeyboardMarkup()
    for text, callback in start_test.items():
        btn = types.InlineKeyboardButton(text=text, callback_data=callback)
        markup.add(btn)
    bot.send_message(message.chat.id, text=start_message, parse_mode="html", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "start")
def start(call):
    chat_id = call.message.chat.id
    user_test_progress[chat_id] = {"step": 1, "answers": {}}
    markup = generate_markup(age_buttons)
    bot.send_message(chat_id=chat_id, text=first_questions, parse_mode="html", reply_markup=markup)


def initialize_user(chat_id):
    if chat_id not in user_test_progress:
        user_test_progress[chat_id] = {"step": 1, "answers": {}}


@bot.callback_query_handler(func=lambda call: call.data in age_buttons.values())
def process_age(call):
    chat_id = call.message.chat.id
    initialize_user(chat_id)

    answer = call.data
    user_test_progress[chat_id]["answers"]["age"] = answer

    question = second_questions["experience_question"]
    markup = generate_markup(gym_experience)
    user_test_progress[chat_id]["step"] += 1
    bot.edit_message_text(text=question, chat_id=chat_id, message_id=call.message.message_id, parse_mode="html",
                          reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in gym_experience.values())
def process_experience(call):
    chat_id = call.message.chat.id
    initialize_user(chat_id)

    answer = call.data
    user_test_progress[chat_id]["answers"]["experience"] = answer

    question = third_questions["test_question"]
    markup = generate_markup(test_buttons)
    user_test_progress[chat_id]["step"] += 1
    bot.edit_message_text(text=question, chat_id=chat_id, message_id=call.message.message_id, parse_mode="html",
                          reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in test_buttons.values())
def process_goal(call):
    chat_id = call.message.chat.id
    initialize_user(chat_id)
    answer = call.data
    user_test_progress[chat_id]["answers"]["goal"] = answer

    analyzing_message = bot.send_message(chat_id, text="Анализирую ваши ответы.")
    time.sleep(1)
    bot.edit_message_text(chat_id=chat_id, message_id=analyzing_message.message_id, text="Анализирую ваши ответы..")
    time.sleep(1)
    bot.edit_message_text(chat_id=chat_id, message_id=analyzing_message.message_id, text="Анализирую ваши ответы...")
    bot.delete_message(chat_id, message_id=analyzing_message.message_id)
    analyze_answers(chat_id, call)


def analyze_answers(chat_id, call):
    answers = user_test_progress[chat_id]["answers"]

    age = answers.get("age")
    if age is None:
        bot.send_message(chat_id, "Ошибка: возраст не был выбран.")
        return

    experience = answers.get("experience")
    if experience is None:
        bot.send_message(chat_id, "Ошибка: опыт тренировок не был выбран.")
        return

    goal = answers.get("goal")
    if goal is None:
        bot.send_message(chat_id, "Ошибка: цель не была выбрана.")
        return

    if goal == "lose_weight":
        with (open("C:/Users/Александр/PycharmProjects/pythonProject4/weight_loss_program.pdf", "rb") as pdf_file):
            bot.send_document(chat_id, pdf_file, caption="Вот ваша программа для похудения!")
    elif goal in ["gain_mass", "strengthen_body"]:
        question = final_text["choose_program"]
        markup = generate_markup(menu_btn)
        bot.edit_message_text(text=question, chat_id=chat_id, message_id=call.message.message_id,
                              parse_mode="html", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in menu_btn.values())
def send_program(call):
    program = call.data
    if program == "split":
        with open("C:/Users/Александр/PycharmProjects/pythonProject4/split_training.pdf", "rb") as pdf_file:
            bot.send_document(call.message.chat.id, pdf_file, caption="Вот ваша программа сплит тренировки!")
    elif program == "fullbody":
        with open("C:/Users/Александр/PycharmProjects/pythonProject4/fullbody_training.pdf",
                  "rb") as pdf_file:
            bot.send_document(call.message.chat.id, pdf_file, caption="Вот ваша программа фуллбоди тренировки!")


@bot.callback_query_handler(func=lambda call: call.data == "back")
def go_back(call):
    global question, markup
    user_id = call.message.chat.id
    if user_id in user_test_progress:
        progress = user_test_progress[user_id]
        step = progress["step"]

        if step > 1:
            progress["step"] -= 1

        if step == 2:
            question = first_questions["age_question"]
            markup = generate_markup(age_buttons, include_back=False)
        elif step == 3:
            question = second_questions["experience_question"]
            markup = generate_markup(gym_experience)
        elif step == 4:
            question = third_questions["test_question"]
            markup = generate_markup(test_buttons)
        elif step == 5:
            question = final_text["choose_program"]
            markup = generate_markup(menu_btn)

        bot.edit_message_text(text=question, chat_id=call.message.chat.id,  message_id=call.message.message_id,
                              parse_mode="html",  reply_markup=markup)


def startBot():
    print("Gym Bot is started and ready to work.")
    bot.polling(none_stop=True, interval=0)