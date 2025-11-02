import sys
import os
import json
import traceback
from datetime import datetime
from pathlib import Path
import argparse


try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def _supports_emoji():
    try:
        "✅".encode(sys.stdout.encoding)
        return True
    except Exception:
        return False

_USE_EMOJI = _supports_emoji()
ICON = {
    "ok": "✅" if _USE_EMOJI else "[OK]",
    "fail": "❌" if _USE_EMOJI else "[FAIL]",
    "run": "🚀" if _USE_EMOJI else "[RUN]",
    "info": "💡" if _USE_EMOJI else "[INFO]",
}

def load_config():
  
    yaml_path = PROJECT_ROOT / "config.yaml"
    json_path = PROJECT_ROOT / "config.json"

  
    if yaml_path.exists():
        try:
            import yaml  
            with yaml_path.open("r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
                print(f"{ICON['info']} Loaded config.yaml")
                return cfg
        except Exception as e:
            print(f"{ICON['fail']} Could not load config.yaml: {e}")

  
    if json_path.exists():
        try:
            with json_path.open("r", encoding="utf-8") as f:
                cfg = json.load(f)
                print(f"{ICON['info']} Loaded config.json")
                return cfg
        except Exception as e:
            print(f"{ICON['fail']} Could not load config.json: {e}")

 
    print(f"{ICON['info']} No config file found — using fallback defaults.")
    return {
        "projects": ["SPARK", "HADOOP", "KAFKA"],
        "scraping": {"max_issues_per_project": 50},
        "api": {"base_url": "https://issues.apache.org/jira/rest/api/2", "rate_limit_delay": 1},
        "output": {"raw_dir": "data/raw", "final_output": "output/training_data.jsonl"},
    }

def ensure_paths(cfg):
 
    raw_dir = Path(cfg.get("output", {}).get("raw_dir", "data/raw"))
    raw_dir.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def run_scraper(cfg, project=None):

    try:
        from scraper.jira_scraper import JiraScraper  
    except Exception as e:
        print(f"{ICON['fail']} Could not import JiraScraper: {e}")
        traceback.print_exc()
        return False

    try:
        print(f"\n{ICON['run']} Starting scraper")
        scraper = JiraScraper(cfg)
        projects = [project] if project else cfg.get("projects", [])
        for p in projects:
            print(f"{ICON['info']} Scraping project: {p}")
            try:
                scraper.scrape_project(p)
                print(f"{ICON['ok']} Finished scraping: {p}")
            except Exception as e:
                print(f"{ICON['fail']} Error while scraping {p}: {e}")
                traceback.print_exc()
                
        print(f"{ICON['ok']} Scraping done.")
        return True
    except Exception:
        print(f"{ICON['fail']} Scraper phase failed:")
        traceback.print_exc()
        return False

def run_transformer(cfg):
    """
    Import and run the data transformer.
    Returns True on success, False on error.
    """
    try:
        from transformer.data_transformer import Transformer
    except Exception as e:
        print(f"{ICON['fail']} Could not import Transformer: {e}")
        traceback.print_exc()
        return False

    try:
        print(f"\n{ICON['run']} Starting transformer")
        transformer = Transformer(cfg)
        if hasattr(transformer, "run"):
            transformer.run()
            print(f"{ICON['ok']} Transformer.run() finished.")
        elif hasattr(transformer, "transform_to_jsonl"):
            transformer.transform_to_jsonl()
            print(f"{ICON['ok']} transform_to_jsonl() finished.")
        else:
            print(f"{ICON['info']} No recognized transformer method found; nothing to run.")
        return True
    except Exception:
        print(f"{ICON['fail']} Transformer phase failed:")
        traceback.print_exc()
        return False

def write_run_log(start_time, end_time, actions, ok):
    """
    Write a small JSON run log in output/ for reproducibility and debugging.
    """
    fname = OUTPUT_DIR / f"run_log_{start_time.strftime('%Y%m%d_%H%M%S')}.json"
    payload = {
        "start": start_time.isoformat(),
        "end": end_time.isoformat(),
        "duration_seconds": (end_time - start_time).total_seconds(),
        "actions": actions,
        "success": ok,
    }
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"{ICON['info']} Run log saved: {fname}")

def parse_args():
    p = argparse.ArgumentParser(description="Run Jira LLM pipeline (scraper + transformer).")
    p.add_argument("--mode", choices=["scrape", "transform", "all"], default="all", help="Which part to run.")
    p.add_argument("--project", default=None, help="Single project key to scrape (e.g. SPARK).")
    return p.parse_args()

def main():
    """
    Main entry point.
    Loads config, ensures directories, runs requested phases, logs results.
    """
    args = parse_args()
    cfg = load_config()

 
    if "output" not in cfg:
        cfg["output"] = {"raw_dir": "data/raw", "final_output": "output/training_data.jsonl"}

    ensure_paths(cfg)

    start = datetime.utcnow()
    print(f"\n=== Jira LLM Pipeline — starting ({start.isoformat()}) ===\n")

    actions = []
    ok = True

    if args.mode in ("scrape", "all"):
        actions.append("scrape")
        ok_scrape = run_scraper(cfg, project=args.project)
        ok = ok and ok_scrape
        if not ok_scrape:
            print(f"{ICON['fail']} Some scraping tasks failed. You can retry a single project with --project <KEY>.")

    if args.mode in ("transform", "all"):
        actions.append("transform")
        if ok:  
            ok_transform = run_transformer(cfg)
            ok = ok and ok_transform
        else:
            print(f"{ICON['info']} Skipping transformer because previous step failed.")

    end = datetime.utcnow()
    print(f"\n=== Pipeline finished at {end.isoformat()} — success: {ok} ===\n")

    write_run_log(start, end, actions, ok)

  
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
