# coding=utf-8

"""
The MemoryCgroupCollector collects memory metric for cgroups

Stats that we are interested in tracking
cache - # of bytes of page cache memory.
rss   - # of bytes of anonymous and swap cache memory.
swap  - # of bytes of swap usage

#### Dependencies

/sys/fs/cgroup/memory/memory.stat
"""

import diamond.collector
import diamond.convertor
import os
import collections


class MemoryCgroupCollector(diamond.collector.Collector):
    MEMORY_PATH = '/sys/fs/cgroup/memory/'

    def get_default_config_help(self):
        config_help = super(
            MemoryCgroupCollector, self).get_default_config_help()
        config_help.update({
        })
        return config_help

    def get_default_config(self):
        """
        Returns the default collector settings
        """
        config = super(MemoryCgroupCollector, self).get_default_config()
        config.update({
            'path':     'memory_cgroup',
            'method':   'Threaded',
            'enabled_keys': 'cache,rss,swap',
        })
        return config

    def collect(self):
        results = collections.defaultdict(dict)
        enabled_keys = self.config['enabled_keys'].split(',')
        for root, dirnames, filenames in os.walk(self.MEMORY_PATH):
            for filename in filenames:
                parent = root.replace(self.MEMORY_PATH, "").replace("/", ".")
                if parent == '':
                    parent = 'system'
                filepath = os.path.join(root, filename)
                if filename == 'memory.stat':
                    # matches will contain a tuple with lines from stat
                    # and the parent of the stat
                    with open(filepath) as stat_file:
                        for line in stat_file:
                            name, value = line.split()
                            if name not in enabled_keys:
                                continue
                            results[parent][name] = value
                elif filename == 'memory.limit_in_bytes':
                    with open(filepath) as limits_file:
                        results[parent]['limit'] = limits_file.readline()

        print(self.config['byte_unit'])
        for parent, stats in results.items():
            for key, value in stats.items():
                for unit in self.config['byte_unit']:
                    newvalue = diamond.convertor.binary.convert(
                            value=value, oldUnit='byte', newUnit=unit)
                    newkey = key if unit == 'byte' else '_'.join([unit,key])
                    metric_name = '.'.join([parent, newkey])
                    print('publishing {}={}'.format(metric_name, newvalue))
                    self.publish(metric_name, newvalue, metric_type='GAUGE')
        return True
