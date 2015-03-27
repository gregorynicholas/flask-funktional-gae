flask-funktional-gae
====================

[flask](http://flask.pocoo.org) extension to make functional testing of flask
applications with the [app engine sdk](http://appengine.google.com) easier.


[![Build Status](https://secure.travis-ci.org/gregorynicholas/flask-funktional-gae.png?branch=master)](https://travis-ci.org/gregorynicholas/flask-funktional-gae)


* [docs](http://gregorynicholas.github.io/flask-funktional-gae)
* [source](http://github.com/gregorynicholas/flask-funktional-gae)
* [package](https://pypi.python.org/pypi/flask-funktional-gae)
* [changelog](https://github.com/gregorynicholas/flask-funktional-gae/blob/master/CHANGES.md)
* [travis-ci](http://travis-ci.org/gregorynicholas/flask-funktional-gae)


-----


### getting started

install with *pip*:

    pip install flask-funktional-gae==0.0.1


-----


### overview

used on top of the [`flask-funktional`](http://github.com/gregorynicholas/flask-funktional)
extension, it provides setup of app engine sdk stubs with a focus on being
transparent, seamless, and minimally invasive.


### features

* [todo]


-----


### example usage

    from flask.ext import funktional
    from flask.ext import funktional_gae


    # define a test Flask application..
    app = Flask(__name__)
    app.debug = True
    app.request_class = funktional.FileUploadRequest


    class TestCase(funktional.TestCase):
      def test_upload_returns_valid_blob_result(self):
        data, filename, size = funktional.open_test_file('test_file.jpg')
        response = app.test_client().post(
          data={'test': (data, filename)},
          path='/test_upload1',
          headers={},
          query_string={})
        self.assertEqual(200, response.status_code)
