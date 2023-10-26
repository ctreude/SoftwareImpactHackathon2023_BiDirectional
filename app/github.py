import logging
from urllib.parse import urlsplit
from github import Auth, Github

logger = logging.getLogger("GitHubAPI")


class GitHubAPI:
    def __init__(self, access_token):
        auth = Auth.Token(access_token)
        self.github = Github(auth=auth)

    def _split(self, url):
        _, _, path, _, _ = urlsplit(url)
        org, repo = path.strip("/").split("/")
        return org, repo

    def get_repo(self, url):
        logger.debug(f"getting repo for URL: `{url}`")
        org, repo = self._split(url)
        logger.info(f"url parsing: org `{org}`, repo `{repo}`")
        repo = self.github.get_repo(f"{org}/{repo}")
        logger.info(repo)

    def close(self):
        self.github.close()
