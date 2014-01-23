from setuptools import setup, find_packages
import os

version = '0.0'

long_description = open('README.rst').read()

setup(name='idleiss',
      version=version,
      description="",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Development Status :: 4 - Beta",
        ],
      keywords='',
      author='DuskDragon',
      author_email='',
      url='https://github.com/DuskDragon/IdleISS/',
      license='mit',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=[],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
