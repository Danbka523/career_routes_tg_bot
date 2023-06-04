from secret import client_token
from telebot import types
import telebot
import sqlite3
import sys
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
        bot.send_photo(chat_id=message.chat.id, photo=open('assets/img.jpg','rb'))
        text= "Привет! Меня зовут Макар! Я буду рад помочь тебе с поиском — просто нажми кнопку, и я расскажу всё, что знаю!"
        keyboard = types.InlineKeyboardMarkup()
        key_yes = create_key(text="Начать поиск!", callback_data="br")
        key_about = create_key(text="Сведения", callback_data="about")
        key_help = create_key(text="Помощь", callback_data="help")
        keyboard.add(key_yes)
        #keyboard.add(key_help)
        keyboard.add(key_about)
        bot.send_message(message.from_user.id,text=text, reply_markup=keyboard)

    if data=="main_menu":
        text= "Привет! Меня зовут Макар! Я буду рад помочь тебе с поиском — просто нажми кнопку, и я расскажу всё, что знаю!"
        keyboard = types.InlineKeyboardMarkup()
        key_yes = create_key(text="Начать поиск!", callback_data="br")
        key_about = create_key(text="Сведения", callback_data="about")
        key_help = create_key(text="Помощь", callback_data="help")
        keyboard.add(key_yes)
        #keyboard.add(key_help)
        keyboard.add(key_about)
        bot.edit_message_text(chat_id=message.chat.id,message_id=message.message_id,  text=text, reply_markup=keyboard)

def ask_branch(message, i):
    text="Выбери отрасль"
    keyboard = types.InlineKeyboardMarkup()

    query = '''
    select branch_name, branch_id from branches
    '''

    connection = sqlite3.connect("maindb.sqlite3")
    branches=execute_read_query(connection,query)

    for t in range(i, i+2):
        if t<len(branches):
            key=create_key(branches[t][0],callback_data="spec;0"+str(branches[t][1]))
            keyboard.add(key)

    if i+2<len(branches):
        key=create_key("Еще?", callback_data=f"br;{i+2}")
        keyboard.add(key)

    if i!=0:
        key=create_key("Посмотреть прошлые?", callback_data=f"br;{i-2}")
        keyboard.add(key)
    
   

    main_menu_key = create_key("На главное меню", "main_menu")
    keyboard.add(main_menu_key)
    bot.edit_message_text(chat_id=message.chat.id,message_id=message.message_id, text=text, reply_markup=keyboard)


def ask_spec(message,data,i):
    text="Выбери специальность"
    keyboard = types.InlineKeyboardMarkup()
    b_id=int(data)
    query = f'''
    select job_name, job_id from jobs as j
    join branches as b
    on j.branch_id = b.branch_id
    where b.branch_id = {b_id}
    '''

    connection = sqlite3.connect("maindb.sqlite3")
    jobs=execute_read_query(connection,query)

    for t in range(i, i+2):
        if t<len(jobs):
            key=create_key(str(jobs[t][0]),callback_data="job;"+str(jobs[t][1])+"*"+data)
            keyboard.add(key)

    if i+2<len(jobs):
        key=create_key("Еще?", callback_data=f"spec;{i+2}{data}")
        keyboard.add(key)

    if i!=0:
        key=create_key("Посмотреть прошлые?", callback_data=f"spec;{i-2}{data}")
        keyboard.add(key)
    key_br = create_key(text="Выбрать снова отрасль", callback_data=f"br")
    keyboard.add(key_br)
    main_menu_key = create_key("На главное меню", "main_menu")
    keyboard.add(main_menu_key)
    bot.edit_message_text(chat_id=message.chat.id,message_id=message.message_id, text=text, reply_markup=keyboard)
    

