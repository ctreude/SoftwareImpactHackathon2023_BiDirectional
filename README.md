# Bidirectional Paper-Repository Traceability

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10303607.svg)](https://doi.org/10.5281/zenodo.10303607)

There's a gap between academic papers and data/code repositories due to the absence of bidirectional links. We propose to develop a tool that connects scientific papers to their relevant GitHub repositories and vice versa. Our approach involves devising algorithms to search both academic platforms and GitHub for mutual references, integrating features into the tool for automatic link creation, and incorporating capabilities to auto-comment on platforms like arXiv when a corresponding GitHub repository is detected. Ultimately, we aim to promote the significance of traceability, emphasizing its importance to both the academic and developer communities.

This tool provides functionality to establish and check bidirectional traceability between academic papers and their respective code repositories. It supports operations with PDF and LaTeX files, specifically focusing on ArXiV sources.

## Methodology

Starting with publications from ArXiv.org, our goal was to extract from the PDFs all links to software or dataset repositories on GitHub.com and Zenodo.org. Then, repositories have been queried to find when the ArXiv preprint's link was appearing in any of the README files on GitHub or in the record's metadata on Zenodo, confirming the bidirectional traceability.

Given that preprints may contain multiple links to repositories, one of the challenges is to discover only the link referring to the software or dataset used for the preprint, excluding any other external link. To tackle this, we employed relatively simple heuristics based on regular expressions. These heuristics filter and retain only links appearing closely to words such as `code`, `script`, `data,` and others.
Please note that this approach is not intended to be foolproof but rather offers a straightforward method for exploring basic traceability.

The main issue with this approach is that links in publications are often placed in footnotes or appendices. The text extraction from PDFs does not keep the reference between the sentence mentioning a link and the link itself. Existing software tools for extracting or comprehending PDF content, such as Tika and Grobid, do not seem to offer a solution to this problem. Large language models might be explored in the future to overcome this limitation.

### LaTeX approach

In ArXiv, about 90% of the publications also contain the original LaTeX files. URLs or citation links are inline in LaTeX sources, meaning that the link appears in the same sentence where it is mentioned (e.g. `sentence \cite{url}`). Starting from the LaTeX, we were able to extract the links and then verify the bidirectional traceability in GitHub or Zenodo.

### PDF approach

A more basic approach consists in retrieving all links to GitHub or Zenodo appearing in the PDF file, independently of where it is mentioned or its context. All repositories are then queried to verify the existence of a link to the ArXiV preprint.

### Application

This software is a proof-of-concept. It has simple commands:

1. **Download Sources**: Allows users to download either PDF or LaTeX files from ArXiV based on a specified query. Not yet functional.
2. **Extract PDFs**: Uses Tika to extract content from all PDFs.
3. **Merge LaTeX**: Merges all LaTeX files embedding citations.
4. **Run**: It checks for bidirectional links between papers and repositories using either PDF or LaTeX files. Internally, it interacts with both GitHub and Zenodo platforms.
5. **Clean Sources**: Provides an option to clean precomputed content of either PDF or LaTeX files.

### Usage

Install (in your virtualenv):

```bash
pip install -e .[test]
```

The typical usage will be the following:

1. download all the LaTeX sources or PDFs from ArXiv:

```bash
python main.py download --type [pdf|latex] --query YOUR_QUERY
```
Note: this is not yet functional. A first version of the scripts is available in the module `src.arxiv`.

2. When working with PDFs, each PDF content should be extracted to get the text. With LaTeX sources,
the multiple LaTeX files should be merged into one, embedding citations.

The following commands expect to find PDFs or LaTeX sources in the local folder `pdfs` or `sources` respectively,
and each folder should be named with the ArXiV id.

Examples:

```bash
$ cd pdf
$ ls
2301.12169v1 2302.08664v3 2303.10131v1 2303.13729v2 2304.05766v1 2305.16365v1 2306.10019v1 2307.04291v1 2308.09637v2 2308.12079v1 2309.04197v1 2302.05564v1 2303.09727v1 2303.10439v2 2303.15684v1 2304.14628v2 2305.16591v1 2306.10021v1 2307.10793v1 2308.09940v1 2309.03914v1
$ cd 2304.05766v1
$ ls
2304.05766v1.pdf
```

```bash
$ cd sources
$ ls
2301.12169v1 2302.08664v3 2303.10131v1 2303.13729v2 2304.05766v1 2305.16365v1 2306.10019v1 2307.04291v1 2308.09637v2 2308.12079v1 2309.04197v1 2302.05564v1 2303.09727v1 2303.10439v2 2303.15684v1 2304.14628v2 2305.16591v1 2306.10021v1 2307.10793v1 2308.09940v1 2309.03914v1
$ cd 2304.05766v1
$ ls
ieee       main.bbl   main.tex
```

The command will create an `extracted.txt` or `merged.tex` respectively:

```bash
python main.py extract-pdfs
python main.py merge-latex
```
Note: for the PDF extraction, run the `Tika` server, for example with Docker: `docker run -p 127.0.0.1:9998:9998 apache/tika`

3. Finally, run it:
```bash
python main.py run --type [pdf|latex]
```
Note: you need a GitHub token. Get a new token at https://github.com/settings/tokens and set the env var `GITHUB_TOKEN`.

The output is logged in files in the `logs` folder, and the results are stored in a `.csv` file.

You can clean generated files by running:
```bash
python main.py clean --type [pdf|latex]
```

## Possible enhancements

* The regex for GitHub only expects the main repo URL. They should be changed to take into account if the link
is pointing to a commit, a tag or a branch.
* If the same link is found multiple times in the same publication, it is not checked only once.
* Extract the list of the most common words close to a link to a repo, to have a good set of keywords to use.
* Run the verification on a much larger dataset of PDFs or LaTeX files.
* Improve the heuristics to detect what is the right link, pointing to the code or dataset used by the paper. LLMs techniques might be explored for this task.

## About this project

This repository was developed as part of the [Mapping the Impact of Research Software in Science](https://github.com/chanzuckerberg/software-impact-hackathon-2023) hackathon hosted by the Chan Zuckerberg Initiative (CZI). By participating in this hackathon, owners of this repository acknowledge the following:
1. The code for this project is hosted by the project contributors in a repository created from a template generated by CZI. The purpose of this template is to help ensure that repositories adhere to the hackathon’s project naming conventions and licensing recommendations.  CZI does not claim any ownership or intellectual property on the outputs of the hackathon. This repository allows the contributing teams to maintain ownership of code after the project, and indicates that the code produced is not a CZI product, and CZI does not assume responsibility for assuring the legality, usability, safety, or security of the code produced.
2. This project is published under a MIT license.

## Code of Conduct

Contributions to this project are subject to CZI’s Contributor Covenant [code of conduct](https://github.com/chanzuckerberg/.github/blob/master/CODE_OF_CONDUCT.md). By participating, contributors are expected to uphold this code of conduct.

## Reporting Security Issues

If you believe you have found a security issue, please responsibly disclose by contacting the repository owner via the ‘security’ tab above.
