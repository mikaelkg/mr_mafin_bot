import telebot
from telebot import types
import time
import random
from classes import *

bot = telebot.TeleBot(<your token>)

               
game=games()#создаем объект игры
               

#главная функция
@bot.message_handler(commands=['startgame'])
def start_game(message):    
        global game
        
        if not game.game_flag:#если игра еще не запущена
                game.game_flag=True

                #создается клавиатура с кнопкой с ссылкой на бота
                #добавление в игру осуществляется функцией add_users
                game.chat_id=message.chat.id
                keyboard = types.InlineKeyboardMarkup()
                callback_button=types.InlineKeyboardButton(url='telegram.me/mr_mafin_bot?start={0}'.format(game.chat_id),text='join')
                keyboard.add(callback_button)
                

                step=10#интервал обновления таймера в секундах
                times_format='{0:0>2}:{1:0>2}'.format(game.times//60,game.times%60)
                players_format='\n'.join([j.username for j in game.players.values()])#строка со списком всех игроков

                #считываение имени и фамилии пользователя
                name=[]
                if message.from_user.first_name:
                        name.append(message.from_user.first_name)
                if message.from_user.last_name:
                     name.append(message.from_user.last_name)
                name=' '.join(name)

                #клавиатура посылается в чат
                text=("<a href='http://telegram.me/{0}'>{4}</a> начал игру\nКоличество игроков: {1}\n"
                "Осталось времени: {2}\n{3}".format(message.from_user.username,len(game.players),
                                                    times_format,players_format,name))
                send=bot.send_message(message.chat.id, text, reply_markup=keyboard,parse_mode="HTML",disable_web_page_preview=True)

                #изменять значение таймера, пока не выйдет время
                while game.times>0:
                        game.times-=step
                        time.sleep(step)
                        times_format='{0:0>2}:{1:0>2}'.format(game.times//60,game.times%60)
                        players_format=('\n'.join(["<a href='http://telegram.me/{0}'>{1}</a>".format(j.true_username,j.username)
                                                   for j in game.players.values()]))
                        text=("<a href='http://telegram.me/{0}'>{4}</a> начал игру\nКоличество игроков: {1}\n"
                        "Осталось времени: {2}\n{3}".format(message.from_user.username,len(game.players),
                                                            times_format,players_format,name))
                        
                        bot.edit_message_text(chat_id=message.chat.id, message_id=send.message_id, text=text, reply_markup=keyboard,
                                              parse_mode="HTML",disable_web_page_preview=True)
                
                #удаление клавиатуры с кнопкой
                bot.edit_message_text(chat_id=game.chat_id, message_id=send.message_id, text=text,parse_mode="HTML",disable_web_page_preview=True)

                if len(game.players)<1:
                        bot.send_message(message.chat.id, 'Эх, мало игроков(((')
                        game=games()
                        
                else:
                        bot.send_message(message.chat.id, 'Ура, собрались!\nТак, сейчас раздам всем роли')
                        
                        game.gen_role()#генерация ролей

                        #отправление информации о роли
                        for i in game.players.values():
                                i.about_role(game,bot)
                                                           
                        while True:

                                #отправка в чат сообщения о начале ночи
                                with open("Text_for_night.txt",encoding="UTF-8") as text:
                                        text=text.read().split('break\n')
                                bot.send_message(message.chat.id, random.choice(text))

                                #ночные действия
                                for i in game.players.values():
                                        i.night_action(bot,game)

                                #ожидание пока не истечет время или все совершат действие
                                night_time_counter=game.night_time
                                while (night_time_counter>=0 and
                                       not all(map(lambda x: x.sloupok_flag==False or x.status!='Жив',game.players.values()))):
                                        night_time_counter-=1
                                        time.sleep(1)
                                        
                                #оповещение не успевших проголосовать игроков  
                                for i in game.players.values():
                                        i.sent_sloupok(bot)

                                game.night_kill(bot)#решние кого убить

                                #проверка статуса игры
                                if game.game_status(bot):
                                        break

                                bot.send_message(game.chat_id, 'Попробуйте вычислить кто мафия')
                                time.sleep(game.day_time)
                                bot.send_message(game.chat_id, 'Пришло время голосования')

                                #дневные действия 
                                for i in game.players.values():
                                        i.day_action(bot,game)
                                    
                                #ожидание пока не истечет время или все совершат действие
                                vote_time_counter=game.vote_time
                                while (vote_time_counter>0 and
                                       not all(map(lambda x: x.sloupok_flag==False or x.status!='Жив',game.players.values()))):
                                        vote_time_counter-=1
                                        time.sleep(1)
                                    
                                #оповещение не успевших проголосовать игроков      
                                for i in game.players.values():
                                       i.sent_sloupok(bot)
                                       
                                game.day_kill(bot)#решние кого казнить

                                #проверка статуса игры
                                if game.game_status(bot):
                                        break
                                
                        game=games()
                        
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
        global game
        if game.game_flag:
                data=call.data.split('_')
                if data[0] == "kill":
                        game.players[int(data[1])].death_digit+=1
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text='Выбор принят ' + game.players[int(data[1])].username)
                        game.players[call.message.chat.id].sloupok_flag=False
                elif data[0] == "skip":
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text='Выбор принят ')
                        game.players[call.message.chat.id].sloupok_flag=False 
                elif data[0] == 'execute':
                        game.players[int(data[1])].death_digit+=1
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text='Выбор принят ' + game.players[int(data[1])].username)
                        game.players[call.message.chat.id].sloupok_flag=False
                        bot.send_message(game.chat_id, '{0} думет, что {1} мафия'.format(game.players[call.from_user.id].username,
                                                                                    game.players[int(data[1])].username))
                elif data[0] == 'check':
                        game.players[call.message.chat.id].checks=game.players[int(data[1])]
                        game.players[call.message.chat.id].check=game.players[int(data[1])].role
                        game.players[call.message.chat.id].whom_check=game.players[int(data[1])].username
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text='Выбор принят ' + game.players[int(data[1])].username)
                        if not game.players[call.message.chat.id].choices(bot):
                                game.players[call.message.chat.id].sloupok_flag=False
                elif data[0] == 'drunk':
                        game.players[call.message.chat.id].drunk=game.players[int(data[1])]
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text='Выбор принят ' + game.players[int(data[1])].username)
                        game.players[call.message.chat.id].sloupok_flag=False
                elif data[0] == 'treat':
                        game.players[call.message.chat.id].treat=game.players[int(data[1])]
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text='Выбор принят ' + game.players[int(data[1])].username)
                        game.players[call.message.chat.id].sloupok_flag=False
                elif data[0] == 'choice':
                        game.players[call.message.chat.id].choice=data[1]
                        if data[1]=="Yes":
                                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                      text='Выбор принят ' + "Да")
                        else:
                                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                      text='Выбор принят ' + "Нет")
                        game.players[call.message.chat.id].sloupok_choice=False
                        game.players[call.message.chat.id].sloupok_flag=False
                                        
