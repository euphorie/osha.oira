#!/usr/bin/env python

# Author: Wolfgang Thomas <thomas@syslab.com>

"""%(program)s: Escape HTML inside XML tags (in case the translators were
    too stupid to use an XML-capable editor).

usage:  %(program)s input.xml output.xml
input.xml    The filename of the exported survey
output.xml   The filename for the fixed survey
"""

# from BeautifulSoup import BeautifulStoneSoup
from BeautifulSoup import BeautifulSoup
from BeautifulSoup import Tag
from xml.sax.saxutils import escape

import os
import sys


PLACEHOLDER = "XXXXX"


def usage(stream, msg=None):
    if msg:
        print(msg, file=stream)
        print("\n", file=stream)
    program = os.path.basename(sys.argv[0])
    print(__doc__ % {"program": program}, file=stream)
    sys.exit(0)


if len(sys.argv) < 3:
    usage(sys.stderr, "\nNot enough arguments")
input = sys.argv[1]
output = sys.argv[2]

fh = open(input)
data = fh.read()
fh.close()

soup = BeautifulSoup(data)

# stonesoup = BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.XML_ENTITIES)


tags = [
    "title",
    "solution-direction",
    "description",
    "problem-description",
    "action-plan",
    "legal-reference",
    "introduction",
]

for tag in tags:
    entities = soup.findAll(tag)
    for entity in entities:
        contents = []
        for line in entity.contents:
            if isinstance(line, Tag):
                txt = escape(line.prettify()).decode("utf-8")
            else:
                txt = line.string
            txt = txt.strip()
            contents.append(txt)
        entity.setString("".join(contents))


fh = open(output, "w")
fh.write(soup.renderContents())
fh.close()


sys.exit("ok")
