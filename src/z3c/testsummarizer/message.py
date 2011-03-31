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

import datetime
import re
import rfc822
import urllib2


# Parses subjects like these:
#
#    OK: Test Zope 2.7 / Python 2.3 / Linux
#    FAIL: Test Zope 2.7 / Python 2.3 / Linux
#    FAILED: Test Zope 2.7 / Python 2.3 / Linux
#
#    TODO: Write these examples as a DocTest.
subject_regex = re.compile(
    r"^(?P<success>OK|FAIL(ED)?)\s*:\s*(?P<description>.*?)$")


class Message:
    """Represents a single message, scraped from the mail archive."""

    def __init__(self, url, datetext, subject, fromaddr):
        self.url = url
        self.datetext = datetext
        self.date = datetime.datetime.utcfromtimestamp(
            rfc822.mktime_tz(rfc822.parsedate_tz(self.datetext))
            )
        self.fromaddr = fromaddr
        self.subject = ' '.join(subject.split())

        self.status = 'UNKNOWN'
        self.description = self.subject

        subject_search = subject_regex.search(self.subject)
        if subject_search:
            groups = subject_search.groupdict()
            self.description = groups['description']
            status = groups['success']
            if status.startswith('FAIL'):
                self.status = 'FAILED'
            else:
                self.status = status

    @classmethod
    def load(cls, url):
        f = urllib2.urlopen(url)
        data = f.read()

        # Although the data on the web has lower-case tag names, for some
        # reason these become upper-cased when retrieved using urllib2.

        # There should be only one date, between <I> tags.
        dates = re.compile(r'<I>([^<]*)</I>', re.M|re.I).findall(data)
        if len(dates) != 1:
            print "ERROR", dates
            if not dates:
                raise RuntimeError('Cannot find date')
        datetext = dates[0]

        # The subject and from-address should look like this:
        #   <H1>[listname] subject line</H1>  <B>from address</B>
        subjects = re.compile(r'<H1>\[.*\] ([^<]*)</H1>\s*'
                               '<B>([^>]*)</B>',
                              re.M|re.I).findall(data)
        if len(subjects) != 1:
            print "ERROR", subjects
            if subjects:
                subject, fromaddr = subjects[0]
            else:
                subject, fromaddr = ['ERROR IN TEST AGGREGATOR'] * 2
        else:
            subject, fromaddr = subjects[0]
        return cls(url, datetext, subject, fromaddr)
