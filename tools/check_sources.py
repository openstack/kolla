# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import os
import re
import shutil
import subprocess  # nosec
import sys
import textwrap

import requests

sys.path.append(os.getcwd())

from kolla.common.sources import SOURCES  # noqa: E402


def github_headers():
    """Return auth headers if GITHUB_TOKEN is set, otherwise empty dict."""
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        return {'Authorization': f'Bearer {token}'}
    return {}


def check_github_rate_limit():
    """Warn if GitHub API rate limit is exhausted or nearly so."""
    try:
        response = requests.get(
            "https://api.github.com/rate_limit",
            headers=github_headers(), timeout=10)
        if response.status_code != 200:
            return
        data = response.json()['rate']
        remaining = data['remaining']
        limit = data['limit']
        if remaining == 0:
            print(f"ERROR: GitHub API rate limit exhausted "
                  f"(0/{limit}). Set GITHUB_TOKEN to raise the limit.")
            sys.exit(1)
        if remaining < 10:
            print(f"WARNING: GitHub API rate limit low "
                  f"({remaining}/{limit} remaining).")
    except Exception:
        print("ERROR: Could not check GitHub rate limits")
        raise


_PRERELEASE_RE = re.compile(r'alpha|beta|rc', re.IGNORECASE)


def is_prerelease(tag, release_data=None):
    if release_data and release_data.get('prerelease'):
        return True
    return bool(_PRERELEASE_RE.search(tag))


def get_github_details(location):
    """Extracts user and repo from GitHub URL."""
    match = re.search(r'github\.com/([^/]+)/([^/]+)', location)
    if not match:
        return None, None
    user, repo = match.groups()
    repo = repo.replace('.git', '').split('/')[0]
    return user, repo


def get_latest_release_info(user, repo, arch_map, lts_branch=None):
    """Fetch latest tag and find sha256 checksums from assets.

    :param user: GitHub username
    :param repo: GitHub repository name
    :param arch_map: dict of {kolla_arch: github_arch_string}
    :param lts_branch: if set (e.g. '3.5'), only consider releases in that
                       major.minor series
    :returns: tuple (tag, hashes_dict)
    """
    url = f"https://api.github.com/repos/{user}/{repo}/releases/latest"
    if lts_branch:
        url = (f"https://api.github.com/repos/{user}/{repo}/releases?"
               f"per_page=100")
    try:
        response = requests.get(url, headers=github_headers(), timeout=10)
        if response.status_code not in (200, 404):
            return None, {}

        if lts_branch and response.status_code == 200:
            releases = [
                r for r in response.json()
                if not is_prerelease(r['tag_name'].lstrip('v'), r)
                and r['tag_name'].lstrip('v').startswith(lts_branch + '.')
            ]
            if not releases:
                return None, {}
            data = releases[0]
        elif response.status_code == 404:
            tag_resp = requests.get(
                f"https://api.github.com/repos/{user}/{repo}/tags",
                headers=github_headers(), timeout=10)
            if tag_resp.status_code == 200 and tag_resp.json():
                stable_tags = [t for t in tag_resp.json()
                               if not is_prerelease(t['name'].lstrip('v'))]
                if stable_tags:
                    tag = stable_tags[0]['name'].lstrip('v')
                    return tag, {}
            return None, {}

        else:
            data = response.json()
        tag = data['tag_name'].lstrip('v')

        if is_prerelease(tag, data):
            rel_resp = requests.get(
                f"https://api.github.com/repos/{user}/{repo}/releases",
                headers=github_headers(), timeout=10)
            if rel_resp.status_code != 200:
                return None, {}
            stable = next((r for r in rel_resp.json()
                           if not is_prerelease(r['tag_name'].lstrip('v'), r)),
                          None)
            if not stable:
                return None, {}
            tag = stable['tag_name'].lstrip('v')
            data = stable

        hashes = {}

        # Try reading sha256 from the digest field on each asset directly.
        # Skip supplementary files (sbom, sig, etc.)
        skip_suffixes = ('.sbom.json', '.sig', '.pem', '.crt', '.asc')
        for asset in data['assets']:
            digest = asset.get('digest', '')
            if not digest.startswith('sha256:'):
                continue
            if any(asset['name'].endswith(s) for s in skip_suffixes):
                continue
            sha = digest.split(':', 1)[1]
            for kolla_arch, github_arch in arch_map.items():
                # Match flexibly: split on - or _ and check each part is there.
                # This handles both linux-amd64 and linux_amd64 naming styles.
                parts = re.split(r'[-_]', github_arch)
                if all(p in asset['name'] for p in parts):
                    hashes[kolla_arch] = sha

        # Fall back to a separate checksum file if digests weren't found
        if len(hashes) < len(arch_map):
            checksum_asset = next(
                (a for a in data['assets'] if "checksum" in a['name'].lower()
                 or "sha256" in a['name'].lower()), None
            )

            if checksum_asset:
                sum_resp = requests.get(
                    checksum_asset['browser_download_url'], timeout=10)
                if sum_resp.status_code == 200:
                    content = sum_resp.text
                    for kolla_arch, github_arch in arch_map.items():
                        if kolla_arch not in hashes:
                            # Accept both - and _ as separators in filenames
                            flexible = github_arch.replace('-', '[-_]')
                            pattern = rf"([a-fA-F0-9]{{64}})\s+.*{flexible}.*"
                            match = re.search(pattern, content)
                            if match:
                                hashes[kolla_arch] = match.group(1)

        return tag, hashes
    except Exception:
        return None, {}


