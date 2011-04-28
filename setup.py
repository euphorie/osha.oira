from setuptools import setup, find_packages
import os

version = '0.12dev'

tests_require = [
          "Euphorie [tests]",
      ]

setup(name='osha.oira',
      version=version,
      description="'EU-OSHA customisations for Euphorie/OiRA'",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
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
      author_email='thomas@syslab.com',
      url="'http://www.oira.osha.europa.eu/'",
      license='GPL',
      packages=find_packages('src'),
      package_dir={"": "src"},
      namespace_packages=['osha'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Euphorie',
          'plone.tiles',
          'collective.alerts',
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
