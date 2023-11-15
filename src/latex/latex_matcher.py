import csv
import glob
import logging
import os
import re
from datetime import datetime

from ..errors import LatexMergedNotFound
from ..repos_finder import ReposFinder
from ..pub_finder import PubFinder

logger = logging.getLogger("Latex Matcher")

ARXIV_ID_REGEX = r"/(\d+\.\d+)(:v\d+)?/"
#ARXIV_ID_REGEX = r"/(\d+\.\d+)(:v\d+)?/"

class LatexMatcher:
    SOURCES_FOLDER = "sources"

    def __init__(self, github, zenodo):
        self._github = github
        self._zenodo = zenodo

    def clean_merged(self):
        self._merger.clean(self.SOURCES_FOLDER)

    def merge_latex(self):
        self._merger.run(self.SOURCES_FOLDER)

    def run(self):
        repos_finder = ReposFinder()
        pub_finder = PubFinder(self._github, self._zenodo)

        merged_filepaths = os.path.join(self.SOURCES_FOLDER, "**", "merged.tex")
        filepaths = glob.glob(merged_filepaths, recursive=True)
        if not filepaths:
            raise LatexMergedNotFound()

        results = {}
        i = 0
        total = len(filepaths)
        for filepath in filepaths:
            i += 1
            logger.info(f"Working on `{filepath}` - {i}/{total}")
            match = re.search(ARXIV_ID_REGEX, filepath)
            if not match:
                continue
            arxiv_id = match[1]
            results.setdefault(arxiv_id, {})
            with open(filepath) as fp:
                text = fp.read()

                repos_ids = repos_finder.find(arxiv_id, text, contextualized=True)
                results[arxiv_id] = pub_finder.find(arxiv_id, repos_ids)

        self._github.close()

        # Dump to a CSV file
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        with open(f"results_sources_{timestamp}.csv", mode="w", newline="") as file:
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

