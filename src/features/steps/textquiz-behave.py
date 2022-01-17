from behave import given, when, then
import os
import sys
import json
sys.path.append('..')
from src.config import Config
from src.games import TextQuiz
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@given('a TextQuiz instance')
def step_impl(context):
    db_engine = create_engine(Config.SQLALCHEMY_DB_CONN)
    # self.connection = self.db_engine.connect()
    # self.metadata = sqlalchemy.MetaData()
    Session = sessionmaker(db_engine)
    context.quiz_obj = TextQuiz(Session())


@when('checking "{attr}" attribute')
def step_impl(context, attr):
    context.attr = getattr(context.quiz_obj, attr)


@then('then value is "{value}"')
def step_impl(context, value):
    assert context.attr == value
