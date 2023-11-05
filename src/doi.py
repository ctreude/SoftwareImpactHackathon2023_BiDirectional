import logging
import re

import requests

from .utils import is_valid_url

logger = logging.getLogger("DOI")

DOI_REGEX = r"^10\.\d{4,9}/[-._;()/:A-Z0-9]+$"
DOI_URL_REGEX = r"https?:\/\/doi\.org\/10.5281/zenodo.[0-9]+"


def is_valid_doi(doi):
    # Use re.match to check if the input matches the pattern
    if re.match(DOI_REGEX, doi, re.I):
        return True
    else:
        return False


def get_valid_url(doi_url):
    match = re.search(DOI_URL_REGEX, doi_url)
    # fails if invalid
    return match.group(0)


def get_redirect_url(doi):
    """Given a DOI or a URL of a DOI, returns the redirect URL."""
    if is_valid_doi(doi):
        doi_url = f"https://doi.org/{doi}"
    elif is_valid_url(doi):
        doi_url = get_valid_url(doi)
    else:
        error_msg = f"Not a valid DOI: {doi}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    try:
        logger.debug(f"Resolving DOI for `{doi_url}`")
        response = requests.get(doi_url, allow_redirects=False)

        logger.debug(f"DOI response: `{response.text}`")

        # Check if the response has a 'Location' header
        if "Location" in response.headers or "location" in response.headers:
            location = response.headers.get("Location") or response.headers.get(
                "location"
            )
            logger.debug(f"Response: {location}")
            return location
        else:
            error_msg = f"No 'Location' header found in the response for DOI {doi}."
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    except requests.exceptions.RequestException as e:
        error_msg = f"An error occurred: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
