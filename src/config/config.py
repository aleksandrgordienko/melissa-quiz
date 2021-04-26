# python-telegram-quiz
# @author: Aleksandr Gordienko
# @site: https://github.com/aleksandrgordienko/melissa-quiz

import os


class Config:
    """Configuration class"""

    TEST_MODE = False

    TELEGRAM_TOKEN = os.environ.get('MELISSA_QUIZ_BOT_KEY')
    TELEGRAM_CHANNEL = os.environ.get('MELISSA_QUIZ_TG_CHANNEL')
    TELEGRAM_ADMINS = os.environ.get('MELISSA_QUIZ_TG_ADMINS')

    SQLALCHEMY_DB_CONN = os.environ.get('MELISSA_QUIZ_SQLALCHEMY_DB_CONN')

    LOG_LEVEL = 30  # 10-DEBUG, 20-INFO, 30-WARNING, 40-ERROR, 50-CRITICAL
    LOG_FILE_NAME = 'log.txt'

    DEFAULT_PARAMETERS = {'adv_minutes': 10,
                          'adv_questions': 20,
                          'base_points': 5,
                          'current_broadcast': 0,
                          'google_points': -50,
                          'hint_pause': 5,
                          'max_time': 180,
                          'min_members': 4,
                          'next_pause': 30,
                          'series_max': 20,
                          'top_limit': 25, }
