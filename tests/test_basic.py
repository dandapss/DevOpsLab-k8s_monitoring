import importlib.util
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from kubernetes import config
from prometheus_client.parser import text_string_to_metric_families


@pytest.fixture
def exporter(monkeypatch):
    # The exporter normally loads in-cluster credentials when its module starts.
    # Disable that setup so this unit test can supply mocked Kubernetes APIs.
    monkeypatch.setattr(config, "load_incluster_config", lambda: None)

    source_path = Path(__file__).resolve().parents[1] / "src" / "main.py"
    spec = importlib.util.spec_from_file_location("monitor_exporter", source_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _namespace(name):
    return SimpleNamespace(
        metadata=SimpleNamespace(name=name),
        status=SimpleNamespace(phase="Active"),
    )


def _deployment(namespace):
    return SimpleNamespace(
        metadata=SimpleNamespace(namespace=namespace),
        spec=SimpleNamespace(replicas=1),
        status=SimpleNamespace(ready_replicas=1),
    )


def test_namespace_deployment_counts_use_the_existing_clusterwide_list(
    exporter, monkeypatch, capsys
):
    core_api = Mock()
    core_api.list_pod_for_all_namespaces.return_value = SimpleNamespace(items=[])
    core_api.list_namespace.return_value = SimpleNamespace(
        items=[_namespace("platform"), _namespace("apps"), _namespace("empty")]
    )
    core_api.list_event_for_all_namespaces.return_value = SimpleNamespace(items=[])

    apps_api = Mock()
    apps_api.list_deployment_for_all_namespaces.return_value = SimpleNamespace(
        items=[
            _deployment("platform"),
            _deployment("platform"),
            _deployment("apps"),
        ]
    )

    monkeypatch.setattr(exporter, "v1", core_api)
    monkeypatch.setattr(exporter, "apps1", apps_api)

    exporter.collect_metrics()
    capsys.readouterr()

    namespace_counts = {
        (sample.labels["NS_Name"], sample.labels["State"]): sample.value
        for family in text_string_to_metric_families(
            exporter.generate_latest(exporter.registry).decode("utf-8")
        )
        for sample in family.samples
        if sample.name == "k8s_namespace"
    }

    assert namespace_counts == {
        ("platform", "Active"): 2,
        ("apps", "Active"): 1,
        ("empty", "Active"): 0,
    }
    apps_api.list_deployment_for_all_namespaces.assert_called_once_with(
        _request_timeout=5
    )
    apps_api.list_namespaced_deployment.assert_not_called()
