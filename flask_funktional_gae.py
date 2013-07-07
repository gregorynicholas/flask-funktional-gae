"""
  flask_funktional_gae
  ~~~~~~~~~~~~~~~~~~~~

  flask extension to make functional testing of flask applications with the
  app engine sdk easier.

  http://gregorynicholas.github.io/flask-funktional-gae


  :copyright: (c) 2013 by gregorynicholas.
  :license: MIT, see LICENSE for more details.
"""
from io import BytesIO
from json import loads
from flask import url_for, TestClient
from flask.testsuite import FlaskTestCase
from werkzeug import cached_property
from google.appengine.ext import ndb
from google.appengine.ext import testbed
from google.appengine.datastore import datastore_stub_util as ds_stub_util
from random import choice

__all__ = ['TestCase', 'GaeTestClient',
'open_file', 'create_file',
'random_ndb_entity', 'random_word', 'random_email', 'ndbpprint',
'testbed']


# Global test client which should be set in setUp and cleared in tearDown for
# test cases which need to test the result of running tasks
taskqueue_test_client = None


try:
  # we'll use signals for template-related tests if
  # available in this version of Flask
  import blinker
  from flask import template_rendered
  _is_signals = True
except ImportError:
  _is_signals = False


class JsonResponseMixin:
  """
  Mixin with testing helper methods.
  """
  @cached_property
  def json(self):
    return loads(self.data)


