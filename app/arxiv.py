import logging
import os
import requests
import arxiv
import tarfile

logger = logging.getLogger("ArXiV")


class ArXiVDownloader:
    def get_latex(search_query="au:Treude", dir="sources"):
        if not os.path.exists(dir):
            os.makedirs(dir)

        search = arxiv.Search(query=search_query)
        for paper in search.get():
            # Check if the paper was published in 2023
            if paper.published.year != 2023:
                continue

            # Extract the arXiv ID from the entry_id URL
            arxiv_id = paper.entry_id.split("/")[-1]
            filename = f"{arxiv_id}.tar.gz"
            download_url = f"https://arxiv.org/e-print/{arxiv_id}"

            try:
                logger.debug(f"Downloading sources for {paper.title}...")
                # Fetch the source archive directly using requests
                response = requests.get(download_url, stream=True)
                response.raise_for_status()

                # Save the fetched content to the desired location
                with open(os.path.join(dir, filename), "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                logger.debug(f"Sources for {paper.title} downloaded successfully!")

            except Exception as e:
                logger.error(
                    f"Failed to download sources for {paper.title}. Error: {e}"
                )

        logger.debug("Download complete! Now extracting archives...")

        source_directory = dir
        # Loop through each file in the source directory
        for filename in os.listdir(source_directory):
            if filename.endswith(".tar.gz"):
                file_path = os.path.join(source_directory, filename)

                # Construct directory name based on the filename (without extension)
                extract_dir = os.path.join(source_directory, filename[:-7])

                if not os.path.exists(extract_dir):
                    os.makedirs(extract_dir)

                # Extract the tar.gz file into its directory
                with tarfile.open(file_path, "r:gz") as archive:
                    valid_files = [
                        member
                        for member in archive.getmembers()
                        if member.name.endswith((".tex", ".bbl"))
                    ]
                    archive.extractall(path=extract_dir, members=valid_files)

                # Delete the original tar.gz file
                os.remove(file_path)

        logger.debug("Extraction complete!")
