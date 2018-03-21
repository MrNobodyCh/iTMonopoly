# -*- coding: utf-8 -*-
import re
import sys
import time
import logging

from datetime import datetime

import telebot

import texts

from getters import DBGetter, EMailGetter
from config import BotSettings, DBSettings

reload(sys)
sys.setdefaultencoding('utf-8')

logging.basicConfig(filename='logs/debug.log', level=logging.INFO,
                    format="%(asctime)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S %p")

bot = telebot.TeleBot(BotSettings.TOKEN)
async_bot = telebot.AsyncTeleBot(BotSettings.TOKEN)
types = telebot.types


@bot.message_handler(commands=["start"])
def greeting_menu(message):
    user_id = message.chat.id
    first_name = message.chat.first_name
    main_menu_buttons(user_id, texts.GREETING % first_name)
    DBGetter(DBSettings.HOST).insert(execution="INSERT INTO users (user_id, first_name) SELECT %s, %s "
                                               "WHERE NOT EXISTS (SELECT user_id FROM users WHERE user_id = %s)",
                                     values=(user_id, first_name, user_id))


@bot.message_handler(content_types=['text'], func=lambda message: message.text == texts.BACK_TO_MAIN_MENU)
def back_to_main_menu(message):
    user_id = message.chat.id
    main_menu_buttons(user_id, texts.MAIN_MENU)


@bot.message_handler(commands=["courses"])
def courses_command(message):
    courses_menu(message)


@bot.message_handler(commands=["events"])
def events_command(message):
    events_view(message)


@bot.message_handler(commands=["contacts"])
def contacts_command(message):
    contacts_menu(message)


@bot.message_handler(commands=["about"])
def about_command(message):
    about_menu(message)


@bot.message_handler(content_types=['text'], func=lambda message: message.text == texts.COURSES)
def courses_menu(message):
    user_id = message.chat.id
    markup = types.InlineKeyboardMarkup()
    markup_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.InlineKeyboardButton(text=texts.COURSES_FOR_KIDS, callback_data="courses_kids"))
    markup.add(types.InlineKeyboardButton(text=texts.COURSES_FOR_ADULT, callback_data="courses_adult"))
    bot.send_message(user_id, text=texts.KINDS_OF_COURSES, reply_markup=markup)
    is_subscribe = DBGetter(DBSettings.HOST).get("SELECT is_subscribed_to_courses "
                                                 "FROM users WHERE user_id = %s" % user_id)[0][0]
    if is_subscribe is False:
        markup_keyboard.row(texts.SUBSCRIBE_TO_NEW_COURSES)
        markup_keyboard.row(texts.BACK_TO_MAIN_MENU)
        bot.send_message(user_id, text=texts.YOU_CAN_SUBSCRIBE_TO_COURSES, reply_markup=markup_keyboard)
    if is_subscribe is True:
        markup_keyboard.row(texts.UNSUBSCRIBE_TO_NEW_COURSES)
        markup_keyboard.row(texts.BACK_TO_MAIN_MENU)
        bot.send_message(user_id, text=texts.YOU_CAN_UNSUBSCRIBE_TO_COURSES, reply_markup=markup_keyboard)


@bot.message_handler(content_types=['text'], func=lambda message: message.text == texts.CONTACTS)
def contacts_menu(message):
    user_id = message.chat.id
    bot.send_message(user_id, text=texts.CONTACTS_TEXT, parse_mode="Markdown")
    bot.send_venue(user_id, title=texts.MAIN_STAGE_TITLE, address=texts.MAIN_STAGE_ADDRESS,
                   latitude=55.760312, longitude=37.664644)
    bot.send_venue(user_id, title=texts.SECOND_STAGE_TITLE, address=texts.SECOND_STAGE_ADDRESS,
                   latitude=55.783157, longitude=37.594732)


@bot.message_handler(content_types=['text'], func=lambda message: message.text == texts.ABOUT)
def about_menu(message):
    user_id = message.chat.id
    bot.send_message(user_id, text=texts.ABOUT_TEXT, parse_mode="Markdown")


@bot.message_handler(content_types=['text'], func=lambda message: message.text in [texts.SUBSCRIBE_TO_NEW_COURSES,
                                                                                   texts.UNSUBSCRIBE_TO_NEW_COURSES,
                                                                                   texts.SUBSCRIBE_TO_NEW_EVENTS,
                                                                                   texts.UNSUBSCRIBE_TO_NEW_EVENTS])
def subscribe_worker(message):
    user_id = message.chat.id
    markup_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if message.text == texts.SUBSCRIBE_TO_NEW_COURSES:
        DBGetter(DBSettings.HOST).insert("UPDATE users SET is_subscribed_to_courses = TRUE "
                                         "WHERE user_id = %s" % user_id)
        markup_keyboard.row(texts.UNSUBSCRIBE_TO_NEW_COURSES)
        markup_keyboard.row(texts.BACK_TO_MAIN_MENU)
        bot.send_message(user_id, texts.YOU_SUBSCRIBED_TO_COURSES, reply_markup=markup_keyboard)

    if message.text == texts.UNSUBSCRIBE_TO_NEW_COURSES:
        DBGetter(DBSettings.HOST).insert("UPDATE users SET is_subscribed_to_courses = FALSE "
                                         "WHERE user_id = %s" % user_id)
        markup_keyboard.row(texts.SUBSCRIBE_TO_NEW_COURSES)
        markup_keyboard.row(texts.BACK_TO_MAIN_MENU)
        bot.send_message(user_id, texts.YOU_UNSUBSCRIBED_FROM_COURSES, reply_markup=markup_keyboard)

    if message.text == texts.SUBSCRIBE_TO_NEW_EVENTS:
        DBGetter(DBSettings.HOST).insert("UPDATE users SET is_subscribed_to_events = TRUE "
                                         "WHERE user_id = %s" % user_id)
        markup_keyboard.row(texts.UNSUBSCRIBE_TO_NEW_EVENTS)
        markup_keyboard.row(texts.BACK_TO_MAIN_MENU)
        bot.send_message(user_id, texts.YOU_SUBSCRIBED_TO_EVENTS, reply_markup=markup_keyboard)

    if message.text == texts.UNSUBSCRIBE_TO_NEW_EVENTS:
        DBGetter(DBSettings.HOST).insert("UPDATE users SET is_subscribed_to_events = FALSE "
                                         "WHERE user_id = %s" % user_id)
        markup_keyboard.row(texts.SUBSCRIBE_TO_NEW_EVENTS)
        markup_keyboard.row(texts.BACK_TO_MAIN_MENU)
        bot.send_message(user_id, texts.YOU_UNSUBSCRIBED_FROM_EVENTS, reply_markup=markup_keyboard)


