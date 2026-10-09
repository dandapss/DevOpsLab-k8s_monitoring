"""Pure helpers used by the exporter and its unit tests."""


def count_by(items, key_fn):
    """Count items by a tuple key returned by key_fn."""
    counts = {}
    for item in items:
        key = key_fn(item)
        counts[key] = counts.get(key, 0) + 1
    return counts
