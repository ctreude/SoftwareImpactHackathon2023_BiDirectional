import csv
import glob
import logging
import os
import re
from datetime import datetime

from .errors import PDFsExtractedNotFound

logger = logging.getLogger("PDF Matcher")

GITHUB_URL_REGEX = r"https?://(?:www\.)?github.com/[a-zA-Z0-9-]+/[a-zA-Z0-9_.-]+"
ZENODO_URL_REGEX = r"https?://(?:www\.)?zenodo.org/records?/[a-zA-Z0-9_.-]+"
ZENODO_DOI_URL_REGEX = r"https://doi\.org/10\.5281/[a-zA-Z0-9\._%~-]+"
ARXIV_ID_REGEX = r"/(\d+\.\d+)(?:v\d+)/"


class PDFMatcher:
    PDFS_FOLDER = "pdfs"

    def __init__(self, zenodo, github):
        self._zenodo = zenodo
        self._github = github

    def run(self):
        results_with_code = dict()
        results_without_code = set()

        extracted_filepaths = os.path.join(self.PDFS_FOLDER, "**", "extracted.txt")
        filepaths = glob.glob(extracted_filepaths, recursive=True)
        if not filepaths:
            raise PDFsExtractedNotFound()

        i = 0
        total = len(filepaths)
        for filepath in filepaths:
            i += 1
            logger.info(f"Working on `{filepath}` - {i}/{total}")

            arxiv_id = re.search(ARXIV_ID_REGEX, filepath)[1]
            ARXIV_URL_REGEX = f"arxiv.org/[^/]+/{arxiv_id}"

            with open(filepath) as fp:
                text = fp.read()

                github_links = re.findall(GITHUB_URL_REGEX, text)
                zenodo_links = re.findall(ZENODO_URL_REGEX, text) + re.findall(
                    ZENODO_DOI_URL_REGEX, text
                )

                if not github_links and not zenodo_links:
                    results_without_code.add(arxiv_id)
                    continue

                results_with_code.setdefault(
                    arxiv_id,
                    {
                        "arxiv in GitHub": "",
                        "arxiv in Zenodo": "",
                    },
                )
                results = results_with_code[arxiv_id]
                for url in github_links:
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

                    has_arxiv = re.search(
                        ARXIV_URL_REGEX, description.lower()
                    ) or re.search(ARXIV_URL_REGEX, readme.lower())
                    if has_arxiv:
                        results["arxiv in GitHub"] = "Found"
                        logger.info(f"{filepath}: found arxiv link in GitHub")
                    else:
                        results["arxiv in GitHub"] = "Missing"
                        logger.info(f"{filepath}: not found arxiv link in GitHub")

                for url in zenodo_links:
                    logger.info(f"Zenodo link: {url}")
                    record_text, correct_url = self._zenodo.get_record(url)

                    has_arxiv = re.search(ARXIV_URL_REGEX, record_text.lower())
                    if has_arxiv:
                        results["arxiv in Zenodo"] = "Found"
                        logger.info(f"{filepath}: found arxiv link in Zenodo")
                    else:
                        results["arxiv in Zenodo"] = "Missing"
                        logger.info(f"{filepath}: not found arxiv link in Zenodo")

        self._github.close()

        logger.info(f"No code: {results_without_code}")

        # Dump to a CSV file
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        with open(f"results_{timestamp}.csv", mode="w", newline="") as file:
            writer = csv.writer(file)

            # Write the header row
            header = [
                "ArXiV id",
                "GitHub repo contains ArXiV URL",
                "Zenodo record contains ArXiV URL",
            ]
            writer.writerow(header)

            # Write data for each key-value pair in the dictionary
            for arxiv_id in results_with_code.keys():
                d = results_with_code[arxiv_id]
                row = [arxiv_id, d["arxiv in GitHub"], d["arxiv in Zenodo"]]
                writer.writerow(row)