paginate_courses = {}
paginate_events = {}


def chunk_it(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out


@bot.callback_query_handler(func=lambda call: call.data.split("_")[0] == "courses")
def courses_view(call):
    user_id = call.message.chat.id
    courses = DBGetter(DBSettings.HOST).get("SELECT id, title, cost, image FROM courses "
                                            "WHERE course_type = '%s' ORDER BY id DESC " % call.data.split("_")[1])
    paginate_courses[user_id] = courses
    try:
        for course in chunk_it(paginate_courses.get(user_id),
                               float('%.1f' % len(paginate_courses.get(user_id))) / 1)[0]:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(text=texts.READ_MORE, callback_data="more_%s_%s" % (course[0], 1)))
            row = [types.InlineKeyboardButton(u"\u27A1", callback_data=">>_%s_courses" % 1)]
            markup.row(*row)
            bot.send_photo(user_id, photo=course[3], caption="*%s*\n\n_%s_" % (course[1], course[2]),
                           reply_markup=markup, disable_notification=True, parse_mode="Markdown")
            bot.answer_callback_query(call.id, text="")
    except ZeroDivisionError:
        bot.send_message(user_id, text=texts.COURSES_NOT_FOUND)
        bot.answer_callback_query(call.id, text="")


@bot.message_handler(content_types=['text'], func=lambda message: message.text == texts.EVENTS)
def events_view(message):
    user_id = message.chat.id
    events = DBGetter(DBSettings.HOST).get("SELECT id, title, event_date, image FROM events ORDER BY event_date ASC")
    paginate_events[user_id] = events
    try:
        for event in chunk_it(paginate_events.get(user_id), float('%.1f' % len(paginate_events.get(user_id))) / 1)[0]:
            event_date = datetime.fromtimestamp(event[2]).strftime('%d/%m/%Y')
            markup = types.InlineKeyboardMarkup()
            markup_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.InlineKeyboardButton(text=texts.READ_MORE,
                                                  callback_data="moreevent_%s_%s" % (event[0], 1)))
            row = [types.InlineKeyboardButton(u"\u27A1", callback_data=">>_%s_events" % 1)]
            markup.row(*row)
            bot.send_photo(user_id, photo=event[3], caption="*%s*\n\n_%s_" % (event[1], event_date),
                           reply_markup=markup, disable_notification=True, parse_mode="Markdown")

            is_subscribe = DBGetter(DBSettings.HOST).get("SELECT is_subscribed_to_events "
                                                         "FROM users WHERE user_id = %s" % user_id)[0][0]
            if is_subscribe is False:
                markup_keyboard.row(texts.SUBSCRIBE_TO_NEW_EVENTS)
                markup_keyboard.row(texts.BACK_TO_MAIN_MENU)
                bot.send_message(user_id, text=texts.YOU_CAN_SUBSCRIBE_TO_EVENTS, reply_markup=markup_keyboard)
            if is_subscribe is True:
                markup_keyboard.row(texts.UNSUBSCRIBE_TO_NEW_EVENTS)
                markup_keyboard.row(texts.BACK_TO_MAIN_MENU)
                bot.send_message(user_id, text=texts.YOU_CAN_UNSUBSCRIBE_TO_EVENTS, reply_markup=markup_keyboard)
    except ZeroDivisionError:
        markup_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        is_subscribe = DBGetter(DBSettings.HOST).get("SELECT is_subscribed_to_events "
                                                     "FROM users WHERE user_id = %s" % user_id)[0][0]
        if is_subscribe is False:
            markup_keyboard.row(texts.SUBSCRIBE_TO_NEW_EVENTS)
            markup_keyboard.row(texts.BACK_TO_MAIN_MENU)
            bot.send_message(user_id, text=texts.YOU_CAN_SUBSCRIBE_TO_EVENTS, reply_markup=markup_keyboard)
        if is_subscribe is True:
            markup_keyboard.row(texts.UNSUBSCRIBE_TO_NEW_EVENTS)
            markup_keyboard.row(texts.BACK_TO_MAIN_MENU)
            bot.send_message(user_id, text=texts.YOU_CAN_UNSUBSCRIBE_TO_EVENTS, reply_markup=markup_keyboard)
        bot.send_message(user_id, text=texts.EVENTS_NOT_FOUND, reply_markup=markup_keyboard)


@bot.callback_query_handler(func=lambda call: call.data.split("_")[0] in ["more", "moretmp"])
def full_courses_view(call):
    user_id = call.message.chat.id
    course_id = call.data.split("_")[1]
    if call.data.split("_")[0] == "more":
        course_info = DBGetter(DBSettings.HOST).get("SELECT title, description, age, start_date, duration, cost, "
                                                    "site_link FROM courses WHERE id = %s" % course_id)[0]
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(texts.REGISTER_FREE,
                                              callback_data="regfree_%s" % course_id))
        markup.add(types.InlineKeyboardButton(texts.REGISTER_FOR_COURSE,
                                              callback_data="reg_%s" % course_id))
        markup.add(types.InlineKeyboardButton(texts.BACK_TO_COURSES, callback_data="<<_%s_courses_%s" %
                                                                                   (int(call.data.split("_")[2]),
                                                                                    call.data.split("_")[2])))
        try:
            bot.delete_message(user_id, message_id=call.message.message_id)
            bot.send_message(user_id, text=texts.FULL_COURSE_DESC % (course_info[0], course_info[1], course_info[2],
                                                                     course_info[3], course_info[4], course_info[5],
                                                                     course_info[6]),
                             parse_mode="Markdown", disable_web_page_preview=True, reply_markup=markup)
            bot.answer_callback_query(call.id, text="")
        except Exception as error:
            logging.info("Error occurred during the courses pagination: %s" % error)
            bot.answer_callback_query(call.id, text="")

    if call.data.split("_")[0] == "moretmp":
        course_info = DBGetter(DBSettings.HOST).get("SELECT title, description, age, start_date, duration, cost, "
                                                    "site_link FROM courses_tmp "
                                                    "WHERE id = %s" % course_id)[0]
        markup = types.InlineKeyboardMarkup()
        row = [types.InlineKeyboardButton(texts.SAVE, callback_data="savecourse_%s" % course_id),
               types.InlineKeyboardButton(texts.DELETE, callback_data="deletecourse_%s" % course_id)]
        markup.row(*row)
        try:
            bot.delete_message(user_id, message_id=call.message.message_id)
            bot.send_message(user_id, text=texts.FULL_COURSE_DESC % (course_info[0], course_info[1], course_info[2],
                                                                     course_info[3], course_info[4], course_info[5],
                                                                     course_info[6]),
                             parse_mode="Markdown", disable_web_page_preview=True, reply_markup=markup)
            bot.answer_callback_query(call.id, text="")
        except Exception as error:
            logging.info("Error occurred during the courses pagination: %s" % error)
            bot.answer_callback_query(call.id, text="")


