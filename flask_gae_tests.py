#!/usr/bin/env python
"""
  gae_tests
  ~~~~~~~~~~~~~~~~~

  Flask Extension with base test cases to simplify testing Flask applications
  on App Engine.

  :copyright: (c) 2012 by gregorynicholas.
  :license: MIT, see LICENSE for more details.
"""
from flask.testsuite import FlaskTestCase
from google.appengine.ext import testbed


class TestCase(FlaskTestCase):
  '''Enable app engine sdk stubs and disable services. This will replace calls
  to the service with calls to the service stub.'''

  def setUp(self):
    ''' '''
    FlaskTestCase.setUp(self)
    # First, create an instance of the Testbed class.
    self.testbed = testbed.Testbed()
    # Then activate the testbed, which prepares the
    # service stubs for use
    self.testbed.activate()
    # Next, declare which service stubs you want to use.
    self.testbed.init_mail_stub()
    self.testbed.init_xmpp_stub()
    self.testbed.init_files_stub()
    # if PIL is not installed this will raise..
    try:
      import PIL
      self.testbed.init_images_stub()
    except ImportError:
      pass
    except testbed.StubNotSupportedError:
      pass
    self.testbed.init_channel_stub()
    self.testbed.init_memcache_stub()
    self.testbed.init_urlfetch_stub()
    self.testbed.init_blobstore_stub()
    self.testbed.init_taskqueue_stub()
    self.testbed.init_capability_stub()
    self.testbed.init_logservice_stub()
    self.testbed.init_app_identity_stub()
    self.testbed.init_datastore_v3_stub()

  def tearDown(self):
    '''Deactivate the testbed once the tests are completed. Otherwise the
    original stubs will not be restored.'''
    self.testbed.deactivate()

  # mail api helpers..
  # ---------------------------------------------------------------------------

  @property
  def mail_stub(self):
    return self.testbed.get_stub(testbed.MAIL_SERVICE_NAME)

  def get_sent_messages(self, to=None, sender=None, subject=None, body=None,
    html=None):
    '''Get a list of ```mail.EmailMessage``` objects sent via the Mail API.'''
    return self.mail_stub.get_sent_messages(
      to=to, sender=sender, subject=subject, body=body, html=html)

  def assertMailSent(self, to=None, sender=None, subject=None, body=None,
    html=None):
    messages = self.get_sent_messages(
      to=to, sender=sender, subject=subject, body=body, html=html)
    self.assertNotEqual(
      0, len(messages),
      "No matching email messages were sent.")

  # memcache api helpers..
  # ---------------------------------------------------------------------------

  @property
  def memcache_stub(self):
    return self.testbed.get_stub(testbed.MEMCACHE_SERVICE_NAME)

  def assertMemcacheHits(self, hits):
    '''Asserts that the memcache API has had ``hits`` successful lookups.'''
    self.assertEqual(
      hits, self.memcache_stub.get_stats()['hits'])

  def assertMemcacheItems(self, items):
    '''Asserts that the memcache API has ``items`` key-value pairs.'''
    self.assertEqual(
      items, self.memcache_stub.get_stats()['items'])

  # taskqueue api helpers..
  # ---------------------------------------------------------------------------

  @property
  def taskqueue_stub(self):
    return self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)

  def get_tasks(self, url=None, name=None, queue_names=None):
    '''Returns a list of `Task`_ objects with the specified criteria.

      :param url:
          URL criteria tasks must match. If ``url`` is ``None``, all tasks
          will be matched.
      :param name:
          name criteria tasks must match. If ``name`` is ``None``, all tasks
          will be matched.
      :param queue_names:
          queue name criteria tasks must match. If ``queue_name`` is ``None``
          tasks in all queues will be matched.'''
    return self.taskqueue_stub.get_filtered_tasks(
      url=url,
      name=name,
      queue_names=queue_names)

  def assertTasksInQueue(self, n=None, url=None, name=None, queue_names=None):
    '''Search for `Task`_ objects matching the given criteria and assert that
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
          tasks in all queues will be matched.'''
    tasks = self.get_tasks(
      url=url,
      name=name,
      queue_names=queue_names)
    self.assertEqual(n or 0, len(tasks))

  # blobstore api helpers..
  # ---------------------------------------------------------------------------

  @property
  def blobstore_stub(self):
    return self.testbed.get_stub(testbed.BLOBSTORE_SERVICE_NAME)

  def create_blob(self, blob_key, content):
    """Create new blob and put in storage and Datastore.

      :param blob_key: String blob-key of new blob.
      :param content: Content of new blob as a string.

      :returns:
        New Datastore BlobInfo entity without blob meta-data fields.
    """
    return self.blobstore_stub.CreateBlob(blob_key, content)


# mock a file upload request..
# see README for usage.

from StringIO import StringIO
from flask import Request

class FileObj(StringIO):
  def close(self):
    print 'file upload test..'

class FileUploadRequest(Request):
  def _get_file_stream(*args, **kwargs):
    return FileObj()

def open_test_file(filename='test_file.jpg'):
  f = open(filename, 'r')
  data = f.read()
  size = len(data)
  f.close()
  return (StringIO(data), filename, size)

def create_test_file(data='testing', filename='test_file.jpg'):
  return (StringIO(data), filename, len(data))