def ask_type_event(message,data):
    print(data)
    dt=data.split("*")
    text = "Выбери что тебя интересует"
    keyboard = types.InlineKeyboardMarkup()

    query = '''
    select event_type, event_id from events
    '''
    connection = sqlite3.connect("maindb.sqlite3")
    events = execute_read_query(connection,query)
 
    for event in events:
        
        key=create_key(str(event[0]),callback_data="event;0"+str(event[1])+"*"+data)
        keyboard.add(key)
    key_yes = create_key(text="Выбрать снова специальность", callback_data=f"spec;0{dt[1]}")
    keyboard.add(key_yes)
    bot.edit_message_text(chat_id=message.chat.id,message_id=message.message_id, text=text, reply_markup=keyboard)

def display_events(message,data, i):
    dt=data.split("*")
    
    print(data)
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    text = f"Вот, что я для тебя нашел:"   
    query_t = f'''
        SELECT event_name, event_id FROM job_events as je
        where je.event_job_id = {dt[1]} and je.event_type_id = {dt[0]}
    '''
    connection = sqlite3.connect("maindb.sqlite3")
    events = execute_read_query(connection,query_t)
        
    
    for n in range (i, i+2):
        if n<len(events):
            key=create_key(str(events[n][0]),callback_data=f"curr;{data}*{str(events[n][1])}")
            keyboard.add(key)
   
    if i+2<len(events):
        key=create_key("Еще?", callback_data=f"event;{i+2}{data}")
        keyboard.add(key)
        
    if i!=0:
        key=create_key("Посмотреть прошлые?", callback_data=f"event;{i-2}{data}")
        keyboard.add(key)
    
    key_type = create_key(text="Выбрать снова тип", callback_data=f"job;{dt[1]}*{dt[2]}")
    print(dt)
    keyboard.add(key_type)
    bot.edit_message_text(chat_id=message.chat.id,message_id=message.message_id, text=text, reply_markup=keyboard)

def display_event(message,data):
    dt=data.split("*")
    event=data.split("*")[3]
    keyboard = types.InlineKeyboardMarkup()

    query = f'''
    select event_name, event_desc, date, source from job_events
    where event_id={int(event)}
    '''

    connection = sqlite3.connect("maindb.sqlite3")
    info=execute_read_query(connection,query)

    text=f"{info[0][0]}\n{info[0][1]}\nКогда:{info[0][2]}\nПодробнее:{info[0][3]}"

    key_back = create_key(text="Назад", callback_data=f"event;0{dt[0]}*{dt[1]}*{dt[2]}")
    keyboard.add(key_back)

    main_menu_key = create_key("На главное меню", "main_menu")
    keyboard.add(main_menu_key)

    bot.edit_message_text(chat_id=message.chat.id,message_id=message.message_id, text=text,reply_markup=keyboard )

def display_about(message):
    text =  "\"Маршруты карьеры\" разработали для вас помощника в вопросах трудоустройства и практики\! Макар с удовольствием поделится самыми актуальными новостями, собранными со всего города\! Больше никаких многочасовых поисков — только пара кликов, только свежие сведения\."
    social = "[Наша группа в ВК](vk.com/public220791588)"
    keyboard = types.InlineKeyboardMarkup()
    key_back = create_key("На главное меню", "main_menu")
    keyboard.add(key_back)
    bot.edit_message_text(chat_id=message.chat.id,message_id=message.message_id, text=f"{social}\n{text}",reply_markup=keyboard, parse_mode='MarkDownV2' )

def display_help(message):
    text="В этом разделе будут предложены консулттации с экспертами(?????)\nРазличные полезные статьи и тесты тут тоже будут присутствовать"
    keyboard = types.InlineKeyboardMarkup()
    key_main_menu = create_key("На главное меню", "main_menu")
    keyboard.add(key_main_menu)
    bot.edit_message_text(chat_id=message.chat.id,message_id=message.message_id, text=text,reply_markup=keyboard )

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):

    if call.data[:2]=="br":
        i=0
        if (len(call.data)>3):
            i = int(call.data[4:5])
        ask_branch(call.message,i)

    if call.data[:4] == "spec":
        i=int(call.data[5:6])
        ask_spec(call.message,call.data[6:],i)
        
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
    
    if call.data=="help":
        display_help(call.message)



bot.polling(none_stop=True, interval=0)