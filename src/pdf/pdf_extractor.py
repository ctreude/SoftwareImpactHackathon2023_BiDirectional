import glob
import logging
import os

from tika import unpack

logger = logging.getLogger("PDF Extractor")


class PDFExtractor:
    def __init__(
        self, tika_server_url="http://127.0.0.1:9998/tika", input_folder="pdfs"
    ):
        self._tika_server_url = tika_server_url
        self._input_folder = input_folder

    def clean(self):
        """Deleted all `extracted.txt` files."""
        logger.info(f"Deleting all `extracted.txt` from {self._input_folder}")
        for dir in os.listdir(self._input_folder):
            extracted_filepath = os.path.join(self._input_folder, dir, "extracted.txt")
            if os.path.exists(extracted_filepath):
                os.remove(extracted_filepath)
        logger.info("Done!")

    def run(self):
        """Extract all PDFs content in `extracted.txt` file, using Tika."""
        dirs = os.listdir(self._input_folder)
        total = len(dirs)
        logger.info(f"Extracting the content of {total} PDFs")

        i = 0
        for dir in dirs:
            extracted_filepath = os.path.join(self._input_folder, dir, "extracted.txt")
            if os.path.exists(extracted_filepath):
                # already done
                continue

            i += 1
            logger.debug(f"Extracting PDF content of `{dir}` | {i}/{total}")
            pdf_filepaths = os.path.join(self._input_folder, dir, "**", "*.pdf")
            with open(extracted_filepath, "w") as output:
                for pdf_filepath in glob.glob(pdf_filepaths, recursive=True):
                    parsed = unpack.from_file(pdf_filepath, self._tika_server_url)
                    if parsed and parsed["content"]:
                        output.write(parsed["content"] + "\n")
        logger.info("Done!")
