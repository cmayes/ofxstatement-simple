#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_ofxstatement-simple
----------------------------------

Tests for `ofxstatement-simple` module.
"""
from datetime import date
import logging

import unittest
import uuid
import os
from ofxstatement.plugins.simple import SimpleBankPlugin, is_zero

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('test_simple')

DATA_DIR = os.path.join(os.path.dirname(__file__), 'test_data')
BAL_0_BAL_JSON_PATH = os.path.join(DATA_DIR, 'exported_transactions.json')
BAL_500_BAL_JSON_PATH = os.path.join(DATA_DIR, 'exported_transactions-500.json')
BAL_0_AMT_JSON_PATH = os.path.join(DATA_DIR, 'exported_transactions-0-amount.json')


# Shared Methods #


class TestSimpleBankStatement(unittest.TestCase):
    def test0Balance(self):
        """Statement starts with a zero balance."""
        stmt = SimpleBankPlugin(None, {}).get_parser(BAL_0_BAL_JSON_PATH).parse()

        self.assertAlmostEqual(0.0, stmt.start_balance)
        self.assertAlmostEqual(20.03, stmt.end_balance)
        self.assertEqual(date(2013, 2, 6), to_date(stmt.start_date))
        self.assertEqual(date(2014, 8, 30), to_date(stmt.end_date))
        self.assertEqual(19, len(stmt.lines))
        for stline in stmt.lines:
            self.assertIsNotNone(stline.memo)
            self.assertFalse(is_zero(stline.amount))
            self.assertTrue(date(2014, 8, 30) >= to_date(stline.date) >= date(2013, 2, 6))

    def test500Balance(self):
        """Statement starts with a $500 balance."""
        stmt = SimpleBankPlugin(None, {}).get_parser(BAL_500_BAL_JSON_PATH).parse()

        self.assertAlmostEqual(500.0, stmt.start_balance)
        self.assertAlmostEqual(20.03, stmt.end_balance)
        self.assertEqual(date(2013, 3, 3), to_date(stmt.start_date))
        self.assertEqual(date(2014, 8, 30), to_date(stmt.end_date))
        self.assertEqual(15, len(stmt.lines))
        for stline in stmt.lines:
            self.assertIsNotNone(stline.memo)
            self.assertFalse(is_zero(stline.amount))
            self.assertTrue(date(2014, 8, 30) >= to_date(stline.date) >= date(2013, 3, 3))

    def test0AmountExclude(self):
        """Statement starts with a zero-amount balance that's filtered out."""
        stmt = SimpleBankPlugin(None, {'account': '12345', 'filter_zeros': 'true'}
                                ).get_parser(BAL_0_AMT_JSON_PATH).parse()

        self.assertEqual(stmt.account_id, '12345')
        self.assertEqual(stmt.bank_id, 'Simple')
        self.assertAlmostEqual(480.0, stmt.start_balance)
        self.assertAlmostEqual(20.03, stmt.end_balance)
        self.assertEqual(date(2013, 3, 30), to_date(stmt.start_date))
        self.assertEqual(date(2014, 8, 30), to_date(stmt.end_date))
        self.assertEqual(14, len(stmt.lines))
        for stline in stmt.lines:
            self.assertIsNotNone(stline.memo)
            self.assertFalse(is_zero(stline.amount))
            self.assertTrue(date(2014, 8, 30) >= to_date(stline.date) >= date(2013, 3, 30))

    def test0AmountInclude(self):
        """Statement starts with a zero-amount balance that's included."""
        stmt = SimpleBankPlugin(None, {'account': '12345', 'filter_zeros': 'false'}
                                ).get_parser(BAL_0_AMT_JSON_PATH).parse()

        self.assertEqual(stmt.account_id, '12345')
        self.assertEqual(stmt.bank_id, 'Simple')
        self.assertAlmostEqual(480.0, stmt.start_balance)
        self.assertAlmostEqual(20.03, stmt.end_balance)
        self.assertEqual(date(2013, 3, 3), to_date(stmt.start_date))
        self.assertEqual(date(2014, 8, 30), to_date(stmt.end_date))
        self.assertEqual(15, len(stmt.lines))
        for stline in stmt.lines:
            self.assertIsNotNone(stline.memo)
            if is_zero(stline.amount):
                self.assertEqual(date(2013, 3, 3), to_date(stline.date))
            self.assertTrue(date(2014, 8, 30) >= to_date(stline.date) >= date(2013, 3, 3))

def to_date(dt):
    """Creates a comparable date object from the given datetime."""
    return date(dt.year, dt.month, dt.day)
