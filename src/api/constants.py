""" constants use in the api"""

from enum import Enum


class Question(Enum):
    """
    An enumeration representing a question with possible answers.

    Attributes:
        no (str): The answer "No".
        yes (str): The answer "Yes".
    """

    NO = "No"
    YES = "Yes"
