from Acquisition import aq_parent
from euphorie.content import MessageFactory as _
from plone import api
from plone.base.utils import base_hasattr
from plonetheme.nuplone.skin import actions
from Products.Five import BrowserView


class Delete(actions.Delete):
    """Only delete the surveygroup if it doesn't have a published version."""

    def verify(self, container, context):
        surveygroup = context
        sector = container
        country = aq_parent(sector)
        client = api.portal.get().client

        if country.id not in client:
            return True

        cl_country = client[country.id]
        if sector.id not in cl_country:
            return True

        cl_sector = cl_country[sector.id]
        if surveygroup.id not in cl_sector:
            return True

        surveys = [s for s in cl_sector[surveygroup.id].values() if s.id != "preview"]
        if surveys:
            api.portal.show_message(
                _(
                    "message_not_delete_published_surveygroup",
                    default="You can not delete an OiRA tool that has been published.",
                ),
                self.request,
                "error",
            )
            self.request.response.redirect(context.absolute_url())
            return False
        return True


class SurveyGroupAttribute(BrowserView):
    """Base view to return an attribute of a surveygroup from its surveys.

    We want to show both an 'image' and 'introduction' for a survey group,
    and we can get them from one of its surveys.
    """

    attribute_name = ""

    @property
    def surveys(self):
        """Iterator over the surveys contained in the surveygroup.

        The published survey (if it exists) comes first.
        """
        published = self.context.published
        if published:
            published_obj = self.context.get(published)
            if published_obj:
                yield published_obj

        for obj in self.context.listFolderContents({"portal_type": "Survey"}):
            if obj.getId() != published:
                yield obj

    def get_obj_attribute(self, obj):
        """Return the attribute of the given object."""
        if not obj:
            return
        if not base_hasattr(obj, self.attribute_name):
            return
        return getattr(obj, self.attribute_name)


class SurveyGroupImage(SurveyGroupAttribute):
    """Return the image of the surveygroup."""

    attribute_name = "image"

    @property
    def image_url(self) -> str:
        """Return the image URL of the survey group."""
        for survey in self.surveys:
            if self.get_obj_attribute(survey):
                return f"{survey.absolute_url()}/@@images/image"
        return ""

    def __call__(self):
        """Check all the surveys, if they have an image, redirect to that image.

        The image is set by a cron script,
        see e.g. https://github.com/syslabcom/scrum/issues/2552.

        This might change in the future.

        Return a fallback if it does not exist.
        """
        image_url = self.image_url
        if image_url:
            return self.request.response.redirect(image_url)

        self.request.response.redirect(
            f"{api.portal.get().absolute_url()}"
            f"/++resource++osha.oira.content/clipboard.svg"
        )


class SurveyGroupIntroduction(SurveyGroupAttribute):
    """Return the introduction of the surveygroup."""

    attribute_name = "introduction"

    def __call__(self):
        """Check all the surveys, if they have an introduction, show it.

        We only need to return the contents of the field, which is expected
        to be html.
        """
        for survey in self.surveys:
            value = self.get_obj_attribute(survey)
            if value:
                return value
        return ""
