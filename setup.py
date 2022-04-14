from setuptools import setup, find_packages
import os

version = '0.0.1'

long_description = open('README.rst').read()

def clean_lines(filename):
    with open(filename) as fd:
        return [line.strip() for line in fd.readlines()]

requirements = clean_lines('requirements.txt')
test_requirements = clean_lines('requirements-test.txt')

setup(name='idleiss',
      version=version,
      description="Idle Internet Spaceships",
      long_description=long_description,
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python :: 3.7.4',
        ],
      keywords='idlerpg spaceships internetspaceships',
      author='DuskDragon',
      author_email='',
      url='https://github.com/DuskDragon/IdleISS/',
      license='gpl',
      packages=['idleiss'],
      package_dir={'idleiss': './idleiss'},
      namespace_packages=[],
      include_package_data=True,
      zip_safe=False,
      install_requires=requirements,
      test_suite='nose.collector',
      tests_require=test_requirements,
      extras_require={'dev': [test_requirements]},
      entry_points={
          'console_scripts': [
              'idleiss = idleiss.main:run',
          ],
      },
)
