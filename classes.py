import telebot
from telebot import types
import time
import random
class games:
        def __init__(self):
                #количество персонажей в зависимости от количества игроков
                self.mafia={1:1,2:1,3:1,4:1,5:2,6:2,7:2} 
                self.comissars={1:0,2:0,3:1,4:1,5:1,6:1,7:1}
                self.alcoholic={1:0,2:0,3:1,4:1,5:1,6:1,7:1}
                self.doctors={1:0,2:0,3:0,4:1,5:1,6:1,7:1}
                
                self.players=dict()#словарь игроков ключ - id, значение - объект игрока
                self.game_flag=False#флаг игры, пока игра не начата в состоянии False
                
                self.chat_id=None#id часта

                self.times=2*60#время для того, чтобы собраться игрокам
                
                self.night_time=60#время для ночи
                self.day_time=30#время для обсуждения
                self.vote_time=30#время для голосования

                self.count_mafia=0
                self.count_civilian=0
                
        #статус игры возвращает False, пока игра не закончится
        def game_status(self,bot):
                
                flag=False
                
                if self.count_civilian<=self.count_mafia:
                        bot.send_message(self.chat_id,'Мафия победила!')
                        for i in self.players.values():
                                if i.role=='Мафия':
                                        i.position='Победитель'
                                else:
                                        i.position='Проигравший'
                        flag=True
                        
                elif self.count_mafia==0:
                        bot.send_message(self.chat_id,'Мирные победили!')
                        for i in self.players.values():
                                if i.role!='Мафия':
                                        i.position='Победитель'
                                else:
                                        i.position='Проигравший'
                        flag=True

                players_format=('\n'.join(["{4}.<a href='http://telegram.me/{5}'>{0}</a>: "
                                          "<b>{1}</b>{2}<i>{3}</i>".format(j.username,j.status if j.status!="Пьян" else "Жив",
                                                                           " - " + j.role if j.status=="Мертвец" or j.position else '',
                                                                           " - " + j.position if j.position else '',i+1,
                                                                           j.true_username) for i,j in enumerate(self.players.values())]))

                text='Живые и мертвые:\n'+players_format
                bot.send_message(self.chat_id, text,parse_mode="HTML",disable_web_page_preview=True)
                return flag
        
        #генерация ролей
        def gen_role(self):
                
                players_list=list(self.players.keys())
                self.count_mafia=self.mafia[len(self.players)]
                self.count_civilian=len(self.players)-self.count_mafia
                self.count_comissars=self.comissars[len(self.players)]
                self.count_doctors=self.doctors[len(self.players)]
                self.count_alcoholic=self.alcoholic[len(self.players)]
                
                for i in range(self.count_mafia):
                        vibor=random.choice(players_list)
                        list_param=[self.players[vibor].username,
                                    self.players[vibor].gamer_id,self.players[vibor].chat_id,self.players[vibor].true_username]
                        self.players[vibor]=mafia(*list_param)
                        self.players[vibor].role="Мафия"
                        #self.players[vibor+1]=doctor(*list_param)
                        players_list.remove(vibor)
                        
                for i in range(self.count_comissars):
                        vibor=random.choice(players_list)
                        list_param=[self.players[vibor].username,
                                    self.players[vibor].gamer_id,self.players[vibor].chat_id,self.players[vibor].true_username]
                        self.players[vibor]=comissar(*list_param)
                        self.players[vibor].role="Комиссар"
                        #self.players[vibor+1]=civilian(*list_param)
                        players_list.remove(vibor)

                for i in range(self.count_doctors):
                        vibor=random.choice(players_list)
                        list_param=[self.players[vibor].username,
                                    self.players[vibor].gamer_id,self.players[vibor].chat_id,self.players[vibor].true_username]
                        self.players[vibor]=doctor(*list_param)
                        self.players[vibor].role="Доктор"
                        #self.players[vibor+1]=mafia(*list_param)
                        players_list.remove(vibor)
                        
                for i in range(self.count_alcoholic):
                        vibor=random.choice(players_list)
                        list_param=[self.players[vibor].username,
                                    self.players[vibor].gamer_id,self.players[vibor].chat_id,self.players[vibor].true_username]
                        self.players[vibor]=alcoholic(*list_param)
                        self.players[vibor].role="Алкоголик"
                        players_list.remove(vibor)
                        
                for i in players_list:
                        list_param=[self.players[i].username,
                                    self.players[i].gamer_id,self.players[i].chat_id,self.players[i].true_username]
                        self.players[i]=civilian(*list_param)
                        self.players[i].role="Мир"

        #Решение, кого убить
        def night_kill(self,bot):
                def send_alcoholic():
                        for i in self.players.values():
                                if i.role=="Алкоголик" and i.status=="Жив":
                                        if i.drunk:
                                                i.drunk.status="Пьян"
                                                i.send_result(bot)
                send_alcoholic()
                def mafia_choices():
                        vibor=[]
                        for i in self.players.values():
                                if i.status=="Пьян" and i.role=="Мафия":
                                        return None
                        for j,i in self.players.items():
                               if i.death_digit>0 and i.status=="Жив":
                                       vibor.append(i)
                        if len(vibor)==1:
                                return vibor[0]
                mafia_choice=mafia_choices()

                def send_doctor(mafia_choice):
                        ans=mafia_choice
                        for i in self.players.values():
                                if i.role=="Доктор" and i!=mafia_choice and i.status=="Жив" and i.treat:
                                        if mafia_choice==i.treat or mafia_choice=="Вылечен":
                                                i.send_result(bot,True)
                                                ans="Вылечен"
                                        else:
                                                i.send_result(bot,False)
                        return ans
                
                mafia_choice=send_doctor(mafia_choice)
                
                def send_comissar(mafia_choice):
                        kill=0
                        for i in self.players.values():
                                if i.role=="Комиссар" and i!=mafia_choice and i.status=="Жив":
                                        kill+=i.send_role(bot)
                        return kill
                
                kill=send_comissar(mafia_choice)
                
                if mafia_choice!="Вылечен" and mafia_choice!=None:
                        if mafia_choice.status!="Мертвец":
                                mafia_choice.status="Мертвец"
                                if mafia_choice.role=="Мир":
                                        with  open(r'night_kill\civilian.txt',encoding="UTF-8") as text:
                                                text=text.read()
                                elif mafia_choice.role=="Комиссар":
                                        with  open(r'night_kill\comissar.txt',encoding="UTF-8") as text:
                                                text=text.read()
                                elif mafia_choice.role=="Алкоголик":
                                        with  open(r'night_kill\alcoholic.txt',encoding="UTF-8") as text:
                                                text=text.read()
                                elif mafia_choice.role=="Доктор":
                                        with  open(r'night_kill\doctor.txt',encoding="UTF-8") as text:
                                                text=text.read()
                                bot.send_message(self.chat_id, text.format(mafia_choice.username))
                        self.count_civilian-=1
                else:
                        if not kill:
                                with  open(r'night_kill\nothing.txt',encoding="UTF-8") as text:
                                        text=text.read()
                                bot.send_message(self.chat_id, text)
                        else:
                                self.count_civilian-=1
                for i in self.players.values():
                        i.death_digit=0

        def day_kill(self,bot):
                killed=max(self.players.values(),key=lambda x: x.death_digit)
                if killed.death_digit!=0:
                        killed=random.choice([i for i in self.players.values() if i==killed])
                        killed.status="Мертвец"
                        bot.send_message(self.chat_id, 'Решением жителей был казнен {0}. Он был {1}'.format(killed.username,killed.role))
                        if killed.role=="Мафия":
                                self.count_mafia-=1
                        else:
                                self.count_civilian-=1

                else:
                        bot.send_message(self.chat_id, 'Хмм...Похоже никто не проголосовал')
                        
                for i in self.players.values():
                        i.death_digit=0
                        if i.status=="Пьян":
                                i.status="Жив"

