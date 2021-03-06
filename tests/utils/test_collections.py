# -*- coding: utf-8 -*-

from baph.test.base import TestCase
from baph.utils.collections import OrderedDefaultDict


class OrderedDefaultDictTestCase(TestCase):
    '''Tests ``OrderedDefaultDict``.'''

    def test_simple(self):
        d = OrderedDefaultDict(int)
        self.assertEqual(len(d), 0)
        self.assertEqual(d['nonexistent'], 0)
        self.assertEqual(d['will-exist'], 0)
        self.assertEqual(d['will-exist3'], 0)
        d['will-exist'] = 4
        d['will-exist3'] = 7
        d['will-exist4'] = 8
        self.assertEqual(d['will-exist'], 4)
        self.assertEqual(d['will-exist3'], 7)
        self.assertEqual(d['will-exist4'], 8)
        expected_items = [
            ('nonexistent', 0),
            ('will-exist', 4),
            ('will-exist3', 7),
            ('will-exist4', 8),
        ]
        self.assertEqual(d.items(), expected_items)
        self.assertEqual([i for i in d.iteritems()], expected_items)
