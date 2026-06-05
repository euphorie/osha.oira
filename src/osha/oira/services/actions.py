from osha.oira.tiles.tabs import OiRASiteRootTabsTile
from plone import api
from plone.restapi.services.actions.get import ActionsGet


class OSHAActionsGet(ActionsGet):

    def reply(self):
        """Override the default actions service to add the tabs tile actions
        to the response.

        Unluckily, these tabs were not implemented using the portal_actions machinery.
        """
        actions: dict = super().reply()
        tabs_view: OiRASiteRootTabsTile = api.content.get_view(
            name="tabs", context=self.context, request=self.request
        )  # type: ignore
        tabs_view.update()
        actions["tabs_tile"] = tabs_view.tabs
        return actions
