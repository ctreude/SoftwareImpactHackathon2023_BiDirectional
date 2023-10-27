import logging
import re

from github import Auth, Github
from github.GithubException import GithubException

logger = logging.getLogger("GitHubAPI")


GITHUB_URL = r"https?://github.com/([a-zA-Z0-9-]+)/([a-zA-Z0-9_.-]+)"
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

    def _split(self, url):
        match = re.match(GITHUB_URL, url)
        org_name = match.group(1)
        repo_name = match.group(2)

        # Check if the repository name is not a reserved name
        if (
            org_name in GITHUB_RESERVED_ORG_NAMES
            or repo_name in GITHUB_RESERVED_REPO_NAMES
        ):
            raise ValueError(
                f"GitHub reserved org/repo name: org `{org_name}`, repo `{repo_name}`"
            )

        return org_name, repo_name

    def get_description_readme(self, url):
        logger.debug(f"getting repo for URL: `{url}`")
        try:
            org_name, repo_name = self._split(url)
        except ValueError as ex:
            logger.info(f"this URL is reserved by GitHub, skipping...")
            raise ex

        logger.info(f"url parsing: org `{org_name}`, repo `{repo_name}`")
        try:
            repo = self.github.get_repo(f"{org_name}/{repo_name}")

            filenames = [file.name for file in repo.get_contents("")]
            readme_files = [
                filename
                for filename in filenames
                if filename.lower().startswith("readme")
            ]
            logger.info(f"all readme files: {', '.join(readme_files)}")

            concatenated_readme_contents = ""
            for readme_file in readme_files:
                file_content = repo.get_contents(readme_file).decoded_content.decode(
                    "utf-8"
                )
                concatenated_readme_contents += file_content
        except GithubException:
            logger.info(f"GitHub repo deleted, skipping...")
            raise ValueError("GitHub repo deleted")

        return (
            repo.description or "",
            concatenated_readme_contents,
            f"https://github.com/{org_name}/{repo_name}",
        )

    def close(self):
        self.github.close()
