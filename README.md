flask-funktional-gae
====================

[flask](http://flask.pocoo.org) extension with base test cases to simplify
testing flask web applications on [google app-engine](http://appengine.google.com)

reduces setup code in `TestCase` classes.
removes tedious api-service stubbing.
adds some nifty assertion helpers.


<br>
<br>
build-status:
`master ` [![travis-ci build-status: master](https://secure.travis-ci.org/gregorynicholas/flask-funktional-gae.svg?branch=master)](https://travis-ci.org/gregorynicholas/flask-funktional-gae)
`develop` [![travis-ci build-status: develop](https://secure.travis-ci.org/gregorynicholas/flask-funktional-gae.svg?branch=develop)](https://travis-ci.org/gregorynicholas/flask-funktional-gae)

<br>
<br>
* [docs](http://gregorynicholas.github.io/flask-funktional-gae)
* [source](http://github.com/gregorynicholas/flask-funktional-gae)
* [package](http://packages.python.org/flask-funktional-gae)
* [issues](https://github.com/gregorynicholas/flask-funktional-gae/issues)
* [changelog](https://github.com/gregorynicholas/flask-funktional-gae/blob/master/CHANGES.md)
* [travis-ci](http://travis-ci.org/gregorynicholas/flask-funktional-gae)


<br>
-----
<br>


### getting started


install with pip:

    $ pip install flask-funktional-gae


<br>
-----
<br>


### features

* [todo]


<br>
-----
<br>


### example usage

    import flask_funktional

    # create a test Flask application..
    app = Flask(__name__)
    app.debug = True
    app.request_class = gae_tests.FileUploadRequest

    class TestCase(gae_tests.TestCase):
      def test_upload_returns_valid_blob_result(self):
        data, filename, size = gae_tests.open_test_file('test_file.jpg')
        response = app.test_client().post(
          data={'test': (data, filename)},
          path='/test_upload1',
          headers={},
          query_string={})
        self.assertEqual(200, response.status_code)
