import csv
import glob
import logging
import os
import re
from datetime import datetime

from .errors import LatexMergedNotFound

logger = logging.getLogger("Latex Matcher")

N_WORDS = 10
HIT_WORDS = "code|data|script|available|appendix|supplementary|replication|companion|artifact|artefact"
GITHUB_REGEX = rf"^(?=.*https://(?:www\.)?github\.com/\w+/\w+)(?=(?:\S+\s+){{0,{N_WORDS}}}(?:{HIT_WORDS})).*$|^.*(?:{HIT_WORDS})(?:\S+\s+){{0,{N_WORDS}}}https://github\.com/\w+/\w+.*$|^.*https://github\.com/\w+/\w+(?:\S+\s+){{0,{N_WORDS}}}(?:{HIT_WORDS}).*$"
ZENODO_REGEX = rf"^(?=.*https://(doi\.org/10\.5281/zenodo\.\d+|zenodo\.org/record/\d+))(?=(?:\S+\s+){{0,{N_WORDS}}}(?:{HIT_WORDS})).*$|^.*(?:{HIT_WORDS})(?:\S+\s+){{0,{N_WORDS}}}https://(doi\.org/10\.5281/zenodo\.\d+|zenodo\.org/record/\d+).*$|^.*https://(doi\.org/10\.5281/zenodo\.\d+|zenodo\.org/record/\d+)(?:\S+\s+){{0,{N_WORDS}}}(?:{HIT_WORDS}).*$"
GITHUB_URL_REGEX = r"https?://(?:www\.)?github.com/([a-zA-Z0-9-]+)/([a-zA-Z0-9_.-]+)"
ZENODO_URL_REGEX = r"https?://(?:www\.)?zenodo.org/records?/([a-zA-Z0-9_.-]+)"
ZENODO_DOI_URL_REGEX = r"https://doi\.org/10\.\d+/[a-zA-Z0-9\._%~-]+"
ARXIV_ID_REGEX = r"/(\d+\.\d+)(?:v\d+)/"


def has_github_link(content):
    return re.search(GITHUB_REGEX, content, re.M)


def has_zenodo_link(content):
    return re.search(ZENODO_REGEX, content, re.M)


class LatexMatcher:
    SOURCES_FOLDER = "sources"

    def __init__(self, zenodo, github):
        self._zenodo = zenodo
        self._github = github

    def clean_merged(self):
        self._merger.clean(self.SOURCES_FOLDER)

    def merge_latex(self):
        self._merger.run(self.SOURCES_FOLDER)

    def run(self):
        results_with_code = dict()
        results_without_code = set()

        merged_filepaths = os.path.join(self.SOURCES_FOLDER, "**", "merged.tex")
        filepaths = glob.glob(merged_filepaths, recursive=True)
        if not filepaths:
            raise LatexMergedNotFound()

        i = found_github = found_zenodo = 0
        total = len(filepaths)
        for filepath in filepaths:
            i += 1
            logger.info(f"Working on `{filepath}` - {i}/{total}")

            arxiv_id = re.search(ARXIV_ID_REGEX, filepath)[1]
            ARXIV_URL_REGEX = f"arxiv.org/[^/]+/{arxiv_id}"

            with open(filepath) as fp:
                text = fp.read()

                github_matched = has_github_link(text)
                zenodo_matched = has_zenodo_link(text)

                if not github_matched and not zenodo_matched:
                    results_without_code.add(arxiv_id)
                    continue

                results_with_code.setdefault(
                    arxiv_id,
                    {
                        "github": "",
                        "github_url": "",
                        "arxiv in GitHub": "",
                        "zenodo": "",
                        "zenodo_url": "",
                        "arxiv in Zenodo": "",
                    },
                )
                results = results_with_code[arxiv_id]
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

                    results["github"] = "Found"
                    results["github_url"] = correct_url

                    has_arxiv = re.search(
                        ARXIV_URL_REGEX, description.lower()
                    ) or re.search(ARXIV_URL_REGEX, readme.lower())
                    if has_arxiv:
                        results["arxiv in GitHub"] = "Found"
                        logger.info(f"{filepath}: found arxiv link in GitHub")
                        found_github += 1
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
                        found_zenodo += 1
                    else:
                        results["arxiv in Zenodo"] = "Missing"
                        logger.info(f"{filepath}: not found arxiv link in Zenodo")
                else:
                    results["zenodo"] = "Missing"

        self._github.close()

        logger.info(f"No code: {results_without_code}")
        logger.info(
            f"Total latex files: {total} | 2-ways links - GitHub: {found_github}, Zenodo: {found_zenodo}"
        )

        # Dump to a CSV file
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        with open(f"results_{timestamp}.csv", mode="w", newline="") as file:
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
            for arxiv_id in results_with_code.keys():
                d = results_with_code[arxiv_id]
                row = [
                    arxiv_id,
                    d["github"],
                    d["github_url"],
                    d["arxiv in GitHub"],
                    d["zenodo"],
                    d["zenodo_url"],
                    d["arxiv in Zenodo"],
                ]
                writer.writerow(row)
