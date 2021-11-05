# coding=utf-8
from osha.oira import _
from osha.oira.client.model import Training
from datetime import datetime
from euphorie.client.browser.training import TrainingSlide
from euphorie.client.browser.training import TrainingView
from json import dumps
from json import loads
from logging import getLogger
from plone import api
from plone.memoize.view import memoize
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from random import shuffle
from sqlalchemy.orm.exc import NoResultFound
from z3c.saconfig import Session
from zExceptions import Unauthorized
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


logger = getLogger(__name__)


class OSHATrainingSlide(TrainingSlide):
    """Template / macro to hold the training slide markup"""

    @property
    def image(self):
        if self.is_custom:
            if not getattr(self.context, "image_data", None):
                return None
            _view = self.context.__of__(
                self.webhelpers.traversed_session.aq_parent["custom-risks"]
            ).restrictedTraverse("image-display")
            _view.fieldname = "training_export"
            return _view.get_or_create_image_scaled()
        image = self.zodb_elem.image and self.zodb_elem.image.data or None
        if image and self.for_download:
            try:
                scales = self.zodb_elem.restrictedTraverse("images", None)
                if scales:
                    if self.item_type == "module":
                        scale_name = "training_module_export"
                    else:
                        scale_name = "training_export"
                    scale = scales.scale(fieldname="image", scale=scale_name)
                    if scale and scale.data:
                        image = scale.data.data
            except Exception:
                image = None
                logger.warning(
                    "Image data could not be fetched on %s", self.context.absolute_url()
                )
        return image

    @property
    def department(self):
        return "XXX - deparment not defined"
        # return self.webhelpers.group_label_by_id(
        #     getattr(self.context.session, "group_id", "")
        # )


class TrainingBase(object):
    @property
    @memoize
    def webhelpers(self):
        return api.content.get_view("webhelpers", self.context, self.request)

    @property
    def survey_title(self):
        return self.webhelpers._survey.title

    @property
    @memoize
    def questions(self):
        survey = self.webhelpers._survey
        return survey.listFolderContents({"portal_type": "osha.training_question"})

    @memoize
    def get_or_create_training(self):
        """Return the training for this session"""
        account_id = self.webhelpers.get_current_account().id
        session_id = self.webhelpers.session_id
        try:
            return (
                Session.query(Training)
                .filter(
                    Training.session_id == session_id, Training.account_id == account_id
                )
                .one()
            )
        except NoResultFound:
            pass
        status = "in_progress" if self.questions else "correct"
        training = Training(
            account_id=account_id,
            session_id=session_id,
            status=status,
            time=datetime.now(),
            answers=u"{}",
        )
        Session.add(training)
        return training

    @property
    @memoize
    def training_status(self):
        return self.get_or_create_training().status


class OSHATrainingView(TrainingView, TrainingBase):
    """The view that shows the main-menu Training module
    Currently not active in default Euphorie
    """

    @property
    def skip_unanswered(self):
        # return not isinstance(self.session, ExternalSurveySession)
        return True

    @property
    def question_intro_url(self):
        survey = self.webhelpers._survey
        if not getattr(survey, "enable_web_training", False):
            return ""
        view_name = "slide_question_success"
        if (
            survey.listFolderContents({"portal_type": "osha.training_question"})
            and self.training_status != "success"
        ):
            view_name = "slide_question_intro"
        return "{}/@@{}".format(self.context.absolute_url(), view_name)

    @property
    def training_email_subject(self):
        subject = _(
            "training_email_subject",
            default=u"Training request for assessment “${title}”",
            mapping={"title": self.session.title},
        )
        return api.portal.translate(subject)

    @property
    def training_email_body(self):
        body = _(
            "training_email_body",
            default=u"""I would like to share a training with you.
You can follow this training online via the following link:

${url}

Kind regards,
${name}""",
            mapping={
                "url": u"{0}/@@training".format(self.context.absolute_url()),
                "name": self.webhelpers.get_user_fullname(),
            },
        )
        return api.portal.translate(body)


class SlideQuestionIntro(BrowserView, TrainingBase):
    """The slide that introduces the questions"""

    def first_question_url(self):
        """Check the questions in the survey and take the first one"""
        if not self.questions:
            return ""
        return "{base_url}/@@slide_question/{slide_id}".format(
            base_url=self.context.absolute_url(), slide_id=self.questions[0].getId()
        )


