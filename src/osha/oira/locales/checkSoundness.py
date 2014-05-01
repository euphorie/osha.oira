#!/usr/bin/env python

# Author: Wolfgang Thomas <thomas@syslab.com>

"""%(program)s: Check that all po files are sound and don't break when they
are compiled

usage:    %(program)s
"""

import sys
import os
import re
from popen2 import popen3
# import polib

# Define here the patterns for all error messages you want to ignore
messages_to_ignore = [
  '.*?entry ignored',
  '^msgfmt: found .*',
  '.*?warning: source file contains fuzzy translation',
]
ignore = [re.compile(patt) for patt in messages_to_ignore]

def usage(stream, msg=None):
    if msg:
        print >> stream, msg
        print >> stream
    program = os.path.basename(sys.argv[0])
    print >> stream, __doc__ % {"program": program}
    sys.exit(0)

dirs = [x for x in os.listdir('.') if len(x) == 2 and os.path.isdir(x)]
houstonwehaveaproblem = False
for dirname in dirs:
    path = "%s/LC_MESSAGES" % dirname
    names = [x for x in os.listdir(path) if x.endswith('po') and not x.startswith('._')]
    for name in names:
        #print "\nchecking", name
        cmd = "msgfmt -C %s/%s" % (path, name)
        stout, stdin, stderr = popen3(cmd)
        err = stderr.read()
        if err:
            problems = list()
            lines = err.split('\n')
            for line in lines:
                if line.strip() == '':
                    continue
                do_print = True
                for patt_ignore in ignore:
                    if patt_ignore.match(line):
                        do_print = False
                        break
                if do_print:
                    problems.append(line)

            if problems:
                print "\n%s/%s" % (path, name)
                print "\n".join(problems)
                houstonwehaveaproblem = True

if houstonwehaveaproblem:
    sys.exit('FAILURE')
