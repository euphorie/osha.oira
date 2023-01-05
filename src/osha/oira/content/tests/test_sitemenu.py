from osha.oira.testing import OiRAIntegrationTestCase
from zope.component import getMultiAdapter


class TestSitemenu(OiRAIntegrationTestCase):
    def test_sitemenu_items_sectors_overview(self):
        """Test, if the sitemenu on the sectors overview contains the correct
        items.

        The admin menu should contain the statistics entry but not the
        country tools.
        """
        self.loginAsPortalOwner()
        sitemenu = getMultiAdapter((self.portal.sectors, self.request), name="sitemenu")

        menu = sitemenu.actions

        self.assertEqual(menu["title"], "menu_actions")
        self.assertEqual(len(menu["children"]), 3)
        self.assertEqual(menu["children"][0]["title"], "menu_add_new")
        self.assertEqual(menu["children"][1]["title"], "menu_organise")
        self.assertEqual(menu["children"][2]["title"], "menu_admin")
        self.assertEqual(len(menu["children"][2]["children"]), 1)
        self.assertEqual(menu["children"][2]["children"][0]["title"], "menu_statistics")

    def test_sitemenu_items_country(self):
        """Test, if the sitemenu on a country page contains the correct items.

        The admin menu should contain the statistics entry and the
        country tools.
        """
        self.loginAsPortalOwner()
        sitemenu = getMultiAdapter(
            (self.portal.sectors.nl, self.request), name="sitemenu"
        )

        menu = sitemenu.actions

        self.assertEqual(menu["title"], "menu_actions")
        self.assertEqual(len(menu["children"]), 3)
        self.assertEqual(menu["children"][0]["title"], "menu_add_new")
        self.assertEqual(menu["children"][1]["title"], "menu_organise")
        self.assertEqual(menu["children"][2]["title"], "menu_admin")
        self.assertEqual(len(menu["children"][2]["children"]), 2)
        self.assertEqual(
            menu["children"][2]["children"][0]["title"], "menu_country_tools"
        )
        self.assertEqual(menu["children"][2]["children"][1]["title"], "menu_statistics")

    def test_statistics_menu_availability(self):
        """Test, if the statistics menu is available in different contexts with
        different users."""
        import plone.api

        with plone.api.env.adopt_roles(["Manager"]):
            sitemenu = getMultiAdapter(
                (self.portal.sectors.nl, self.request), name="sitemenu"
            )
            self.assertIsNotNone(sitemenu.statistics())

            sitemenu = getMultiAdapter(
                (self.portal.sectors, self.request), name="sitemenu"
            )
            self.assertIsNotNone(sitemenu.statistics())

            sitemenu = getMultiAdapter((self.portal, self.request), name="sitemenu")
            self.assertIsNone(sitemenu.statistics())

        with plone.api.env.adopt_roles(["Anonymous"]):
            sitemenu = getMultiAdapter(
                (self.portal.sectors.nl, self.request), name="sitemenu"
            )
            self.assertIsNone(sitemenu.statistics())

            sitemenu = getMultiAdapter(
                (self.portal.sectors, self.request), name="sitemenu"
            )
            self.assertIsNone(sitemenu.statistics())

            sitemenu = getMultiAdapter((self.portal, self.request), name="sitemenu")
            self.assertIsNone(sitemenu.statistics())
