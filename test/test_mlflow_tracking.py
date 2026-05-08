from pathlib import Path
import sys
from types import SimpleNamespace

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from utils.config_loader import load_config
import utils.mlflow_tracking as tracking


class FakeMlflow:
    def __init__(self):
        self.calls = []

    def set_tracking_uri(self, uri):
        self.calls.append(("set_tracking_uri", uri))

    def set_experiment(self, name):
        self.calls.append(("set_experiment", name))

    def start_run(self, run_name=None, tags=None):
        self.calls.append(("start_run", run_name, tags))
        return SimpleNamespace(info="run")

    def end_run(self):
        self.calls.append(("end_run",))

    def log_params(self, params):
        self.calls.append(("log_params", params))

    def log_metrics(self, metrics, step=None):
        self.calls.append(("log_metrics", metrics, step))

    def log_artifact(self, path, artifact_path=None):
        self.calls.append(("log_artifact", path, artifact_path))


def test_configure_mlflow_resolves_local_uri(monkeypatch):
    cfg = load_config()
    fake_mlflow = FakeMlflow()
    monkeypatch.setattr(tracking, "mlflow", fake_mlflow)

    uri = tracking.configure_mlflow(cfg)

    assert uri.startswith("file:///")
    assert ("set_experiment", cfg.mlflow.tracking.experiment_name) in fake_mlflow.calls


def test_start_mlflow_run_is_noop_when_disabled(monkeypatch):
    cfg = load_config(overrides=["mlflow.tracking.enabled=false"])
    fake_mlflow = FakeMlflow()
    monkeypatch.setattr(tracking, "mlflow", fake_mlflow)

    with tracking.start_mlflow_run(cfg, run_name="disabled-run") as active_run:
        assert active_run is None

    assert fake_mlflow.calls == []