@bot.callback_query_handler(func=lambda call: call.data.split("_")[0] in ["moreevent", "moreeventtmp"])
def full_events_view(call):
    user_id = call.message.chat.id
    event_id = call.data.split("_")[1]
    if call.data.split("_")[0] == "moreevent":
        event_info = DBGetter(DBSettings.HOST).get("SELECT title, description, event_date, age, "
                                                   "conditions, site_link FROM events WHERE id = %s" % event_id)[0]

        event_date = datetime.fromtimestamp(event_info[2]).strftime('%d/%m/%Y')
        start_event_date = datetime.fromtimestamp(event_info[2]).strftime('%d/%m/%Y %H:%M:%S')
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(texts.REGISTER_FOR_EVENT,
                                              callback_data="regfreeevent_%s" % call.data.split("_")[1]))
        markup.add(types.InlineKeyboardButton(texts.BACK_TO_EVENTS, callback_data="<<_%s_events_%s" %
                                                                                  (int(call.data.split("_")[2]),
                                                                                   call.data.split("_")[2])))
        try:
            bot.delete_message(user_id, message_id=call.message.message_id)
            bot.send_message(user_id, text=texts.FULL_EVENT_DESC % (event_info[0], event_info[1],
                                                                    event_date, start_event_date,
                                                                    event_info[3], event_info[4], event_info[5]),
                             parse_mode="Markdown", disable_web_page_preview=True, reply_markup=markup)
            bot.answer_callback_query(call.id, text="")
        except Exception as error:
            logging.info("Error occurred during the events pagination: %s" % error)
            bot.answer_callback_query(call.id, text="")

    if call.data.split("_")[0] == "moreeventtmp":
        event_info = DBGetter(DBSettings.HOST).get("SELECT title, description, event_date, age, "
                                                   "conditions, site_link FROM events_tmp WHERE id = %s" % event_id)[0]
        event_date = datetime.fromtimestamp(event_info[2]).strftime('%d/%m/%Y')
        start_event_date = datetime.fromtimestamp(event_info[2]).strftime('%d/%m/%Y %H:%M:%S')
        markup = types.InlineKeyboardMarkup()
        row = [types.InlineKeyboardButton(texts.SAVE, callback_data="saveevent_%s" % event_id),
               types.InlineKeyboardButton(texts.DELETE, callback_data="deleteevent_%s" % event_id)]
        markup.row(*row)
        try:
            bot.delete_message(user_id, message_id=call.message.message_id)
            bot.send_message(user_id, text=texts.FULL_EVENT_DESC % (event_info[0], event_info[1],
                                                                    event_date, start_event_date,
                                                                    event_info[3], event_info[4], event_info[5]),
                             parse_mode="Markdown", disable_web_page_preview=True, reply_markup=markup)
            bot.answer_callback_query(call.id, text="")
        except Exception as error:
            logging.info("Error occurred during the events pagination: %s" % error)
            bot.answer_callback_query(call.id, text="")


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] in [">>", "<<"])
def pagination_worker(call):
    user_id = call.message.chat.id
    markup = types.InlineKeyboardMarkup()
    # pagination for courses
    if call.data.split("_")[2] == "courses":
        try:
            for course in chunk_it(paginate_courses.get(user_id),
                                   float('%.1f' %
                                         len(paginate_courses.get(user_id))) / 1)[int(call.data.split("_")[1])]:
                markup.add(types.InlineKeyboardButton(text=texts.READ_MORE,
                                                      callback_data="more_%s_%s" % (course[0],
                                                                                    int(call.data.split("_")[1]))))
                row = [types.InlineKeyboardButton(u"\u2B05", callback_data="<<_%s_courses_%s" %
                                                                           (int(call.data.split("_")[1]) - 1,
                                                                            call.data.split("_")[1])),
                       types.InlineKeyboardButton(u"\u27A1", callback_data=">>_%s_courses_%s" %
                                                                           (int(call.data.split("_")[1]) + 1,
                                                                            call.data.split("_")[1]))]
                markup.row(*row)
                try:
                    bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
                    bot.send_photo(user_id, photo=course[3], caption="*%s*\n\n_%s_" % (course[1], course[2]),
                                   reply_markup=markup, disable_notification=True, parse_mode="Markdown")
                    bot.answer_callback_query(call.id, text="")
                except Exception as error:
                    logging.info("Error occurred during the courses pagination: %s" % error)
        except (IndexError, TypeError):
            main_menu_buttons(user_id, texts.ALL_COURSES_DISPLAYED)
            bot.answer_callback_query(call.id, text="")

    # pagination for events
    if call.data.split("_")[2] == "events":
        try:
            for event in chunk_it(paginate_events.get(user_id),
                                  float('%.1f' % len(paginate_events.get(user_id))) / 1)[int(call.data.split("_")[1])]:
                event_date = datetime.fromtimestamp(event[2])bot.answer_callback_query(call.id, text="")bot.answer_callback_query(call.id, text="").strftime('%d/%m/%Y')
                markup.add(types.InlineKeyboardButton(text=texts.READ_MORE,
                                                      callback_data="moreevent_%s_%s" % (event[0],
                                                                                         int(call.data.split("_")[1]))))
                row = [types.InlineKeyboardButton(u"\u2B05", callback_data="<<_%s_events_%s" %
                                                                           (int(call.data.split("_")[1]) - 1,
                                                                            call.data.split("_")[1])),
                       types.InlineKeyboardButton(u"\u27A1", callback_data=">>_%s_events_%s" %
                                                                           (int(call.data.split("_")[1]) + 1,
                                                                            call.data.split("_")[1]))]
                markup.row(*row)
                try:
                    bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
                    bot.send_photo(user_id, photo=event[3], caption="*%s*\n\n_%s_" % (event[1], event_date),
                                   reply_markup=markup, disable_notification=True, parse_mode="Markdown")
                    bot.answer_callback_query(call.id, text="")
                except Exception as error:
                    logging.info("Error occurred during the events pagination: %s" % error)
        except (IndexError, TypeError):
            main_menu_buttons(user_id, texts.ALL_EVENTS_DISPLAYED)
            bot.answer_callback_query(call.id, text="")


@bot.message_handler(commands=["add_course"])
def add_course_command(message):
    user_id = message.chat.id
    is_admin = DBGetter(DBSettings.HOST).get("SELECT is_administrator FROM users WHERE user_id = %s" % user_id)
    if is_admin[0][0] is False:
        bot.send_message(user_id, text=texts.HAVE_NOT_PERMISSIONS)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(texts.CANCEL_OPERATION)
        msg = bot.send_message(user_id, text=texts.SEND_PICTURE, reply_markup=markup)
        bot.register_next_step_handler(msg, process_course_picture)