def get_helm_sh_hashes(version, arch_map):
    """Fetch sha256 checksums from get.helm.sh for a given Helm version.

    :param version: version string (with or without leading 'v')
    :param arch_map: dict of {kolla_arch: github_arch_string}
    :returns: dict of {kolla_arch: sha256_hex}
    """
    hashes = {}
    version = version.lstrip('v')
    for kolla_arch, github_arch in arch_map.items():
        url = (f"https://get.helm.sh/helm-v{version}"
               f"-{github_arch}.tar.gz.sha256sum")
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                sha = resp.text.split()[0]
                if re.match(r'^[a-fA-F0-9]{64}$', sha):
                    hashes[kolla_arch] = sha
        except Exception:
            print("ERROR: GitHub connection failed")
            raise
    return hashes


SOURCES_PATH = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 '..', 'kolla', 'common', 'sources.py'))


def apply_update(name, info, new_v, new_hashes):
    """Update version and sha256 entries for one source in sources.py."""
    with open(SOURCES_PATH) as f:
        content = f.read()

    version_key = 'reference' if info.get('type') == 'git' else 'version'
    old_v = info.get(version_key, '')
    if old_v:
        new_v_str = ('v' + new_v) if old_v.startswith('v') else new_v
        content = content.replace(
            f"'{version_key}': '{old_v}'",
            f"'{version_key}': '{new_v_str}'", 1)

    for arch, new_sha in new_hashes.items():
        old_sha = info.get('sha256', {}).get(arch, '')
        if old_sha and old_sha != new_sha:
            content = content.replace(old_sha, new_sha)

    with open(SOURCES_PATH, 'w') as f:
        f.write(content)


REPO_ROOT = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


def create_releasenote(changes):
    """Create a reno release note listing all updated components.

    :param changes: list of (name, old_version, new_version) tuples
    """
    if len(changes) == 1:
        slug = f"update-{changes[0][0]}"
    else:
        slug = "update-external-components"

    result = subprocess.run(  # nosec
        ['reno', 'new', slug, REPO_ROOT],
        capture_output=True, text=True)

    if result.returncode != 0:
        print(f"ERROR: reno failed: {result.stderr.strip()}")
        return

    # reno prints: "Created new notes file in <path>"
    note_path = result.stdout.strip().split()[-1]

    lines = ["---", "upgrade:"]
    for name, old_v, new_v in changes:
        lines.append("  - |")
        text = (f"``{name}`` has been updated from "
                f"``{old_v.lstrip('v')}`` to ``{new_v.lstrip('v')}``.")
        lines.append(textwrap.fill(
            text, width=79, initial_indent='    ',
            subsequent_indent='    '))

    with open(note_path, 'w') as f:
        f.write('\n'.join(lines) + '\n')

    print(f"Created release note: {note_path}")


def check_versions(update=False):
    """Monitor Kolla architectures and compare with latest releases."""
    check_github_rate_limit()
    arch_map = {'amd64': 'linux-amd64', 'arm64': 'linux-arm64'}
    version_changes = []

    header = (f"{'COMPONENT':<40} | {'CURR VER':<10} | "
              f"{'LATEST':<15} | {'ARCH':<7} | {'NEW SHA256'}")
    print(header)
    print("-" * 110)

    for name, info in SOURCES.items():
        current_v = info.get('version') or info.get('reference', '')
        if not re.match(r'^v?\d+[\.\d]+', current_v or ''):
            current_v = None
        location = info.get('location', '')
        github = info.get('github', '')

        if current_v and ('github.com' in location or github):
            if github:
                user, repo = github.split('/', 1)
            else:
                user, repo = get_github_details(location)
            if not user:
                continue

            latest_v, new_hashes = get_latest_release_info(
                user, repo, arch_map,
                lts_branch=info.get('lts_branch')
            )

            if latest_v and len(new_hashes) < len(arch_map):
                if 'get.helm.sh' in location:
                    new_hashes.update(get_helm_sh_hashes(latest_v, arch_map))

            if latest_v:
                status_v = "UPDATE" if latest_v != current_v.lstrip('v') \
                           else "OK"

                lines_to_print = []
                for arch in arch_map.keys():
                    new_sha = new_hashes.get(arch, 'Not Found')
                    current_sha = info.get('sha256', {}).get(arch)

                    line = (f"{name:<40} | {current_v:<10} | "
                            f"{latest_v:<15} | {arch:<7} | {new_sha}")

                    if status_v == "UPDATE" or (new_sha != 'Not Found'
                       and new_sha != current_sha):
                        lines_to_print.append(line)

                for line in lines_to_print:
                    print(line)

                if update and lines_to_print:
                    apply_update(name, info, latest_v, new_hashes)
                    if status_v == "UPDATE":
                        version_changes.append(
                            (name, current_v, latest_v))

    if update and version_changes:
        create_releasenote(version_changes)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Check and optionally update Kolla source versions.')
    parser.add_argument('--update', action='store_true',
                        help='Update kolla/common/sources.py in place')
    args = parser.parse_args()
    if args.update and not shutil.which('reno'):
        print("ERROR: 'reno' is not installed or not in PATH. "
              "Install it with: pip install reno")
        sys.exit(1)
    check_versions(update=args.update)
