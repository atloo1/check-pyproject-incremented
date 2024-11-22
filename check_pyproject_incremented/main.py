import re
import subprocess
from typing import Tuple


def main() -> Tuple[int, str]:
    """
    return 1 if feature branch version needs incrementing, else 0

    compare pyproject.toml semvers when both branches != 'main'
    """
    this_branch_name = _get_this_branch_name()
    if this_branch_name == 'main':
        return 0, 'no comparison performed: this branch is main'

    main_version = _get_main_version()
    this_branch_version = _get_this_branch_version()
    main_version_tuple = _get_version_tuple(main_version)
    this_branch_version_tuple = _get_version_tuple(this_branch_version)
    sorted_version_tuples = sorted(
        {main_version_tuple, this_branch_version_tuple},
        key=lambda x: (x[0], x[1], x[2]),
    )

    this_branch_ahead_of_main = (
        len(sorted_version_tuples) == 2 and this_branch_version_tuple == sorted_version_tuples[1]
    )
    return_code = 0 if this_branch_ahead_of_main else 1
    comparator = '≤' if return_code else '>'
    message = f'this branch ({this_branch_name}) version {this_branch_version} {comparator} main ({main_version})'
    return return_code, message


def _get_this_branch_name() -> str:
    this_branch_name = subprocess.run(
        'git rev-parse --abbrev-ref HEAD',
        shell=True,
        stdout=subprocess.PIPE,
        text=True,
    ).stdout.strip()
    return this_branch_name


def _get_main_version() -> str:
    subprocess.run('git fetch origin main:main', shell=True)
    main_pyproject_content = subprocess.run(
        'git show main:pyproject.toml',
        shell=True,
        stdout=subprocess.PIPE,
        text=True,
    ).stdout
    main_version = _get_version_str(main_pyproject_content)
    return main_version


def _get_this_branch_version() -> str:
    with open('pyproject.toml') as f:
        this_branch_pyproject_content = f.read()
    this_branch_version = _get_version_str(this_branch_pyproject_content)
    return this_branch_version


def _get_version_tuple(semver: str) -> Tuple[int, ...]:
    version = tuple(map(int, semver.split('.')))
    return version


def _get_version_str(stdout: str) -> str:
    version_match = re.search(r'^version = "([^"]+)"', stdout, re.MULTILINE)
    if version_match is None:
        raise ValueError('no version info in stdout')
    version = version_match.group(1)
    return version


if __name__ == '__main__':
    return_code, message = main()
    print(message)
    raise SystemExit(return_code)
