from setuptools import setup, find_packages
import os

version = '0.0.1'

long_description = open('README.rst').read()

setup(name='idleiss',
      version=version,
      description="Idle Internet Spaceships",
      long_description=long_description,
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python :: 3.6',
        ],
      keywords='idlerpg spaceships internetspaceships',
      author='DuskDragon',
      author_email='',
      url='https://github.com/DuskDragon/IdleISS/',
      license='gpl',
      packages=find_packages('src/idleiss', exclude=['ez_setup', 'docs', 'config']),
      package_dir={'': 'src'},
      namespace_packages=[],
      include_package_data=True,
      test_suite='nose.collector',
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points={
          'console_scripts': [
              'idleiss = idleiss.main:run',
          ],
      },
)