@bot.message_handler(commands=["add_event"])
def add_event_command(message):
    user_id = message.chat.id
    is_admin = DBGetter(DBSettings.HOST).get("SELECT is_administrator FROM users WHERE user_id = %s" % user_id)
    if is_admin[0][0] is False:
        bot.send_message(user_id, text=texts.HAVE_NOT_PERMISSIONS)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(texts.CANCEL_OPERATION)
        msg = bot.send_message(user_id, text=texts.SEND_PICTURE, reply_markup=markup)
        bot.register_next_step_handler(msg, process_event_picture)


def process_course_picture(message):
    picture = message.text
    if picture not in BotSettings.COMMANDS and picture != texts.CANCEL_OPERATION:
        try:
            file_id = str(message.photo[-1].file_id)
            DBGetter(DBSettings.HOST).insert("INSERT INTO courses_tmp (image) VALUES ('%s')" % file_id)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row(texts.CANCEL_OPERATION)
            msg = bot.send_message(message.chat.id, text=texts.SEND_COURSE_INFO, reply_markup=markup,
                                   parse_mode="Markdown", disable_web_page_preview=True)
            bot.register_next_step_handler(msg, process_course_info)
        except Exception as error:
            bot.send_message(message.chat.id, text=texts.ERROR_DURING_PHOTO_ADD)
            time.sleep(1)
            add_course_command(message)
            logging.error("Error during course photo processing: %s" % error)


def process_event_picture(message):
    picture = message.text
    if picture not in BotSettings.COMMANDS and picture != texts.CANCEL_OPERATION:
        try:
            file_id = str(message.photo[-1].file_id)
            DBGetter(DBSettings.HOST).insert("INSERT INTO events_tmp (image) VALUES ('%s')" % file_id)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row(texts.CANCEL_OPERATION)
            msg = bot.send_message(message.chat.id, text=texts.SEND_EVENT_INFO, reply_markup=markup,
                                   parse_mode="Markdown", disable_web_page_preview=True)
            bot.register_next_step_handler(msg, process_event_info)
        except Exception as error:
            bot.send_message(message.chat.id, text=texts.ERROR_DURING_PHOTO_ADD)
            time.sleep(1)
            add_event_command(message)
            logging.error("Error during event photo processing: %s" % error)


def process_course_info(message):
    course_info = message.text
    user_id = message.chat.id
    if course_info not in BotSettings.COMMANDS and course_info != texts.CANCEL_OPERATION:
        try:
            image_id = DBGetter(DBSettings.HOST).get("SELECT image FROM courses_tmp ORDER BY id DESC LIMIT 1")[0][0]
            caption = str(message.text).split(";")
            age = int(caption[2].split("-")[1].replace('лет', ''))
            if age <= 15:
                course_type = "kids"
            else:
                course_type = "adult"
            course_exists = DBGetter(DBSettings.HOST).get("SELECT COUNT(*) FROM courses "
                                                          "WHERE title = '%s'" % caption[0])[0][0]
            if course_exists > 0:
                msg = bot.send_message(user_id, text=texts.COURSE_EXISTS)
                bot.register_next_step_handler(msg, process_course_info)
            else:
                DBGetter(DBSettings.HOST).insert(execution="UPDATE courses_tmp SET title = %s, description = %s, "
                                                           "age = %s, start_date = %s, duration = %s, cost = %s, "
                                                           "course_type = %s, site_link  = %s WHERE image = %s",
                                                 values=(caption[0], caption[1], caption[2], caption[3], caption[4],
                                                         caption[5], course_type, caption[6], image_id))
                course_id = DBGetter(DBSettings.HOST).get("SELECT id FROM courses_tmp "
                                                          "WHERE image = '%s'" % image_id)[0][0]
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.row(texts.ADD_ANOTHER_COURSE)
                markup.row(texts.BACK_TO_MAIN_MENU)
                markup_inline = types.InlineKeyboardMarkup()
                markup_inline.add(types.InlineKeyboardButton(text=texts.READ_MORE,
                                                             callback_data="moretmp_%s" % course_id))
                row = [types.InlineKeyboardButton(texts.SAVE, callback_data="savecourse_%s" % course_id),
                       types.InlineKeyboardButton(texts.DELETE, callback_data="deletecourse_%s" % course_id)]
                markup_inline.row(*row)
                bot.send_message(user_id, text=texts.COURSE_SUCCESSFULLY_ADDED, reply_markup=markup)
                bot.send_photo(user_id, photo=image_id, caption="*%s*\n\n_%s_" % (caption[0], caption[5]),
                               reply_markup=markup_inline, parse_mode="Markdown")
        except Exception as error:
            msg = bot.send_message(user_id, text=texts.ERROR_DURING_INFO_ADD)
            logging.error("Error during course info processing: %s" % error)
            bot.register_next_step_handler(msg, process_course_info)


def process_event_info(message):
    event_info = message.text
    user_id = message.chat.id
    if event_info not in BotSettings.COMMANDS and event_info != texts.CANCEL_OPERATION:
        try:
            image_id = DBGetter(DBSettings.HOST).get("SELECT image FROM events_tmp ORDER BY id DESC LIMIT 1")[0][0]
            caption = str(message.text).split(";")
            event_date_tmstmp = int(time.mktime(datetime.strptime(caption[2], "%d/%m/%Y %H:%M:%S").timetuple()))
            event_date = datetime.fromtimestamp(event_date_tmstmp).strftime('%d/%m/%Y')
            event_exists = DBGetter(DBSettings.HOST).get("SELECT COUNT(*) FROM events "
                                                         "WHERE title = '%s'" % caption[0])[0][0]
            if event_exists > 0:
                msg = bot.send_message(user_id, text=texts.EVENT_EXISTS)
                bot.register_next_step_handler(msg, process_event_info)
            else:
                DBGetter(DBSettings.HOST).insert(execution="UPDATE events_tmp SET title = %s, description = %s, "
                                                           "event_date = %s, age = %s, "
                                                           "conditions = %s, site_link = %s WHERE image = %s",
                                                 values=(caption[0], caption[1], event_date_tmstmp, caption[3],
                                                         caption[4], caption[5], image_id))
                event_id = DBGetter(DBSettings.HOST).get("SELECT id FROM events_tmp "
                                                         "WHERE image = '%s'" % image_id)[0][0]
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.row(texts.ADD_ANOTHER_EVENT)
                markup.row(texts.BACK_TO_MAIN_MENU)
                markup_inline = types.InlineKeyboardMarkup()
                markup_inline.add(types.InlineKeyboardButton(text=texts.READ_MORE,
                                                             callback_data="moreeventtmp_%s" % event_id))
                row = [types.InlineKeyboardButton(texts.SAVE, callback_data="saveevent_%s" % event_id),
                       types.InlineKeyboardButton(texts.DELETE, callback_data="deleteevent_%s" % event_id)]
                markup_inline.row(*row)
                bot.send_message(user_id, text=texts.EVENT_SUCCESSFULLY_ADDED, reply_markup=markup)
                bot.send_photo(user_id, photo=image_id, caption="*%s*\n\n_%s_" % (caption[0], event_date),
                               reply_markup=markup_inline, parse_mode="Markdown")
        except Exception as error:
            msg = bot.send_message(user_id, text=texts.ERROR_DURING_INFO_ADD)
            logging.error("Error during event info processing: %s" % error)
            bot.register_next_step_handler(msg, process_event_info)


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] in ["saveevent", "deleteevent",
                                                                          "savecourse", "deletecourse"])
