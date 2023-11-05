"""Find URLs in a given text."""

import logging
import re

from enums import Repos

logger = logging.getLogger("URLs finder")

KEYWORDS = [
    "code",
    "data",
    "script",
    "available",
    "appendix",
    "supplementary",
    "replication",
    "companion",
    "artifact",
    "artefact",
]
URLS_REGEX = [
    (
        Repos.GITHUB.value,
        "https?://(?:www\.)?github\.com/([a-zA-Z0-9]+)/([a-zA-Z0-9]+)",
    ),  # FIXME: review allowed org/repo names in GitHub
    (Repos.ZENODO_RECORD.value, "https?://zenodo\.org/records?/(\d+)"),
    (Repos.ZENODO_DOI.value, "(https?://doi\.org/10\.5281/zenodo\.\d+)"),
    # ADD MORE
]
KEYWORDS_REGEX = r"\b(?:{KEYWORDS})\b"
MAX_DISTANCE_BEFORE_REGEX = r"(?:\s+\S+){{0,{N_WORDS}}}"
URL_MATCH_BEFORE_REGEX = r"{keywords}{max_distance}(?:\s+|){url}"
MAX_DISTANCE_AFTER_REGEX = r"(?:\S+\s+){{0,{N_WORDS}}}"
URL_MATCH_AFTER_REGEX = r"{url}(?:\s+|){max_distance}{keywords}"

class ReposFinder:
    """Find repos URLs in text."""

    def __init__(self, contextualized_words=10):
        self._contextualized_words = contextualized_words

    def _clean_empty_tuples(self, _tuple):
        if type(_tuple) == tuple:
            return tuple(t for t in _tuple if t)
        else:
            return _tuple

    def _find_contextualized(self, publication_id, text):
        results = dict()
        for repo, url_regex in URLS_REGEX:
            results.setdefault(repo, [])
            for max_distance_regex, url_match_regex in [(MAX_DISTANCE_BEFORE_REGEX, URL_MATCH_BEFORE_REGEX), (MAX_DISTANCE_AFTER_REGEX, URL_MATCH_AFTER_REGEX)]:
                regex = url_match_regex.format(
                    max_distance=max_distance_regex.format(N_WORDS=self._contextualized_words),
                    keywords=KEYWORDS_REGEX.format(KEYWORDS="|".join(KEYWORDS)),
                    url=url_regex,
                )
                urls = re.findall(regex, text, re.M | re.I)
                if urls:
                    no_empty_urls = [self._clean_empty_tuples(_tuple) for _tuple in urls]  # keep only non-empty
                    _urls = [str(t) for t in no_empty_urls]  # convert tuples to string
                    logger.debug(
                        f"{publication_id} | {repo}: found URLs `{', '.join(_urls)}`"
                    )
                    results[repo] += no_empty_urls
            if not results[repo]:
                logger.debug(f"{publication_id} | {repo}: no URLs found")
        return results

    def _find_all(self, publication_id, text):
        results = dict()
        for repo, url_regex in URLS_REGEX:
            urls = re.findall(url_regex, text, re.M | re.I)
            if urls:
                _urls = [str(t) for t in urls]  # convert tuples to string
                logger.debug(
                    f"{publication_id} | {repo}: found URLs `{', '.join(_urls)}`"
                )
                results[repo] = urls
            else:
                logger.debug(f"{publication_id} | {repo}: no URLs found")
                results[repo] = []
        return results

    def find(self, publication_id, text, contextualized=False):
        """Find all configured URLs in the given text.

        When contextualized is True, apply heuristics to find only URLs that refer
        to code/dataset of the publication. When False, find all URLs.
        """
        if contextualized:
            return self._find_contextualized(publication_id, text)
        else:
            return self._find_all(publication_id, text)
