from setuptools import find_packages
from setuptools import setup

import monkeypatch_setup  # noqa: F401
import os


version = "9.1.1"

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
        "Framework :: Plone :: 5.1",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="euphorie osha oira",
    author="syslab.com",
    author_email="info@syslab.com",
    url="http://www.oiraproject.eu/",
    license="GPL",
    packages=find_packages("src"),
    package_dir={"": "src"},
    namespace_packages=["osha"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "Euphorie >=14.0.0",
        "ftw.upgrade",
        "htmllaundry",
        "mobile.sniffer",
        "NuPlone >=2.1.0",
        "pas.plugins.ldap",
        "Pillow",
        "plone.api",
        "plone.autoform",
        "plone.formwidget.recaptcha",
        "plone.tiles",
        "Products.statusmessages",
        "requests",
        "setuptools",
        "slc.zopescript",
        "zope.app.publication",
        "zope.publisher",
    ],
    extras_require={
        "tests": [
            "alchemy_mock",
            "Euphorie [tests]",
            "node.ext.ldap",
            "pas.plugins.ldap",
            "plone.app.robotframework[debug]",
            "plone.app.testing",
        ],
    },
    entry_points="""
      [z3c.autoinclude.plugin]
      target = plone

      [console_scripts]
      outdated_tools = osha.oira.scripts:outdated_tools
      write_statistics = osha.oira.scripts:write_statistics
      update_statistics = osha.oira.statistics.scripts:update_statistics
      clean_up_guest_sessions = osha.oira.sql_scripts:clean_up_guest_sessions
      """,
)
