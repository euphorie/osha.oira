from setuptools import setup

import monkeypatch_setup  # noqa: F401
import os

version = "14.0.2.dev0"

setup(
    name="osha.oira",
    version=version,
    description="Euphorie customisations for OSHA-OiRA site.",
    long_description=open("README.rst").read()
    + "\n"
    + open(os.path.join("docs", "changes.rst")).read(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 6.2",
        "Framework :: Plone :: 6.3",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Programming Language :: Python :: 3.15",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="euphorie osha oira",
    author="syslab.com",
    author_email="info@syslab.com",
    project_urls={"Homepage": "http://www.oiraproject.eu/"},
    license_expression="GPL-2.0-only",
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "Euphorie >=20.0.0",
        "Zope",
        "alembic",
        "collective.ftw.upgrade",
        "lxml",
        "mobile.sniffer",
        "NuPlone >= 4.0.1",
        "openpyxl",
        "pas.plugins.ldap",
        "Pillow",
        "plone.api",
        "plone.app.content",
        "plone.app.dexterity",
        "plone.app.layout",
        "plone.app.vocabularies",
        "plone.app.z3cform",
        "plone.autoform",
        "plone.base",
        "plone.dexterity",
        "plone.formwidget.recaptcha",
        "plone.indexer",
        "plone.memoize",
        "plone.namedfile",
        "plone.protect",
        "plone.restapi",
        "plone.scale",
        "plone.supermodel",
        "plone.theme",
        "plone.tiles",
        "Products.CMFCore",
        "Products.CMFPlone",
        "Products.MemcachedManager",
        "Products.statusmessages",
        "requests",
        "slc.zopescript",
        "SQLAlchemy",
        "z3c.form",
        "z3c.saconfig",
        "zope.app.publication",
        "zope.publisher",
        "zope.sqlalchemy",
    ],
    python_requires=">=3.11",
    extras_require={
        "tests": [
            "Euphorie [tests]",
            "node.ext.ldap",
            "pas.plugins.ldap",
            "plone.app.robotframework[debug]",
            "plone.app.testing",
            "plone.testing",
            "robotsuite",
        ],
    },
    entry_points="""
      [z3c.autoinclude.plugin]
      target = plone

      [console_scripts]
      outdated_tools = osha.oira.scripts:outdated_tools
      write_statistics = osha.oira.scripts:write_statistics
      clean_up_guest_sessions = osha.oira.sql_scripts:clean_up_guest_sessions
      """,
)
