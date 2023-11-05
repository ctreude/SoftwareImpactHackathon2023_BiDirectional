import glob
import logging
import os
import re

logger = logging.getLogger("Latex Merger")

BIBITEM_REGEX = r"\\bibitem{([^}]+)}([\s\S]*?)\\bibitem{[^}]+}"
BIBITEM_URL_REGEX = r"\\url{([^}]+)}"
CITE_REGEX = r"\\cite{([^}]+)}"


class LatexMerger:
    def __init__(self, input_folder="sources"):
        self._input_folder = input_folder

    def clean(self):
        """Remove all merged tex files."""
        logger.info(f"Deleting all `merged.tex` from {self._input_folder}")
        for dir in os.listdir(self._input_folder):
            merged_filepath = os.path.join(self._input_folder, dir, "merged.tex")
            if os.path.exists(merged_filepath):
                os.remove(merged_filepath)
        logger.info("Done!")

    def _merge(self, input_folder):
        """Merge multiple latex file into one single file."""
        dirs = os.listdir(self._input_folder)
        total = len(dirs)
        logger.info(f"Merging the content of {total} Latex")

        merged_dirs = []
        i = 0
        for dir in dirs:
            merged_filepath = os.path.join(input_folder, dir, "merged.tex")
            if os.path.exists(merged_filepath):
                # already done
                continue

            merged_dirs.append(dir)
            i += 1
            logger.debug(f"Merging Latex content {i}/{total}")
            with open(merged_filepath, "w") as output:
                tex_filespath = os.path.join(input_folder, dir, "**", "*.tex")
                for latex_filepath in glob.glob(tex_filespath, recursive=True):
                    with open(latex_filepath, "r", errors="replace") as input_file:
                        output.write(input_file.read() + "\n")
        return merged_dirs

    def _get_citation_url(self, bbl_file):
        """Parse a BBL file and return a map of `bibitem key` -> `url`."""
        with open(bbl_file, "r") as file:
            content = file.read()

        citation_data = {}
        for _match in re.finditer(BIBITEM_REGEX, content):
            bibitem_key = _match.group(1)
            bibitem_content = _match.group(2)

            inner_match = re.search(BIBITEM_URL_REGEX, bibitem_content)
            url = inner_match.group(1) if inner_match else None

            if url:
                citation_data[bibitem_key] = url

        return citation_data

    def _replace_cite_with_bibitem(self, merged_tex, citation_data):
        """Replace `cite` with the `bibitem url`."""
        with open(merged_tex, "r") as file:
            tex_content = file.read()

        tex_content = re.sub(
            CITE_REGEX,
            lambda match: citation_data.get(match.group(1), match.group(0)),
            tex_content,
        )

        # Optionally, save the modified content back to merged.tex
        with open(merged_tex, "w") as file:
            file.write(tex_content)

    def _embed_bbl(self, input_folder, merged_dirs):
        """Replace the \cite in the latex template with the bbl"""
        for dir in merged_dirs:
            merged_filepath = os.path.join(input_folder, dir, "merged.tex")
            bbls_filespath = os.path.join(input_folder, dir, "**", "*.bbl")

            # extra citations
            citation_urls = {}
            for bbl_filepath in glob.glob(bbls_filespath, recursive=True):
                citation_urls.update(self._get_citation_url(bbl_filepath))

            # Process the merged.tex file to replace \cite with \bibitem
            self._replace_cite_with_bibitem(merged_filepath, citation_urls)

    def run(self):
        """Merge all .tex into one and replace inline all bibitem urls."""
        merged_dirs = self._merge(self._input_folder)
        if merged_dirs:
            logger.info("Embedding all citations")
            self._embed_bbl(self._input_folder, merged_dirs)
        logger.info("Done!")
