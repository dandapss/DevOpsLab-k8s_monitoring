"""Basic edge-case coverage for the exporter's pure aggregation helper."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from metric_helpers import count_by


def test_empty_resource_list_has_no_count_series():
    assert count_by([], lambda item: item) == {}
