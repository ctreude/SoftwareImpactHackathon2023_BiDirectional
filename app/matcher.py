import re
import glob
import logging
import json

logger = logging.getLogger("Matcher")

GITHUB_REGEX = r"^(?=.*https:\/\/github\.com\/\w+\/\w+)(?=.*(?:code|data|script)).*$|^(?=.*https:\/\/github\.com\/\w+\/\w+).*$\n^.*(?:code|data|script).*$|^.*(?:code|data|script).*$\n(?=.*https:\/\/github\.com\/\w+\/\w+).*"
ZENODO_REGEX = r"^(?=.*https:\/\/(doi\.org\/10\.5281\/zenodo\.\d+|zenodo\.org\/record\/\d+))(?=.*(?:code|data|script)).*$|^(?=.*https:\/\/(doi\.org\/10\.5281\/zenodo\.\d+|zenodo\.org\/record\/\d+)).*$\n^.*(?:code|data|script).*$|^.*(?:code|data|script).*$\n(?=.*https:\/\/(doi\.org\/10\.5281\/zenodo\.\d+|zenodo\.org\/record\/\d+)).*"
URL_REGEX = r"http(s)?://[^\s]+"


def has_github_link(content):
    return re.search(GITHUB_REGEX, content, re.M)


def has_zenodo_link(content):
    return re.search(ZENODO_REGEX, content, re.M)


def get_url(content):
    return re.search(URL_REGEX, content)[0]


class TwoWaysMatcher:
    def __init__(self, zenodo, github):
        self._zenodo = zenodo
        self._github = github

    def _get_sources(self):
        return glob.glob("./sources/**/*.tex", recursive=True)

    def run(self):
        results = dict()
        for filepath in self._get_sources():
            results.setdefault(filepath, dict(has_code=False, github=None, zenodo=None))
            logger.info(f"Working on `{filepath}`")
            with open(filepath) as fp:
                text = fp.read()

                github_matched = has_github_link(text)
                zenodo_matched = has_zenodo_link(text)

                if github_matched or zenodo_matched:
                    results[filepath]["has_code"] = True

                # if github_matched:
                #     url = get_url(match[0])
                #     repo = self._github.get_repo(url)

                if zenodo_matched:
                    url = get_url(zenodo_matched[0])
                    record_text = self._zenodo.get_record(url)
                    has_arxiv = "arxiv.org" in record_text.lower()

                    if has_arxiv:
                        results[filepath]["zenodo"] = "Found"
                        results[filepath]["zenodo_url"] = "Found"
                        logger.info(f"{filepath}: found arxiv link")
                    else:
                        results[filepath]["zenodo"] = "Missing"
                        logger.info(f"{filepath}: not found arxiv link")

        self._github.close()

        logger.info(json.dumps(results, indent=4)
)
