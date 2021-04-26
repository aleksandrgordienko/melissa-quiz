# python-telegram-quiz
# @author: Aleksandr Gordienko
# @site: https://github.com/aleksandrgordienko/melissa-quiz

class User:
    """User class"""

    def __init__(self, u_id, name, correct_answers=0, points=0):
        self.id = u_id
        self.correct_answers = correct_answers
        self.points = points
        self.name = name

    def count_correct_answer(self):
        """
            Increments user messages count
        :return: None
        """
        self.correct_answers += 1

    def add_points(self, points):
        """
            Change user points
        :return: None
        """
        self.points += points

    def get_points(self):
        return self.points

    def get_name(self):
        """
            Returns username
        :return: str
            Username
        """
        return self.name
