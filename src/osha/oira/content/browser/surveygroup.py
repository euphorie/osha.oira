from Acquisition import aq_base
from Acquisition import aq_parent
from euphorie.content import MessageFactory as _
from plone import api
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


class SurveyGroupImage(BrowserView):
    """Return the image of the surveygroup."""

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

    def get_obj_image_url(self, obj):
        """Return the URL of the image of the given object.

        The image is set by a cron script,
        see e.g. https://github.com/syslabcom/scrum/issues/2552.

        This might change in the future.
        """
        if obj and aq_base(obj.image):
            return f"{obj.absolute_url()}/@@images/image"

    def __call__(self):
        """Check all the surveys, if they have an image, redirect to that image.

        Return a fallback if it does not exist.
        """
        for survey in self.surveys:
            image_url = self.get_obj_image_url(survey)
            if image_url:
                return self.request.response.redirect(image_url)

        self.request.response.redirect(
            f"{api.portal.get().absolute_url()}"
            f"/++resource++osha.oira.content/clipboard.svg"
        )
