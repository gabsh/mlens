"""
Entry point — delegates to sub-commands.

Usage:
  python run.py download        # download IMDB + GloVe data
  python run.py train           # train all embedding × classifier combos
  python run.py evaluate        # evaluate all saved models
  python run.py api             # start FastAPI server
  python run.py mlflow          # start MLflow tracking server
"""
import sys
import subprocess

COMMANDS = {
    "download": ["python", "scripts/download_data.py"],
    "train":    ["python", "scripts/train.py"],
    "evaluate": ["python", "scripts/evaluate.py"],
    "api":      ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
    "mlflow":   ["mlflow", "server", "--host", "127.0.0.1", "--port", "5000",
                 "--backend-store-uri", "./mlruns", "--default-artifact-root", "./mlruns"],
}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "api"
    if cmd not in COMMANDS:
        print(f"Unknown command: {cmd}")
        print(f"Available: {', '.join(COMMANDS)}")
        sys.exit(1)
    subprocess.run(COMMANDS[cmd] + sys.argv[2:])
