from setuptools import setup, find_packages
import os

version = '0.9dev'

setup(name='osha.oira',
      version=version,
      description="'EU-OSHA customisations for Euphorie/OiRA'",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='syslab.com',
      author_email='thomas@syslab.com',
      url="'http://www.oira.osha.europa.eu/'",
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['osha'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.tiles',
          'collective.alerts',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
