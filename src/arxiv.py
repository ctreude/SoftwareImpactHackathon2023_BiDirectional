import logging
import os
import tarfile
import time

import requests

import arxiv

logger = logging.getLogger("ArXiV")


class ArXiVDownloader:
    PDFS_FOLDER = "pdfs"
    SOURCES_FOLDER = "sources"
    SLEEP_TIME = 0.5

    def __init__(self):
        self._url_pdf = "https://arxiv.org/pdf/{arxiv_id}.pdf"
        self._url_latex = "https://arxiv.org/e-print/{arxiv_id}"

        if not os.path.exists(self.PDFS_FOLDER):
            os.makedirs(self.PDFS_FOLDER)
        if not os.path.exists(self.SOURCES_FOLDER):
            os.makedirs(self.SOURCES_FOLDER)

    def _search(self, query="cat:cs.SE", limit=1000):
        """Search in ArXiV."""
        search = arxiv.Search(
            query=query,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )

        i = 0
        for entry in search.get():
            i += 1
            if i > limit:
                break

            arxiv_id = entry.entry_id.split("/")[-1]
            yield arxiv_id

    def _download_pdf(self, arxiv_id):
        """Download a single PDF by ArXiV id."""
        logger.info(f"Downloading {arxiv_id} PDF.")
        download_url = self._url_pdf.format(arxiv_id)
        filename = f"{arxiv_id}.pdf"

        try:
            response = requests.get(download_url, stream=True)
            response.raise_for_status()  # Raise an error for failed requests

            with open(os.path.join(self.PDFS_FOLDER, filename), "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        except Exception:
            logger.error(f"Failed to download {arxiv_id} PDF.")

    def download_pdfs(self, query, limit=1000):
        """Download all PDFs found by search query."""
        for arxiv_id in self._search(query, limit):
            self._download_pdf(arxiv_id)
            time.sleep(self.SLEEP_TIME)

    def _extract_tar(self, filepath, arxiv_id):
        """Extract tex/bbl from tar."""
        folder_path = os.path.join(self.SOURCES_FOLDER, arxiv_id)
        os.makedirs(folder_path, exist_ok=True)

        logger.debug(f"Extracting {filepath} to {folder_path}...")
        try:
            with tarfile.open(filepath, "r:gz") as archive:
                for member in archive.getmembers():
                    if member.name.endswith((".tex", ".bbl")):
                        archive.extract(member, path=folder_path)
        except (tarfile.ReadError, EOFError) as e:
            logger.error(f"Error extracting {filepath}. Reason: {e}. Skipping...")

        os.remove(filepath)
        return folder_path

    def _download_source(self, arxiv_id):
        """Download a single Latex by ArXiV id."""
        logger.info(f"Downloading {arxiv_id} Latex.")
        download_url = self._url_latex.format(arxiv_id)
        filename = f"{arxiv_id}.tar.gz"

        try:
            response = requests.get(download_url, stream=True)
            response.raise_for_status()

            filepath = os.path.join(self.SOURCES_FOLDER, filename)
            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            self._extract_tar(filepath)
        except Exception:
            logger.error(f"Failed to download {arxiv_id} Latex.")

    def download_sources(self, query, limit=1000):
        """Download all Latex found by search query."""
        for arxiv_id in self._search(query, limit):
            self._download_source(arxiv_id)
            time.sleep(self.SLEEP_TIME)

    def download(self, query, limit=1000):
        """Download all PDFs and Latex found by search query."""
        for arxiv_id in self._search(query, limit):
            self._download_pdf(arxiv_id)
            self._download_source(arxiv_id)
            time.sleep(self.SLEEP_TIME)
