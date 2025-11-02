import os
import subprocess
import sys
import time
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')


def supports_emoji():
    try:
        "✅".encode(sys.stdout.encoding)
        return True
    except Exception:
        return False

USE_EMOJI = supports_emoji()

ICON = {
    "ok": "✅" if USE_EMOJI else "[OK]",
    "fail": "❌" if USE_EMOJI else "[FAIL]",
    "run": "🚀" if USE_EMOJI else "[RUN]",
    "work": "⚙️" if USE_EMOJI else "[WORK]",
    "info": "💡" if USE_EMOJI else "[INFO]",
}

# --- Config ---
PROJECTS = ["HADOOP", "SPARK", "KAFKA"]
DATA_DIR = "data/raw"
OUTPUT_FILE = "output/training_data.jsonl"

def clear():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    """Pause before returning to main menu."""
    input("\nPress ENTER to return to the menu...")

def banner():
    """Print the app banner."""
    print("=" * 70)
    print(f"{ICON['run']}  Jira LLM Pipeline Dashboard")
    print("=" * 70)

def run_command(command):
    """Run a command in a subprocess and show its output live."""
    print(f"\n{ICON['info']} Running: {command}\n{'-'*70}")
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    while True:
        line = process.stdout.readline()
        if not line:
            break
        print(line, end="")
    process.wait()
    code = process.returncode
    print(f"\n{'-'*70}\nProcess exited with code {code}.")
    pause()


def run_scraper(project=None):
    """Run the scraper for one or all projects."""
    if project:
        print(f"\n{ICON['work']} Scraping JIRA data for project: {project}")
        cmd = f'{sys.executable} -c "from run_pipeline import load_config; cfg = load_config(); from scraper.jira_scraper import JiraScraper; JiraScraper(cfg).scrape_project(\'{project}\')"'
    else:
        print(f"\n{ICON['work']} Running scraper for all configured projects...")
        cmd = f"{sys.executable} run_pipeline.py --mode scrape"
    run_command(cmd)

def run_transformer():
    """Run the transformer phase only."""
    print(f"\n{ICON['work']} Running Transformer (data cleaning + dataset generation)...")
    cmd = f"{sys.executable} run_pipeline.py --mode transform"
    run_command(cmd)

def run_full_pipeline():
    """Run the full pipeline: scraper + transformer."""
    print(f"\n{ICON['run']} Running full pipeline (Scraper + Transformer)...")
    cmd = f"{sys.executable} run_pipeline.py"
    run_command(cmd)

def show_stats():
    """Display a quick overview of pipeline data."""
    print(f"\n{ICON['info']} Data Summary\n" + "-" * 70)
    raw_count = len(os.listdir(DATA_DIR)) if os.path.exists(DATA_DIR) else 0
    print(f"🗂️  Raw issues scraped: {raw_count}")
    if os.path.exists(OUTPUT_FILE):
        size_kb = os.path.getsize(OUTPUT_FILE) / 1024
        print(f"📄 Training dataset: {OUTPUT_FILE} ({size_kb:.1f} KB)")
    else:
        print(f"📄 Training dataset: not generated yet.")
    pause()


def main_menu():
    """Display menu and handle user input in a loop."""
    while True:
        clear()
        banner()
        print("Choose what you’d like to do:\n")
        print("  1️⃣  Run full pipeline (Scraper + Transformer)")
        print("  2️⃣  Run scraper for a specific project")
        print("  3️⃣  Run transformer only")
        print("  4️⃣  Show data summary")
        print("  5️⃣  Exit\n")

        choice = input("Enter your choice [1-5]: ").strip()

        if choice == "1":
            run_full_pipeline()
        elif choice == "2":
            print("\nAvailable projects:")
            for i, p in enumerate(PROJECTS, 1):
                print(f"  {i}. {p}")
            sel = input("\nType project name or number: ").strip()
            if sel.isdigit() and 1 <= int(sel) <= len(PROJECTS):
                run_scraper(PROJECTS[int(sel)-1])
            else:
                run_scraper(sel.upper())
        elif choice == "3":
            run_transformer()
        elif choice == "4":
            show_stats()
        elif choice == "5":
            print(f"\n{ICON['ok']} Exiting dashboard. See you again!")
            time.sleep(1)
            break
        else:
            print(f"\n{ICON['fail']} Invalid choice, please try again.")
            time.sleep(1)

if __name__ == "__main__":
    main_menu()
