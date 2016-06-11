#!/usr/bin/env zopepy

# Author: Wolfgang Thomas <thomas@syslab.com>

# The methods wrap_str and wrap_list have been copied from word_wrap.py,
# which has the following Copyright:

#    Copyright (c) 2001 Alan Eldridge. All rights reserved.
#    Alan Eldridge 2001-09-16 alane@wwweasel.geeksrus.net
#    $Id: word_wrap.py,v 1.4 2001/10/14 05:04:37 alane Exp $
#    2001-09-16 alane@wwweasel.geeksrus.net

"""%(program)s: Strip the image tags from an exported OiRA survey and save it
agan. Additionally export a text-only version for word counting. Please refer
to the code for additional options.

usage:  %(program)s input.xml output.xml raw_text.txt
input.xml           The filename of the exported survey
input_stripped.xml  The filename for the stripped version
output.xml          The filename for the converted survey
raw_text.txt        The filename for the text-only file
"""

import re
import os
import string
import sys

from bs4 import BeautifulSoup


def usage(stream, msg=None):
    if msg:
        print >> stream, msg
        print >> stream
    program = os.path.basename(sys.argv[0])
    print >> stream, __doc__ % {"program": program}
    sys.exit(0)


def setString(entity, txt):
    entity.clear()
    entity.append(txt)


def wrap_str(str, max):
    ll = []
    lines = string.split(str, '\n')
    if len(lines) > 1:
        return wrap_list(lines, max)
    words = string.split(lines[0])
    for i in range(len(words)):
        if len(words[i]) == 0:
            del words[i]
    while len(words):
        cc = 0
        cw = 0
        for w in words:
            tmp = (cc > 0) + cc + len(w)
            if tmp > max:
                break
            cc = tmp
            cw = cw + 1
        if cw == 0:
            # must break word in middle
            ll.append(words[cw][:max - 1] + '+')
            words[cw] = words[cw][max - 1:]
        else:
            ll.append(string.join(words[:cw]))
            words = words[cw:]
    return ll


def wrap_list(lines, max):
    ll = []
    for l in lines:
        if len(ll):
            ll.append('')
        ll = ll + wrap_str(l, max)
    return ll


if len(sys.argv) < 4:
    usage(sys.stderr, "\nNot enough arguments")
input = sys.argv[1]
input_stripped = sys.argv[2]
output = sys.argv[3]
txtfile = sys.argv[4]

fh = open(input, 'r')
data = fh.read()
fh.close()

soup = BeautifulSoup(data, 'xml')


# Special requirement: Strip all legal references
legalrefs = soup.find_all('legal-reference')
print "We have %d legal references" % len(legalrefs)
extracted = [legalref.extract() for legalref in legalrefs]
if len(extracted):
    # For some weird reason, images are not found any more after this step
    # => Make a fresh soup
    soup = BeautifulSoup(unicode(soup), 'xml')

# Special requirement: Strip section EN SAVOIR PLUS
patt = re.compile(u'<(p|strong|li)>\s*EN SAVOIR PLUS\s*:*\?*\s*<.*')
tags = ['description', 'solution-direction']
for tag in tags:
    entities = soup.find_all(tag)
    [setString(entity, patt.sub(u"", entity.text)) for entity in entities]


fh = open(input_stripped, 'w')
fh.write(soup.encode('utf-8'))
fh.close()


images = soup.find_all('image')
print "We have %d images" % len(images)
extracted = [img.extract() for img in images]
if len(extracted):
    soup = BeautifulSoup(unicode(soup), 'xml')

fh = open(output, 'w')
fh.write(soup.encode('utf-8'))
fh.close()

# Some tags of the survey contain only functional information, such
# as true/false or calculated/evaluated
# Strip them for the word counting
functional_tags = (
    'evaluation-method', 'evaluation-algorithm', 'language',
    'show-not-applicable', 'classification-code', 'evaluation-optional')
for tag in functional_tags:
    entities = soup.find_all(tag)
    extracted = [entity.extract() for entity in entities]
    if len(extracted):
        soup = BeautifulSoup(unicode(soup), 'xml')

# formatter=None means HTML entities are rendered as HTML tags
text = soup.prettify(formatter=None)

# remove all tags
TAG = re.compile(u"<.*?>")
text = TAG.sub(u" ", text)

# condense whitespaces
WHITESPACE = re.compile(u"\s+")
text = WHITESPACE.sub(u" ", text)
INTERPUNCTUATION = re.compile(u"\s+[.|,|;|:]\s+")
text = INTERPUNCTUATION.sub(u" ", text)
# wrap text into lines of max 80 characters
text = u"\n".join(wrap_str(text, 80))

fh = open(txtfile, 'w')
fh.write(text.encode('utf-8'))
fh.close()

sys.exit('ok')
