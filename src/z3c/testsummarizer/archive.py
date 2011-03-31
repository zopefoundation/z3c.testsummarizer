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
import urllib2
import z3c.testsummarizer.message


class Archive(object):
    """Provides access to the message archive URLs."""

    def __init__(self, base_url):
        self.url = base_url
        if not self.url.endswith('/'):
            self.url += '/'

    def messages_sent_on(self, date):
        this_month_urls = self._message_urls_for_month(date)
        last_month_urls = self._message_urls_for_month(
            self.month_add(date, -1))
        urls = this_month_urls + last_month_urls

        yesterday = date - datetime.timedelta(days=1)
        tomorrow = date + datetime.timedelta(days=1)

        result = []
        for url in urls:
            message = z3c.testsummarizer.message.Message.load(url)
            if message.date >= tomorrow:
                continue
            if message.date < yesterday:
                break
            result.append(message)
        return result

    def _message_urls_for_month(self, date):
        """Returns a list of the URLs archived for the given year and month.

        If there is nothing at the appropriate URL for that year and month,
        returns an empty list.
        """
        stem = self.url + '%s-%s' % (date.year, self.month_name[date.month])
        url = '%s/date.html' % stem
        try:
            f = urllib2.urlopen(url)
        except urllib2.HTTPError, e:
            if e.code == 404:
                return []
            else:
                raise
        data = f.read()
        results = re.compile(r'(\d{6}.html)', re.M).findall(data)
        return ['%s/%s' % (stem, result) for result in results]

    @staticmethod
    def month_add(date, amount):
        months = date.year * 12 + date.month + amount
        year, month = divmod(months - 1, 12)
        return datetime.date(year, month+1, 1)

    month_name = (
        'Dummy-so-it-is-1-based January February March April May June'
        ' July August September October November December').split()