class TestCase(FlaskTestCase):
  """
  Enable app engine sdk stubs and disable services. This will replace calls
  to the service with calls to the service stub.
  """
  # for high replication datastore tests
  # see: https://developers.google.com/appengine/docs/python/tools/localunittesting#Introducing_the_Python_Testing_Utilities
  # create a consistency policy that will simulate the high replication
  # consistency model.
  pseudorandomhrconsistencypolicy = None

  def create_app(self):
    """
    Create your Flask app here, with any configuration you need.
    """
    raise NotImplementedError


  def __call__(self, result=None):
    """
    Intitializes the appengine sdk service stubs, doing setup here
    means subclasses don't have to call super.setUp.
    """
    try:
      self._pre_setup()
      FlaskTestCase.__call__(self, result)
    finally:
      self._post_teardown()


  def _pre_setup(self):
    if hasattr(self, 'pre_setup_hook'):
      self.pre_setup_hook()
    # First, create an instance of the Testbed class.
    self.tb = testbed.Testbed()
    # Then activate the testbed, which prepares the
    # service stubs for use
    self.tb.activate()
    # Next, declare which service stubs you want to use.
    self.tb.init_mail_stub()
    self.tb.init_xmpp_stub()
    self.tb.init_files_stub()
    # if PIL is not installed this will raise..
    try:
      import PIL
      self.testbed.init_images_stub()
    except ImportError:
      pass
    except testbed.StubNotSupportedError:
      pass
    self.tb.init_channel_stub()
    self.tb.init_memcache_stub()
    self.tb.init_urlfetch_stub()
    self.tb.init_blobstore_stub()
    self.tb.init_taskqueue_stub()
    # hack to load in yaml file definition for queue names
    # see: http://stackoverflow.com/questions/5324515/task-queue-works-from-view-but-unknownqueueerror-when-run-from-unit-tests
    if hasattr(self, 'taskqueue_yaml_path'):
      self.taskqueue_stub._root_path = self.taskqueue_yaml_path

    self.tb.init_capability_stub()
    self.tb.init_logservice_stub()
    self.tb.init_app_identity_stub()

    # for high replication datastore tests
    if self.pseudorandomhrconsistencypolicy is not None:
      self.policy = ds_stub_util.PseudoRandomHRConsistencyPolicy(
        probability=self.pseudorandomhrconsistencypolicy)
    # initialize the datastore stub with this policy.
    # self.tb.init_datastore_v3_stub(consistency_policy=self.policy)
    self.tb.init_datastore_v3_stub()

    # from google.appengine.ext.ndb import model, tasklets
    # model.make_connection()
    # model.Model._reset_kind_map()
    # ctx = tasklets.make_default_context()
    # tasklets.set_context(ctx)
    # ctx.set_datastore_policy(True)
    # ctx.set_cache_policy(False)
    # ctx.set_memcache_policy(True)

    # flask setup
    self.gae_client = GaeTestClient()
    self.app = self._ctx = None
    self.app = self.create_app()
    self._orig_response_class = self.app.response_class
    self.app.response_class = self._test_response_cls(self.app.response_class)
    self.client = self.app.test_client()
    self._ctx = self.app.test_request_context()
    self._ctx.push()
    self.templates = []
    if _is_signals:
      template_rendered.connect(self._add_template)

    global taskqueue_test_client
    taskqueue_test_client = self.app.test_client()

    if hasattr(self, 'post_setup_hook'):
      self.post_setup_hook()


  def _post_teardown(self):
    """
    Deactivate the testbed once the tests are completed. Otherwise the
    original stubs will not be restored.
    """
    if hasattr(self, 'pre_teardown_hook'):
      self.pre_teardown_hook()
    self.tb.deactivate()

    if self._ctx is not None:
      self._ctx.pop()
    if self.app is not None:
      self.app.response_class = self._orig_response_class
    if _is_signals:
      template_rendered.disconnect(self._add_template)

    global taskqueue_test_client
    taskqueue_test_client = None

    if hasattr(self, 'post_teardown_hook'):
      self.post_teardown_hook()


  # flask helpers..
  # ---------------------------------------------------------------------------

  def url_for(self, handler, **kw):
    """
      :param handler: String path to the route handler.
    """
    with self.app.test_request_context():
      url = url_for(handler, **kw)
      server_name = self.app.config.get('SERVER_NAME')
      if server_name is None:
        return url
      else:
        pre, name, path = url.partition(server_name)
        if len(path) == 0:
          return None, pre
        return pre + name, path


  def _test_response_cls(self, response_class):
    class TestResponse(response_class, JsonResponseMixin):
      pass
    return TestResponse


  def assertTemplateUsed(self, name):
    """
    Checks if a given template is used in the request. Only works if your
    version of Flask has signals support (0.6+) and blinker is installed.

      :param name: String name of the template.
    """
    if not _is_signals:
      raise RuntimeError("Signals not supported")
    for template, context in self.templates:
      if template.name == name:
        return True
    raise AssertionError("template %s not used".format(name))
  assert_template_used = assertTemplateUsed


  def assertStatus(self, response, status_code):
    """
    Helper method to check matching response status.

      :param response: Flask response
      :param status_code: response status code (e.g. 200)
    """
    self.assertIsNotNone(response, 'response is None')
    self.assertIsInstance(response.status_code, int,
      'response status_code is not an int.')
    self.assertEqual(response.status_code, status_code,
      'response status code {} is not {}'.format(
        response.status_code, status_code))
  assert_status = assertStatus


  def assert200(self, response):
    """
    Checks if response status code is 200

      :param response: Flask response
    """
    self.assertStatus(response, 200)
  assert_200 = assert200


  def assert400(self, response):
    """
    Checks if response status code is 400

      :param response: Flask response
    """
    self.assertStatus(response, 400)
  assert_400 = assert400


  def assert401(self, response):
    """
    Checks if response status code is 401

      :param response: Flask response
    """
    self.assertStatus(response, 401)
  assert_401 = assert401


  def assert403(self, response):
    """
    Checks if response status code is 403

      :param response: Flask response
    """
    self.assertStatus(response, 403)
  assert_403 = assert403


  def assert404(self, response):
    """
    Checks if response status code is 404

      :param response: Flask response
    """
    self.assertStatus(response, 404)
  assert_404 = assert404


  def assert405(self, response):
    """
    Checks if response status code is 405

      :param response: Flask response
    """
    self.assertStatus(response, 405)
  assert_405 = assert405


  # mail api helpers..
  # ---------------------------------------------------------------------------

  @property
  def mail_stub(self):
    return self.tb.get_stub(testbed.MAIL_SERVICE_NAME)

  def get_sent_messages(self, to=None, sender=None, subject=None, body=None,
    html=None):
    """Get a list of ```mail.EmailMessage``` objects sent via the Mail API."""
    return self.mail_stub.get_sent_messages(
      to=to, sender=sender, subject=subject, body=body, html=html)

  def assertMailSent(self, to=None, sender=None, subject=None, body=None,
    html=None):
    messages = self.get_sent_messages(
      to=to, sender=sender, subject=subject, body=body, html=html)
    self.assertNotEqual(0, len(messages),
      "No matching email messages were sent.")
  assert_mail_sent = assertMailSent


  # memcache api helpers..
  # ---------------------------------------------------------------------------

  @property
  def memcache_stub(self):
    return self.tb.get_stub(testbed.MEMCACHE_SERVICE_NAME)

  def assertMemcacheHits(self, hits):
    """Asserts that the memcache API has had ``hits`` successful lookups."""
    self.assertEqual(
      hits, self.memcache_stub.get_stats()['hits'])
  assert_memcache_hits = assertMemcacheHits

  def assertMemcacheItems(self, items):
    """Asserts that the memcache API has ``items`` key-value pairs."""
    self.assertEqual(
      items, self.memcache_stub.get_stats()['items'])
  assert_memcache_items = assertMemcacheItems


  # taskqueue api helpers..
  # ---------------------------------------------------------------------------

  @property
  def taskqueue_stub(self):
    return self.tb.get_stub(testbed.TASKQUEUE_SERVICE_NAME)

  def get_tasks(self, url=None, name=None, queue_names=None):
    """Returns a list of `Task`_ objects with the specified criteria.

      :param url:
          URL criteria tasks must match. If ``url`` is ``None``, all tasks
          will be matched.
      :param name:
          name criteria tasks must match. If ``name`` is ``None``, all tasks
          will be matched.
      :param queue_names:
          queue name criteria tasks must match. If ``queue_name`` is ``None``
          tasks in all queues will be matched."""
    return self.taskqueue_stub.get_filtered_tasks(
      url=url, name=name, queue_names=queue_names)

  def assertTasksInQueue(self, n=None, url=None, name=None, queue_names=None):
    """Search for `Task`_ objects matching the given criteria and assert that
    there are ``n`` tasks.

      :usage::

        deferred.defer(some_task, _name='some_task')
        self.assertTasksInQueue(n=1, name='some_task')

      :param n:
          the number of tasks in the queue. If not specified, ``n`` defaults
          to 0.
      :param url:
          URL criteria tasks must match. If ``url`` is ``None``, all tasks
          will be matched.
      :param name:
          name criteria tasks must match. If ``name`` is ``None``, all tasks
          will be matched.
      :param queue_names:
          queue name criteria tasks must match. If ``queue_name`` is ``None``
          tasks in all queues will be matched."""
    tasks = self.get_tasks(
      url=url, name=name, queue_names=queue_names)
    self.assertEqual(n or 0, len(tasks))
  assert_tasks_in_queue = assertTasksInQueue


  # blobstore api helpers..
  # ---------------------------------------------------------------------------

  @property
  def blobstore_stub(self):
    return self.tb.get_stub(testbed.BLOBSTORE_SERVICE_NAME)

  def create_blob(self, blob_key, content):
    """Create new blob and put in storage and Datastore.

      :param blob_key: String blob-key of new blob.
      :param content: Content of new blob as a string.

      :returns:
        New Datastore BlobInfo entity without blob meta-data fields.
    """
    return self.blobstore_stub.CreateBlob(blob_key, content)

  def random_ndb_entity(self, model_class, **kw):
    """
      :param model_class:
      :param **kw:
      :returns:
        Instance of an `ndb.Model` subclass, with randomly selected values.
    """
    return random_ndb_entity(model_class, **kw)


