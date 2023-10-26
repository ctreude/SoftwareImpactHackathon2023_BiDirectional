from app.logger import setup_logger
import os

from app.github import GitHubAPI
from app.zenodo import ZenodoAPI
from app.matcher import TwoWaysMatcher

if __name__ == "__main__":
    setup_logger()

    access_token = os.environ.get("GITHUB_TOKEN")
    if not access_token:
        raise Exception(
            "GitHub token undefined in env var `GITHUB_TOKEN`. Get a new token at https://github.com/settings/tokens and set the env var `GITHUB_TOKEN`."
        )
    github = GitHubAPI(access_token)
    zenodo = ZenodoAPI()

    matcher = TwoWaysMatcher(zenodo, github)
    matcher.run()