@implementer(IPublishTraverse)
class SlideQuestion(SlideQuestionIntro):
    """The view for a question slide, the question id has to be passed
    as a traversal parameter
    """

    def publishTraverse(self, request, name):
        self.question_id = name
        return self

    @property
    @memoize
    def question(self):
        """The question we want to display"""
        return self.webhelpers._survey[self.question_id]

    @property
    @memoize
    def answers(self):
        """Return the randomized answers for this question"""
        question = self.question
        answers = [
            question.right_answer,
            question.wrong_answer_1,
            question.wrong_answer_2,
        ]
        shuffle(answers)
        return answers

    @property
    def progress(self):
        """Return a progress indicator, something like 2/3"""
        idx = self.questions.index(self.question)
        return "{}/{}".format(idx + 1, len(self.questions))

    @property
    @memoize
    def previous_question(self):
        idx = self.questions.index(self.question)
        if idx == 0:
            return
        try:
            return self.questions[idx - 1]
        except IndexError:
            pass

    @property
    @memoize
    def next_question(self):
        idx = self.questions.index(self.question)
        try:
            return self.questions[idx + 1]
        except IndexError:
            pass

    @property
    def next_url(self):
        """Go to next question (if we have one) or to the success or try again slides"""
        next_question = self.next_question
        if next_question:
            next_slide = "slide_question/{}".format(next_question.getId())
        elif self.get_or_create_training().status == "correct":
            next_slide = "slide_question_success"
        else:
            next_slide = "slide_question_try_again"
        return "{}/@@{}".format(self.context.absolute_url(), next_slide)

    def initialize_training(self):
        """Initialize the training.

        This is particularly important if the user starts again the training
        after a first attempt
        """
        training = self.get_or_create_training()
        training.answers = u"{}"
        training.status = u"in_progress"
        training.time = datetime.now()

    def post(self):
        if not self.previous_question:
            self.initialize_training()
        training = self.get_or_create_training()
        answer = safe_unicode(self.request.form["answer"])
        answer_history = loads(training.answers)
        answer_history[self.question_id] = answer == self.question.right_answer
        training.answers = dumps(answer_history)
        training.time = datetime.now()
        if not self.next_question:
            training.status = u"correct" if all(answer_history.values()) else "failed"

    def posted(self):
        if self.request.method != "POST":
            return False
        self.post()
        return True

    def validate(self):
        previous_question = self.previous_question
        if not previous_question:
            return
        training = self.get_or_create_training()
        try:
            answers = loads(training.answers)
        except ValueError:
            answers = {}
        if not answers:
            raise Unauthorized(_("You should start the training from the beginning"))
        if previous_question.getId() not in answers:
            raise Unauthorized(_("It seems you missed a slide"))

    def __call__(self):
        self.validate()
        if self.posted():
            return self.request.response.redirect(self.next_url)
        return super(SlideQuestion, self).__call__(self)


class SlideQuestionSuccess(SlideQuestionIntro):
    def post(self):
        training = self.get_or_create_training()
        if bool(self.request.form.get("legal_crap")):
            training.status = "success"
        else:
            training.status = "correct"

    def __call__(self):
        training = self.get_or_create_training()
        if training.status not in ("correct", "success"):
            raise Unauthorized("You do not own the certificate")
        if self.request.method == "POST":
            return self.post()
        return super(SlideQuestionSuccess, self).__call__()


class SlideQuestionTryAgain(SlideQuestionIntro):
    @property
    def failed_questions(self):
        training = self.get_or_create_training()
        try:
            answers = loads(training.answers)
        except ValueError:
            answers = {}
        return [
            question.title
            for question in self.questions
            if not answers.get(question.getId())
        ]


class MyTrainingsPortlet(BrowserView):
    columns = "1"

    @property
    @memoize
    def webhelpers(self):
        return api.content.get_view("webhelpers", self.context, self.request)

    @property
    @memoize
    def my_unfinished_trainings(self):
        account_id = self.webhelpers.get_current_account().id
        return [
            session
            for session in (
                Session.query(Training)
                .filter(Training.account_id == account_id, Training.status != "success")
                .order_by(Training.time.desc())
                .all()
            )
            if session.session.tool
        ]

    @property
    @memoize
    def my_certificates(self):
        account_id = self.webhelpers.get_current_account().id
        return [
            session
            for session in (
                Session.query(Training)
                .filter(Training.account_id == account_id, Training.status == "success")
                .order_by(Training.time.desc())
                .all()
            )
            if session.session.tool
        ]