def save_delete_courses_events_worker(call):
    user_id = call.message.chat.id
    save_delete_id = call.data.split('_')[1]
    save_delete_type = call.data.split('_')[0]
    try:
        # save new event process
        if save_delete_type == "saveevent":
            new_event = DBGetter(DBSettings.HOST).get("SELECT image, title, description, "
                                                      "event_date, age, conditions, site_link "
                                                      "FROM events_tmp WHERE id = %s" % save_delete_id)[0]
            # delete event info from 'events_tmp' table and insert into 'events' table
            DBGetter(DBSettings.HOST).insert("DELETE FROM events_tmp WHERE id = %s" % save_delete_id)
            DBGetter(DBSettings.HOST).insert("INSERT INTO events (image, title, description, "
                                             "event_date, age, conditions, site_link) "
                                             "VALUES ('%s', '%s', '%s', %s, "
                                             "'%s', '%s', '%s')" % (new_event[0], new_event[1], new_event[2],
                                                                    new_event[3], new_event[4], new_event[5],
                                                                    new_event[6]))
            new_event_id = DBGetter(DBSettings.HOST).get("SELECT id FROM events "
                                                         "WHERE title = '%s'" % new_event[1])[0][0]
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(texts.SEND_NOTIFICATION,
                                                  callback_data="sendnotifyevent_%s" % new_event_id))
            markup.add(types.InlineKeyboardButton(text=texts.SAVED, callback_data="saved"))
            bot.edit_message_reply_markup(chat_id=user_id, message_id=call.message.message_id, reply_markup=markup)
            bot.answer_callback_query(call.id, text="")
        # save new course process
        if save_delete_type == "savecourse":
            new_course = DBGetter(DBSettings.HOST).get("SELECT title, description, age, start_date, duration, "
                                                       "cost, image, course_type, site_link "
                                                       "FROM courses_tmp WHERE id = %s" % save_delete_id)[0]
            # delete course info from 'course_tmp' table and insert into 'course' table
            DBGetter(DBSettings.HOST).insert("DELETE FROM courses_tmp WHERE id = %s" % save_delete_id)
            DBGetter(DBSettings.HOST).insert("INSERT INTO courses (title, description, age, start_date, duration, "
                                             "cost, image, course_type, site_link) VALUES ('%s', '%s', '%s', '%s', "
                                             "'%s', '%s', '%s', '%s', '%s')" % (new_course[0], new_course[1],
                                                                                new_course[2], new_course[3],
                                                                                new_course[4], new_course[5],
                                                                                new_course[6], new_course[7],
                                                                                new_course[8]))
            new_course_id = DBGetter(DBSettings.HOST).get("SELECT id FROM courses "
                                                          "WHERE title = '%s'" % new_course[0])[0][0]
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(texts.SEND_NOTIFICATION,
                                                  callback_data="sendnotifycourse_%s" % new_course_id))
            markup.add(types.InlineKeyboardButton(text=texts.SAVED, callback_data="saved"))
            bot.edit_message_reply_markup(chat_id=user_id, message_id=call.message.message_id, reply_markup=markup)
            bot.answer_callback_query(call.id, text="")

        # delete new event process
        if save_delete_type == "deleteevent":
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(text=texts.DELETED, callback_data="deleted"))
            bot.edit_message_reply_markup(chat_id=user_id, message_id=call.message.message_id, reply_markup=markup)
            bot.answer_callback_query(call.id, text="")
            DBGetter(DBSettings.HOST).insert("DELETE FROM events_tmp WHERE id = %s" % save_delete_id)

        # delete new course process
        if save_delete_type == "deletecourse":
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(text=texts.DELETED, callback_data="deleted"))
            bot.edit_message_reply_markup(chat_id=user_id, message_id=call.message.message_id, reply_markup=markup)
            bot.answer_callback_query(call.id, text="")
            DBGetter(DBSettings.HOST).insert("DELETE FROM courses_tmp WHERE id = %s" % save_delete_id)
    except Exception as error:
        logging.error("Error during save/delete course/event: %s" % error)
        pass


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] in ["sendnotifyevent", "sendnotifycourse"])
def notifier_worker(call):
    user_id = call.message.chat.id
    notification_id = call.data.split("_")[1]
    notification_type = call.data.split("_")[0]
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(texts.NOTIFICATION_SEND, callback_data="send"))
    bot.edit_message_reply_markup(chat_id=user_id, message_id=call.message.message_id, reply_markup=markup)
    # sending notifications about new event process
    if notification_type == "sendnotifyevent":
        try:
            events_subscribers = DBGetter(DBSettings.HOST).get("SELECT user_id FROM users "
                                                               "WHERE is_subscribed_to_events = TRUE")
            new_event = DBGetter(DBSettings.HOST).get("SELECT image, title, event_date FROM events "
                                                      "WHERE id = %s" % notification_id)[0]
            event_date = datetime.fromtimestamp(new_event[2]).strftime('%d/%m/%Y')
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(text=texts.READ_MORE,
                                                  callback_data="moreevent_%s_%s" % (notification_id, 1)))
            for user in events_subscribers:
                async_bot.send_photo(user[0], photo=new_event[0], caption="*%s*\n\n*%s*\n\n_%s_" % (texts.NEW_EVENT,
                                                                                                    new_event[1],
                                                                                                    event_date),
                                     reply_markup=markup, parse_mode="Markdown")
                logging.info("Starting send notification to user: %s" % user[0])
        except Exception as error:
            logging.error("Error during sending notifications about new event: %s" % error)
            pass

    # sending notifications about new event process
    if notification_type == "sendnotifycourse":
        try:
            courses_subscribers = DBGetter(DBSettings.HOST).get("SELECT user_id FROM users "
                                                                "WHERE is_subscribed_to_courses = TRUE")
            new_course = DBGetter(DBSettings.HOST).get("SELECT image, title, cost FROM courses "
                                                       "WHERE id = %s" % notification_id)[0]
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(text=texts.READ_MORE,
                                                  callback_data="more_%s_%s" % (notification_id, 1)))
            for user in courses_subscribers:
                async_bot.send_photo(user[0], photo=new_course[0], caption="*%s*\n\n*%s*\n\n_%s_" % (texts.NEW_COURSE,
                                                                                                     new_course[1],
                                                                                                     new_course[2]),
                                     reply_markup=markup, parse_mode="Markdown")
                logging.info("Starting send notification to user: %s" % user[0])
        except Exception as error:
            logging.error("Error during sending notifications about new course: %s" % error)
            pass


