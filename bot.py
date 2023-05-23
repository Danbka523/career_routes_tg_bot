from secret import client_token
from telebot import types
import telebot
import sqlite3
from sqlite3 import Error

bot=telebot.TeleBot(client_token)


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
def get_text_messages(message,data=""):
    if message.text=='/start':
        text= "Привет! Меня зовут МаКар! Я буду рад помочь тебе с поиском — просто нажми кнопку, и я расскажу всё, что знаю!"
        keyboard = types.InlineKeyboardMarkup()
        key_yes = types.InlineKeyboardButton(text="Начать поиск!", callback_data="spec")
        key_about = types.InlineKeyboardButton(text="О проекте", callback_data="about")
        keyboard.add(key_yes)
        keyboard.add(key_about)
        bot.send_message(message.from_user.id,text=text, reply_markup=keyboard)

    if data=="main_menu":
        text= "Привет! Меня зовут МаКар! Я буду рад помочь тебе с поиском — просто нажми кнопку, и я расскажу всё, что знаю!"
        keyboard = types.InlineKeyboardMarkup()
        key_yes = types.InlineKeyboardButton(text="Начать поиск!", callback_data="spec")
        key_about = types.InlineKeyboardButton(text="О проекте", callback_data="about")
        keyboard.add(key_yes)
        keyboard.add(key_about)
        bot.edit_message_text(chat_id=message.chat.id,message_id=message.message_id,  text=text, reply_markup=keyboard)


def ask_spec(message,i):
    text="Выбери специальность"
    keyboard = types.InlineKeyboardMarkup()

    query = '''
    select job_name from jobs
    '''

    connection = sqlite3.connect("maindb.sqlite3")
    jobs=execute_read_query(connection,query)

    for t in range(i, i+2):
        key=create_key(jobs[t][0],callback_data="job;"+jobs[t][0])
        keyboard.add(key)

    if i+2<len(jobs):
        key=create_key("Еще?", callback_data=f"spec;{i+2}")
        keyboard.add(key)

    if i!=0:
        key=create_key("Посмотреть прошлые?", callback_data=f"spec;{i-2}")
        keyboard.add(key)

    main_menu_key = create_key("На главное меню", "main_menu")
    keyboard.add(main_menu_key)
    bot.edit_message_text(chat_id=message.chat.id,message_id=message.message_id, text=text, reply_markup=keyboard)
    

def ask_type_event(message,data):
    print(data)
    text = "Выбери что тебя интересует"
    keyboard = types.InlineKeyboardMarkup()

    query = '''
    select event_type from events
    '''
    connection = sqlite3.connect("maindb.sqlite3")
    events = execute_read_query(connection,query)

    for event in events:
        key=create_key(event[0],callback_data="event;0"+data+"*"+event[0])
        keyboard.add(key)
    key_yes = types.InlineKeyboardButton(text="Выбрать снова специальность", callback_data="spec")
    keyboard.add(key_yes)
    bot.edit_message_text(chat_id=message.chat.id,message_id=message.message_id, text=text, reply_markup=keyboard)

def display_events(message,data, i):
    dt=data.split("*")
    
    print(data)
    keyboard = types.InlineKeyboardMarkup()
    text = f"Список:{dt[1]}"   
    query_t = f'''
        SELECT event_name FROM job_events as je
        join events as e
        on je.event_type_id = e.event_id
        join jobs as j
        on je.event_job_id = j.job_id
        where j.job_name="{dt[0]}" and e.event_type="{dt[1]}"
        
        '''
    connection = sqlite3.connect("maindb.sqlite3")
    events = execute_read_query(connection,query_t)
        
    
    for n in range (i, i+2):
        if n<len(events):
            key=create_key(events[n][0],callback_data=f"curr;{data}*{events[n][0]}")
            keyboard.add(key)
   
    if i+2<len(events):
        key=create_key("Еще?", callback_data=f"event;{i+2}{data}")
        keyboard.add(key)
    if i!=0:
        key=create_key("Посмотреть прошлые?", callback_data=f"event;{i-2}{data}")
        keyboard.add(key)
    
    key_type = types.InlineKeyboardButton(text="Выбрать снова тип", callback_data=f"job;{dt[0]}")
    keyboard.add(key_type)
    bot.edit_message_text(chat_id=message.chat.id,message_id=message.message_id, text=text, reply_markup=keyboard)

def display_event(message,data):
    dt=data.split("*")
    event=data.split("*")[2]
    keyboard = types.InlineKeyboardMarkup()

    query = f'''
    select event_name, event_desc from job_events
    where event_name="{event}"
    '''

    connection = sqlite3.connect("maindb.sqlite3")
    info=execute_read_query(connection,query)
    text=f"{info[0][0]}\n{info[0][1]}"
    key_back = types.InlineKeyboardButton(text="Назад", callback_data=f"event;0{dt[0]}*{dt[1]}")
    keyboard.add(key_back)
    main_menu_key = create_key("На главное меню", "main_menu")
    keyboard.add(main_menu_key)
    bot.edit_message_text(chat_id=message.chat.id,message_id=message.message_id, text=text,reply_markup=keyboard )

def display_about(message):
    text =  "\"Маршруты карьеры\" разработали для вас помощника в вопросах трудоустройства и практики! МаКар с удовольствием поделится самыми актуальными новостями, собранными со всего города! Больше никаких многочасовых поисков — только пара кликов, только свежие сведенья."
    keyboard = types.InlineKeyboardMarkup()
    key_back = create_key("Вернуться назад", "main_menu")
    keyboard.add(key_back)
    bot.edit_message_text(chat_id=message.chat.id,message_id=message.message_id, text=text,reply_markup=keyboard )

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data[:4] == "spec":
        i=0
        if len(call.data)>4:
            i=int(call.data[5:6])
        ask_spec(call.message,i)
        
    if call.data[:3]=="job":
        ask_type_event(call.message,call.data[4:])

    if call.data[:5]=="event":
        i=int(call.data[6:7])
        display_events(call.message,call.data[7:],i)

    if call.data[:4]=="curr":
        display_event(call.message,call.data[5:])

    if call.data=="about":
        display_about(call.message)

    if call.data=="main_menu":
        get_text_messages(call.message, call.data)
    
    

bot.polling(none_stop=True, interval=0)