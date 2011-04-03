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

import StringIO


def create_summary(messages, start, end, listname='zope-tests'):
    messages = sorted(messages, key=lambda m: m.description)
    out = StringIO.StringIO()

    print >>out, "This is the summary for test reports received on the "
    print >>out, "%s list between %s UTC and %s UTC:" % (
        listname, start.isoformat(' '), end.isoformat(' '))
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

    return out.getvalue()
