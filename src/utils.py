"""Shared helper functions for the project."""

from pathlib import Path

# Local folder with the processed data (not committed to git, see README "Where to put the data")
DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
