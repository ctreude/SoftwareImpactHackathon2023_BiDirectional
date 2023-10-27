import os

import arxiv
import requests

##### DOWNLOAD PDFs files

# Ensure the "pdfs" directory exists
if not os.path.exists("pdfs"):
    os.makedirs("pdfs")

# Define the search query for author "Treude"
search = arxiv.Search(query="au:Treude")

# Loop through each paper written by "Treude" and download
for paper in search.get():
    # Check if the paper was published in 2023
    if paper.published.year != 2023:
        continue

    # Extract the arXiv ID from the entry_id URL
    arxiv_id = paper.entry_id.split("/")[-1]
    filename = f"{arxiv_id}.pdf"
    download_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

    try:
        print(f"Downloading {paper.title}...")

        # Fetch the PDF content directly using requests
        response = requests.get(download_url, stream=True)
        response.raise_for_status()  # Raise an error for failed requests

        # Save the fetched content to the desired location
        with open(os.path.join("pdfs", filename), "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"{paper.title} downloaded successfully!")

    except Exception as e:
        print(f"Failed to download {paper.title}. Error: {e}")

print("Download complete!")