# mock a file upload request..
# see README for usage.

from StringIO import StringIO
from flask import Request

class FileObj(StringIO):
  type_options = {}

  def close(self):
    print 'file upload test..'

class FileUploadRequest(Request):
  def _get_file_stream(*args, **kwargs):
    return FileObj()


def open_file(filename):
  """
    :param filename: String, path to a file.
    :returns: Instance of a tuple.
  """
  f = open(filename, 'r')
  data = f.read()
  size = len(data)
  f.close()
  return (StringIO(data), filename, size)


def create_file(data='testing', filename=None):
  """
    :param data: String of the filename.
    :param filename: Optional, string of the filename.
    :returns: Instance of a tuple for data, filename, size.
  """
  if filename is None:
    filename = random_word()
  return (BytesIO(data), filename, len(data))


def random_email(domain=None):
  """
    :param domain: String hostname of the email domain.
    :returns:
  """
  if domain is None:
    domain = random_word()
  return '{}@{}.com'.format(random_word(), domain)


def random_word():
  """
    :returns: uuid1 as string.
  """
  import uuid
  return str(uuid.uuid1())


_propertytype_method_map = {
  ndb.StringProperty: lambda _: random_word(),
  ndb.TextProperty: lambda _: random_word(),
  ndb.KeyProperty: lambda _: _random_key(_),
  ndb.BooleanProperty: lambda _: None,
  ndb.IntegerProperty: lambda _: None,
  ndb.FloatProperty: lambda _: None,
  ndb.DateTimeProperty: lambda _: None,
  ndb.DateProperty: lambda _: None,
  ndb.TimeProperty: lambda _: None,
  ndb.BlobProperty: lambda _: None,
  ndb.BlobKeyProperty: lambda _: None,
}


