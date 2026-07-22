from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from typing import Any


API_VERSION = "2022-11-28"
DEFAULT_RELEASE_TAG = "instagram-media"


class GitHubApiError(RuntimeError):
    pass


def parse_github_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def plan_cleanup(
    assets: list[dict[str, Any]],
    *,
    now: datetime,
    retention_days: int,
    max_total_bytes: int,
    target_total_bytes: int,
) -> list[dict[str, Any]]:
    if retention_days < 1:
        raise ValueError("retention_days must be at least 1")
    if target_total_bytes > max_total_bytes:
        raise ValueError("target_total_bytes must not exceed max_total_bytes")

    cutoff = now - timedelta(days=retention_days)
    selected_ids = {
        int(asset["id"])
        for asset in assets
        if parse_github_datetime(str(asset["created_at"])) < cutoff
    }

    remaining = [asset for asset in assets if int(asset["id"]) not in selected_ids]
    remaining_bytes = sum(int(asset.get("size", 0)) for asset in remaining)

    if remaining_bytes > max_total_bytes:
        for asset in sorted(
            remaining,
            key=lambda item: parse_github_datetime(str(item["created_at"])),
        ):
            selected_ids.add(int(asset["id"]))
            remaining_bytes -= int(asset.get("size", 0))
            if remaining_bytes <= target_total_bytes:
                break

    return sorted(
        [asset for asset in assets if int(asset["id"]) in selected_ids],
        key=lambda item: parse_github_datetime(str(item["created_at"])),
    )


class GitHubClient:
    def __init__(self, *, repository: str, token: str = "") -> None:
        self.repository = repository
        self.token = token
        self.base_url = f"https://api.github.com/repos/{repository}"

    def _request(self, path: str, *, method: str = "GET") -> Any:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": "misa-public-media-cleanup",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            headers=headers,
            method=method,
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                if response.status == 204:
                    return None
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return None
            body = exc.read().decode("utf-8", errors="replace")
            message = f"GitHub API HTTP {exc.code}"
            try:
                message = json.loads(body).get("message", message)
            except json.JSONDecodeError:
                pass
            raise GitHubApiError(message) from exc
        except urllib.error.URLError as exc:
            raise GitHubApiError(f"network error: {exc.reason}") from exc

    def list_release_assets(self, tag: str) -> list[dict[str, Any]]:
        encoded_tag = urllib.parse.quote(tag, safe="")
        release = self._request(f"/releases/tags/{encoded_tag}")
        if release is None:
            return []
        release_id = int(release["id"])
        assets: list[dict[str, Any]] = []
        page = 1
        while True:
            batch = self._request(
                f"/releases/{release_id}/assets?per_page=100&page={page}"
            )
            if not batch:
                break
            assets.extend(batch)
            if len(batch) < 100:
                break
            page += 1
        return assets

    def delete_release_asset(self, asset_id: int) -> None:
        if not self.token:
            raise GitHubApiError("GITHUB_TOKEN is required for deletion")
        self._request(f"/releases/assets/{asset_id}", method="DELETE")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Clean old public Instagram media assets")
    parser.add_argument("--release-tag", default=DEFAULT_RELEASE_TAG)
    parser.add_argument("--retention-days", type=int, default=30)
    parser.add_argument("--max-total-mb", type=int, default=5000)
    parser.add_argument("--target-total-mb", type=int, default=4000)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repository = os.environ.get("GITHUB_REPOSITORY", "misa-yoru/misa-public-media")
    client = GitHubClient(
        repository=repository,
        token=os.environ.get("GITHUB_TOKEN", ""),
    )
    try:
        assets = client.list_release_assets(args.release_tag)
        if not assets:
            print("no release assets found")
            return 0

        to_delete = plan_cleanup(
            assets,
            now=datetime.now(timezone.utc),
            retention_days=args.retention_days,
            max_total_bytes=args.max_total_mb * 1024 * 1024,
            target_total_bytes=args.target_total_mb * 1024 * 1024,
        )
        if not to_delete:
            total_mb = sum(int(asset.get("size", 0)) for asset in assets) / 1024 / 1024
            print(f"nothing to delete; {len(assets)} asset(s), {total_mb:.1f} MB")
            return 0

        for asset in to_delete:
            name = str(asset.get("name", asset["id"]))
            if args.dry_run:
                print(f"would delete: {name}")
            else:
                client.delete_release_asset(int(asset["id"]))
                print(f"deleted: {name}")
        return 0
    except (GitHubApiError, ValueError) as exc:
        print(f"cleanup error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
