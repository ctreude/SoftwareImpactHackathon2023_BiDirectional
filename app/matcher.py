import re
import glob
import logging
import json
import os
import csv
from .merger import Merger

logger = logging.getLogger("Matcher")

GITHUB_REGEX = r"^(?=.*https:\/\/github\.com\/([a-zA-Z0-9-]+)\/([a-zA-Z0-9_.-]+))(?=.*(?:code|data|script)).*$|^(?=.*https:\/\/github\.com\/([a-zA-Z0-9-]+)\/([a-zA-Z0-9_.-]+)).*$\n^.*(?:code|data|script).*$|^.*(?:code|data|script).*$\n(?=.*https:\/\/github\.com\/([a-zA-Z0-9-]+)\/([a-zA-Z0-9_.-]+)).*"
ZENODO_REGEX = r"^(?=.*https:\/\/(doi\.org\/10\.5281\/zenodo\.\d+|zenodo\.org\/record\/\d+))(?=.*(?:code|data|script)).*$|^(?=.*https:\/\/(doi\.org\/10\.5281\/zenodo\.\d+|zenodo\.org\/record\/\d+)).*$\n^.*(?:code|data|script).*$|^.*(?:code|data|script).*$\n(?=.*https:\/\/(doi\.org\/10\.5281\/zenodo\.\d+|zenodo\.org\/record\/\d+)).*"
GITHUB_URL_REGEX = r"https?://github.com/([a-zA-Z0-9-]+)/([a-zA-Z0-9_.-]+)"
ZENODO_URL_REGEX = r"https?://zenodo.org/records?/([a-zA-Z0-9_.-]+)"
ZENODO_DOI_URL_REGEX = r"https:\/\/doi\.org\/10\.\d+\/[a-zA-Z0-9\._%~-]+"
ARXIV_ID_REGEX = r"/(\d+\.\d+)(?:v\d+)/"


def has_github_link(content):
    return re.search(GITHUB_REGEX, content, re.M)


def has_zenodo_link(content):
    return re.search(ZENODO_REGEX, content, re.M)


class TwoWaysMatcher:
    def __init__(self, zenodo, github):
        self._zenodo = zenodo
        self._github = github
        self._merger = Merger()

    def run(self):
        results_with_code = dict()
        results_without_code = set()

        # self._merger.run("sources")

        merged_filepaths = os.path.join("sources", "**", "merged.tex")
        for filepath in glob.glob(merged_filepaths, recursive=True):
            logger.info(f"Working on `{filepath}`")

            arxiv_id = re.search(ARXIV_ID_REGEX, filepath)[1]
            ARXIV_URL_REGEX = f"arxiv.org/[^/]+/{arxiv_id}"

            with open(filepath) as fp:
                text = fp.read()

                github_matched = has_github_link(text)
                zenodo_matched = has_zenodo_link(text)

                if not (github_matched or zenodo_matched):
                    results_without_code.add(filepath)
                    continue

                results_with_code.setdefault(filepath, dict())
                if github_matched:
                    paragraph = github_matched[0]
                    url = re.search(GITHUB_URL_REGEX, paragraph, re.M)[0]
                    logger.info(f"GitHub link: {url}")
                    try:
                        (
                            description,
                            readme,
                            correct_url,
                        ) = self._github.get_description_readme(url)
                    except ValueError:
                        # skip if not valid GitHub repo
                        continue

                    results = results_with_code[arxiv_id]
                    results["github"] = "Found"
                    results["github_url"] = correct_url

                    has_arxiv = re.search(
                        ARXIV_URL_REGEX, description.lower()
                    ) or re.search(ARXIV_URL_REGEX, readme.lower())
                    if has_arxiv:
                        results["arxiv in GitHub"] = "Found"
                        logger.info(f"{filepath}: found arxiv link in GitHub")
                    else:
                        results["arxiv in GitHub"] = "Missing"
                        logger.info(f"{filepath}: not found arxiv link in GitHub")
                else:
                    results["github"] = "Missing"

                if zenodo_matched:
                    paragraph = zenodo_matched[0]
                    # try with Zenodo URL
                    match = re.search(ZENODO_URL_REGEX, paragraph, re.M)
                    if not match:
                        # try with Zenodo DOI
                        match = re.search(ZENODO_DOI_URL_REGEX, paragraph, re.M)

                    url = match[0]
                    logger.info(f"Zenodo link: {url}")
                    record_text, correct_url = self._zenodo.get_record(url)

                    results["zenodo"] = "Found"
                    results["zenodo_url"] = correct_url

                    has_arxiv = re.search(ARXIV_URL_REGEX, record_text.lower())
                    if has_arxiv:
                        results["arxiv in Zenodo"] = "Found"
                        logger.info(f"{filepath}: found arxiv link in Zenodo")
                    else:
                        results["arxiv in Zenodo"] = "Missing"
                        logger.info(f"{filepath}: not found arxiv link in Zenodo")
                else:
                    results["zenodo"] = "Missing"

        self._github.close()

        logger.info(f"No code: {results_without_code}")

        # Dump to a CSV file
        with open("results.csv", mode="w", newline="") as file:
            writer = csv.writer(file)

            # Write the header row
            header = [
                "ArXiV id",
                "Contains GitHub URL",
                "GitHub URL",
                "GitHub repo contains ArXiV URL",
                "Contains Zenodo URL",
                "Zenodo URL",
                "Zenodo record contains ArXiV URL",
            ]
            writer.writerow(header)

            # Write data for each key-value pair in the dictionary
            for key, values in results_with_code.items():
                row = [key]
                row.extend(values.values())
                writer.writerow(row)