class gamer:
        def __init__(self,username,gamer_id,chat_id,true_username):
                
                self.username=username#Имя и фамилия пользователя
                self.gamer_id=gamer_id
                self.chat_id=chat_id
                self.true_username=true_username#username пользователя, если есть
                
                self.status="Жив"
                self.position=None#Принимает значение Победитель и Приогравший
                self.sloupok_flag=True#Флаг несовершения действия
                self.sloupok_choice=False
                self.death_digit=0#другой флаг несовершения действия (сейчас для только для комиссара)
                self.role=None
                
        def day_action(self,bot,game):
                if self.status=='Жив':
                        self.sloupok_flag=True
                        keyboard = types.InlineKeyboardMarkup(1)
                        for j in game.players.values():
                                if (j.status=='Жив' or j.status=="Пьян") and self.gamer_id!=j.gamer_id:
                                        button=types.InlineKeyboardButton(callback_data='execute_'+str(j.gamer_id),text=j.username)
                                        keyboard.add(button)
                        self.text_message=bot.send_message(self.gamer_id, 'Как думаешь, кто из них мафия?', reply_markup=keyboard)
                
        def sent_sloupok(self,bot):
                if self.status=="Жив":
                        if self.sloupok_choice:
                                bot.edit_message_text(chat_id=self.gamer_id,
                                                              message_id=self.text_choice.message_id,text='Выбор принят Нет')
                                self.choice="No"
                                self.sloupok_flag=False
                        if self.sloupok_flag:
                              bot.edit_message_text(chat_id=self.gamer_id,message_id=self.text_message.message_id,text='Время вышло!')

                self.sloupok_flag=True

