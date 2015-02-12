from setuptools import setup, find_packages
import os

version = '2.3.4'

tests_require = [
        'Euphorie [tests]',
        'mock',
      ]

setup(name='osha.oira',
      version=version,
      description="Euphorie customisations for OSHA-OiRA site.",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "changes.rst")).read(),
      classifiers=[
          "Framework :: Plone",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='euphorie osha oira',
      author='syslab.com',
      author_email='info@syslab.com',
      url="http://www.oiraproject.eu/",
      license='GPL',
      packages=find_packages('src'),
      package_dir={"": "src"},
      namespace_packages=['osha'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Euphorie >=6.0b2',
          'NuPlone >=1.3.9',
          'Pillow',
          'Products.statusmessages',
          # We seem to have a persisten utility that prevents running upgrade
          # steps. The following package is therefore added for providing the
          # required interface.
          'collective.js.jqueryui',
          'plone.autoform',
          'plone.tiles',
          'setuptools',
          'zope.publisher',
          'mobile.sniffer',
          'plone.api',
      ],
      tests_require=tests_require,
      extras_require={
          "tests": tests_require + ['plone.app.testing'],
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
