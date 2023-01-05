from lxml import etree
from pkg_resources import resource_exists
from pkg_resources import resource_stream
from plone import api
from plone.namedfile.file import NamedBlobImage
from tempfile import TemporaryDirectory
from urllib.parse import unquote

import logging
import requests
import urllib.request


BASE_URL = "https://oiraproject.eu"

log = logging.getLogger(__name__)


def map_images(context):
    portal = api.portal.get()
    wt = api.portal.get_tool("portal_workflow")
    for page_num in range(26):
        url = "{}/en/oira-tools?search_api_fulltext=&sort_by=title" "&page={}".format(
            BASE_URL, page_num
        )
        page = requests.get(url).text
        tree = etree.HTML(page)
        for elem in tree.findall(".//div[@class='views-field views-field-nothing']"):
            link = elem.find(".//div[@class='tool-link']/a")
            if link is not None:
                path = "/".join(unquote(link.attrib["href"]).strip().split("/")[-3:])
            else:
                continue

            try:
                surveygroup = portal.unrestrictedTraverse(
                    "/".join(("/Plone2/sectors", path))
                )
            except KeyError:
                log.warning(f"Tool not found: {path}")
                continue

            img = elem.find(".//div[@class='views-field views-field-field-image']/img")
            if img is None:
                log.warning(f"No image for {path}")
                continue
            sourcename = img.attrib["src"].split("/")[-1]
            basename = unquote(sourcename.split(".")[0]).strip()
            if " " in basename:
                name = " ".join([part for part in basename.split(" ")[:-1]])
            else:
                name = basename
            filename = f"{name} 300.png"
            blob_image = None
            if not resource_exists(
                "osha.oira.data", "/".join(("OiRA-Icons", filename))
            ):
                log.warning(
                    "Image file not found: {} ({}). Attempting download".format(
                        filename, sourcename
                    )
                )
                with TemporaryDirectory(prefix="euphorieimage") as tmpdir:
                    temp_file_path = f"{tmpdir}/{filename}"
                    urllib.request.urlretrieve(  # nosec # TODO
                        "{}{}".format(BASE_URL, img.attrib["src"]),
                        temp_file_path,
                    )
                    try:
                        with open(temp_file_path, "rb") as imagefile:
                            blob_image = NamedBlobImage(
                                data=imagefile.read(), filename=filename
                            )
                    except Exception as e:
                        log.warning(
                            f"Unable to download image from website. Error: {e}"
                        )
                        continue
            else:
                with resource_stream(
                    "osha.oira.data", "/".join(("OiRA-Icons", filename))
                ) as imagefile:
                    blob_image = NamedBlobImage(
                        data=imagefile.read(), filename=filename
                    )

            if not blob_image:
                continue
            for survey in surveygroup.values():
                if getattr(survey, "image", None):
                    # log.warning("Already has image: {}".format(path))
                    continue
                else:
                    setattr(survey, "image", blob_image)

                if getattr(surveygroup, "published", None) == survey.getId():
                    try:
                        wt.doActionFor(survey, "update")
                    except Exception as e:
                        log.exception(e)
                        continue
