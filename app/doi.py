import re
import logging
from .utils import is_valid_url
import requests

logger = logging.getLogger("DOI")


def is_valid_doi(doi):
    # Define the regex pattern for a valid DOI
    doi_pattern = r"^10\.\d{4,9}/[-._;()/:A-Z0-9]+$"

    # Use re.match to check if the input matches the pattern
    if re.match(doi_pattern, doi, re.IGNORECASE):
        return True
    else:
        return False


def get_valid_url(doi_url):
    doi_url_pattern = r"https:\/\/doi\.org\/10\.\d+\/[a-zA-Z0-9\._%~-]+"
    match = re.search(doi_url_pattern, doi_url)
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

        # Check if the response has a 'Location' header
        if "Location" in response.headers:
            location = response.headers["Location"]
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
