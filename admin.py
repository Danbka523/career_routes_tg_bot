from secret import admin_token, login, password
from telebot import types
import telebot
import sqlite3
from sqlite3 import Error

bot=telebot.TeleBot(admin_token)

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")

def create_key(text,callback_data):
    return types.InlineKeyboardButton(text=text, callback_data=callback_data)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text=='/start':
        bot.send_message(message.from_user.id,"Введите логин и пароль")
    if message.text==login+" "+password:
        text="Добро пожаловать, Даня, или кому ты уже успел дать логин с паролем лол"
        keyboard=types.InlineKeyboardMarkup()
        key=create_key(text="создать запись в бд", callback_data="create")
        keyboard.add(key)
        bot.send_message(message.from_user.id,text=text, reply_markup=keyboard)


def ask_type(message):
    text="выбери что добавить"
    keyboard = types.InlineKeyboardMarkup()
    key_spec=create_key("профессию","spec")
    keyboard.add(key_spec)
    key_event=create_key("мероприятие","event")
    keyboard.add(key_event)
    #key_type=create_key("тип мероприятия","type")
    #keyboard.add(key_type)
    bot.send_message(message.chat.id,text=text, reply_markup=keyboard)

#region events

def create_event(message):
    text = "введите название мероприятия"
    keyboard = types.InlineKeyboardMarkup()
    key_ret = create_key("начать снова", "ret")
    keyboard.add(key_ret)
    bot.send_message(message.chat.id,text=text, reply_markup=keyboard)
    bot.register_next_step_handler(message,add_event_type)

def add_event_type(message,name=""):
    name=message.text
    text = "введите тип мероприятия (только те которые есть в бд)"
    keyboard = types.InlineKeyboardMarkup()
    key_ret = create_key("начать снова", "ret")
    keyboard.add(key_ret)
    bot.send_message(message.chat.id,text=text, reply_markup=keyboard)
    print(name)
    bot.register_next_step_handler(message,add_event_desc,name)

def add_event_desc(message,name,type=""):
    type=message.text
    text = "введите описание мероприятия"
    keyboard = types.InlineKeyboardMarkup()
    key_ret = create_key("начать снова", "ret")
    keyboard.add(key_ret)
    bot.send_message(message.chat.id,text=text, reply_markup=keyboard)
    print(name)
    print(type)
    bot.register_next_step_handler(message,add_event_job,name,type,message.text)

def add_event_job(message,name,type,desc=""):
    desc=message.text
    text = "введите профессию (только те которые есть в бд)"
    keyboard = types.InlineKeyboardMarkup()
    key_ret = create_key("начать снова", "ret")
    keyboard.add(key_ret)
    bot.send_message(message.chat.id,text=text, reply_markup=keyboard)
    print(name)
    print(type)
    print(desc)
    bot.register_next_step_handler(message,add_event,name,type,desc,message.text)


def add_event(message,name,type,desc,job=""):
    job=message.text
    connection = sqlite3.connect("maindb.sqlite3")
    q_j=f'''
    select job_id from jobs
    where job_name="{job}"
    '''
    q_id=f'''
    select event_id from events
    where event_type="{type}"
    '''
    e_id=execute_read_query(connection,q_id)[0]
    j_id=execute_read_query(connection,q_j)[0]
    print(e_id[0],j_id[0])
    q=f'''
    insert into job_events
    values(null,{e_id[0]},"{name}","{desc}",{j_id[0]})
    '''
    execute_query(connection,q)
    text="готово!"
    keyboard = types.InlineKeyboardMarkup()
    key_ret = create_key("начать снова", "ret")
    keyboard.add(key_ret)
    bot.send_message(message.chat.id,text=text, reply_markup=keyboard)

#endregion

def create_spec(message):
    text = "введите название профессии"
    #bot.send_message(message.chat.id,text=text)
    keyboard = types.InlineKeyboardMarkup()
    key_ret = create_key("начать снова", "ret")
    keyboard.add(key_ret)
    bot.send_message(message.chat.id,text=text, reply_markup=keyboard)
    bot.register_next_step_handler(message,add_spec)


def add_spec(message):
    connection = sqlite3.connect("maindb.sqlite3")
    q=f'''
    insert into jobs
    values(null, "{message.text}")
    '''
    execute_query(connection,q)
    text="готово!"
    keyboard = types.InlineKeyboardMarkup()
    key_ret = create_key("начать снова", "ret")
    keyboard.add(key_ret)
    bot.send_message(message.chat.id,text=text, reply_markup=keyboard)



@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data=="create":
        ask_type(call.message)
    if call.data=="spec":
        create_spec(call.message)
    if call.data=="event":
        create_event(call.message)
    if call.data=="ret":
        ask_type(call.message)
  


bot.polling(none_stop=True, interval=0)