@bot.message_handler(content_types=['text'], func=lambda message: message.text == texts.CANCEL_OPERATION)
def cancel_add_course_or_event(message):
    user_id = message.chat.id
    main_menu_buttons(user_id, texts.OPERATION_CANCELED)
    try:
        image_id = DBGetter(DBSettings.HOST).get("SELECT image FROM courses_tmp "
                                                 "WHERE title IS NULL ORDER BY id DESC LIMIT 1")[0][0]
        DBGetter(DBSettings.HOST).insert("DELETE FROM courses_tmp WHERE image = '%s' AND title IS NULL" % image_id)
    except IndexError:
        pass
    try:
        image_id = DBGetter(DBSettings.HOST).get("SELECT image FROM events_tmp "
                                                 "WHERE title IS NULL ORDER BY id DESC LIMIT 1")[0][0]
        DBGetter(DBSettings.HOST).insert("DELETE FROM events_tmp WHERE image = '%s' AND title IS NULL" % image_id)
    except IndexError:
        pass


@bot.message_handler(commands=["delete_course"])
def delete_course_command(message):
    user_id = message.chat.id
    is_admin = DBGetter(DBSettings.HOST).get("SELECT is_administrator FROM users WHERE user_id = %s" % user_id)
    if is_admin[0][0] is False:
        bot.send_message(user_id, text=texts.HAVE_NOT_PERMISSIONS)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(texts.CANCEL_OPERATION)
        msg = bot.send_message(user_id, text=texts.SEND_COURSE_TITLE, reply_markup=markup)
        bot.register_next_step_handler(msg, process_course_title)


@bot.message_handler(commands=["delete_event"])
def delete_event_command(message):
    user_id = message.chat.id
    is_admin = DBGetter(DBSettings.HOST).get("SELECT is_administrator FROM users WHERE user_id = %s" % user_id)
    if is_admin[0][0] is False:
        bot.send_message(user_id, text=texts.HAVE_NOT_PERMISSIONS)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(texts.CANCEL_OPERATION)
        msg = bot.send_message(user_id, text=texts.SEND_EVENT_TITLE, reply_markup=markup)
        bot.register_next_step_handler(msg, process_event_title)


def process_course_title(message):
    course_title = message.text
    user_id = message.chat.id
    if course_title not in BotSettings.COMMANDS and course_title != texts.CANCEL_OPERATION:
        try:
            course_exists = DBGetter(DBSettings.HOST).get("SELECT COUNT(*) FROM courses "
                                                          "WHERE title = '%s'" % course_title)[0][0]
            if course_exists == 0:
                msg = bot.send_message(user_id, text=texts.COURSE_NOT_FOUND)
                bot.register_next_step_handler(msg, process_course_title)
            else:
                DBGetter(DBSettings.HOST).insert("DELETE FROM courses WHERE title = '%s'" % course_title)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.row(texts.DELETE_ANOTHER_COURSE)
                markup.row(texts.BACK_TO_MAIN_MENU)
                bot.send_message(user_id, text=texts.COURSE_DELETED, reply_markup=markup)
        except Exception as error:
            msg = bot.send_message(user_id, text=texts.ERROR_DURING_INFO_ADD)
            logging.error("Error during course delete process: %s" % error)
            bot.register_next_step_handler(msg, process_course_title)


def process_event_title(message):
    event_title = message.text
    user_id = message.chat.id
    if event_title not in BotSettings.COMMANDS and event_title != texts.CANCEL_OPERATION:
        try:
            course_exists = DBGetter(DBSettings.HOST).get("SELECT COUNT(*) FROM events "
                                                          "WHERE title = '%s'" % event_title)[0][0]
            if course_exists == 0:
                msg = bot.send_message(user_id, text=texts.EVENT_NOT_FOUND)
                bot.register_next_step_handler(msg, process_event_title)
            else:
                DBGetter(DBSettings.HOST).insert("DELETE FROM events WHERE title = '%s'" % event_title)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.row(texts.DELETE_ANOTHER_EVENT)
                markup.row(texts.BACK_TO_MAIN_MENU)
                bot.send_message(user_id, text=texts.EVENT_DELETED, reply_markup=markup)
        except Exception as error:
            msg = bot.send_message(user_id, text=texts.ERROR_DURING_INFO_ADD)
            logging.error("Error during event delete process: %s" % error)
            bot.register_next_step_handler(msg, process_event_title)


