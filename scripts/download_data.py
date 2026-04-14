"""
Download and save the Stanford IMDB dataset and GloVe pretrained vectors.

Usage:
  python scripts/download_data.py
  python scripts/download_data.py --skip-glove   # skip GloVe download (~862 MB)
"""
import argparse
import os
import urllib.request
import zipfile
from pathlib import Path

from datasets import load_dataset
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path(os.getenv("DATA_DIR", "./data"))
RAW_DIR = DATA_DIR / "raw"

GLOVE_URL = "https://nlp.stanford.edu/data/glove.6B.zip"
GLOVE_FILE = "glove.6B.100d.txt"


def download_imdb():
    print("Downloading Stanford IMDB dataset...")
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    ds = load_dataset("stanfordnlp/imdb")

    for split in ["train", "test"]:
        df = ds[split].to_pandas()
        assert set(df.columns) >= {"text", "label"}, f"Unexpected schema in {split}"
        assert df["label"].nunique() == 2, f"Expected binary labels in {split}"

        out = RAW_DIR / f"{split}.parquet"
        df.to_parquet(out, index=False)
        counts = df["label"].value_counts().to_dict()
        print(f"  Saved {split}: {len(df)} rows → {out}  (labels: {counts})")


def download_glove():
    glove_out = RAW_DIR / GLOVE_FILE
    if glove_out.exists():
        print(f"GloVe already present at {glove_out}, skipping.")
        return

    zip_path = RAW_DIR / "glove.6B.zip"
    print(f"Downloading GloVe 6B (~862 MB) → {zip_path} ...")

    def _progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        pct = downloaded / total_size * 100 if total_size > 0 else 0
        print(f"\r  {pct:.1f}%", end="", flush=True)

    urllib.request.urlretrieve(GLOVE_URL, zip_path, reporthook=_progress)
    print()

    print(f"Extracting {GLOVE_FILE} ...")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extract(GLOVE_FILE, RAW_DIR)
    zip_path.unlink()
    print(f"  GloVe saved → {glove_out}")


def main():
    parser = argparse.ArgumentParser(description="Download project datasets")
    parser.add_argument("--skip-glove", action="store_true",
                        help="Skip GloVe download (only download IMDB)")
    args = parser.parse_args()

    download_imdb()
    if not args.skip_glove:
        download_glove()
    print("\nAll downloads complete.")


if __name__ == "__main__":
    main()