@bot.message_handler(commands=['start'])
def add_users(message):
        global game
        text=message.text.split()
        if len(text)>1:#проверка на то, что человек нажал start, а не прислал команду
                if game.game_flag:#проверка на то, что начата игра
                        
                        #считываение имени и фамилии пользователя
                        name=[]
                        if message.from_user.first_name:
                                name.append(message.from_user.first_name)
                        if message.from_user.last_name:
                                name.append(message.from_user.last_name)
                        name=' '.join(name)
                        
                        game.players[message.from_user.id]=gamer(name,message.from_user.id,int(text[1]),
                                                                 message.from_user.username)#создание объекта игрока
                        
                        bot.send_message(message.from_user.id, 'Ты присоединился!')
                                
@bot.message_handler(commands=['extend'])
def extend_time(message):
        global game
        if game.game_flag:
                extend=message.text.split()
                if len(extend)==1:
                        game.times+=30
                else:
                        if extend[1].isdigit() and 0<int(extend[1]) and game.times+int(extend[1])<=5*60:
                                game.times+=int(extend[1])
                                

@bot.message_handler(commands=['flee'])
def flee(message):
        global game
        if game.game_flag:
                if message.from_user.id in players:
                        if game.times<=0:
                                if game.players[message.from_user.id].status=='Жив':
                                        game.players[message.from_user.id].status=='Сбежал'
                                        game.players[message.from_user.id].position=='Проигравший'
                                        bot.send_message(message.chat.id, '{0} оставил игру'.format(game.players[message.from_user.id].username))
                        else:
                                bot.send_message(message.chat.id, '{0} передумал играть'.format(game.players[message.from_user.id].username))
                                del game.players[message.from_user.id]
                
@bot.message_handler(commands=['forcestart'])
def force_start(message):
        global game
        if game.game_flag==True:
                game.times=0
@bot.message_handler(content_types=["text"])
def mafia_chat(message):
        global game
        if game.game_flag==True:
                if game.players[message.from_user.id].role=='Мафия' and game.players[message.from_user.id].status=='Жив':
                        for i in game.players.values():
                                if i.role=='Мафия' and i.status=='Жив' and i.gamer_id!= message.from_user.id:
                                        bot.send_message(i.gamer_id, message.from_user.username+':\n'+message.text)

if __name__ == '__main__':
    bot.polling(none_stop=True)
