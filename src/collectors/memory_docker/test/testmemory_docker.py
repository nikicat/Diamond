#!/usr/bin/python
# coding=utf-8
################################################################################
import os
from test import CollectorTestCase
from test import get_collector_config
from test import unittest
from mock import Mock
from mock import patch
from mock import mock_open

try:
    from cStringIO import StringIO
    StringIO  # workaround for pyflakes issue #13
except ImportError:
    from StringIO import StringIO

from diamond.collector import Collector
from memory_docker import MemoryDockerCollector
import docker

dirname = os.path.dirname(__file__)
fixtures_path = os.path.join(dirname, 'fixtures/')
fixtures = []
for root, dirnames, filenames in os.walk(fixtures_path):
    fixtures.append([root, dirnames, filenames])

docker_fixture = [
    {u'Id': u'c3341726a9b4235a35b390c5f6f28e5a6869879a48da1d609db8f6bf4275bdc5',
     u'Names': [u'/testcontainer']},
    {u'Id': u'9c151939e20682b924d7299875e94a4aabbe946b30b407f89e276507432c625b',
     u'Names': None}]


class TestMemoryDockerCollector(CollectorTestCase):
    def setUp(self):
        config = get_collector_config('MemoryDockerCollector', {
            'interval': 10,
            'byte_unit': ['megabyte', 'byte']
        })

        self.collector = MemoryDockerCollector(config, None)

    def test_import(self):
        self.assertTrue(MemoryDockerCollector)

    @patch('os.walk', Mock(return_value=iter(fixtures)))
    @patch.object(docker.Client, '__init__', Mock(return_value=None))
    @patch.object(docker.Client, 'containers', Mock(return_value=[]))
    @patch.object(Collector, 'publish')
    def test_should_open_all_stat(self, publish_mock):
        open_mock = mock_open()
        with patch('__builtin__.open', open_mock):
            self.collector.collect()
            for filename in ('memory.stat', 'memory.limit_in_bytes'):
                open_mock.assert_any_call(
                    fixtures_path + 'lxc/testcontainer/' + filename)
                open_mock.assert_any_call(fixtures_path + 'lxc/' + filename)
                open_mock.assert_any_call(fixtures_path + filename)

    @patch('__builtin__.open', mock_open())
    @patch('os.walk', Mock(return_value=iter(fixtures)))
    @patch.object(docker.Client, '__init__', Mock(return_value=None))
    @patch.object(docker.Client, 'containers')
    @patch.object(Collector, 'publish')
    def test_should_get_containers(self, publish_mock, containers_mock):
        containers_mock.return_value = []
        self.collector.collect()
        containers_mock.assert_called_once_with(all=True)

    @patch.object(Collector, 'publish')
    @patch.object(docker.Client, 'containers',
                  Mock(return_value=docker_fixture))
    def test_should_work_with_real_data(self, publish_mock):
        MemoryDockerCollector.MEMORY_PATH = fixtures_path
        self.collector.collect()

        self.assertPublishedMany(publish_mock, {
            'lxc.testcontainer.megabyte_cache': 1,
            'lxc.testcontainer.megabyte_rss': 1,
            'lxc.testcontainer.megabyte_swap': 1,
            'lxc.testcontainer.megabyte_limit': 1,
            'lxc.megabyte_cache': 1,
            'lxc.megabyte_rss': 1,
            'lxc.megabyte_swap': 1,
            'lxc.megabyte_limit': 1,
            'system.megabyte_cache': 1,
            'system.megabyte_rss': 1,
            'system.megabyte_swap': 1,
            'system.megabyte_limit': 1,
            'docker.testcontainer.megabyte_cache': 1,
            'docker.testcontainer.megabyte_rss': 1,
            'docker.testcontainer.megabyte_swap': 1,
            'docker.testcontainer.megabyte_limit': 1,
            'docker.megabyte_cache': 1,
            'docker.megabyte_rss': 1,
            'docker.megabyte_swap': 1,
            'docker.megabyte_limit': 1,
            'lxc.testcontainer.cache': 2**20,
            'lxc.testcontainer.rss': 2**20,
            'lxc.testcontainer.swap': 2**20,
            'lxc.testcontainer.limit': 2**20,
            'lxc.cache': 2**20,
            'lxc.rss': 2**20,
            'lxc.swap': 2**20,
            'lxc.limit': 2**20,
            'system.cache': 2**20,
            'system.rss': 2**20,
            'system.swap': 2**20,
            'system.limit': 2**20,
            'docker.testcontainer.cache': 2**20,
            'docker.testcontainer.rss': 2**20,
            'docker.testcontainer.swap': 2**20,
            'docker.testcontainer.limit': 2**20,
            'docker.cache': 2**20,
            'docker.rss': 2**20,
            'docker.swap': 2**20,
            'docker.limit': 2**20,
        })

if __name__ == "__main__":
    unittest.main()
