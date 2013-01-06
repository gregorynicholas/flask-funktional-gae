#!/usr/bin/env python
"""
flask-gae_tests
--------------

Flask Extension with base test cases to simplify testing Flask applications
on App Engine.

Links
`````

* `documentation <http://packages.python.org/flask-gae_tests>`_
* `development version
  <http://github.com/gregorynicholas/flask-gae_tests/zipball/master#egg=flask_gae_tests-dev>`_

"""
from setuptools import setup

setup(
  name='flask-gae_tests',
  version='1.0.0',
  url='http://github.com/gregorynicholas/flask-gae_tests',
  license='MIT',
  author='gregorynicholas',
  description='Flask Extension with base test cases to simplify testing Flask \
applications on App Engine.',
  long_description=__doc__,
  py_modules=['flask_gae_tests'],
  # packages=['flaskext'],
  # namespace_packages=['flaskext'],
  include_package_data=False,
  data_files=[],
  zip_safe=False,
  platforms='any',
  install_requires=[
    'flask',
  ],
  dependency_links = [
  ],
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
