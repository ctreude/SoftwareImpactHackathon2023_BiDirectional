import logging
import os
import tarfile
import time

import arxiv
import requests

logger = logging.getLogger("ArXiV")


##### DOWNLOAD Latex files
def ensure_directory_exists(dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)


def construct_download_url(arxiv_id):
    if "/" in arxiv_id:
        return f"https://arxiv.org/e-print/cs/{arxiv_id}"
    return f"https://arxiv.org/e-print/{arxiv_id}"


def download_source(download_url, paper_title):
    print(f"Downloading sources for {paper_title}...")

    response = requests.get(download_url, stream=True)
    response.raise_for_status()

    filename = f"{download_url.split('/')[-1]}.tar.gz"
    file_path = os.path.join("sources", filename)
    with open(file_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    return file_path


def extract_files(file_path):
    folder_name = file_path.rsplit(".", 2)[0]
    folder_path = os.path.join("sources", folder_name)

    os.makedirs(folder_path, exist_ok=True)

    print(f"Extracting {file_path} to {folder_path}...")
    try:
        with tarfile.open(file_path, "r:gz") as archive:
            for member in archive.getmembers():
                if member.name.endswith((".tex", ".bbl")):
                    archive.extract(member, path=folder_path)
    except (tarfile.ReadError, EOFError) as e:
        print(f"Error extracting {file_path}. Reason: {e}. Skipping...")

    os.remove(file_path)
    return folder_path


def clean_directory(directory):
    for entry_name in os.listdir(directory):
        entry_path = os.path.join(directory, entry_name)

        if os.path.isdir(entry_path):
            clean_directory(entry_path)
        elif not entry_name.endswith((".tex", ".bbl")):
            os.remove(entry_path)


def process_paper(paper, downloaded_count):
    arxiv_id = paper.entry_id.split("/")[-1]
    download_url = construct_download_url(arxiv_id)

    try:
        file_path = download_source(download_url, paper.title)
        folder_path = extract_files(file_path)
        clean_directory(folder_path)

        print(
            f"Processed sources for {paper.title} (Total: {downloaded_count} sources processed)"
        )
    except Exception as e:
        print(f"Failed to process sources for {paper.title}. Error: {e}")


def main():
    ensure_directory_exists("sources")

    search = arxiv.Search(
        query="cat:cs.SE",
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )

    downloaded_count = 0
    for paper in search.get():
        if downloaded_count >= 1000:
            break
        process_paper(paper, downloaded_count + 1)
        downloaded_count += 1

        time.sleep(3)

    print("All papers processed!")


if __name__ == "__main__":
    main()
