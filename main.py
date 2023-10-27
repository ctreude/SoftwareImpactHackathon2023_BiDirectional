import argparse
import os

from app.github import GitHubAPI
from app.latex_matcher import LatexMatcher
from app.latex_merger import LatexMerger
from app.logger import setup_logger
from app.pdf_extractor import PDFExtractor
from app.pdf_matcher import PDFMatcher
from app.zenodo import ZenodoAPI


def download_sources(source_type, queries):
    print("Not yet integrated. See `app.arxiv_latex.py/app.arxiv_pdfs.py`")
    pass


def run_program(run_type):
    access_token = os.environ.get("GITHUB_TOKEN")
    if not access_token:
        raise Exception(
            "GitHub token undefined in env var `GITHUB_TOKEN`. Get a new token at https://github.com/settings/tokens and set the env var `GITHUB_TOKEN`."
        )
    github = GitHubAPI(access_token)
    zenodo = ZenodoAPI()

    if run_type == "pdf":
        matcher = PDFMatcher(zenodo, github)
    elif run_type == "latex":
        matcher = LatexMatcher(zenodo, github)
    matcher.run()


def extract_pdfs():
    PDFExtractor().run()


def merge_latex():
    LatexMerger().run()


def clean_sources(clean_type):
    if clean_type == "pdf":
        PDFExtractor().clean()
    elif clean_type == "latex":
        LatexMerger().clean()


if __name__ == "__main__":
    setup_logger()

    parser = argparse.ArgumentParser(
        description="Bidirectional Paper-Repository Traceability tool"
    )

    subparsers = parser.add_subparsers(help="subcommands", dest="command")

    # Download command
    download_parser = subparsers.add_parser(
        "download", help="Download sources PDFs or Latex files for ArXiV."
    )
    download_parser.add_argument(
        "--type",
        choices=["pdf", "latex"],
        required=True,
        help="Select whether to download PDFs or Latex files for ArXiV.",
    )
    download_parser.add_argument(
        "--query",
        required=True,
        help="Specify the query string when searching preprints to download on ArXiV.",
    )

    # Run command
    run_parser = subparsers.add_parser("run", help="Check for bidirectional links.")
    run_parser.add_argument(
        "--type",
        choices=["pdf", "latex"],
        required=True,
        help="Select whether to run using PDFs or Latex files.",
    )

    # Clean command
    clean_parser = subparsers.add_parser(
        "clean", help="Clean precomputed PDFs or Latex."
    )
    clean_parser.add_argument(
        "--type",
        choices=["pdf", "latex"],
        required=True,
        help="Select whether to clean extracted PDFs content or merged Latex files.",
    )

    extract_parser = subparsers.add_parser(
        "extract-pdfs", help="Extract all PDFs content using Tika."
    )
    merge_parser = subparsers.add_parser(
        "merge-latex", help="Merge all Latex files embedding citations."
    )

    args = parser.parse_args()

    if args.command == "download":
        download_sources(args.type, args.query)

    if args.command == "run":
        run_program(args.type)

    if args.command == "extract-pdfs":
        extract_pdfs()

    if args.command == "merge-latex":
        merge_latex()

    if args.command == "clean":
        clean_sources(args.type)
