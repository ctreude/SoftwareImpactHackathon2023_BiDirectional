import logging
import re

from github import Auth, Github
from github.GithubException import GithubException

logger = logging.getLogger("GitHubAPI")

GITHUB_RESERVED_ORG_NAMES = ["features", "orgs"]
GITHUB_RESERVED_REPO_NAMES = [
    "settings",
    "billing",
    "new",
    "topics",
    "explore",
    "notifications",
    "stars",
]


class GitHubAPI:
    def __init__(self, access_token):
        auth = Auth.Token(access_token)
        self.github = Github(auth=auth)

    def get_description_readme(self, org_name, repo_name):
        logger.info(f"url parsing: org `{org_name}`, repo `{repo_name}`")
        try:
            repo = self.github.get_repo(f"{org_name}/{repo_name}")
            description = repo.description or ""

            filenames = [file.name for file in repo.get_contents("")]
            readme_files = [
                filename
                for filename in filenames
                if filename.lower().startswith("readme")
            ]
            logger.info(f"all readme files: {', '.join(readme_files)}")

            concatenated_readme_contents = ""
            for readme_file in readme_files:
                try:
                    file_content = repo.get_contents(readme_file).decoded_content.decode(
                        "utf-8"
                    )
                    concatenated_readme_contents += file_content
                except Exception:
                    # weird errors with some readme files
                    continue
        except GithubException:
            logger.info(f"GitHub repo deleted, skipping...")
            description = ""
            concatenated_readme_contents = ""

        return (
            description,
            concatenated_readme_contents,
            f"https://github.com/{org_name}/{repo_name}",
        )

    def close(self):
        self.github.close()
