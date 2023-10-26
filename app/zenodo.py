import requests
import logging
import re

from .doi import get_redirect_url
from .utils import is_valid_url

logger = logging.getLogger("ZenodoAPI")


class ZenodoAPI:
    def __init__(self):
        self.base_url = "https://zenodo.org/api/records"

    def _get_record(self, recid):
        url = f"{self.base_url}/{recid}"
        logger.debug(f"Final URL: `{url}`")
        return requests.get(url).text, url

    def get_record(self, url_or_doi):
        logger.debug(f"Fetching Zenodo record metadata for `{url_or_doi}`")
        is_doi = "doi.org" in url_or_doi
        if is_doi:
            try:
                record_url = get_redirect_url(url_or_doi)
            except (ValueError, RuntimeError):
                logger.error(f"error with url: `{url_or_doi}`. Skipping...")
                return
        else:
            if not is_valid_url(url_or_doi):
                logger.error(f"error with url: `{url_or_doi}`. Skipping...")
                return
            record_url = url_or_doi

        match = re.search(r"[0-9]+", record_url)
        # fail if no match, it should not happen
        recid = match.group(0)
        return self._get_record(recid)
