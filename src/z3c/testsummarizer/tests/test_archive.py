#############################################################################
#
# Copyright (c) 2011 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from z3c.testsummarizer.archive import Archive
import datetime
import pkg_resources
import unittest


class ArchiveTest(unittest.TestCase):

    def setUp(self):
        self.archive = Archive('file://' + pkg_resources.resource_filename(
            'z3c.testsummarizer.tests', 'fixtures'))

    def test_messages_are_scanned_in_reverse_chronological_order(self):
        # the datetime of the first message in the fixture is (UTC!):
        # datetime.datetime(2011, 2, 1, 5, 14, 47)
        # so we choose a window that ends after that.
        messages = self.archive.messages_sent_on(
            datetime.datetime(2011, 2, 3, 19, 0))
        self.assertEqual(28, len(messages))
