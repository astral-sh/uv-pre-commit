import re
import subprocess
import tomllib
import typing
from pathlib import Path

import urllib3
from packaging.requirements import Requirement
from packaging.version import Version


def main():
    with open(Path(__file__).parent / "pyproject.toml", "rb") as f:
        pyproject = tomllib.load(f)

    all_releases = get_all_releases()
    current_version = get_current_version(pyproject=pyproject)
    all_non_yanked_versions = sorted([
        release_version
        for release_version, release in all_releases.items()
        if not any([asset["yanked"] for asset in release])
    ])

    target_versions = [v for v in all_non_yanked_versions if v > current_version]

    if not target_versions and not any([
        asset["yanked"] for asset in all_releases[current_version]
    ]):
        last_valid_version = all_non_yanked_versions[-1]
        paths = process_version(last_valid_version)
        if subprocess.check_output(["git", "status", "-s"]).strip():
            push_changed_version(paths, f"Mirror: yanked {current_version}")

            # Make `last_valid_version` the top tag and release
            subprocess.run(
                [
                    "gh",
                    "release",
                    "delete",
                    f"{last_valid_version}",
                    "--cleanup-tag",
                    "--yes",
                ],
                check=True,
            )
            create_tagged_release(last_valid_version)
        return

    for version in target_versions:
        paths = process_version(version)
        if subprocess.check_output(["git", "status", "-s"]).strip():
            push_changed_version(paths, f"Mirror: {version}")
            create_tagged_release(version)
        else:
            print(f"No change {version}")


def push_changed_version(paths: typing.Sequence[str], commit_message: str) -> None:
    subprocess.run(["git", "add", *paths], check=True)
    subprocess.run(["git", "commit", "-m", commit_message], check=True)
    subprocess.run(["git", "push", "origin", "HEAD:refs/heads/main"], check=True)


def create_tagged_release(version: Version) -> None:
    subprocess.run(["git", "tag", f"{version}"], check=True)
    subprocess.run(
        ["git", "push", "origin", "HEAD:refs/heads/main", "--tags"], check=False
    )
    subprocess.run(
        [
            "gh",
            "release",
            "create",
            f"{version}",
            "--title",
            f"{version}",
            "--notes",
            f"See: https://github.com/astral-sh/uv/releases/tag/{version}",
            "--latest",
        ],
        check=False,
    )


def get_all_releases() -> dict[Version, list[dict[str, typing.Any]]]:
    response = urllib3.request("GET", "https://pypi.org/pypi/uv/json")
    if response.status != 200:
        raise RuntimeError("Failed to fetch versions from pypi")

    return {
        Version(release_version): release
        for release_version, release in response.json()["releases"].items()
    }


def get_current_version(pyproject: dict) -> Version:
    requirements = [Requirement(d) for d in pyproject["project"]["dependencies"]]
    requirement = next((r for r in requirements if r.name == "uv"), None)
    assert requirement is not None, "pyproject.toml does not have uv requirement"

    specifiers = list(requirement.specifier)
    assert (
        len(specifiers) == 1 and specifiers[0].operator == "=="
    ), f"uv's specifier should be exact matching, but `{requirement}`"

    return Version(specifiers[0].version)


def process_version(version: Version) -> typing.Sequence[str]:
    def replace_pyproject_toml(content: str) -> str:
        return re.sub(r'"uv==.*"', f'"uv=={version}"', content)

    def replace_readme_md(content: str) -> str:
        content = re.sub(r"rev: \d+\.\d+\.\d+", f"rev: {version}", content)
        return re.sub(r"/uv/\d+\.\d+\.\d+\.svg", f"/uv/{version}.svg", content)

    paths = {
        "pyproject.toml": replace_pyproject_toml,
        "README.md": replace_readme_md,
    }

    for path, replacer in paths.items():
        with open(path) as f:
            content = replacer(f.read())
        with open(path, mode="w") as f:
            f.write(content)

    return tuple(paths.keys())


if __name__ == "__main__":
    main()
