"""
Entry point — delegates to sub-commands.

Usage:
  python run.py download        # download IMDB + GloVe data
  python run.py train           # train all embedding × classifier combos (also generates roc_curves.json)
"""
import sys
import subprocess

COMMANDS = {
    "download": ["python", "scripts/download_data.py"],
    "train":    ["python", "scripts/train.py"],
}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else None
    if cmd not in COMMANDS:
        print(f"Unknown command: {cmd}")
        print(f"Available: {', '.join(COMMANDS)}")
        sys.exit(1)
    subprocess.run(COMMANDS[cmd] + sys.argv[2:])
