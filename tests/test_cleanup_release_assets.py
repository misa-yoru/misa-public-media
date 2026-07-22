import unittest
from datetime import datetime, timezone

from scripts.cleanup_release_assets import plan_cleanup


def asset(asset_id: int, *, days_old: int, size_mb: int):
    day = 22 - days_old
    if day >= 1:
        created_at = f"2026-07-{day:02d}T00:00:00Z"
    else:
        created_at = "2026-06-01T00:00:00Z"
    return {
        "id": asset_id,
        "name": f"image-{asset_id}.jpg",
        "created_at": created_at,
        "size": size_mb * 1024 * 1024,
    }


class CleanupPlanTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 7, 22, tzinfo=timezone.utc)

    def test_deletes_assets_older_than_retention(self):
        assets = [
            asset(1, days_old=0, size_mb=1),
            asset(2, days_old=31, size_mb=1),
        ]
        selected = plan_cleanup(
            assets,
            now=self.now,
            retention_days=30,
            max_total_bytes=500 * 1024 * 1024,
            target_total_bytes=400 * 1024 * 1024,
        )
        self.assertEqual([item["id"] for item in selected], [2])

    def test_keeps_recent_assets_below_limit(self):
        assets = [
            asset(1, days_old=0, size_mb=100),
            asset(2, days_old=1, size_mb=100),
        ]
        selected = plan_cleanup(
            assets,
            now=self.now,
            retention_days=30,
            max_total_bytes=500 * 1024 * 1024,
            target_total_bytes=400 * 1024 * 1024,
        )
        self.assertEqual(selected, [])

    def test_deletes_oldest_until_target_size(self):
        assets = [
            asset(1, days_old=2, size_mb=200),
            asset(2, days_old=1, size_mb=200),
            asset(3, days_old=0, size_mb=200),
        ]
        selected = plan_cleanup(
            assets,
            now=self.now,
            retention_days=30,
            max_total_bytes=500 * 1024 * 1024,
            target_total_bytes=400 * 1024 * 1024,
        )
        self.assertEqual([item["id"] for item in selected], [1])

    def test_rejects_target_above_maximum(self):
        with self.assertRaises(ValueError):
            plan_cleanup(
                [],
                now=self.now,
                retention_days=30,
                max_total_bytes=400,
                target_total_bytes=500,
            )


if __name__ == "__main__":
    unittest.main()
