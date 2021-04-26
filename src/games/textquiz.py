# python-telegram-quiz
# @author: Aleksandr Gordienko
# @site: https://github.com/aleksandrgordienko/melissa-quiz

from random import randint
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    question = Column(String(1000))
    answer = Column(String(100))
    ask_count = Column(Integer)


class TextQuiz:
    """TextQuiz class"""

    def __init__(self, session):
        self.questions = {}
        self.name = 'textquiz'
        self.session = session
        for question in self.session.query(Question).all():
            self.questions[question.id] = {'question': question.question,
                                           'answer': question.answer,
                                           'ask_count': question.ask_count}

    def nextq(self):
        """Generates next question_id, question_type and initial_hint"""
        question_id = randint(0, len(self.questions))
        question = self.questions[question_id]
        question['ask_count'] += 1
        self.session.merge(Question(id=question_id,
                                    ask_count=question['ask_count']))
        self.session.commit()
        return question_id, self.get_initial_hint_mask(question_id)

    def get_question(self, question_id):
        return self.questions[question_id]['question']

    def get_answer(self, question_id):
        return self.questions[question_id]['answer']

    def answer_is_correct(self, question_id, answer):
        return answer.lower() in self.get_answer(question_id).lower()

    def get_hint_text(self, question_id, hint_symbol, hint_separator, hint_mask):
        out_text = ''
        answer = self.get_answer(question_id)
        if hint_mask:
            for i, c in enumerate(answer):
                if hint_mask[i]:
                    out_text += c
                else:
                    out_text += hint_symbol
                out_text += hint_separator
        else:
            out_text = (hint_symbol + hint_separator) * len(answer)
        return out_text

    def get_initial_hint_mask(self, question_id):
        """Returns initial hint mask"""
        return [False] * len(self.get_answer(question_id))
