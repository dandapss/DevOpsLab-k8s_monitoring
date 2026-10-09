"""Unit tests for deterministic aggregation used by the exporter."""

import sys
from pathlib import Path

# CI and local pytest can import the production helper without Kubernetes access.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from metric_helpers import count_by


def test_count_by_groups_equal_keys():
    assert count_by([("team-a", "Running"), ("team-a", "Running"), ("team-b", "Pending")], lambda row: row) == {
        ("team-a", "Running"): 2,
        ("team-b", "Pending"): 1,
    }


def test_count_by_returns_empty_mapping_for_no_items():
    assert count_by([], lambda item: item) == {}
