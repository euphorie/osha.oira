from setuptools import setup, find_packages
import os

version = '1.2'

tests_require = [
          "Euphorie [tests]",
      ]

setup(name='osha.oira',
      version=version,
      description="OiRA is a comprehensive, easy to use and cost-free web application. It helps micro and small organisations to put in place a thorough step-by-step risk assessment process - from the identification and evaluation of workplace risks, through decision making on preventive actions and the completion of these actions, to continued monitoring and reporting.",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "changes.rst")).read(),
      classifiers=[
        "Framework :: Plone",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 2.6",
        ],
      keywords='euphorie osha oira',
      author='syslab.com',
      author_email='info@syslab.com',
      url="'http://www.oiraproject.eu/'",
      license='GPL',
      message_extractors = {"src": [
            ("**.py",    "lingua_python", None),
            ("**.pt",    "chameleon_xml", None),
            ("**.xml",   "chameleon_xml", None),
            ]},
      packages=find_packages('src'),
      package_dir={"": "src"},
      namespace_packages=['osha'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Euphorie',
          'NuPlone',
          'Products.CMFCore',
          'Products.statusmessages',
          'SQLAlchemy',
          'collective.alerts',
          'five.grok',
          'plone.autoform',
          'plone.dexterity',
          'plone.directives.dexterity',
          'plone.directives.form',
          'plone.tiles',
          'pyrtf-ng',
          'setuptools',
          'z3c.appconfig',
          'z3c.saconfig',
          'zope.component',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.publisher',
          'zope.schema',
          'mobile.sniffer',
      ],
      tests_require=tests_require,
      extras_require={
        "tests" : tests_require,
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
