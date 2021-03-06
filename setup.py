from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='uvc.qah',
      version=version,
      description="Quick Ad Hoc",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['uvc'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'grok',
          'pycrypto',
          'setuptools',
          'uvc.tbskin',
          'uvcsite',
          'zope.catalog',
          'zope.component',
          'zope.interface',
          'zope.pluggableauth',
          'zope.publisher',
          'zope.schema',
      ],
      entry_points={
         'z3c.autoinclude.plugin': 'target=uvcsite', 
      }
)
