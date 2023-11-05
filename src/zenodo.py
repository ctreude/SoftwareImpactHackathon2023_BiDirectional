import logging
import re

import requests

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

    def get_record(self, recid_or_doi):
        logger.debug(f"Fetching Zenodo record metadata for `{recid_or_doi}`")
        is_doi = "doi.org" in recid_or_doi
        if is_doi:
            try:
                record_url = get_redirect_url(recid_or_doi)
                match = re.search(r"[0-9]+", record_url)
                # fail if no match, it should not happen
                recid = match.group(0)
            except (ValueError, RuntimeError):
                logger.error(f"error with url: `{recid_or_doi}`. Skipping...")
                return
        else:
            recid = recid_or_doi

        return self._get_record(recid)
