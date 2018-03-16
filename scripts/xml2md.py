#!/usr/bin/env python


"""%(program)s: UPDATE ME.

usage:  %(program)s input.xml output/directory
"""
import base64
import codecs
import os
import random
import re
import sys
import unicodedata

from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from html2text import html2text
from datetime import datetime
from datetime import timedelta
from xml.sax.saxutils import unescape

STATES = ['answered', 'postponed', 'unvisited']
EVALUATION_TYPES = ['risk_calculated', 'risk_estimated', 'risk_direct', 'priority', 'policy']
LOCATIONS = [u'Abby Road', u'Baker Street']

MAX_NUMBER_MODULES = 1
MAX_NUMBER_PROFILES = 2
MAX_NUMBER_SUBMODULES = 3


def usage(stream, msg=None):
    if msg:
        print >> stream, msg
        print >> stream
    program = os.path.basename(sys.argv[0])
    print >> stream, __doc__ % {"program": program}
    sys.exit(0)


def str2filename(text):
    stripped_text = re.sub("[()\[\]{}/.,;:!?]", "", text)
    stripped_text = unicodedata.normalize('NFKD', stripped_text).encode(
        'ascii', 'ignore')
    return stripped_text.lower().replace(" ", "-")


def escape2markdown(text):
    """Convert escaped html to markdown"""
    html = BeautifulStoneSoup(
        text, convertEntities=BeautifulStoneSoup.XML_ENTITIES).text
    return html2text(html)

# Hack to order entries by date
current_date = datetime(2014, 1, 1)

# Hack to enforce the 5 different risk evaluation types on the first risks
risk_counter = 0


def write_md(id, content):
    filename = "{}-{}.md".format(current_date.strftime("%Y-%m-%d"), id)
    global current_date
    current_date += timedelta(days=1)
    file_path = os.path.join(dir_path, filename)
    with codecs.open(file_path, "w", encoding="utf-8") as md_file:
        md_file.write(content)


def increment_number(num):
    """ 2.3.4 -> 2.3.5 """
    num_list = num.split(".")
    incremented_num_list = num_list[:-1] + [str(int(num_list[-1:].pop()) + 1)]
    return ".".join(incremented_num_list)


def _r(t):
    return t.replace('"', '\'')


def create_risk(risk, parent_id=None, number="1"):
    risk_template = u"""---
layout: risk
fid: {id}
classes: {classes}
number: "{number}"
parent_id: {parent_id}
title: "{title}"
problem_description: "{problem_description}"
description: "{description}"
legal_reference: "{legal_reference}"
evaluation_method: {evaluation_method}
measures_in_place:
{measures_in_place}
{image_information}
solutions:
  solution_1:
    description: "Visual inspection of work areas."
    action_plan: "Make sure a visual inspection of work areas is carried out in
                  order to identify the potential hazards of falls and slips.
                  Check that the anti-fall fittings and protective measures are
                  present and in good condition."
---
{body}
""".format

    title = risk.find("title").text
    id = str2filename(title)
    problem_description = _r(risk.find("problem-description").text)
    description = unescape(_r(risk.find("description").text))
    legal_reference_node = risk.find("legal-reference")
    legal_reference = legal_reference_node and unescape(_r(legal_reference_node.text)) or ""
    global risk_counter
    if risk_counter < len(EVALUATION_TYPES):
        evaluation_method = EVALUATION_TYPES[risk_counter]
        state = 'answered'
        risk_class = 'risk'
        print u"Risk {0} with method {1}".format(title, evaluation_method)
    else:
        evaluation_method = random.choice(EVALUATION_TYPES)
        state = random.choice(STATES)
        risk_class = state == 'answered' and random.choice(['risk', '']) or ''
    classes = "{} {}".format(state, risk_class)
    # solutions = risk.find("solutions").text
    # xxx handle the sub solutions
    risk_counter += 1

    images = risk.findAll('image')
    image_data = []
    image_info = u""
    for image in images:
        image_path = os.path.join(media_path, image['filename'])
        image_filename = os.path.join(dir_path, image_path)
        with open(image_filename, 'w') as img_file:
            img_file.write(base64.decodestring(image.contents[0]))
        image_data.append(dict(
            url=u"/{0}".format(image_path),
            caption=image.get('caption', '')))

    if image_data:
        image_info = u"images:\n"
        for entry in image_data:
            image_info += u"    - url: {0}\n".format(entry['url'])
            image_info += u"      caption: {0}\n".format(entry['caption'])

    mip = ""
    existing_measures = _r(risk.find("existing_measures").text)
    if existing_measures:
        # import pdb; pdb.set_trace( )
        for measure in existing_measures.split('\n'):
            if measure.strip():
                mip += u'    - label: "%s"\n      state: checked\n' % (
                    measure.replace('&#13;', ''))

    fields = {
        "id": id,
        "title": title,
        "classes": classes.strip(),
        "number": number,
        "parent_id": parent_id,
        "module": "\nmodule: {}".format(parent_id) if parent_id else "",
        "description": description,
        "problem_description": problem_description,
        "legal_reference": legal_reference,
        "evaluation_method": evaluation_method,
        "body": html2text(description),
        "measures_in_place": mip,
        "image_information": image_info,
    }

    content = risk_template(**fields)
    write_md(id, content)


