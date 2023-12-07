import logging
import re
import time

from enums import Repos

logger = logging.getLogger("Pub link finder")

ARXIV_URL_REGEX = "arxiv.org/[^/]+/{arxiv_id}"


class PubFinder:
    """Find publication URLs in repos."""

    def __init__(self, github, zenodo):
        self._github_apis = github
        self._zenodo_apis = zenodo
        self._rate_limiter_sleep = 0.1  # 100 milliseconds

    def _github(self, publication_id, _id):
        org, repo = _id
        try:
            (
                description,
                readme,
                correct_url,
            ) = self._github_apis.get_description_readme(org, repo)
        except ValueError:
            # skip if not valid GitHub repo
            return ""

        return description.lower() + readme.lower(), correct_url

    def _zenodo(self, publication_id, _id):
        recid_or_doi = _id
        if zenodo_record := self._zenodo_apis.get_record(recid_or_doi):
            record_text, correct_url = zenodo_record
            return record_text, correct_url
        logging.error("_zenodo: Zenodo API has returned a Non-usable value")
        return "", ""

    def find(self, publication_id, repo_ids):
        """Find publication URL in repos metadata or files."""
        results = {}
        if not repo_ids:
            logging.error(f"pub_finder_find Error: no ID's given for repos: '{repo_ids}'.")
            return results
        if not publication_id:
            logging.error("pub_finder_find Error: The publication ID is empty or None.")
            return results

        arxiv_url = ARXIV_URL_REGEX.format(arxiv_id=publication_id)
        for repo, ids in repo_ids.items():
            if repo == Repos.GITHUB.value:
                func = self._github
            elif repo == Repos.ZENODO_RECORD.value:
                func = self._zenodo
            elif repo == Repos.ZENODO_DOI.value:
                func = self._zenodo
            else:
                logger.error(f"Finder for {repo} not implemented.")
                continue

            results.setdefault(repo, {})
            for _id in ids:
                content, correct_url = func(publication_id, _id)
                has_arxiv_url = re.search(arxiv_url, content.lower(), re.M | re.I)
                if has_arxiv_url:
                    results[repo][_id] = "Found"
                    logger.info(f"ArXiV id {publication_id} found in {repo}: {_id} ({correct_url})")
                else:
                    results[repo][_id] = "Not found"
                    logger.debug(f"ArXiV id {publication_id} not found in {repo}: {_id} ({correct_url})")
                time.sleep(self._rate_limiter_sleep)

        return results
