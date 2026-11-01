"""Update the architecture-specific Harbor cask only after validating both assets."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ARCHES = {"arm": "Apple-Silicon", "intel": "Intel"}
BASE_URL = "https://github.com/thsnkhn/harbor/releases/download"


def select_assets(release):
    tag = release.get("tag_name", "")
    if not re.fullmatch(r"v[0-9]+(?:\.[0-9]+){2}", tag):
        raise ValueError(f"Invalid Harbor release tag: {tag!r}")
    version = tag[1:]
    assets = {}
    for arch, suffix in ARCHES.items():
        name = f"Harbor-{version}-{suffix}.dmg"
        matches = [asset for asset in release.get("assets", []) if asset.get("name") == name]
        if len(matches) != 1:
            raise ValueError(f"Expected exactly one release asset named {name}; found {len(matches)}")
        asset = matches[0]
        if asset.get("browser_download_url") != f"{BASE_URL}/{tag}/{name}":
            raise ValueError(f"Unexpected download URL for {name}")
        assets[arch] = asset
    return version, assets


def download_sha256(asset):
    with tempfile.TemporaryDirectory() as directory:
        target = Path(directory) / asset["name"]
        subprocess.run([
            "curl", "--fail", "--location", "--retry", "3", "--silent", "--show-error",
            "--proto", "=https", "--proto-redir", "=https",
            "--output", str(target), asset["browser_download_url"],
        ], check=True)
        digest = hashlib.sha256()
        with target.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()


def replace_once(pattern, replacement, content, description):
    result, count = re.subn(pattern, replacement, content, flags=re.MULTILINE)
    if count != 1:
        raise ValueError(f"Expected exactly one {description}; found {count}")
    return result


def update_cask(release, path, downloader=download_sha256):
    version, assets = select_assets(release)
    original = path.read_text()
    # Fail closed if the cask's URL/architecture layout has changed.
    expected_url = f'  url "{BASE_URL}/v#{{version}}/Harbor-#{{version}}-#{{arch}}.dmg"'
    if expected_url not in original.splitlines() or '  arch arm: "Apple-Silicon", intel: "Intel"' not in original.splitlines():
        raise ValueError("Unexpected cask architecture or URL layout")
    updated = replace_once(r'^  version "[^"]+"$', f'  version "{version}"', original, "version")
    for arch, asset in assets.items():
        checksum = downloader(asset)
        if not re.fullmatch(r"[0-9a-f]{64}", checksum):
            raise ValueError(f"Invalid SHA256 for {asset['name']}")
        if asset.get("digest") and asset["digest"] != f"sha256:{checksum}":
            raise ValueError(f"Release digest mismatch for {asset['name']}")
        updated = replace_once(
            rf'(^  on_{arch} do\n    sha256 ")[^"]+("\n  end$)',
            lambda match: match[1] + checksum + match[2], updated, f"{arch} checksum block",
        )
    # Nothing is written unless both downloads, digests and replacements succeed.
    if updated != original:
        path.write_text(updated)
    return version


if __name__ == "__main__":
    try:
        release = json.loads(Path(sys.argv[1]).read_text())
        print(update_cask(release, Path("Casks/harbor.rb")))
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        sys.exit(f"Harbor cask update failed: {error}")
