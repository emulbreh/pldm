import random
import tempfile
import shutil
import json

import elasticsearch
import redis
from tornado import testing

from bikeshed.server.app import Application
from bikeshed.storage.filesystem import FileSystemDocumentStore
from bikeshed import builtin_types
from bikeshed.auth import create_session_key


class ApiTestCase(testing.AsyncHTTPTestCase):
    def setUp(self):
        self.tmp_document_dir = tempfile.mkdtemp()
        store = FileSystemDocumentStore(
            es=elasticsearch.Elasticsearch(),
            root_dir=self.tmp_document_dir,
            redis=redis.StrictRedis(),
            default_type=builtin_types.Ticket,
            default_project='bikeshed-test',
            index_name='bikeshed-test-%x' % random.getrandbits(32),
        )
        store.register(builtin_types.Ticket)
        store.register(builtin_types.Feature)
        store.register(builtin_types.Bug)
        store.register(builtin_types.Story)
        store.register(builtin_types.Project)
        store.register(builtin_types.User)
        self.store = store
        store.create_index()
        store.es.cluster.health(wait_for_nodes=1)
        self._app = Application(store)
        super(ApiTestCase, self).setUp()
        
    def tearDown(self):
        super(ApiTestCase, self).tearDown()
        self.store.delete_index()
        shutil.rmtree(self.tmp_document_dir)

    def get_app(self):
        return self._app


class DocumentSearchTests(ApiTestCase):
    def test_empty_search(self):
        self.http_client.fetch(self.get_url('/api/documents/'), self.stop, headers={
            'Authorization': 'session %s' % create_session_key('0')
        })
        response = self.wait()
        self.assertEqual(json.loads(response.body), {'documents': []})


class DocumentDetailsTests(ApiTestCase):
    def test_get_document_json(self):
        pass
    