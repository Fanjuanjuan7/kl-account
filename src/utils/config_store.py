from pathlib import Path
import json


DEFAULTS = {
    "api_base": "http://127.0.0.1:54345",
    "platform_url": "https://klingai.com",
    "group_id": "",
    "concurrency": 3,
    "interval_ms": 300,
    "auto": True,
    "csv_path": "",
    "xpath_path": ""
}


def config_path(runtime_dir: Path) -> Path:
    return runtime_dir / "config.json"


def load_config(runtime_dir: Path) -> dict:
    p = config_path(runtime_dir)
    if p.exists():
        try:
            return {**DEFAULTS, **json.loads(p.read_text(encoding="utf-8"))}
        except Exception:
            return dict(DEFAULTS)
    return dict(DEFAULTS)


def save_config(runtime_dir: Path, cfg: dict):
    p = config_path(runtime_dir)
    p.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")


def reset_config(runtime_dir: Path):
    save_config(runtime_dir, DEFAULTS)

