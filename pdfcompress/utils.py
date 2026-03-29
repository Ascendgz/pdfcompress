import os
import tempfile
import shutil
from pathlib import Path
from typing import Optional


def get_output_path(input_path: str, suffix: str = "_compressed") -> str:
    p = Path(input_path)
    return str(p.parent / f"{p.stem}{suffix}{p.suffix}")


def ensure_dir(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def get_temp_dir() -> str:
    return tempfile.mkdtemp(prefix="pdfcompress_")


def cleanup_temp_dir(path: str) -> None:
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)


def format_size(size_bytes: int) -> str:
    size = float(size_bytes)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"


def validate_pdf(path: str) -> bool:
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    if not path.lower().endswith('.pdf'):
        raise ValueError(f"Not a PDF file: {path}")
    return True
