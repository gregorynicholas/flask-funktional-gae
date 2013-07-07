#!/usr/bin/env python
"""
flask-funktional-gae
~~~~~~~~~~~~~~~~~~~~

flask extension to make functional testing of flask applications with the
app engine sdk easier.

used on top of the `flask-funktional <http://github.com/gregorynicholas/\
flask-funktional>`_ extension, it provides setup of app engine sdk stubs with
a focus on being transparent and minimally invasive.


links
`````

* `docs <http://gregorynicholas.github.io/flask-funktional-gae>`_
* `source <http://github.com/gregorynicholas/flask-funktional-gae>`_
* `package <http://packages.python.org/flask-funktional-gae>`_
* `travis-ci <http://travis-ci.org/gregorynicholas/flask-funktional-gae>`_

"""
from setuptools import setup

__version__ = "0.0.1"

with open("requirements.txt", "r") as f:
  requires = f.readlines()

with open("README.md", "r") as f:
  long_description = f.readlines()


setup(
  name='flask-funktional-gae',
  version=__version__,
  url='http://github.com/gregorynicholas/flask-funktional-gae',
  license='MIT',
  author='gregorynicholas',
  author_email='gn@gregorynicholas.com',
  description=__doc__,
  long_description=long_description,
  zip_safe=False,
  platforms='any',
  install_requires=requires,
  py_modules=[
    'flask_funktional_gae'
    'flask_funktional_gae_tests'
  ],
  dependency_links=[
  ],
  tests_require=[
  ],
  test_suite='flask_funktional_gae_tests',
  classifiers=[
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development :: Libraries :: Python Modules'
  ]
)
