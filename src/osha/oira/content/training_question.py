# coding=utf-8
from osha.oira import _
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.interface import implementer


class ITrainingQuestion(model.Schema):
    """A simple schema that adds three answer fields to the content type"""

    title = schema.Text(title=_("Question"))
    right_answer = schema.Text(title=_("Right answer"))
    wrong_answer_1 = schema.Text(title=_("First wrong answer"))
    wrong_answer_2 = schema.Text(title=_("Second wrong answer"))


@implementer(ITrainingQuestion)
class TrainingQuestion(Container):
    """A Question for the training"""
