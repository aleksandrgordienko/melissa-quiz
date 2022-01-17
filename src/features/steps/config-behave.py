from behave import given, when, then
import os
import sys
sys.path.append('..')
from src.config import Config


@given('a Config instance')
def step_impl(context):
    context.config_obj = Config()


@when('checking the properties')
def step_impl(context):
    context.config_check = {
        'TEST_MODE': bool,
        'TELEGRAM_TOKEN': str,
        'TELEGRAM_CHANNEL': str,
        'TELEGRAM_ADMINS': str,
        'SQLALCHEMY_DB_CONN': str,
        'LOG_LEVEL': int,
        'LOG_FILE_NAME': str,
        'DEFAULT_PARAMETERS': dict
    }


@then('all mandatory properties are defined')
def step_impl(context):
    for key, value in context.config_check.items():
        assert key in dir(context.config_obj)
        type_ = type(getattr(context.config_obj, key))
        print(f'The config parameter {key} is of type {type_}. {value} was expected')
        assert type_ is value
