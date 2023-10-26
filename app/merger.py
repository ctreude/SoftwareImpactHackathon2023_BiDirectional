import os
import glob
import re

BIBITEM_REGEX = r"\\bibitem{([^}]+)}([\s\S]*?)\\bibitem{[^}]+}"
BIBITEM_URL_REGEX = r"\\url{([^}]+)}"
CITE_REGEX = r"\\cite{([^}]+)}"


class Merger:
    def merge_latex(self, input_folder):
        """Merge multiple latex file into one"""
        for dir in os.listdir(input_folder):
            merged_filepath = os.path.join(input_folder, dir, "merged.tex")
            with open(merged_filepath, "w") as output:
                tex_filespath = os.path.join(input_folder, dir, "**", "*.tex")
                for latex_filepath in glob.glob(tex_filespath, recursive=True):
                    with open(latex_filepath, "r") as input_file:
                        output.write(input_file.read() + "\n")

    def _parse_bbl_file(self, bbl_file):
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

    def embed_bbl(self, input_folder):
        """Replace the \cite in the latex template with the bbl"""
        for dir in os.listdir(input_folder):
            merged_filepath = os.path.join(input_folder, dir, "merged.tex")
            bbls_filespath = os.path.join(input_folder, dir, "**", "*.bbl")

            # extra citations
            citation_data = {}
            for bbl_filepath in glob.glob(bbls_filespath, recursive=True):
                citation_data.update(self._parse_bbl_file(bbl_filepath))

            # Process the merged.tex file to replace \cite with \bibitem
            self._replace_cite_with_bibitem(merged_filepath, citation_data)

    def run(self, input_folder="sources"):
        self.merge_latex(input_folder)
        self.embed_bbl(input_folder)