# regfreeevent - заявка на регистрацию на мероприятие
# reg - заявка на курс
# regfree - заявка на бесплатный урок
@bot.callback_query_handler(func=lambda call: call.data.split("_")[0] in ["regfreeevent", "reg", "regfree"])
def registrations_worker(call):
    user_id = call.message.chat.id
    user_name = call.message.chat.first_name
    user_email = DBGetter(DBSettings.HOST).get("SELECT email FROM users WHERE user_id = %s" % user_id)[0][0]
    user_phone = DBGetter(DBSettings.HOST).get("SELECT phone_number FROM users WHERE user_id = %s" % user_id)[0][0]

    if user_email is None and user_phone is None:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(texts.BACK_TO_MAIN_MENU)
        msg = bot.send_message(user_id, text=texts.SEND_EMAIL, reply_markup=markup)
        bot.register_next_step_handler(msg, process_email)

    if user_email is not None and user_phone is None:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton(request_contact=True, text=texts.SENDING_PHONE))
        markup.add(types.KeyboardButton(text=texts.BACK_TO_MAIN_MENU))
        bot.send_message(user_id, text=texts.SEND_PHONE, reply_markup=markup)

    if user_email is not None and user_phone is not None:
        # events registration process
        if call.data.split("_")[0] == "regfreeevent":
            is_processed = DBGetter(DBSettings.HOST).get("SELECT COUNT(*) FROM users_requests "
                                                         "WHERE user_id = %s "
                                                         "AND event_id = %s" % (user_id, call.data.split("_")[1]))[0][0]
            if is_processed == 0:
                event_name = DBGetter(DBSettings.HOST).get("SELECT title FROM events "
                                                           "WHERE id = %s" % call.data.split("_")[1])[0][0]
                DBGetter(DBSettings.HOST).insert("INSERT INTO users_requests (user_id, event_name, event_id) "
                                                 "VALUES (%s, '%s', %s)" % (user_id, event_name,
                                                                            call.data.split("_")[1]))
                EMailGetter().send_email(subject=texts.SUBJECT_REGFREEEVENT % (event_name, user_id),
                                         body=texts.EMAIL_BODY_REGFREEEVENT % (event_name, user_name,
                                                                               user_phone, user_email))
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text=texts.CANCEL_REQUEST,
                                                      callback_data="cancelevent_%s" % call.data.split("_")[1]))
                bot.send_message(user_id, text=texts.REQUEST_FOR_EVENT_WAS_SEND % event_name,
                                 reply_markup=markup, parse_mode="Markdown")
                bot.answer_callback_query(call.id, text="")
            if is_processed == 1:
                bot.send_message(user_id, text=texts.REQUEST_ALREADY_SEND_FOR_EVENT)
                bot.answer_callback_query(call.id, text="")

        # courses registration process
        if call.data.split("_")[0] == "reg":
            is_processed = DBGetter(DBSettings.HOST).get("SELECT COUNT(*) FROM users_requests "
                                                         "WHERE user_id = %s AND course_id = %s "
                                                         "AND request_type = '%s'" % (user_id,
                                                                                      call.data.split("_")[1],
                                                                                      call.data.split("_")[0]))[0][0]
            if is_processed == 0:
                course_name = DBGetter(DBSettings.HOST).get("SELECT title FROM courses "
                                                            "WHERE id = %s" % call.data.split("_")[1])[0][0]
                DBGetter(DBSettings.HOST).insert("INSERT INTO users_requests (user_id, course_name, "
                                                 "course_id, request_type) "
                                                 "VALUES (%s, '%s', %s, '%s')" % (user_id, course_name,
                                                                                  call.data.split("_")[1],
                                                                                  call.data.split("_")[0]))
                EMailGetter().send_email(subject=texts.SUBJECT_REG % (course_name, user_id),
                                         body=texts.EMAIL_BODY_REG % (course_name, user_name,
                                                                      user_phone, user_email))
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text=texts.CANCEL_REQUEST,
                                                      callback_data="cancelreg_%s" % call.data.split("_")[1]))
                bot.send_message(user_id, text=texts.REQUEST_FOR_COURSE_WAS_SEND % course_name,
                                 reply_markup=markup, parse_mode="Markdown")
                bot.answer_callback_query(call.id, text="")
            if is_processed == 1:
                bot.send_message(user_id, text=texts.REQUEST_ALREADY_SEND_FOR_COURSE)
                bot.answer_callback_query(call.id, text="")

        # free lessons registration process
        if call.data.split("_")[0] == "regfree":
            is_processed = DBGetter(DBSettings.HOST).get("SELECT COUNT(*) FROM users_requests "
                                                         "WHERE user_id = %s AND course_id = %s "
                                                         "AND request_type = '%s'" % (user_id,
                                                                                      call.data.split("_")[1],
                                                                                      call.data.split("_")[0]))[0][0]
            if is_processed == 0:
                course_name = DBGetter(DBSettings.HOST).get("SELECT title FROM courses "
                                                            "WHERE id = %s" % call.data.split("_")[1])[0][0]
                DBGetter(DBSettings.HOST).insert("INSERT INTO users_requests (user_id, course_name, "
                                                 "course_id, request_type) "
                                                 "VALUES (%s, '%s', %s, '%s')" % (user_id, course_name,
                                                                                  call.data.split("_")[1],
                                                                                  call.data.split("_")[0]))
                EMailGetter().send_email(subject=texts.SUBJECT_REGFREE % (course_name, user_id),
                                         body=texts.EMAIL_BODY_REGFREE % (course_name, user_name,
                                                                          user_phone, user_email))
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text=texts.CANCEL_REQUEST,
                                                      callback_data="cancelregfree_%s" % call.data.split("_")[1]))
                bot.send_message(user_id, text=texts.REQUEST_FOR_COURSE_FREE_WAS_SEND % course_name,
                                 reply_markup=markup, parse_mode="Markdown")
                bot.answer_callback_query(call.id, text="")
            if is_processed == 1:
                bot.send_message(user_id, text=texts.REQUEST_ALREADY_SEND_FOR_COURSE_FREE)
                bot.answer_callback_query(call.id, text="")


# cancelevent - отмена заявки на регистрацию на мероприятие
# cancelreg - отмена заявки на курс
# cancelregfree - отмена заявки на бесплатный урок
@bot.callback_query_handler(func=lambda call: call.data.split("_")[0] in ["cancelevent", "cancelreg", "cancelregfree"])
def cancel_requests_process(call):
    user_id = call.message.chat.id
    user_name = call.message.chat.first_name
    user_email = DBGetter(DBSettings.HOST).get("SELECT email FROM users WHERE user_id = %s" % user_id)[0][0]
    user_phone = DBGetter(DBSettings.HOST).get("SELECT phone_number FROM users WHERE user_id = %s" % user_id)[0][0]
    cancel_type = call.data.split("_")[0]
    cancel_id = call.data.split("_")[1]
    try:
        # event requests cancellation
        if cancel_type == "cancelevent":
            event_name = DBGetter(DBSettings.HOST).get("SELECT title FROM events WHERE id = %s" % cancel_id)[0][0]
            DBGetter(DBSettings.HOST).insert("DELETE FROM users_requests "
                                             "WHERE event_id = %s AND user_id = %s" % (cancel_id, user_id))
            bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id,
                                  text=texts.CANCEL_REQUEST_FOR_EVENT % event_name, parse_mode="Markdown")
            bot.answer_callback_query(call.id, text="")
            EMailGetter().send_email(subject=texts.SUBJECT_REGFREEEVENT_CANCEL % (event_name, user_id),
                                     body=texts.EMAIL_BODY_REGFREEEVENT % (event_name, user_name,
                                                                           user_phone, user_email))
        # courses requests cancellation
        if cancel_type == "cancelreg":
            course_name = DBGetter(DBSettings.HOST).get("SELECT title FROM courses WHERE id = %s" % cancel_id)[0][0]
            DBGetter(DBSettings.HOST).insert("DELETE FROM users_requests "
                                             "WHERE course_id = %s AND request_type = '%s' "
                                             "AND user_id = %s" % (cancel_id, 'reg', user_id))
            bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id,
                                  text=texts.CANCEL_REQUEST_FOR_COURSE % course_name, parse_mode="Markdown")
            bot.answer_callback_query(call.id, text="")
            EMailGetter().send_email(subject=texts.SUBJECT_REG_CANCEL % (course_name, user_id),
                                     body=texts.EMAIL_BODY_REG % (course_name, user_name, user_phone, user_email))
        # free lessons requests cancellation
        if cancel_type == "cancelregfree":
            course_name = DBGetter(DBSettings.HOST).get("SELECT title FROM courses WHERE id = %s" % cancel_id)[0][0]
            DBGetter(DBSettings.HOST).insert("DELETE FROM users_requests "
                                             "WHERE course_id = %s AND request_type = '%s' "
                                             "AND user_id = %s" % (cancel_id, 'regfree', user_id))
            bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id,
                                  text=texts.CANCEL_REQUEST_FOR_COURSE_FREE % course_name, parse_mode="Markdown")
            bot.answer_callback_query(call.id, text="")
            EMailGetter().send_email(subject=texts.SUBJECT_REGFREE_CANCEL % (course_name, user_id),
                                     body=texts.EMAIL_BODY_REGFREE % (course_name, user_name, user_phone, user_email))
    except Exception as error:
        logging.error("Error during cancellation events/courses: %s" % error)
        pass


