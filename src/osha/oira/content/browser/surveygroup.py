# coding=utf-8
from Acquisition import aq_parent
from euphorie.content import MessageFactory as _
from euphorie.content.browser import surveygroup
from plone import api
from plonetheme.nuplone.skin import actions
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class AddForm(surveygroup.AddForm):

    template = ViewPageTemplateFile("templates/surveygroup_add.pt")


class AddView(surveygroup.AddView):
    form = AddForm


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
                    default=u"You can not delete an OiRA tool that has been published.",
                ),
                self.request,
                "error",
            )
            self.request.response.redirect(context.absolute_url())
            return False
        return True
