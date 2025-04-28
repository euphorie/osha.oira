from lxml import etree
from plone import api
from plone.namedfile.file import NamedBlobImage
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five import BrowserView
from urllib.parse import unquote
from urllib.parse import urlparse
from zope.interface import alsoProvides

import logging
import os
import requests
import sys
import urllib.request


class MapImages(BrowserView):
    """This used to be a buildout script, see:

    https://github.com/EU-OSHA/oira.application.buildout/blob/f75c33a3db968bcb1b2ffa68b3ca4a66b396a6d4/scripts/map_images.py
    """  # noqa: E501

    def __call__(self):
        log = logging.getLogger(__name__)

        log.info("Updating tool images")
        BASE_URL = "https://oira.osha.europa.eu"

        if len(sys.argv) > 3:
            images_path = os.path.abspath(sys.argv[3])
        else:
            images_path = os.path.abspath(".")

        portal = api.portal.get()
        sectors = portal.sectors
        wt = api.portal.get_tool("portal_workflow")

        def get_filename():
            sourcename = urlparse(img.attrib["src"]).path.split("/")[-1]
            basename = unquote(sourcename.split(".")[0]).strip()
            if " " in basename:
                name = " ".join([part for part in basename.split(" ")[:-1]])
            else:
                name = basename
            filename = f"{name} 300.png"
            return filename

        for page_num in range(255):
            url = (
                "{}/en/oira-tools?search_api_fulltext=&sort_by=title"
                "&page=%2C{}".format(BASE_URL, page_num)
            )
            log.info("Scanning %s", url)
            page = requests.get(url).text
            tree = etree.HTML(page)
            tool_elements = tree.findall(
                ".//div[@class='views-field views-field-nothing']"
            )
            if not tool_elements:
                log.warning(f"Stopping at page {page_num} (no more tools found)")
                break
            for elem in tool_elements:
                link = elem.find('.//div[@class="button-risk"]/a')
                if link is not None:
                    path = "/".join(
                        urlparse(unquote(link.attrib["href"]))
                        .path.strip()
                        .rstrip("/")
                        .split("/")[-3:]
                    )
                else:
                    continue

                try:
                    surveygroup = sectors.unrestrictedTraverse(path)
                except KeyError:
                    log.warning(f"Tool not found: {path}")
                    continue
                if all(
                    getattr(survey, "image", None) for survey in surveygroup.values()
                ):
                    log.warning(f"Already has image: {path}")
                    continue

                img = elem.find(".//div[@class='content-view-oira-tools-view']/img")
                if img is None:
                    log.warning(f"No image for {path}")
                    continue
                filename = get_filename()
                filepath = os.path.join(images_path, filename)
                blob_image = None
                if not os.path.exists(filepath):
                    log.warning(
                        "{}: Image file not found: {} ({}). Attempting download".format(
                            path, filepath, img.attrib["src"]
                        )
                    )
                    try:
                        urllib.request.urlretrieve(
                            "{}{}".format(BASE_URL, img.attrib["src"]),  # nosec B310
                            filepath,
                        )
                    except Exception as e:
                        log.warning(
                            f"Unable to download image from website. Error: {e}"
                        )
                        continue
                try:
                    with open(filepath, "rb") as imagefile:
                        blob_image = NamedBlobImage(
                            data=imagefile.read(), filename=filename
                        )
                except Exception as e:
                    log.warning(f"Unable to open image. Error: {e}")
                    continue

                if not blob_image:
                    continue
                for survey in surveygroup.values():
                    setattr(survey, "image", blob_image)

                    if getattr(surveygroup, "published", None) == survey.getId():
                        try:
                            wt.doActionFor(survey, "update")
                        except Exception as e:
                            log.exception(e)
                            continue

        alsoProvides(self.request, IDisableCSRFProtection)
        return "OK"
