# libs
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import Bot, ReplyKeyboardMarkup, KeyboardButton, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.utils.request import Request

import time
import datetime

from threading import Thread

import config

## -- logging -- ##

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)



## -- game logic -- ##

class GameBot:
    def __init__(self, game, bot):
        self.game = game
        self.bot = bot
        self.upd = self.bot.upd
        self.dp = self.bot.dp

    def send_message(self, *args, **kwargs):
        self.bot.send_message(chat_id=self.game.chat.id)
    


class Game:
    bots_rights = ["can_invite_users", "can_pin_messages", "can_promote_members"]
    squirrel_rights = ["can_delete_messages", "can_restrict_members"]

    roles = ["Редактура", "СММ", "Дизайн", "Корректура", "Аналитика"]

    ok_message = "Понятно"
    ready_message = "Готово"
    publish_message = "Опубликовать"
    
    total_success = 20

    stickers = config.data.stickers

    @classmethod
    def inline_button(cls, action_type):
        return InlineKeyboardMarkup.from_button(InlineKeyboardButton(getattr(Game, action_type+"_message"), callback_data=action_type))

    def next_step(self, cb, handler_type, text=None):
        def base_cb(update, context):
            context.bot.dp.remove_handler(self.query_handler)
            return cb(update, context)
        if handler_type == CallbackQueryHandler:
            def new_cb(update, context):
                update.callback_query.answer()
                return base_cb(update, context)
            self.query_handler = handler_type(new_cb)
        else:
            self.query_handler = handler_type(Filters.text([text]), base_cb)
        return self.query_handler

    def __init__(self, chat, bots={}):
        self.chat = chat
        self.bots = bots
        self.scale_msg = None
        self.success = 0
        self.players = []

    def inc_success(self, v):
        raw_success = self.success + v
        self.success = min(max(raw_success, 0), Game.total_success)
    
    def __getattr__(self, name):
        if name in self.bots.keys():
            return self.bots[name]
        else:
            raise AttributeError

    def update_preparations(self):
        status = {"ready": None, "bots": [], "rights": None, "is_supergroup": None}
        for bot in self.bots.values():
            try:
                bot_member = self.chat.get_member(bot.id)
            except:
                status["bots"].append(bot.name)
            else:
                if bot_member.status == 'left':
                    status["bots"].append(bot.name)
                else:
                    try:
                        self.squirrel.promote_chat_member(self.chat.id, bot.id, **{r: True for r in Game.bots_rights})
                    except:
                        pass
        squirrel_member = self.chat.get_member(self.squirrel.id)
        check_rights = Game.bots_rights + Game.squirrel_rights
        print({r: getattr(squirrel_member, r) for r in check_rights})
        rights = all(map(lambda a: getattr(squirrel_member, a), Game.bots_rights+Game.squirrel_rights))
        status["rights"] = rights
        status["supergroup"] = self.chat.type == "supergroup"
        status["ready"] = (not status["bots"]) and status["rights"] and status["supergroup"]
        print(status)
        return status

    def scale_ui(self):
        return f"Шкала *Злободневности*: `[{'#'*self.success + '.'*(Game.total_success-self.success)}]`"

    def redraw_scale(self):
        self.scale_msg.edit_text(self.scale_ui(), parse_mode=ParseMode.MARKDOWN)
        time.sleep(0.2)
        self.scale_msg.unpin()
        time.sleep(0.2)
        self.scale_msg.pin()

    def update_scale(self, value):
        self.inc_success(value)
        self.redraw_scale()
        self.squirrel.send_sticker(self.chat.id,
                                   Game.stickers['hype'])


    def timer_text(self, current_time):
        ms = lambda s: f"{s//60}:{'0'*(2-len(str(s%60)))}{s%60}"
        if current_time > self.timer_end:
            return "Время закончилось!"
        else:
            return f"У вас осталось *{ms((self.timer_end-current_time).seconds)}*"

    def send_timer(self, minutes):
        current_time = datetime.datetime.now()
        self.timer = True
        self.timer_end = current_time + datetime.timedelta(0, minutes*60)
        self.timer_msg = self.squirrel.send_message(self.chat.id,
            text=self.timer_text(current_time),
            parse_mode=ParseMode.MARKDOWN)
        
        def timer_loop():
            isend = False
            while not isend and self.timer:
                time.sleep(3)
                isend = self.update_timer()

        self.timer_thread = Thread(target=timer_loop, name="timer_loop")
        self.timer_thread.start()
        
    def update_timer(self):
        current_time = datetime.datetime.now()
        self.timer_msg.edit_text(self.timer_text(current_time), parse_mode=ParseMode.MARKDOWN)
        if current_time > self.timer_end: return True    

    def start(self, update, context):
        self.chat = update.effective_chat
        status = self.update_preparations()
        if status["ready"]:
            self.squirrel.send_message(self.chat.id,
                        text="все здесь??? добро пожаловать в «сорокин хвост»! я белка, налаживаю процессы работы редакции!!!")
            
            time.sleep(2)
            
            self.squirrel.send_message(self.chat.id,
                        text="конечно, вы все знаете про наш журнал, но вот кое-что про наше внутреннее устройство")
            
            time.sleep(2)

            self.squirrel.send_message(self.chat.id,
                        text='*Сорокин хвост* существует для укрепления горизонтальных связей внутри сообщества птиц, зверей и рыб в Хвойном Лесу. ' +\
                            'Каждый день мы публикуем материалы наших читателей и собственные новостные заметки о жизни в регионе. Наша команда состоит '+\
                            'из энтузиастов, которых объединяют две вещи: любовь к журналистике и желание помочь своему родному краю. ' +\
                            'Мы верим в каждого из наших сотрудников и надеемся, что вместе мы сможем сделать наш общий дом лучше.',
                        parse_mode = ParseMode.MARKDOWN,
                        reply_markup=InlineKeyboardMarkup.from_button(InlineKeyboardButton(text=Game.ok_message, callback_data="ok")))
            
            self.squirrel.dp.add_handler(self.next_step(self.start2, CallbackQueryHandler))

        else:
            self.squirrel.send_message(self.chat.id,
                        text="еще не все готово для начала игры!\n" +\
                             f"добавьте ботов в чат: {' '.join(status['bots'])}\n" if status['bots'] else "" +\
                             f"дайте мне полные права администратора!\n" if not status["rights"] else "" +\
                             f"для игры необходимо чтобы этот чат был супергруппой." if not status["supergroup"] else "" )

            

    def start2(self, update, context):

        time.sleep(2)

        self.floppa.send_message(self.chat.id,
                    text="Как я вас ждал! Столько новостей, а рук не хватает…")
        
        time.sleep(1.5)

        self.squirrel.send_message(self.chat.id,
                    text="даа! знакомьтесь, Флоппа - будет курировать вашу работу над журналистскими расследованиями!!")
        
        time.sleep(1.5)

        self.squirrel.sendPhoto(self.chat.id, open('team_floppa_2.jpg', 'rb'))
        
        time.sleep(3)
        
        self.floppa.send_message(self.chat.id,
                    text="Приятно познакомиться! Мы всем Фондом заинтересованы в вашей работе")

        time.sleep(1.5)

        self.floppa.send_sticker(self.chat.id,
                    Game.stickers['good_day'])
        
        time.sleep(4)

        keyboard = lambda roles: InlineKeyboardMarkup.from_column([InlineKeyboardButton(text=role, callback_data=role) for role in roles])

        roles_heading = "так, хорошо бы распределить роли\. выберите что вам подходит:"
        self.squirrel.send_message(self.chat.id,
                    text=roles_heading,
                    reply_markup=keyboard(Game.roles),
                    parse_mode=ParseMode.MARKDOWN_V2
                    )
        
        choosen_roles = lambda: list(map(lambda p: p["role"], self.players))

        ready_sent = False

        def button(update, context):
            query = update.callback_query
            query.answer()
            already_choosed = next(filter(lambda p: p['user'].id == query.from_user.id, self.players), None)
            if already_choosed:
                already_choosed['role'] = query.data
            else:
                self.players.append({'role': query.data, 'user': query.from_user})
            query.edit_message_text(text=roles_heading+"\n"+\
                "\n".join(map(lambda p: f"`@{p['user'].username}` : *{p['role']}*", self.players)),
                reply_markup=keyboard(filter(lambda r: r not in choosen_roles(), Game.roles)),
                parse_mode=ParseMode.MARKDOWN_V2)
            
            nonlocal ready_sent
            if not ready_sent:
                self.squirrel.send_message(self.chat.id,
                                            text=f"Пришлите мне сообщение *{Game.ready_message}* как закончите!",
                                            parse_mode=ParseMode.MARKDOWN)
                ready_sent = True

        self.button_handler = CallbackQueryHandler(button)

        def end_roles(update, context):
            self.squirrel.dp.remove_handler(self.button_handler)
            return self.start3(update, context)

        self.squirrel.dp.add_handler(self.button_handler)
        self.squirrel.dp.add_handler(self.next_step(end_roles, MessageHandler, Game.ready_message))
            

    def start3(self, update, context):

        self.squirrel.send_message(self.chat.id,
                text="приятно вас видеть в нашей редакции!!")

        time.sleep(1)

        self.init_scale(update, context)

        self.squirrel.send_sticker(self.chat.id,
                Game.stickers['peace'])

        time.sleep(4)

        self.magpie.send_message(self.chat.id,
                text="коллеги привет! у меня сообщение для вас")

        time.sleep(3)

        self.squirrel.send_message(self.chat.id,
                text="привет! Знакомьтесь, это Cорока - наша корреспондентка, присылает вести с полей")

        time.sleep(3)

        self.magpie.send_message(self.chat.id,
                text="вот что мне удалось собрать")

        time.sleep(1)

        self.magpie.send_message(self.chat.id,
                text="""Здравствуйте, Сорока!

Я живу на Пихтовой улице и буквально только что увидел, как лисичкам снова продавали спички! Это возмутительно! Прошлым летом они подожгли море, и мы всем лесом ходили его тушить, Вы же сами об этом писали. Я уверен, что они опять что-то задумали. Надо предпринять какие-то меры! Сейчас по всей области идут пожары, поэтому мы все должны быть крайне осторожны со спичками.

С уважением,
Кролик

Пожалуйста, не пишите, что это я Вам пожаловался. Я немного боюсь лисичек после того случая с Медведем. Думаю, Вы в курсе.
""",
                reply_markup=InlineKeyboardMarkup.from_button(InlineKeyboardButton(text=Game.ok_message, callback_data="ok")))

        self.magpie.dp.add_handler(self.next_step(self.start4, CallbackQueryHandler))

    
        
    def start4(self, update, context):

        time.sleep(0.5)

        self.magpie.send_message(self.chat.id,
                text="мне нужно срочно вылетать")
        
        time.sleep(1)

        self.magpie.send_message(self.chat.id,
                text="отредактируете сами")

        time.sleep(2.5)

        self.floppa.send_message(self.chat.id,
                text="Неужели это так трудно?")

        time.sleep(1.5)

        self.magpie.send_message(self.chat.id,
                text="да")

        time.sleep(2)

        self.squirrel.send_message(self.chat.id,
                text="хватит!!")

        time.sleep(1)

        self.squirrel.send_message(self.chat.id,
                text="так, новенькие!")
                
        time.sleep(1)
        
        self.squirrel.send_message(self.chat.id,
                text="возьмите этот текст и уберите всё лишнее")

        time.sleep(2)

        self.squirrel.send_message(self.chat.id,
                text="важно! автор просит сохранить анонимность, будьте аккуратны"
        )

        time.sleep(3)

        self.squirrel.send_message(self.chat.id,
                text="УБЕРИТЕ ИЗ ТЕКСТА ВООБЩЕ ВСЮ ЛИЧНУЮ ИНФОРМАЦИЮ ИНАЧЕ НАМ НИКТО НЕ БУДЕТ ПИСАТЬ ПОНЯТНЕНЬКО")

        time.sleep(3)

        self.squirrel.send_message(self.chat.id,
                text="редактируйте текст в этом <a href='https://docs.google.com/document/d/15zQO1kA9yF_Vew1PUk6NXsEB0o0LSrXKOQtEyV1MGxU/edit?usp=sharing'>гугл доке</a>. у вас есть <b>3 минуты</b> на это задание",
                parse_mode=ParseMode.HTML)

        time.sleep(1)

        self.send_timer(3)

        self.squirrel.dp.add_handler(self.next_step(self.start5, MessageHandler, Game.ready_message))

        time.sleep(15)

        self.squirrel.send_message(self.chat.id,
                text=f"напишите мне *{Game.ready_message}*, если закончите раньше",
                parse_mode=ParseMode.MARKDOWN)
    

    def start5(self, update, context):
        self.squirrel.send_message(self.chat.id,
                text="класс, сейчас отсмотрю. а пока вы можете узнать больше про анонимность информатов")

        time.sleep(2)

        self.owl.send_message(self.chat.id,
                text="Статья 41 закона о СМИ запрещает редакции разглашать в распространяемых сообщениях и материалах сведения, предоставленные гражданином с условием сохранения их в тайне. Также редакция обязана сохранять в тайне источник информации и не вправе называть лицо, предоставившее сведения с условием неразглашения его имени, за исключением случая, когда соответствующее требование поступило от суда в связи с находящимся в его производстве делом.",
                reply_markup=Game.inline_button('ok'))

        self.owl.dp.add_handler(self.next_step(self.publication_ready, CallbackQueryHandler))


    def publication_ready(self, update, context):

        self.timer = False

        self.squirrel.send_message(self.chat.id,
                text="пост готов!")

        time.sleep(1.5)

        self.squirrel.send_message(self.chat.id,
                text="ну чтож может его прямо сейчас и опубликуем?",
                reply_markup=Game.inline_button("publish"))

        self.squirrel.dp.add_handler(self.next_step(self.publication, CallbackQueryHandler))


    def publication(self, update, context):
        time.sleep(0.5)

        self.update_scale(3)

        time.sleep(2)

        self.floppa.send_message(self.chat.id,
            text="Ого, ваша публикация привлекает внимание!")

        time.sleep(2)

        self.squirrel.send_message(self.chat.id,
            text="наш материал разлетелся и его активно обсуждают в Хвойном Лесу!") 
        
        return self.ending(update, context)


    def ending(self, update, context):
        time.sleep(2.5)

        self.floppa.send_message(self.chat.id,
            text="Мы заслужили перерыв на обед.")

        time.sleep(1)

        self.floppa.send_video(self.chat.id,
            "BAACAgQAAx0CWUm3XAACBHZgV1L3vB6OIUw70DnZvF4ffmH7lQACxgsAAk3XgVGJYpfMEBrLBB4E")


    def init_scale(self, update, context):
        self.squirrel.send_message(self.chat.id,
                    text="это шкала актуальности нашего журнала")
        time.sleep(0.5)
        self.scale_msg = self.squirrel.send_message(self.chat.id,
                    text=self.scale_ui(),
                    parse_mode=ParseMode.MARKDOWN)
        self.scale_msg.pin()
        time.sleep(1)
        self.squirrel.send_message(self.chat.id,
                    "постарайтесь довести ее до максимума!")

        

    def test(self, update, context):

        self.init_scale(update, context)

        # add +3 hype score
        def hype(update, context):
            self.update_scale(4)
            update.message.reply_text("Йоу")
            
        self.squirrel.dp.add_handler(CommandHandler("hype", hype))

        #  reply sticker file_id
        def reply_sticker(update, context):
            update.message.reply_text(f"`{update.message.sticker.file_id}`",
                                    parse_mode = ParseMode.MARKDOWN)

        self.squirrel.dp.add_handler(MessageHandler(Filters.sticker, reply_sticker))

        #  reply sticker file_id
        def reply_video(update, context):
            update.message.reply_text(f"`{update.message.video.file_id}`",
                                    parse_mode = ParseMode.MARKDOWN)

        self.squirrel.dp.add_handler(MessageHandler(Filters.video, reply_video))

    
    @classmethod
    def init(cls, stage=None):
        if not stage: stage = Game.start
        def cb(update, context):
            game = context.chat_data.get("game")
            # todo check if chat suitable for game
            if not game:
                game = cls(update.effective_chat, bots)
                context.chat_data["game"] = game
            return stage(game, update, context)
        return cb


## -- boot mechanysm -- ##

def initialize_bots():
    bots = dict()
    for name, token in config.data.tokens.items():
        bots[name] = Bot(token)
        bots[name].upd = Updater(bot=bots[name], use_context=True)
        bots[name].dp = bots[name].upd.dispatcher
    return bots

bots = initialize_bots()

def main():
    bots["squirrel"].dp.add_handler(CommandHandler("start", Game.init()))
    for bot in bots.values():
        bot.upd.start_polling()


if __name__ == '__main__':
    main()