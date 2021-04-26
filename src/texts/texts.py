# python-telegram-quiz
# @author: Aleksandr Gordienko
# @site: https://github.com/aleksandrgordienko/melissa-quiz

import json

from random import choice


class Texts:
    """Text translations class"""

    texts = dict()
    jokes = dict()
    bad_words = dict()

    def __init__(self):
        language_files = {'en': './language/english.json', 'ru': './language/russian.json'}
        for lang in language_files.keys():
            self.texts[lang] = json.load(open(language_files[lang], 'r', encoding='utf8'))
            self.jokes[lang] = self.get_text('jokes').split("\n")
            self.bad_words[lang] = self.get_text('bad_words').split("\n")

    def get_text(self, text_id, lang='en'):
        """
            Returns text in specified language
        :param text_id: int
            ID of text string form language file
        :param lang: str
            language code
        :return: str
            string for requested text ID
        """
        return self.texts[lang][text_id]

    def check_bad(self, message, lang='en'):
        """
            Checks if user has sent a bad word in message
        :param message: str
            user message
        :param lang: str
            language code
        :return: bool
            True if message contains bad word
        """
        if any([True if x in self.bad_words[lang] else False for x in message.lower().split(" ")]):
            return True
        else:
            return False

    def get_joke(self, lang='en'):
        """
            Returns joke
        :param lang: str
            language code
        :return: str
            joke to send
        """
        return choice(self.jokes[lang])
