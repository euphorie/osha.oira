#!/usr/bin/env python

# Author: Wolfgang Thomas <thomas@syslab.com>

"""%(program)s: Strip the image tags from an exported OiRA survey and save it
agan. Additionally export a text-only version for word counting. Please refer
to the code for additional options.

usage:  %(program)s input.xml output.xml raw_text.txt
input.xml    The filename of the exported survey
output.xml   The filename for the converted survey
raw_text.txt The filename for the text-only file
"""

from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from word_wrap import wrap_str
import os
import re
import sys

PLACEHOLDER = 'XXXXX'


def usage(stream, msg=None):
    if msg:
        print >> stream, msg
        print >> stream
    program = os.path.basename(sys.argv[0])
    print >> stream, __doc__ % {"program": program}
    sys.exit(0)


if len(sys.argv) < 4:
    usage(sys.stderr, "\nNot enough arguments")
input = sys.argv[1]
output = sys.argv[2]
txtfile = sys.argv[3]

fh = open(input, 'r')
data = fh.read()
fh.close()

soup = BeautifulSoup(data)

images = soup.findAll('image')
cnt = len(images)
[img.extract() for img in images]
print "We removed %d images" % cnt

#### # Special requirement: Also strip all legal references
legalrefs = soup.findAll('legal-reference')
cnt = len(legalrefs)
[legalref.extract() for legalref in legalrefs]
print "We removed %d legal references" % cnt

solutiondirections = soup.findAll('solution-direction')
cnt = len(solutiondirections)
[elem.extract() for elem in solutiondirections]
print "We removed %d solution directions" % cnt

# Now, remove all descriptions, but only if their parent is a module or risk...
descriptions = soup.findAll('description')
cnt = 0
for elem in descriptions:
    if elem.parent.name in ('module', 'risk',):
        elem.extract()
        cnt += 1
print "We removed %d descriptions" % cnt

# For all available soultions, only leave the 1st one in
cnt = 0
solutions = soup.findAll('solutions')
for elem in solutions:
    solution = elem.findAll('solution')
    for subelem in solution[1:]:
        subelem.extract()
        cnt += 1
print "We removed %d solutions" % cnt


fh = open(output, 'w')
# fh.write(soup.prettify())
result = str(soup)
# replace multiple newlines by a single newline
result = re.sub(r'(\n)+', '\n', result)
fh.write(result)
fh.close()

# soup.text gives us the complete text without tags. Unfortunately, where tags
#  are removed, no space is inserted. Therefore the last word inside one tag
# will be glued to the first word of the next tag -> bad for word counting.
# Therefore we add a placeholder at the end of every tag's text, to be replaced
# by a space after extraction
tags = (
    'title', 'solution-direction', 'description', 'problem-description',
    'action-plan'
)
for tag in tags:
    entities = soup.findAll(tag)
    [entity.setString('%s %s ' % (entity.text, PLACEHOLDER))
        for entity in entities]

# Some tags of the survey contain only functional information, such
# as true/false or calculated/evaluated
# Strip them for the word counting
functional_tags = ('evaluation-method', 'show-not-applicable')
for tag in functional_tags:
    entities = soup.findAll(tag)
    [entity.extract() for entity in entities]

# The extracted texts contain HTML entities such as &lt;p&gt;
# We need to convert them to real tags to be able to strip them too for
# word counting
text = soup.text.encode('utf-8')
stonesoup = BeautifulStoneSoup(
    text, convertEntities=BeautifulStoneSoup.XML_ENTITIES)

txt = stonesoup.prettify()
newsoup = BeautifulSoup("<html>%s</html>" % txt)

# Repeat the game of stuffing text inside entities for the newly generated tags
html_tags = (
    'a', 'p', 'strong', 'em', 'li', 'td',
)
for tag in html_tags:
    entities = newsoup.findAll(tag)
    [entity.setString('%s %s ' % (entity.text, PLACEHOLDER))
        for entity in entities]

text = newsoup.text.replace("xml version='1.0' encoding='%SOUP-ENCODING%'", '')
text = text.encode('utf-8')
text = text.replace(' " ', ' ')

# make a space character out of the placeholder
text = text.replace(PLACEHOLDER, ' ')


text = "\n".join(wrap_str(text, 80))

fh = open(txtfile, 'w')
fh.write(text)
fh.close()

sys.exit('ok')
