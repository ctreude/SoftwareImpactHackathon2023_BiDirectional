from src.enums import Repos
from src.repos_finder import ReposFinder


def test_github_regex():
    finder = ReposFinder()
    must_match = [
        "abore https://github.com/test/myrepo et",
        "abore http://github.com/test/myrepo et",
        "abore https://github.com/test/myrepo/ et",
    ]
    for text in must_match:
        results = finder._find_all("1234", text)
        assert results[Repos.GITHUB.value][0] == ("test", "myrepo")


def test_zenodo_record_regex():
    finder = ReposFinder()
    must_match = [
        "abore https://zenodo.org/records/123456 et",
        "abore http://zenodo.org/records/123456 et",
        "abore https://zenodo.org/record/123456 et",
        "abore http://zenodo.org/record/123456 et",
        "abore https://zenodo.org/record/123456/ et",
        "abore http://zenodo.org/record/123456/ et",
    ]
    for text in must_match:
        results = finder._find_all("1234", text)
        assert results[Repos.ZENODO_RECORD.value][0] == "123456"


def test_zenodo_doi_regex():
    finder = ReposFinder()
    must_match = [
        "abore https://doi.org/10.5281/zenodo.123345 et",
        "abore http://doi.org/10.5281/zenodo.123345 et",
    ]
    for text in must_match:
        results = finder._find_all("1234", text)
        assert "doi.org/10.5281/zenodo.123345" in results[Repos.ZENODO_DOI.value][0]


def test_other_doi_regex():
    finder = ReposFinder()
    no_match = [
        "abore https://doi.org/10.134/other.123345 et",
        "abore http://doi.org/10.5281/other.123345 et",
    ]
    for text in no_match:
        results = finder._find_all("1234", text)
        assert not results[Repos.ZENODO_DOI.value]


def test_find_all():
    finder = ReposFinder()
    text = """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
        incididunt ut labore https://github.com/test/myrepo et dolore magna aliqua. Tincidunt praesent semper feugiat nibh.

        Quis varius quam quisque id diam vel. Maecenas sed enim ut sem viverra aliquet
        eget sit amet. https://zenodo.org/records/123456 Adipiscing elit pellentesque https://github.com/test/myrepo2 habitant morbi tristique.

        Quis varius quam quisque https://doi.org/10.5281/zenodo.123345 id diam vel. Maecenas sed enim ut sem viverra aliquet
        eget sit amet. Adipiscing elit pellentesque habitant morbi tristique.
    """
    results = finder.find("1234", text)
    assert results[Repos.GITHUB.value][0] == ("test", "myrepo")
    assert results[Repos.GITHUB.value][1] == ("test", "myrepo2")
    assert results[Repos.ZENODO_RECORD.value][0] == "123456"
    assert results[Repos.ZENODO_DOI.value][0] == "https://doi.org/10.5281/zenodo.123345"


def test_find_contextualized():
    finder = ReposFinder()
    # no keywords to match
    none = """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
        incididunt ut labore https://github.com/test/myrepo et dolore magna aliqua. Tincidunt praesent semper feugiat nibh.

        Quis varius quam quisque id diam vel. Maecenas sed enim ut sem viverra aliquet
        eget sit amet. https://zenodo.org/records/123456 Adipiscing elit pellentesque https://github.com/test/myrepo2 habitant morbi tristique.

        Quis varius quam quisque https://doi.org/10.5281/zenodo.123345 id diam vel. Maecenas sed enim ut sem viverra aliquet
        eget sit amet. Adipiscing elit pellentesque habitant morbi tristique.
    """
    results = finder.find("1234", none, contextualized=True)
    assert not results[Repos.GITHUB.value]
    assert not results[Repos.ZENODO_RECORD.value]
    assert not results[Repos.ZENODO_DOI.value]

    # match only first GH link
    github_first = """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
        test code ut labore \\url{https://github.com/test/myrepo} et dolore magna aliqua. Tincidunt praesent semper feugiat nibh.

        Quis varius quam quisque id diam vel. Maecenas sed enim ut sem viverra aliquet
        eget sit amet. https://zenodo.org/records/123456 Adipiscing elit pellentesque https://github.com/test/myrepo2 habitant morbi tristique.

        Quis varius quam quisque https://doi.org/10.5281/zenodo.123345 id diam vel. Maecenas sed enim ut sem viverra aliquet
        eget sit amet. Adipiscing elit pellentesque habitant morbi tristique.
    """
    results = finder.find("1234", github_first, contextualized=True)
    assert results[Repos.GITHUB.value][0] == ("test", "myrepo")
    assert not results[Repos.ZENODO_RECORD.value]
    assert not results[Repos.ZENODO_DOI.value]

    # match all and only GH links
    github = """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
        code ut labore https://github.com/test/myrepo et dolore magna aliqua. Tincidunt praesent semper feugiat nibh.

        Quis varius quam quisque id diam vel. Maecenas sed enim ut sem viverra aliquet
        eget sit amet. https://zenodo.org/records/123456 Adipiscing elit pellentesque Adipiscing elit pellentesque Adipiscing elit pellentesque \\url{https://github.com/test/myrepo2} habitant morbi tristique replication.

        Quis varius quam quisque Quis varius quam quisque Quis varius quam quisque https://doi.org/10.5281/zenodo.123345 id diam vel. Maecenas sed enim ut sem viverra aliquet
        eget sit amet. Adipiscing elit pellentesque habitant morbi tristique.
    """
    results = finder.find("1234", github, contextualized=True)
    assert results[Repos.GITHUB.value][0] == ("test", "myrepo")
    assert results[Repos.GITHUB.value][1] == ("test", "myrepo2")
    assert not results[Repos.ZENODO_RECORD.value]
    assert not results[Repos.ZENODO_DOI.value]

    # match all
    match_all = """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
        code ut labore https://github.com/test/myrepo et dolore magna aliqua. Tincidunt praesent semper feugiat nibh.

        Quis varius quam quisque id diam vel. Maecenas sed enim ut sem viverra aliquet
        eget sit amet appendix \\cite{https://zenodo.org/records/123456} Adipiscing elit pellentesque https://github.com/test/myrepo2 habitant tristique replication.

        Quis varius quam quisque Quis varius quam quisque Quis varius supplementary quam quisque https://doi.org/10.5281/zenodo.123345 id diam vel. Maecenas sed enim ut sem viverra aliquet
        eget sit amet. Adipiscing elit pellentesque habitant morbi tristique.
    """
    results = finder.find("1234", match_all, contextualized=True)
    assert results[Repos.GITHUB.value][0] == ("test", "myrepo")
    assert results[Repos.GITHUB.value][1] == ("test", "myrepo2")
    assert results[Repos.ZENODO_RECORD.value][0] == "123456"
    assert results[Repos.ZENODO_DOI.value][0] == "https://doi.org/10.5281/zenodo.123345"

    # too far, no match
    finder = ReposFinder(contextualized_words=3)
    too_far = """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
        code ut labore ut labore https://github.com/test/myrepo et dolore magna aliqua. Tincidunt praesent semper feugiat nibh.
    """
    results = finder.find("1234", too_far, contextualized=True)
    assert not results[Repos.GITHUB.value]
    assert not results[Repos.ZENODO_RECORD.value]
    assert not results[Repos.ZENODO_DOI.value]
