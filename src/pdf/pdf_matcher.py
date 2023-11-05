import csv
import glob
import logging
import os
import re
from datetime import datetime

from ..errors import PDFsExtractedNotFound
from ..repos_finder import ReposFinder
from ..pub_finder import PubFinder

logger = logging.getLogger("PDF Matcher")

ARXIV_ID_REGEX = r"/(\d+\.\d+)(?:v\d+)/"


class PDFMatcher:
    PDFS_FOLDER = "pdfs"

    def __init__(self, github, zenodo):
        self._github = github
        self._zenodo = zenodo

    def run(self):
        repos_finder = ReposFinder()
        pub_finder = PubFinder(self._github, self._zenodo)

        extracted_filepaths = os.path.join(self.PDFS_FOLDER, "**", "extracted.txt")
        filepaths = glob.glob(extracted_filepaths, recursive=True)
        if not filepaths:
            raise PDFsExtractedNotFound()

        results = {}
        i = 0
        total = len(filepaths)
        for filepath in filepaths:
            i += 1
            logger.info(f"Working on `{filepath}` - {i}/{total}")

            arxiv_id = re.search(ARXIV_ID_REGEX, filepath)[1]
            results.setdefault(arxiv_id, {})
            with open(filepath) as fp:
                text = fp.read()

                # PDFs cannot be contextualized, given that URLs might be in
                # footnotes or appendices
                repos_ids = repos_finder.find(arxiv_id, text, contextualized=False)
                results[arxiv_id] = pub_finder.find(arxiv_id, repos_ids)

        self._github.close()

        # Dump to a CSV file
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        with open(f"results_pdfs_{timestamp}.csv", mode="w", newline="") as file:
            writer = csv.writer(file)

            header = [
                "ArXiV id",
                "Result",
                "Where",
            ]
            writer.writerow(header)

            for arxiv_id, repos in results.items():
                found = False
                for repo, ids in repos.items():
                    for _id, value in ids.items():
                        if value == "Found":
                             found = True
                             row = [arxiv_id, "Found", f"Repo: {repo} - {str(_id)}"]
                if not found:
                    row = [arxiv_id, "Not found", ""]

                writer.writerow(row)

