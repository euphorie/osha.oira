# coding=utf-8
from euphorie.content.browser import surveygroup
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class AddForm(surveygroup.AddForm):

    template = ViewPageTemplateFile("templates/surveygroup_add.pt")


class AddView(surveygroup.AddView):
    form = AddForm