def create_module(module, parent_id=None, number="1"):
    module_template = u"""---
layout: module
fid: {id}
number: "{number}"
parent_id: {parent_id}
title: {title}{module}
{image_information}
---
{body}
""".format

    title = module.find("title").text
    id = str2filename(title)
    description = module.find("description").text

    images = module.findAll('image')
    image_info = ""
    if images:
        image_path = os.path.join(media_path, images[0]['filename'])
        image_filename = os.path.join(dir_path, image_path)
        with open(image_filename, 'w') as img_file:
            img_file.write(base64.decodestring(images[0].contents[0]))
        image_info = u"images:\n    - url: /{0}\n      caption: {1}\n".format(
            image_path, images[0].get('caption', ''))

    fields = {
        "id": id,
        "title": title,
        "number": number + '.0',
        "parent_id": parent_id,
        "module": "\nmodule: {}".format(parent_id) if parent_id else "",
        "body": escape2markdown(description),
        "image_information": image_info,
    }

    content = module_template(**fields)
    write_md(id, content)

    sub_modules = module.findChildren("module", recursive=False)
    sub_number = number + ".1"
    sub_id = parent_id and "{0}-{1}".format(parent_id, id) or id
    sub_count = 0
    for sub_module in sub_modules:
        create_module(sub_module, parent_id=sub_id, number=sub_number)
        sub_number = increment_number(sub_number)
        sub_count += 1
        if sub_count >= MAX_NUMBER_SUBMODULES:
            break

    risks = module.findChildren("risk", recursive=False)
    risk_number = number + ".1"
    for risk in risks:
        create_risk(risk, parent_id=sub_id, number=risk_number)
        risk_number = increment_number(risk_number)


def create_location(location_number, location_name, parent_id):
    id = str2filename(location_name)
    content = u"""---
layout: location
fid: {fid}
number: {location_number}
title: {location_name}
parent_id: {parent_id}
---
""".format(
        location_name=location_name,
        location_number=location_number,
        parent_id=parent_id,
        fid=id)
    write_md(id, content)


def create_profile_question(profile_question, number="1", locations=[]):
    question_template = u"""---
layout: profile
fid: {id}
number: "{number}"
title: {title}{images}
---

{body}

""".format

    title = profile_question.find("title").text
    id = str2filename(title)
    description = profile_question.find("description").text

    fields = {
        "id": id,
        "title": title,
        "number": len(locations) and "{0}.0.0.0".format(number) or "{0}.0.0".format(number),
        "images": "",
        "body": escape2markdown(description),
    }

    content = question_template(**fields)
    write_md(id, content)

    sub_modules = profile_question.findChildren("module", recursive=False)
    if len(locations):
        for i in range(len(locations)):
            location_number = "{0}.{1}.0.0".format(number, i + 1)
            create_location(location_number, locations[i], parent_id=id)
            sub_number = "{0}.{1}.1".format(number, i + 1)
            location_id = "{0}-{1}".format(id, str2filename(locations[i]))
            sub_count = 0
            for sub_module in sub_modules:
                create_module(sub_module, parent_id=location_id, number=sub_number)
                sub_number = increment_number(sub_number)
                sub_count += 1
                if sub_count >= MAX_NUMBER_SUBMODULES:
                    break
    else:
        sub_number = number + ".1"
        sub_count = 0
        for sub_module in sub_modules:
            create_module(sub_module, parent_id=id, number=sub_number)
            sub_number = increment_number(sub_number)
            sub_count += 1
            if sub_count >= MAX_NUMBER_SUBMODULES:
                break


if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage(sys.stderr, "\nNot enough arguments")
    input = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    with open(input, 'r') as xml:
        soup = BeautifulSoup(xml.read())

    survey = soup.find("survey")
    survey_title = survey.find("title").text
    survey_id = str2filename(survey_title)
    dir_path = os.path.join(output_dir, survey_id)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    media_path = os.path.join('media', survey_id)
    media_file_path = os.path.join(dir_path, media_path)
    if not os.path.exists(media_file_path):
        os.makedirs(media_file_path)

    number = 1
    profile_number = 1

    profile_questions = survey.findChildren("profile-question",
                                            recursive=False)
    for profile_question in profile_questions:
        # Let X modules be enough
        if MAX_NUMBER_PROFILES and number > MAX_NUMBER_PROFILES:
            break
        print "Export Profile Question '{0}'".format(profile_question.title.text)
        if profile_number > 1:
            create_profile_question(profile_question, number=str(number), locations=LOCATIONS)
        else:
            create_profile_question(profile_question, number=str(number))
        number += 1
        profile_number += 1

    modules = survey.findChildren("module", recursive=False)
    for module in modules:
        # Let X modules be enough
        if MAX_NUMBER_MODULES and number > (MAX_NUMBER_MODULES + MAX_NUMBER_PROFILES):
            break
        print u"Export Module '{0}'".format(module.title.text)
        create_module(module, number=str(number))
        number += 1