def process_email(message):
    email = message.text
    user_id = message.chat.id
    if email not in BotSettings.COMMANDS and email != texts.BACK_TO_MAIN_MENU:
        match = re.search(r'[\w\.-]+@[\w\.-]+', email)
        if match is not None:
            DBGetter(DBSettings.HOST).insert("UPDATE users SET email = '%s' "
                                             "WHERE user_id = %s" % (match.group(0), user_id))
            user_phone = DBGetter(DBSettings.HOST).get("SELECT phone_number "
                                                       "FROM users WHERE user_id = %s" % user_id)[0][0]
            if user_phone is None:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add(types.KeyboardButton(request_contact=True, text=texts.SENDING_PHONE))
                markup.add(types.KeyboardButton(text=texts.BACK_TO_MAIN_MENU))
                bot.send_message(user_id, text=texts.SEND_PHONE, reply_markup=markup)

        else:
            msg = bot.send_message(user_id, text=texts.INCORRECT_EMAIL)
            bot.register_next_step_handler(msg, process_email)


@bot.message_handler(content_types=['contact'])
def process_phone_number(message):
    user_id = message.chat.id
    phone = message.contact.phone_number
    DBGetter(DBSettings.HOST).insert("UPDATE users SET phone_number = %s WHERE user_id = %s" % (phone, user_id))
    main_menu_buttons(user_id, texts.REGISTRATION_PROCESS_DONE)


def main_menu_buttons(user_id, text):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(texts.COURSES, texts.EVENTS)
    markup.row(texts.CONTACTS, texts.ABOUT)
    bot.send_message(user_id, text=text, reply_markup=markup, parse_mode="Markdown")


@bot.message_handler(content_types=['text'], func=lambda message: message.text == texts.ADD_ANOTHER_COURSE)
def add_another_course(message):
    add_course_command(message)


@bot.message_handler(content_types=['text'], func=lambda message: message.text == texts.DELETE_ANOTHER_COURSE)
def delete_another_course(message):
    delete_course_command(message)


@bot.message_handler(content_types=['text'], func=lambda message: message.text == texts.ADD_ANOTHER_EVENT)
def add_another_event(message):
    add_event_command(message)


@bot.message_handler(content_types=['text'], func=lambda message: message.text == texts.DELETE_ANOTHER_EVENT)
def delete_another_course(message):
    delete_event_command(message)


@bot.message_handler(commands=["stats"])
def stats_command(message):
    user_id = message.chat.id
    is_admin = DBGetter(DBSettings.HOST).get("SELECT is_administrator FROM users WHERE user_id = %s" % user_id)
    if is_admin[0][0] is False:
        bot.send_message(user_id, text=texts.HAVE_NOT_PERMISSIONS)
    else:
        users_count = DBGetter(DBSettings.HOST).get("SELECT COUNT(*) FROM users")[0][0]
        courses_requests = DBGetter(DBSettings.HOST).get("SELECT COUNT(*) FROM users_requests "
                                                         "WHERE course_name IS NOT NULL AND request_type = 'reg'")[0][0]
        courses_requests_free = DBGetter(DBSettings.HOST).get("SELECT COUNT(*) FROM users_requests WHERE course_name "
                                                              "IS NOT NULL AND request_type = 'regfree'")[0][0]
        events_requests = DBGetter(DBSettings.HOST).get("SELECT COUNT(*) FROM users_requests "
                                                        "WHERE event_name  IS NOT NULL")[0][0]
        courses = DBGetter(DBSettings.HOST).get("SELECT DISTINCT title FROM courses")
        events = DBGetter(DBSettings.HOST).get("SELECT DISTINCT title FROM events")

        to_show_courses = []
        to_show_events = []

        # aggregate courses statistics
        for item in courses:
            course_name = item[0]
            reg_by_course = DBGetter(DBSettings.HOST).get("SELECT COUNT(*) FROM users_requests WHERE course_name = '%s'"
                                                          "AND request_type = 'reg'" % course_name)[0][0]
            free_reg_by_course = DBGetter(DBSettings.HOST).get("SELECT COUNT(*) FROM users_requests WHERE "
                                                               "course_name = '%s' AND "
                                                               "request_type = 'regfree'" % course_name)[0][0]
            to_show_courses.append(texts.DETAIL_STATISTICS_COURSES % (course_name, reg_by_course, free_reg_by_course))

        # aggregate events statistics
        for item in events:
            event_name = item[0]
            reg_by_event = DBGetter(DBSettings.HOST).get("SELECT COUNT(*) FROM users_requests "
                                                         "WHERE event_name = '%s'" % event_name)[0][0]
            to_show_events.append(texts.DETAIL_STATISTICS_EVENTS % (event_name, reg_by_event))

        bot.send_message(user_id, text=texts.STATISTICS % (str(users_count), str(courses_requests),
                                                           str(courses_requests_free), str(events_requests) + '\n\n' +
                                                           texts.DETAIL_COURSES + '\n' + ''.join(to_show_courses) +
                                                           '\n' + texts.DETAIL_EVENTS + '\n' +
                                                           ''.join(to_show_events)),
                         parse_mode="Markdown")

while True:

    try:

        bot.polling(none_stop=True)

    # ConnectionError and ReadTimeout because of possible timeout of the requests library

    # TypeError for moviepy errors

    # maybe there are others, therefore Exception

    except Exception as e:
        logging.error(e)
        time.sleep(5)
