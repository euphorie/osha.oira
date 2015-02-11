#!/usr/bin/env python

# Author: Wolfgang Thomas <thomas@syslab.com>

"""%(program)s: Strip the image tags from an exported OiRA survey and save it
agan. Additionally export a text-only version for word counting. Please refer
to the code for additional options.

usage:  %(program)s input.xml output/directory
"""
import codecs
import os
import sys
import re

from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from html2text import html2text


def usage(stream, msg=None):
    if msg:
        print >> stream, msg
        print >> stream
    program = os.path.basename(sys.argv[0])
    print >> stream, __doc__ % {"program": program}
    sys.exit(0)


def str2filename(text):
    stripped_text = re.sub("[()\[\]{}/.,;:!?]", "", text)
    return stripped_text.lower().replace(" ", "-")


def escape2markdown(text):
    """Convert escaped html to markdown"""
    html = BeautifulStoneSoup(
        text, convertEntities=BeautifulStoneSoup.XML_ENTITIES).text
    return html2text(html)


def write_md(id, content):
    filename = "2015-01-01-{}.md".format(id)
    file_path = os.path.join(dir_path, filename)
    with codecs.open(file_path, "w", encoding="utf-8") as md_file:
        md_file.write(content)


def create_module(module, parent_id=None):
    module_template = u"""---
layout: module
title: {title}{module}
---
{body}
""".format

    title = module.find("title").text
    id = str2filename(title)
    description = module.find("description").text

    fields = {
        "title": title,
        "module": "\nmodule: {}".format(parent_id) if parent_id else "",
        "body": escape2markdown(description),
    }

    content = module_template(**fields)
    write_md(id, content)

    sub_modules = module.findChildren("module", recursive=False)
    for sub_module in sub_modules:
        create_module(sub_module, parent_id=id)


def create_profile_question(profile_question):
    question_template = u"""---
layout: question
title: {title}{images}
---

{body}

""".format

    title = profile_question.find("title").text
    id = str2filename(title)
    description = profile_question.find("description").text

    fields = {
        "title": title,
        "images": "",
        "body": escape2markdown(description),
    }

    content = question_template(**fields)
    write_md(id, content)

    sub_modules = profile_question.findChildren("module", recursive=False)
    for sub_module in sub_modules:
        create_module(sub_module, parent_id=id)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage(sys.stderr, "\nNot enough arguments")
    input = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    with open(input, 'r') as xml:
        soup = BeautifulSoup(xml.read())

    # TODO: write the imgs to files
    images = soup.findAll('image')
    print "We have %d images" % len(images)
    [img.extract() for img in images]

    survey = soup.find("survey")
    survey_title = survey.find("title").text
    dir_path = os.path.join(output_dir, str2filename(survey_title))
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    profile_questions = survey.findChildren("profile-question", recursive=False)
    for profile_question in profile_questions:
        create_profile_question(profile_question)

    modules = survey.findChildren("module", recursive=False)
    for module in modules:
        create_module(module)
