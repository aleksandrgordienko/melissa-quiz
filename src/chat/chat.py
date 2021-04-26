# python-telegram-quiz
# @author: Aleksandr Gordienko
# @site: https://github.com/aleksandrgordienko/melissa-quiz

import time

from random import randint


class Chat:
    """Chat class"""

    def __init__(self, c_id, u_id, game, parameters, is_on, q_id=None):
        self.id = c_id
        self.game = game
        self.parameters = parameters
        self.q_id = q_id  # current game question
        self.is_on = is_on  # game is active
        self.u_id = u_id  # last user who's correctly answered
        self.answer_count = 0  # count of correct answers from last user who's correctly answered
        self.hint = [True]  # opened letters in answer
        self.last_hint = time.time()  # when hint was asked
        self.last_adv = time.time()  # when last broadcast message sent
        self.q_count = 0  # questions asked since last broadcast message sent
        self.last_q = time.time() - self.parameters['next_pause']  # when question was asked
        self.questions = 0  # questions asked since game start
        self.users = {}  # users who answered at least once

    def new_user(self, user):
        self.users[user.id] = user

    def next_question(self):
        """
            Checks if question could be skipped
        :return: bool
            True if question could be changed, False if not
        """

        time_since_ask = time.time() - self.last_q

        if time_since_ask >= self.parameters['next_pause'] and self.is_on:
            self.q_id, self.hint = self.game.nextq()
            self.questions += 1
            self.q_count += 1
            self.last_q = time.time()
            self.last_hint = time.time()
            return True
        else:
            return False

    def need_broadcast(self):
        """
            Checks if broadcast message should be sent
        :return: bool
            True if message should be sent
        """
        if (time.time() - self.last_adv > self.parameters['adv_minutes'] * 60)\
                and self.q_count >= self.parameters['adv_questions']:
            self.q_count = 0
            self.last_adv = time.time()
            return True
        else:
            self.q_count += 1
            return False

    def max_time_exceed(self):
        """
            Checks if max time for answer exceeded
        :return: bool
            True if time exceeded
        """
        cur_time = round(time.time() - self.last_q, 2)
        if cur_time > self.parameters['max_time']:
            return True
        else:
            return False

    def get_question(self):
        """
            Returns ID of active question in chat
        :return: int
            question ID
        """
        return self.game.get_question(self.q_id)

    def get_hint_text(self, hint_symbol, hint_separator):
        """
            Returns answer string with masked unopened letters
        :param hint_symbol: str
            symbol which would represent hidden letters in answer
        :param hint_separator: str
            placeholder for spaces between answer letters
        :return: str
            hint string with open
        """
        return self.game.get_hint_text(self.q_id, hint_symbol, hint_separator, self.hint)

    def count_correct_answer(self, user):
        """
            Counts correct answer
        :return: None
        """
        self.answer_count += 1
        user.count_correct_answer()
        if self.u_id != user.id:
            self.u_id = user.id
            self.answer_count = 1

    def check_speed(self):
        cur_time = round(time.time() - self.last_q, 2)
        is_cur_answer_fast = False  # TODO fix implementation
        return is_cur_answer_fast

    def do_hint(self):
        """
            Tries to open next letter in answer hint
        :return: str
            result state
        """
        if self.max_time_exceed() is False:
            cur_time = round(time.time() - self.last_hint)
            if cur_time > self.parameters['hint_pause']:
                self.last_hint = time.time()
                false_letters = sum(1 for position in self.hint if position is False)
                false_count = 0
                new_hint = randint(0, false_letters)
                for i, h in enumerate(self.hint):
                    if h is False:
                        false_count += 1
                    if false_count == new_hint:
                        self.hint[i] = True
                if all(self.hint):
                    return 'whole_word_open'
                else:
                    return 'hint_ok'
            else:
                return 'hint_pause_not_spent'
        else:
            return 'max_time_exceed'
