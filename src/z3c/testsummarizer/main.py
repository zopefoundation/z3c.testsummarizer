##############################################################################
#
# Copyright (c) 2003,2010,2011 Zope Corporation and Contributors.
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
"""Script to check pipermail archive for recent messages, and post a summary.
"""

from email.Utils import parseaddr
import ConfigParser
import datetime
import getopt
import pkg_resources
import smtplib
import sys
import z3c.testsummarizer.archive
import z3c.testsummarizer.format


def create_report(archive_url, listname, date):
    yesterday = date - datetime.timedelta(days=1)
    archive = z3c.testsummarizer.archive.Archive(archive_url)
    messages = archive.messages_sent_on(date)
    body = z3c.testsummarizer.format.create_summary(messages, yesterday, date)

    stats = {}
    for message in messages:
        stats.setdefault(message.status, 0)
        stats[message.status] += 1
    subject = '%s - %s' % (
        listname, ', '.join('%s: %s' % x for x in sorted(stats.items())))

    return subject, body


def err_exit(msg, rc=1):
    """Bails out."""
    print >>sys.stderr, msg
    sys.exit(rc)


def main():
    """Get the list of URLs, get the appropriate messages, compose an email,
    send it to the mailing list.
    """
    usage = 'Usage: test-summarizer [-T YYYY-mm-dd] configfile'
    date = None

    try:
        options, args = getopt.getopt(sys.argv, 'hT:')
    except getopt.GetoptError, e:
        err_exit('%s\n%s' % (e.msg, usage))

    for name, value in options:
        if name == '-T':
            date = value.strip()
        elif name == '-h':
            err_exit(usage, 0)
        else:
            err_exit(usage)

    if len(args) != 2:
        err_exit(usage)

    config = ConfigParser.ConfigParser()
    config.readfp(open(args[1]))
    config = dict(config.items('testsummarizer'))

    if date:
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
    else:
        date = datetime.datetime.utcnow().replace(second=0, microsecond=0)

    subject, body = create_report(
        config['archive_url'], config['listname'], date)
    body = "From: %s\nTo: %s\nSubject: %s\n\n%s" % (
        config['from'], config['to'], subject, body)

    fromname, fromaddr = parseaddr(config['from'])
    toname, toaddr = parseaddr(config['to'])

    s = smtplib.SMTP(config['smtpserver'], 25)
    s.sendmail(fromaddr, toaddr, body)
    s.quit()


def debug():
    archive_url = 'file://' + pkg_resources.resource_filename(
        'z3c.testsummarizer.tests', 'fixtures')
    listname = 'zope-tests'

    date = datetime.datetime(2011, 2, 2)
    subject, body = create_report(archive_url, listname, date)

    print 'Subject:', subject
    print
    print body
