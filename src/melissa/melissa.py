# python-telegram-quiz
# @author: Aleksandr Gordienko
# @site: https://github.com/aleksandrgordienko/melissa-quiz

import logging
import errno
import sqlalchemy
import models

from config import Config
from texts import Texts
from chat import Chat
from user import User
from sqlalchemy.orm import sessionmaker
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


class Melissa:
    """Main class"""

    logger = logging.getLogger(__name__)
    chats = dict()
    parameters = dict()
    channel = int(Config.TELEGRAM_CHANNEL)
    admins = [int(user) for user in Config.TELEGRAM_ADMINS.split(',')]
    games = {}
    try:
        texter = Texts()
    except FileNotFoundError as e:
        logger.critical('Cannot find language files')
        exit(errno.ENOENT)
    else:
        logger.info('Language files loaded')

    def __init__(self):

        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename=Config.LOG_FILE_NAME,
            level=Config.LOG_LEVEL
        )
        consoleHandler = logging.StreamHandler()
        self.logger.addHandler(consoleHandler)

        try:
            self.db_engine = sqlalchemy.create_engine(Config.SQLALCHEMY_DB_CONN)
            self.connection = self.db_engine.connect()
            self.metadata = sqlalchemy.MetaData()
            Session = sessionmaker(self.db_engine)
            self.session = Session()
        except Exception as e:  # TODO specify exceptions
            self.logger.critical(e)
            exit(errno.ECONNREFUSED)
        else:
            self.logger.warning('Connection to database established')

        try:
            self.parameters['adv_minutes'] = self.session.query(models.Parameter).get('adv_minutes').value
            self.parameters['adv_questions'] = self.session.query(models.Parameter).get('adv_questions').value
            self.parameters['base_points'] = self.session.query(models.Parameter).get('base_points').value
            self.parameters['current_broadcast'] = self.session.query(models.Parameter).get('current_broadcast').value
            self.parameters['google_points'] = self.session.query(models.Parameter).get('google_points').value
            self.parameters['hint_pause'] = self.session.query(models.Parameter).get('hint_pause').value
            self.parameters['max_time'] = self.session.query(models.Parameter).get('max_time').value
            self.parameters['min_members'] = self.session.query(models.Parameter).get('min_members').value
            self.parameters['next_pause'] = self.session.query(models.Parameter).get('next_pause').value
            self.parameters['series_max'] = self.session.query(models.Parameter).get('series_max').value
            self.parameters['top_limit'] = self.session.query(models.Parameter).get('top_limit').value
        except Exception as e:  # TODO specify exceptions
            self.logger.error(e)
            self.parameters = Config.DEFAULT_PARAMETERS
            self.logger.warning('Cannot load parameters. Defaults used.')

        # TODO improvement: add different game types later
        from games import TextQuiz
        game = TextQuiz(self.session)
        self.games[game.name] = game

        for chat in self.session.query(models.Chat).all():
            self.chats[chat.id] = Chat(c_id=chat.id,
                                       u_id=chat.u_id,
                                       q_id=chat.q_id,
                                       is_on=chat.is_on,
                                       lang=chat.lang,
                                       game=self.games[chat.game],
                                       parameters=self.parameters)
        for user in self.session.query(models.User).all():
            self.chats[user.chat_id].users[user.id] = User(u_id=user.id,
                                                           name=user.user_name,
                                                           correct_answers=user.correct_answers,
                                                           points=user.points)

        try:
            updater = Updater(Config.TELEGRAM_TOKEN, use_context=True)
        except Exception as e:
            self.logger.critical(e)
            exit(errno.ECONNREFUSED)
        else:
            self.logger.warning('Connection to Telegram established')

            dp = updater.dispatcher

            dp.add_handler(CommandHandler('start', self.cmd_start))
            dp.add_handler(CommandHandler('play', self.cmd_play))
            dp.add_handler(CommandHandler('stop', self.cmd_stop))
            dp.add_handler(CommandHandler('hint', self.cmd_hint))
            dp.add_handler(CommandHandler('score', self.cmd_score))
            dp.add_handler(CommandHandler('ask', self.cmd_ask))
            dp.add_handler(CommandHandler('lang', self.cmd_lang))
            dp.add_handler(CommandHandler('next', self.cmd_next))
            dp.add_handler(CommandHandler('setparameter', self.cmd_setparameter))
            # dp.add_handler(CommandHandler('stop_bot', self.cmd_stop_bot))
            #
            dp.add_handler(MessageHandler(Filters.regex('^(/top[\d]+)$'), self.cmd_top))
            dp.add_handler(MessageHandler(Filters.text, self.message))

            dp.add_error_handler(self.errors)

            self.logger.warning('Melissa Quiz started... ')

            updater.start_polling()

            # Run the bot until you press Ctrl-C or the process receives SIGINT,
            # SIGTERM or SIGABRT. This should be used most of the time, since
            # start_polling() is non-blocking and will stop the bot gracefully.
            updater.idle()

    def cmd_start(self, update, context):
        """/start command"""

        if update.effective_user.is_bot is True:
            return

        self.logger.info(update.message.text + ' from user ' + str(update.effective_user.id))

        greetings = self.texter.get_text(text_id='greetings', lang=Config.DEFAULT_LANGUAGE)

        greetings = greetings.format(
            min_members=self.parameters['min_members'],
            max_time=self.parameters['max_time'],
            hint_pause=self.parameters['hint_pause'])
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=greetings,
            parse_mode="HTML",
            disable_web_page_preview=True)

    def cmd_setparameter(self, update, context):
        """/setparameter command"""

        if update.effective_user.is_bot is True:
            return

        if update.effective_user.id not in self.admins:
            return

        if update.effective_chat.id not in self.chats:
            return

        try:
            parameter, value = update.message.text.split(' ', 3)[1:3]
            self.parameters[parameter] = value
        except Exception as e:  # TODO specify exceptions
            update.message.reply_text(self.texter.get_text('set_parameter_format', lang=Config.DEFAULT_LANGUAGE))
        out_text = self.texter.get_text('set_parameter_head')
        for p in self.parameters:
            out_text += self.texter.get_text('set_parameter_text', Config.DEFAULT_LANGUAGE) \
                .format(parameter=p,
                        value=self.parameters[p])
        update.message.reply_text(out_text)

    def cmd_score(self, update, context):
        """/score command"""

        if update.effective_user.is_bot is True:
            return

        self.logger.info(update.message.text + ' from user ' + str(update.effective_user.id))

        if update.effective_chat.id in self.chats \
                and update.effective_user.id in self.chats[update.effective_chat.id].users:
            chat = self.chats[update.effective_chat.id]
            out_text = self.texter.get_text('score_head',
                                            lang=chat.lang) \
                .format(user_name=update.effective_user.name)
            out_text += self.texter.get_text('score_text', lang=chat.lang).format(
                points=self.chats[update.effective_chat.id].users[update.effective_user.id].get_points())
            # TODO implement: return rating place as well
        else:
            out_text = self.texter.get_text('score_notagamer', lang=Config.DEFAULT_LANGUAGE)
        update.message.reply_text(out_text)

    def cmd_top(self, update, context):
        """/top command"""

        if update.effective_user.is_bot is True:
            return

        self.logger.info(update.message.text + ' from user ' + str(update.effective_user.id))

        try:
            top_qty = int(update.message.text[4:])
        except Exception as e:  # TODO specify exceptions
            top_qty = 10
            self.logger.info('Cannot recognize TOP N from ' + update.message.text + str(e))

        if top_qty > self.parameters['top_limit']:
            top_qty = self.parameters['top_limit']

        if update.effective_chat.id not in self.chats:
            return

        chat = self.chats[update.effective_chat.id]
        out_text = self.texter.get_text('top_head', lang=chat.lang) \
            .format(top_qty=top_qty)

        players = self.session.query(models.User).order_by(models.User.points.desc()).limit(top_qty)

        # TODO fix: problem with stored emoji (utf8mb4)
        for player in players:
            out_text += self.texter.get_text('top_line', lang=chat.lang) \
                .format(bullet='•',
                        user=player.user_name,
                        points=player.points)

        context.bot.send_message(chat_id=update.effective_chat.id, text=out_text)

    def cmd_play(self, update, context):
        """/play command"""
        if update.effective_user.is_bot is True:
            return

        self.logger.info(update.message.text + ' from user ' + str(update.effective_user.id))

        if update.effective_chat.get_member_count() < self.parameters['min_members']:
            out_text = self.texter.get_text('min_members_group_play', lang=Config.DEFAULT_LANGUAGE)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=out_text.format(min_members=self.parameters['min_members']),
                parse_mode='HTML')
            return
        if update.effective_chat.id not in self.chats:
            # TODO improvement: add different game types later
            game = self.games['textquiz']
            chat = Chat(c_id=update.effective_chat.id,
                        u_id=update.effective_user.id,
                        game=game,
                        parameters=self.parameters,
                        is_on=True,
                        lang=Config.DEFAULT_LANGUAGE)
            chat.next_question()
            self.chats[update.effective_chat.id] = chat
        else:
            chat = self.chats[update.effective_chat.id]
            chat.is_on = True
        self.session.merge(models.Chat(id=chat.id,
                                       u_id=chat.u_id,
                                       q_id=chat.q_id,
                                       is_on=chat.is_on,
                                       lang=chat.lang,
                                       game=chat.game.name))
        self.session.commit()
        if update.effective_user.id not in chat.users:
            self.new_player(update)
        self.cmd_ask(update, context)

    def cmd_stop(self, update, context):
        """/stop command"""
        if update.effective_user.is_bot is True:
            return

        self.logger.info(update.message.text + ' from user ' + str(update.effective_user.id))

        if update.effective_chat.id not in self.chats \
           or self.chats[update.effective_chat.id].is_on is False:
            return

        chat = self.chats[update.effective_chat.id]
        chat.is_on = False
        self.session.merge(models.Chat(id=chat.id,
                                       u_id=chat.u_id,
                                       q_id=chat.q_id,
                                       is_on=chat.is_on,
                                       lang=Config.DEFAULT_LANGUAGE,
                                       game=chat.game.name))
        self.session.commit()

        stop_message = self.texter.get_text(text_id='game_stopped', lang=chat.lang)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=stop_message,
            parse_mode="HTML",
            disable_web_page_preview=True)

    def cmd_lang(self, update, context):
        """/lang command"""
        if update.effective_user.is_bot is True:
            return

        self.logger.info(update.message.text + ' from user ' + str(update.effective_user.id))

        if update.effective_chat.id not in self.chats \
           or self.chats[update.effective_chat.id].is_on is False:
            return

        chat = self.chats[update.effective_chat.id]
        if chat.lang == 'en':
            chat.lang = 'ru'
        else:
            chat.lang = 'en'
        self.session.merge(models.Chat(id=chat.id,
                                       u_id=chat.u_id,
                                       q_id=chat.q_id,
                                       is_on=chat.is_on,
                                       lang=chat.lang,
                                       game=chat.game.name))
        self.session.commit()

        lang_message = self.texter.get_text(text_id='lang_set', lang=chat.lang).format(lang=chat.lang)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=lang_message,
            parse_mode="HTML",
            disable_web_page_preview=True)

    def cmd_hint(self, update, context):
        """/hint command"""

        if update.effective_user.is_bot is True:
            return

        if update.effective_chat.id not in self.chats:
            return

        self.logger.info(update.message.text + ' from user ' + str(update.effective_user.id))

        chat = self.chats[update.effective_chat.id]
        if chat.is_on is False:
            return

        hint_result = chat.do_hint()

        if hint_result == 'hint_ok':
            sym = self.texter.get_text('hint_symbol', lang=chat.lang)
            sep = self.texter.get_text('hint_separator', lang=chat.lang)
            out_text = self.texter.get_text('hint_text', lang=chat.lang) \
                .format(hint_text=chat.get_hint_text(sym, sep))
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=out_text,
                                     parse_mode='HTML')
        elif hint_result in ['whole_word_open', 'max_time_exceed']:
            chat.next_question()
            self.session.merge(models.Chat(id=chat.id,
                                           u_id=chat.u_id,
                                           q_id=chat.q_id,
                                           is_on=chat.is_on,
                                           lang=chat.lang,
                                           game=chat.game.name))  # TODO improvement: add different game types later
            self.session.commit()
            out_text = self.texter.get_text('nobody_could', lang=chat.lang)
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=out_text,
                                     parse_mode='HTML')
            out_text = self.texter.get_text('ask_question', lang=chat.lang) \
                .format(question=chat.get_question())
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=out_text,
                                     parse_mode='HTML')
        elif hint_result == 'hint_pause_not_spent':
            pass
        else:
            self.logger.error('Hint error: ' + hint_result)

    def cmd_next(self, update, context):
        """/next command"""

        if update.effective_user.is_bot is True:
            return

        if update.effective_chat.id not in self.chats:
            return

        self.logger.info(update.message.text + ' from user ' + str(update.effective_user.id))

        chat = self.chats[update.effective_chat.id]
        if chat.is_on is False:
            return

        if chat.next_question():
            self.session.merge(models.Chat(id=chat.id,
                                           u_id=chat.u_id,
                                           q_id=chat.q_id,
                                           is_on=chat.is_on,
                                           lang=chat.lang,
                                           game=chat.game.name))
            self.session.commit()
            self.cmd_ask(update, context)
        else:
            out_text = self.texter.get_text('lets_think_more', lang=chat.lang) \
                .format(question=chat.get_question())
            context.bot.send_message(
                chat_id=chat.id,
                text=out_text,
                parse_mode='HTML')

    def cmd_ask(self, update, context):
        """/ask command"""

        if update.effective_user.is_bot is True:
            return

        if update.effective_chat.id not in self.chats:
            return

        self.logger.info(update.message.text + ' from user ' + str(update.effective_user.id))

        chat = self.chats[update.effective_chat.id]
        if chat.is_on is False:
            return

        if self.parameters['current_broadcast'] and chat.need_broadcast():
            context.bot.forward_message(chat.id,
                                        self.channel,
                                        self.parameters['current_broadcast'])
        out_text = self.texter.get_text('ask_question', lang=chat.lang) \
            .format(question=chat.get_question())
        context.bot.send_message(
            chat_id=chat.id,
            text=out_text,
            parse_mode='HTML')

    def message(self, update, context):
        """message in chat"""

        # new message in bot channel
        if update.effective_chat.id == self.channel and update.channel_post.message_id:
            self.logger.info(update.channel_post.text + ' from channel ' + str(update.effective_chat.id))
            for user in self.admins:
                context.bot.forward_message(user, self.channel, update.channel_post.message_id)
                out_text = self.texter.get_text('broadcast_newpost', lang=Config.DEFAULT_LANGUAGE) \
                    .format(message_id=str(update.channel_post.message_id))
                context.bot.send_message(chat_id=user,
                                         text=out_text,
                                         parse_mode='HTML')
            return

        # message in game chat
        if update.effective_user.is_bot is True:
            return

        if update.effective_chat.id not in self.chats:
            return

        chat = self.chats[update.effective_chat.id]
        if chat.is_on is False:
            return

        if update.effective_user.id not in chat.users:
            self.new_player(update)
        user = chat.users[update.effective_user.id]

        if chat.max_time_exceed():
            context.bot.send_message(chat_id=chat.id,
                                     text=self.texter.get_text('nobody_could', lang=chat.lang),
                                     parse_mode='HTML')
            chat.next_question()
            self.session.merge(models.Chat(id=chat.id,
                                           u_id=chat.u_id,
                                           q_id=chat.q_id,
                                           is_on=chat.is_on,
                                           lang=chat.lang,
                                           game=chat.game.name))  # TODO improvement: add different game types later
            self.session.commit()
            out_text = self.texter.get_text('ask_question', lang=chat.lang) \
                .format(question=chat.get_question())
            context.bot.send_message(
                chat_id=chat.id,
                text=out_text,
                parse_mode='HTML')
            return

        if chat.game.answer_is_correct(chat.q_id, update.message.text) \
           and chat.is_on and chat.got_correct_answer is False:
            # turn off game, we don't want to get more than one winner
            chat.got_correct_answer = True

            # calculate points for correction answer
            points = chat.parameters['base_points'] \
                - chat.hint.count(True) / len(chat.hint) \
                * chat.parameters['base_points']
            multiplied_points = points = int(round(points, 0))
            if points < 1:
                points = 1
            combo_str_list = []

            # double points if it was quick answer
            if chat.check_speed():
                multiplier = 2
                points = points * multiplier
                combo_str_list.append(
                    self.texter.get_text('quick_answer', lang=chat.lang) \
                        .format(multiplier=multiplier))

            # count correct answer in chat and user
            chat.count_correct_answer(user)

            # if user exceeded limit count of answers in series
            if chat.answer_count > chat.parameters['series_max']:
                points = chat.parameters['google_points']
                combo_str_list.append(self.texter.get_text('was_googled', lang=chat.lang))
            else:
                # series is going, multiply points
                multiplier = chat.answer_count
                multiplied_points = points * multiplier
                combo_str_list.append(
                    self.texter.get_text('series_answer', lang=chat.lang) \
                        .format(multiplier=multiplier))

            user.add_points(multiplied_points)
            self.session.merge(models.User(chat_id=chat.id,
                                           id=user.id,
                                           points=user.points,
                                           user_name=user.name))
            self.session.commit()
            out_text = self.texter.get_text('get_points', lang=chat.lang) \
                .format(username=user.get_name(),
                        points=str(points))
            out_text += '\n' + '\n'.join(combo_str_list)
            out_text += '\n' + self.texter.get_text('result_points', lang=chat.lang) \
                .format(points=str(multiplied_points))

            # congratulate user
            context.bot.send_message(chat_id=chat.id, text=out_text,
                                     parse_mode='HTML')

            # go to the next question
            chat.next_question()
            self.session.merge(models.Chat(id=chat.id,
                                           u_id=chat.u_id,
                                           q_id=chat.q_id,
                                           is_on=chat.is_on,
                                           lang=chat.lang))
            self.session.commit()

            out_text = self.texter.get_text('ask_question', lang=chat.lang) \
                .format(question=chat.get_question())
            context.bot.send_message(
                chat_id=chat.id,
                text=out_text,
                parse_mode='HTML')

        # wrong answer and bad words in it
        elif self.texter.check_bad(update.message.text):
            update.message.reply_text(self.texter.get_joke())

    def new_player(self, update):
        chat = self.chats[update.effective_chat.id]
        try:
            # getting user from database
            result = self.session.query(models.User).\
                filter(models.User.id == update.effective_user.id and models.User.chat_id == chat.id)
            user = User(u_id=result[0].id,
                        name=result[0].user_name,
                        correct_answers=result[0].correct_answers,
                        points=result[0].points)
        except Exception as e:
            # new user
            self.logger.debug(str(e))
            user = User(u_id=update.effective_user.id,
                        name=update.effective_user.username)
            self.session.merge(models.User(chat_id=chat.id,
                                           id=user.id,
                                           points=user.points,
                                           user_name=user.name,
                                           correct_answers=user.correct_answers))
            self.session.commit()
        chat.new_user(user)

    def errors(self, update, context):
        """Error handler"""
        self.logger.warning('Update "%s" caused error "%s"' % (update, context.error))