def _random_key(prop):
  if prop._kind:
    ndb.Key(prop._kind, random_word())
  else:
    ndb.Key(random_word(), random_word())


def random_ndb_entity(cls, **values):
  """
    :returns:
      Instance of an `ndb.Model` subclass, with randomly selected values.
  """
  entity = cls()
  entity._fix_up_properties() # this must be called to avoid uninitialized props
  props = entity._properties
  # set property specific values..
  for key, prop in props.iteritems():
    if key in values:
      continue
    if prop._default:
      values[key] = prop._default
    elif prop._choices:
      values[key] = choice(prop._choices)

    property_meth = None
    for _proptype in _propertytype_method_map.keys():
      if isinstance(prop, _proptype):
        property_meth = _proptype
        break

    if property_meth:
      values[key] = property_meth(prop)

    if prop._repeated:
      if values[key] is not None:
        values[key] = [values[key]]
      else:
        values.pop(key)
  entity.populate(**values)
  return entity


def ndbpprint(model, level=1):
  """
  Pretty prints an `ndb.Model`.
  """
  body = ['<', type(model).__name__, ':']
  values = model.to_dict()
  for key, field in model._properties.iteritems():
    value = values.get(key)
    if value is not None:
      body.append('\n%s%s: %s' % (
      ' '.join([' ' for idx in range(level)]), key, repr(value)))
  body.append('>')
  return ''.join(body)


class GaeTestClient(TestClient):
  def __init__(self, test_case=None, *args, **kw):
    TestClient.__init__(self, *args, **kw)
    self.test_case = test_case

  def open(self, handler, method_args, *args, **kw):
    base_url, url = self.test_case.url_for(handler, **method_args)
    follow_redirects = kw.pop('follow_redirects', True)
    return self.test_case.app.open(
      url, follow_redirects=follow_redirects, base_url=base_url, *args, **kw)

  def post_raw(self, handler, method_args={}, *args, **kw):
    return self.open(
      handler, method_args, method='POST', *args, **kw)

  def post_file(self, path, handler):
    data, filename, size = open_file(filename=path)
    return self.post_raw(handler,
      data={'files[]': (data, filename)},
      headers=[('enctype', 'multipart/form-data')])

  def assertSuccessHttpResponse(self, test_case, response):
    test_case.assert200(response)
  assert_success_http_response = assertSuccessHttpResponse

  def assertErrorHttpResponse(self, test_case, response, error_code=400):
    test_case.assertStatus(response, error_code)
  assert_error_http_response = assertErrorHttpResponse