class mafia(gamer):
        
        def night_action(self,bot,game):
                if self.status=="Жив":
                        keyboard = types.InlineKeyboardMarkup(1)
                        for j in game.players.values():
                                if j.role!='Мафия' and (j.status=='Жив' or j.status=="Пьян") and j.gamer_id!=self.gamer_id:
                                        button=types.InlineKeyboardButton(callback_data='kill_'+str(j.gamer_id),text=j.username)
                                        keyboard.add(button)
                        button=types.InlineKeyboardButton(callback_data='skip_'+"skip",text="skip")
                        keyboard.add(button)   
                        self.text_message=bot.send_message(self.gamer_id, 'Кого ты хочешь убить?', reply_markup=keyboard)
                                
        def about_role(self,game,bot):

                #считывание всех мафий в игре
                bratva=[]
                for j in game.players.values():
                        if self.gamer_id!=j.gamer_id and j.role=='Мафия':
                                bratva.append(j.username)
                                
                if bratva:#если есть другие мафии
                        with open(r'mafia\about_role.txt',encoding="UTF-8") as text:
                                text=text.read()
                        bot.send_message(self.gamer_id,text.format(game.night_time//2,game.night_time,','.join(bratva)))
                else:#если мафия одна
                        with  open(r'mafia\about_role_alone.txt',encoding="UTF-8") as text:
                                text=random.choice(text.read().split('break\n'))
                        bot.send_message(self.gamer_id,text.format(game.night_time))
                
class civilian(gamer):
        
        def night_action(self,players,bot):
                self.sloupok_flag=False
                
        def about_role(self,game,bot):

                with open(r"civilian\about_role.txt",encoding="UTF-8") as text:
                        text=text.read().split('break\n')
                bot.send_message(self.gamer_id,random.choice(text))
        
class comissar(gamer):
        def night_action(self,bot,game):
                if self.status=="Жив":
                        keyboard = types.InlineKeyboardMarkup(1)
                        for j in game.players.values():
                                if j.status=='Жив' and j.gamer_id!=self.gamer_id:
                                        button=types.InlineKeyboardButton(callback_data='check_'+str(j.gamer_id),text=j.username)
                                        keyboard.add(button)
                        button=types.InlineKeyboardButton(callback_data='skip_'+"skip",text="skip")
                        keyboard.add(button)   
                        self.text_message=bot.send_message(self.gamer_id, 'Кого ты хочешь допросить?', reply_markup=keyboard)
        def choices(self,bot):
                self.sloupok_choice=random.choice([True,True])
                if self.sloupok_choice:
                        with open(r"comissar\choice\choice.txt",encoding="UTF-8") as text:
                                text=text.read()
                        if self.check=="Мафия" or self.check=="Доктор":
                                with  open(r"comissar\choice\mafia_doctor.txt",encoding="UTF-8") as texts:
                                        text=text+"breakln\n"+texts.read()
                        text=text.split("breakln\n")
                        self.index=random.randint(0,len(text)-1)
                        text=random.choice(text[self.index].split("break\n")).format(self.whom_check)
                        text=text.split("choice")
                        if self.index==1:
                                self.rnd=0
                        elif self.index==2:
                                self.rnd0=1
                        keyboard = types.InlineKeyboardMarkup(2)
                        button=types.InlineKeyboardButton(callback_data='choice_Yes',text="Да")
                        keyboard.add(button)
                        button=types.InlineKeyboardButton(callback_data='choice_No',text="Нет")
                        keyboard.add(button)
                        bot.send_message(self.gamer_id,text=text[0])
                        self.text_choice=bot.send_message(self.gamer_id,text=text[1],reply_markup=keyboard)
                        return True
                else:
                        return False

        def send_role(self,bot):
                kill=False
                
                if self.whom_check:
                        if not self.choice:
                                if self.check=="Мир":
                                        with open(r"comissar\civilian.txt",encoding="UTF-8") as text:
                                                text=text.read().split("breakln\n")[self.index]
                                                text=random.choice(text.split("break\n"))  
                                elif self.check=="Алкоголик":
                                        with open(r"comissar\alcoholic.txt",encoding="UTF-8") as text:
                                                text=text.read().split("breakln\n")[self.index]
                                                text=random.choice(text.split("break\n"))  
                                elif self.check=="Мафия":
                                        with open(r"comissar\mafia.txt",encoding="UTF-8") as text:
                                                text=text.read().split("breakln\n")[self.index]
                                                text=random.choice(text.split("break\n"))  
                                elif self.check=="Доктор":
                                        with open(r"comissar\doctor.txt",encoding="UTF-8") as text:
                                                text=text.read().split("breakln\n")[self.index]
                                                text=random.choice(text.split("break\n"))     
                        else:
                                if self.choice=="Yes":
                                        if self.check=="Мир":
                                                with open(r"comissar\choice\Yes\civilian.txt",encoding="UTF-8") as text:
                                                        text=text.read().split("breakln\n")[self.index]
                                                        text=random.choice(text.split("break\n"))
                                        elif self.check=="Алкоголик":
                                                with open(r"comissar\choice\Yes\alcoholic.txt",encoding="UTF-8") as text:
                                                        text=text.read().split("breakln\n")[self.index]
                                                        text=random.choice(text.split("break\n"))
                                        elif self.check=="Доктор":
                                                with open(r"comissar\choice\Yes\doctor.txt",encoding="UTF-8") as text:
                                                        text=text.read().split("breakln\n")[self.index]
                                                        text=random.choice(text.split("break\n"))
                                                if self.rnd0:
                                                        self.checks.status="Мертвец"
                                                        kill=True
                                                        with open(r"night_kill/doctor.txt",encoding="UTF-8") as texts:
                                                                texts=texts.read() 
                                                        bot.send_message(self.chat_id,text=texts.format(self.checks.username))
                                                        
                                        elif self.check=="Мафия":
                                                if random.randint(self.rnd0,self.rnd):
                                                        with open(r"comissar\choice\Yes\mafia\luck.txt",encoding="UTF-8") as text:
                                                                text=text.read().split("breakln\n")[self.index]
                                                                text=random.choice(text.split("break\n"))
                                                else:
                                                        with open(r"comissar\choice\Yes\mafia\bad_luck.txt",encoding="UTF-8") as text:
                                                                text=text.read().split("breakln\n")[self.index]
                                                                text=random.choice(text.split("break\n"))
                                                        with open(r"comissar\choice\Yes\kill.txt",encoding="UTF-8") as texts:
                                                                texts=texts.read()
                                                        bot.send_message(self.chat_id,text=texts.format(self.username))
                                                        self.status="Мертвец"
                                                        kill=True
                                else:
                                        if not random.randint(0,2) and not self.rnd0:
                                                with open(r"comissar\choice\No\kill.txt",encoding="UTF-8") as text:
                                                        text=text.read().split("breakln\n")[self.index]
                                                        text=random.choice(text.split("break\n"))  
                                                with open(r"comissar\choice\Yes\kill.txt",encoding="UTF-8") as texts:
                                                        texts=texts.read() 
                                                bot.send_message(self.chat_id,text=texts.format(self.username))
                                                self.status="Мертвец"
                                                kill=True
                                        else:
                                                if self.check=="Мир":
                                                        with open(r"comissar\choice\No\civilian.txt",encoding="UTF-8") as text:
                                                                text=text.read().split("breakln\n")[self.index]
                                                                text=random.choice(text.split("break\n")) 
                                                elif self.check=="Алкоголик":
                                                        with open(r"comissar\choice\No\alcoholic.txt",encoding="UTF-8") as text:
                                                                text=text.read().split("breakln\n")[self.index]
                                                                text=random.choice(text.split("break\n")) 
                                                elif self.check=="Мафия":            
                                                        with open(r"comissar\choice\No\mafia.txt",encoding="UTF-8") as text:
                                                                text=text.read().split("breakln\n")[self.index]
                                                                text=random.choice(text.split("break\n"))
                                                elif self.check=="Доктор":            
                                                        with open(r"comissar\choice\No\doctor.txt",encoding="UTF-8") as text:
                                                                text=text.read().split("breakln\n")[self.index]
                                                                text=random.choice(text.split("break\n"))

                                        
                        bot.send_message(self.gamer_id,text=text.format(self.whom_check))
                        
                self.checks=None                                   
                self.choice=None
                self.whom_check=None
                self.check=None
                self.sloupok_choice=False
                self.rnd=1
                self.rnd0=0
                
                return kill
        
        def about_role(self,game,bot):
                
                self.rnd=1
                self.rnd0=0
                self.checks=None
                self.whom_check=None
                self.check=None
                self.choice=None
                
                with open(r"comissar\about_role.txt",encoding="UTF-8") as text:
                        text=text.read()
                        
                bot.send_message(self.gamer_id,text)
class doctor(gamer):
        def night_action(self,bot,game):
                if self.status=="Жив":
                        keyboard = types.InlineKeyboardMarkup(1)
                        for j in game.players.values():
                                if j.status=='Жив' and j.gamer_id!=self.gamer_id:
                                        button=types.InlineKeyboardButton(callback_data='treat_'+str(j.gamer_id),text=j.username)
                                        keyboard.add(button)
                        button=types.InlineKeyboardButton(callback_data='skip_'+"skip",text="skip")
                        keyboard.add(button)   
                        self.text_message=bot.send_message(self.gamer_id, 'Кого ты хочешь вылечить?', reply_markup=keyboard)
        def send_result(self,bot,result):
                if result:
                        bot.send_message(self.gamer_id,text="Ура, ты спас {0} от неминуемой гибели!".format(self.treat.username))
                        bot.send_message(self.treat.gamer_id,text="Ты был серьезно ранен, но доблестный доктор спас тебя!")
                else:
                        bot.send_message(self.gamer_id,text="Похоже {0} не был атакован...".format(self.treat.username))

                self.treat=None                  
        def about_role(self,game,bot):
                self.role="Доктор"
                
                self.treat=None
                with open(r"doctor\about_role.txt",encoding="UTF-8") as text:
                        text=text.read().split('break\n')
                bot.send_message(self.gamer_id,random.choice(text))
class alcoholic(gamer):
        def night_action(self,bot,game):
                if self.status=="Жив":
                        keyboard = types.InlineKeyboardMarkup(1)
                        for j in game.players.values():
                                if j.status=='Жив' and j.gamer_id!=self.gamer_id:
                                        button=types.InlineKeyboardButton(callback_data='drunk_'+str(j.gamer_id),text=j.username)
                                        keyboard.add(button)
                        button=types.InlineKeyboardButton(callback_data='skip_'+"skip",text="skip")
                        keyboard.add(button)
                        if self.first_flag:
                                with open(r"alcoholic\night_action.txt",encoding="UTF-8") as text:
                                        text=text.read().split('break\n')
                        else:
                                self.text_message=bot.send_message(self.gamer_id, 'С кем ты сегодня будешь пить?', reply_markup=keyboard)
        def send_result(self,bot):
                bot.send_message(self.gamer_id,text="Похоже {0} оказался не таким уж хорошим собутыльником.\n"
                                 "Всего 2 литра водки, а он уже никакой".format(self.drunk.username))
                bot.send_message(self.drunk.gamer_id,text="Да...Давненько ты так не напивался, ты еще не скоро встанешь")

                self.drunk=None
                
        def about_role(self,game,bot):
                self.role="Алкоголик"
                self.drunk=None
                self.first_flag=None
                with open(r"alcoholic\about_role.txt",encoding="UTF-8") as text:
                        text=text.read().split('break\n')
                bot.send_message(self.gamer_id,random.choice(text))
