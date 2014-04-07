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
from memory_cgroup import MemoryCgroupCollector

dirname = os.path.dirname(__file__)
fixtures_path = os.path.join(dirname, 'fixtures/')
fixtures = []
for root, dirnames, filenames in os.walk(fixtures_path):
    fixtures.append([root, dirnames, filenames])


class TestMemoryCgroupCollector(CollectorTestCase):
    def setUp(self):
        config = get_collector_config('MemoryCgroupCollector', {
            'interval': 10,
            'byte_unit': ['megabyte','byte']
        })

        self.collector = MemoryCgroupCollector(config, None)

    def test_import(self):
        self.assertTrue(MemoryCgroupCollector)

    @patch('os.walk', Mock(return_value=iter(fixtures)))
    @patch.object(Collector, 'publish')
    def test_should_open_all_cpuacct_stat(self, publish_mock):
        open_mock = mock_open()
        with patch('__builtin__.open', open_mock):
            self.collector.collect()
            open_mock.assert_any_call(
                fixtures_path + 'lxc/testcontainer/memory.stat')
            open_mock.assert_any_call(fixtures_path + 'lxc/memory.stat')
            open_mock.assert_any_call(fixtures_path + 'memory.stat')

    @patch.object(Collector, 'publish')
    def test_should_work_with_real_data(self, publish_mock):
        MemoryCgroupCollector.MEMORY_PATH = fixtures_path
        self.collector.collect()

        self.assertPublishedMany(publish_mock, {
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
        })

if __name__ == "__main__":
    unittest.main()
