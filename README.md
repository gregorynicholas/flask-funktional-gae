# flask-gae_tests

--------------

Flask Extension with base test cases to simplify testing Flask applications
on App Engine.

----

### install with pip
`pip install https://github.com/gregorynicholas/flask-gae_tests/tarball/master`

### usage

    from flask.ext import gae_tests

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
