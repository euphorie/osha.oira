from functools import cached_property
from lxml import etree
from pathlib import Path
from plone import api
from plone.namedfile.file import NamedBlobImage
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five import BrowserView
from urllib.parse import unquote
from urllib.parse import urlencode
from urllib.parse import urlparse
from zope.interface import alsoProvides

import logging
import os
import requests

log = logging.getLogger(__name__)


class MapImages(BrowserView):
    """This used to be a buildout script, see:

    https://github.com/EU-OSHA/oira.application.buildout/blob/f75c33a3db968bcb1b2ffa68b3ca4a66b396a6d4/scripts/map_images.py
    """  # noqa: E501

    # The URL of the site we are fetching the images from.
    BASE_URL = "https://oira.osha.europa.eu"

    # After this many pages of the tool listing, we stop. Currently we have 38 pages.
    page_limit = 255
    tool_xpath = ".//div[@class='views-field views-field-nothing']"
    link_xpath = ".//div[@class='button-risk']/a"
    img_xpath = ".//div[@class='content-view-oira-tools-view']/img"

    @cached_property
    def images_path(self) -> Path:
        """Directory to cache the downloaded images.

        It will look like this: var/instanceN/oira_images
        """
        images_path = Path(os.environ["CLIENT_HOME"]) / "oira_images"
        images_path.mkdir(exist_ok=True)
        return images_path

    def get_filename(self, img: etree._Element) -> str:
        """Derive a filename from the image URL.

        We expect the src path to be something like
        /sites/oira_revamp/files/styles/media_library/public/$NAME.{jpg,png}?itok=$ITOK
        whatever ITOK is.

        We want to extract $NAME and use it as the filename, with ` 300.png` appended.
        """
        sourcename = urlparse(img.attrib["src"]).path.split("/")[-1]
        basename = unquote(sourcename.split(".")[0]).strip()
        if " " in basename:
            name = " ".join([part for part in basename.split(" ")[:-1]])
        else:
            name = basename
        filename = f"{name} 300.png"
        return filename

    def get_tool_path(self, elem: etree._Element) -> str | None:
        """Extract the tool path from the element's link.

        Finds the link element with class "button-risk" and extracts the path
        from its href attribute.

        Returns the path as a string with format
        "eu/eu-horeca/oira-horeca", or None if no link is found.

        We take care to strip any query parameters and unquote the URL.

        We only take the last three segments of the path,
        as the URL may contain additional segments that are
        not part of the tool path.
        """
        link = elem.find(self.link_xpath)
        if link is None:
            return

        path = "/".join(
            urlparse(unquote(link.attrib["href"]))
            .path.strip()
            .rstrip("/")
            .split("/")[-3:]
        )
        return path

    def get_remote_tools(self, page: int) -> list[etree._Element]:
        """Fetch the tool listing page and return the elements
        corresponding to the tools.

        Returns a list of lxml elements, each representing a tool on the page.
        """
        params = urlencode(
            {"search_api_fulltext": "", "sort_by": "title", "page": f",{page}"}
        )
        url = f"{self.BASE_URL}/en/oira-tools?{params}"
        log.info("Scanning %s", url)
        page = requests.get(url).text
        tree = etree.HTML(page)
        tool_elements = tree.findall(self.tool_xpath)
        return tool_elements

    def get_image_blob(self, elem: etree._Element, path: str) -> NamedBlobImage | None:
        """Extract the image from the tool element, download it if necessary,
        and return it as a NamedBlobImage.
        """
        img = elem.find(self.img_xpath)
        if img is None:
            log.warning("No image for %r", path)
            return

        # Get the filename and look for it in the cache. If it's not there,
        # download it and save it to the cache.
        filename = self.get_filename(img)
        filepath = self.images_path / filename

        if not filepath.exists():
            log.warning(
                "%r: Image file not found: %r (%r). Attempting download",
                path,
                filepath,
                img.attrib["src"],
            )
            try:
                filepath.write_bytes(
                    requests.get(f"{self.BASE_URL}{img.attrib['src']}").content
                )
            except Exception as e:
                log.warning("Unable to download image from website. Error: %s", e)
                return

        try:
            return NamedBlobImage(data=filepath.read_bytes(), filename=filename)
        except Exception as e:
            log.warning("Unable to open image. Error: %s", e)

    def __call__(self):
        portal = api.portal.get()
        sectors = portal.sectors
        wt = api.portal.get_tool("portal_workflow")

        log.info("Updating tool images")
        # We iterate over the pages of the tool listing,
        # until we find a page with no tools on it.
        for page_num in range(self.page_limit):
            tool_elements = self.get_remote_tools(page_num)
            if not tool_elements:
                log.info(f"Stopping at page {page_num} (no more tools found)")
                break

            for elem in tool_elements:
                path = self.get_tool_path(elem)
                if path is None:
                    log.warning("No link found for tool element, skipping")
                    continue

                try:
                    surveygroup = sectors.unrestrictedTraverse(path)
                except KeyError:
                    log.warning(f"Tool not found: {path}")
                    continue

                if all(
                    getattr(survey, "image", None) for survey in surveygroup.values()
                ):
                    log.info(f"Already has image: {path}")
                    continue

                blob_image = self.get_image_blob(elem, path)
                if blob_image is None:
                    log.warning(f"No image found for tool: {path}")
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
