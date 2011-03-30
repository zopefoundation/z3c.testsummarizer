##############################################################################
#
# Copyright (c) 2003,2010,2011 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Script to check pipermail archive for recent messages, and post a summary.
"""

import sys
import getopt
import urllib2
import re
import datetime
import StringIO
import rfc822
import smtplib
from email.Utils import parseaddr


# Settings used by the script. You'll want to customize some of these.
# archive_url = 'http://mail.zope.org/pipermail/zope-tests/'
archive_url = 'file:///tmp/mail.zope.org/pipermail/zope-tests/'

mailfrom = 'Zope tests summarizer <ct+zopetests@gocept.com>'
mailto = 'zope-dev list <zope-dev@zope.org>'
smtpserver = 'mail.gocept.net'
debug_mailto = 'ct@gocept.com'

# used when debugging
print_not_email = False

months = ("January February March April May June July August September "
          "October November December").split()


# Create a regex that parses subjects like these:
#
#    OK: Test Zope 2.7 / Python 2.3 / Linux
#    FAIL: Test Zope 2.7 / Python 2.3 / Linux
#    FAILED: Test Zope 2.7 / Python 2.3 / Linux
#
#    TODO: Write these examples as a DocTest.
subject_regex = re.compile(
    r"^(?P<success>OK|FAIL(ED)?)\s*:\s*(?P<description>.*?)$")


def get_archive(year, month):
    """Returns a list of the URLs archived for the given year and month.

    If there is nothing at the appropriate URL for that year and month,
    returns an empty list.
    """
    stem = archive_url + ('%s-%s' % (year, months[month-1]))
    url = '%s/date.html' % stem
    try:
        f = urllib2.urlopen(url)
    except urllib2.HTTPError, eee:
        if eee.code == 404:
            return []
        else:
            raise
    data = f.read()
    results = re.compile(r'(\d{6}.html)', re.M).findall(data)
    return ['%s/%s' % (stem, result) for result in results]


class Message:
    """Represents a single message, scraped from the mail archive."""

    status = 'UNKNOWN'

    def __init__(self, url, datetext, subject, fromaddr):
        self.url = url
        self.datetext = datetext
        self.date = datetime.datetime.utcfromtimestamp(
            rfc822.mktime_tz(rfc822.parsedate_tz(self.datetext))
            )
        self.fromaddr = fromaddr
        self.subject = ' '.join(subject.split())
        subject_search = subject_regex.search(self.subject)
        if subject_search:
            groups = subject_search.groupdict()
            self.set_status(groups['success'])
            self.description = groups['description']

    def set_status(self, status):
        if status.startswith('FAIL'):
            self.status = 'FAILED'
        else:
            self.status = status


def get_message(url):
    """Returns a Message object from the message archived at the given URL."""
    f = urllib2.urlopen(url)
    data = f.read()

    # Although the data on the web has lower-case tag names, for some reason
    # these become upper-cased when retrieved using urllib2.

    # There should be only one date, between <I> tags.
    dates = re.compile(r'<I>([^<]*)</I>', re.M|re.I).findall(data)
    if len(dates) != 1:
        print "ERROR", dates
        if not dates:
            raise RuntimeError('Cannot find date')
    datetext = dates[0]

    # The subject and from-address should look like this:
    #   <H1>[Zope-tests] subject line</H1>  <B>from address</B>
    subjects = re.compile(r'<H1>\[%s\] ([^<]*)</H1>\s*'
                           '<B>([^>]*)</B>' % list_name,
                          re.M|re.I).findall(data)
    if len(subjects) != 1:
        print "ERROR", subjects
        if subjects:
            subject, fromaddr = subjects[0]
        else:
            subject, fromaddr = ['ERROR IN TEST AGGREGATOR'] * 2
    else:
        subject, fromaddr = subjects[0]
    return Message(url, datetext, subject, fromaddr)


def monthMinusOne(year, month):
    """Takes a year and a 1-based month.

    Returns as a two-tuple (year, month) the year and 1-based month of
    the previous month.
    """
    months = year * 12 + month - 1
    y, m = divmod(months - 1, 12)
    return y, m + 1


def err_exit(msg, rc=1):
    """Bails out."""
    print >>sys.stderr, msg
    sys.exit(rc)


def main(argv):
    """Do the work!

    Get the list of URLs, get the appropriate messages, compose an email,
    send it to the mailing list.
    """
    usage = 'Usage: list_summarizer.py -C zope|cmf|plone [-T isodate] [-D]'
    selected_config = ''
    selected_date = ''
    debug_mode = 0

    try:
        options, arg = getopt.getopt(argv, 'hC:T:D')
    except getopt.GetoptError, e:
        err_exit('%s\n%s' % (e.msg, usage))

    for name, value in options:
        if name == '-C':
            selected_config = value.strip()+'_summarizer'
        elif name == '-T':
            selected_date = value.strip()
        elif name == '-D':
            debug_mode = 1
        elif name == '-h':
            err_exit(usage, 0)
        else:
            err_exit(usage)

    configs = {'zope_summarizer': dict(list_name='zope-tests',
                                       subject_prefix='Zope Tests')}

    if not selected_config in configs:
        err_exit(usage)

    config = configs[selected_config]
    globals().update(config)

    if debug_mode:
        global mailto
        mailto = debug_mailto

    # All dates used are naive dates (no explicit tz).
    now = datetime.datetime.utcnow()
    now = now.replace(second=0)

    if selected_date:
        date = selected_date.replace('-', '')
        y = int(date[0:4])
        m = int(date[4:6])
        d = int(date[6:8])
        now = now.replace(year=y, month=m, day=d)

    this_month_urls = get_archive(now.year, now.month)
    last_month_year, last_month = monthMinusOne(now.year, now.month)
    last_month_urls = get_archive(last_month_year, last_month)

    # urls is a list of urls for this month an last month, most recent first.
    urls = last_month_urls + this_month_urls
    urls.reverse()

    yesterday = now - datetime.timedelta(days=1)
    tomorrow = now + datetime.timedelta(days=1)

    # Get messages starting at the most recent message, and stopping when
    # we run out of messages or when we get a message that was posted more
    # than one day ago.
    messages = []
    for url in urls:
        message = get_message(url)
        if message.date >= tomorrow:
            continue
        if message.date < yesterday:
            break
        messages.append(message)
    messages.sort(key=lambda m: m.description)

    out = StringIO.StringIO()

    print >>out, "This is the summary for test reports received on the "
    print >>out, "zope-tests list between %s UTC and %s UTC:" % (
        yesterday.replace(second=0, microsecond=0).isoformat(' '),
        now.replace(second=0, microsecond=0).isoformat(' '))
    print >>out
    print >>out, "See the footnotes for test reports of unsuccessful builds."
    print >>out
    print >>out, "An up-to date view of the builders is also available in our "
    print >>out, "buildbot documentation: "
    print >>out, "http://docs.zope.org/zopetoolkit/process/buildbots.html"\
                 "#the-nightly-builds"
    print >>out
    print >>out, "Reports received"
    print >>out, "----------------"
    print >>out

    foot_notes = []
    for message in messages:
        ref = ''
        if message.status != 'OK':
            foot_notes.append(message)
            ref = '[%s]' % len(foot_notes)
        print >>out, (ref).ljust(6), message.description

    print >>out
    print >>out, "Non-OK results"
    print >>out, "--------------"
    print >>out

    for i, message in enumerate(foot_notes):
        print >>out, ('[%s]' % (i+1)).ljust(6), \
                      message.status.ljust(7), \
                      message.description
        print >>out, ' '*6, message.url
        print >>out
        print >>out

    stats = {}
    for message in messages:
        stats.setdefault(message.status, 0)
        stats[message.status] += 1

    subject = '%s - %s' % (subject_prefix, ', '.join('%s: %s' % x for x in
                                                     sorted(stats.items())))

    if print_not_email:
        print "Not sending this email."
        print
        print "Subject:", subject
        print "From:", mailfrom
        print "To:", mailto
        print
        print out.getvalue()
    else:
        body = "From: %s\nTo: %s\nSubject: %s\n\n%s" % (
            mailfrom, mailto, subject, out.getvalue())

        fromname, fromaddr = parseaddr(mailfrom)
        toname, toaddr = parseaddr(mailto)

        s = smtplib.SMTP(smtpserver, 25)
        s.sendmail(fromaddr, toaddr, body)
        s.quit()
