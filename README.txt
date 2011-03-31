==================
z3c.testsummarizer
==================

Script that checks a pipermail archive for recent messages, parses them
according to a test result format and creates a summary.

To use, write a configuration file like this::

  [testsummarizer]
  archive_url = https://mail.zope.org/pipermail/zope-tests/
  listname = zope-tests
  from = Zope tests summarizer <noreply@localhost>
  to = user@localhost
  smtpserver = localhost

and then call ``test-summarizer example.ini``.