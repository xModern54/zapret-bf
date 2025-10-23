#!/usr/bin/env python3
"""
Build script for release bundles.

Creates ZIP, RAR, and 7Z archives from the repository root while excluding:
- .github directory
- Debug directory
- .gitignore file
- README.md file (case-insensitive)

Outputs archives into ./ReleaseBuild with a user-provided bundle name.

Notes:
- ZIP is created with Python's standard library.
- 7Z is created with py7zr if available, otherwise attempts to use 7z.exe CLI.
- RAR creation is attempted via patoolib if available, otherwise tries rar.exe/WinRAR.exe CLI.
- Excluded items are skipped without deleting anything from the workspace.
"""

from __future__ import annotations

import os
import sys
import shutil
import zipfile
import subprocess
from pathlib import Path
from typing import Iterable, List


EXCLUDED_DIRS = {".github", "debug", "releasebuild"}
EXCLUDED_FILES = {".gitignore", "readme.md", "build.py"}


def ask_bundle_name() -> str:
    try:
        name = input("Введите название бандла (имя архива): ").strip()
    except EOFError:
        name = "bundle"
    if not name:
        name = "bundle"
    # sanitize minimal: remove path separators
    name = name.replace("/", "-").replace("\\", "-")
    return name


def collect_files(root: Path) -> List[Path]:
    files: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = Path(dirpath).relative_to(root)
        # Skip excluded directories (case-insensitive)
        dirnames[:] = [d for d in dirnames if d.lower() not in EXCLUDED_DIRS and d.lower() != ".git"]
        # Skip files per list
        script_name = Path(__file__).name.lower()
        for fn in filenames:
            low = fn.lower()
            if low in EXCLUDED_FILES or low == script_name:
                continue
            p = Path(dirpath) / fn
            # do not include directories (safety)
            if p.is_file():
                files.append(p)
    return files


def ensure_release_dir(root: Path) -> Path:
    out = root / "ReleaseBuild"
    out.mkdir(parents=True, exist_ok=True)
    return out


def build_zip(files: Iterable[Path], root: Path, out_path: Path) -> None:
    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in files:
            zf.write(p, arcname=p.relative_to(root))


def build_7z(files: List[Path], root: Path, out_path: Path) -> None:
    try:
        import py7zr  # type: ignore

        with py7zr.SevenZipFile(out_path, "w") as z:
            for p in files:
                z.write(p, arcname=str(p.relative_to(root)))
        return
    except Exception:
        pass

    # Fallback to 7z CLI
    sevenz = shutil.which("7z") or shutil.which("7z.exe") or str(Path("C:/Program Files/7-Zip/7z.exe"))
    if not Path(sevenz).exists():
        print("[WARN] 7z not found and py7zr unavailable; skipping 7z build", file=sys.stderr)
        return
    listfile = out_path.with_suffix(".7z.list")
    with open(listfile, "w", encoding="utf-8") as lf:
        for p in files:
            lf.write(str(p) + "\n")
    try:
        subprocess.run([sevenz, "a", "-t7z", str(out_path), f"@{listfile}"], check=True)
    finally:
        try:
            listfile.unlink()
        except Exception:
            pass


def build_rar(files: List[Path], root: Path, out_path: Path) -> None:
    # Try patool first
    try:
        import patoolib  # type: ignore

        # patool creates archives using external tools under the hood
        patoolib.create_archive(str(out_path), [str(p) for p in files])
        return
    except Exception:
        pass

    # Fallback to rar/WinRAR CLI if available
    rar = shutil.which("rar") or shutil.which("rar.exe")
    winrar = shutil.which("winrar") or shutil.which("WinRAR.exe") or str(Path("C:/Program Files/WinRAR/WinRAR.exe"))
    listfile = out_path.with_suffix(".rar.list")
    if rar:
        with open(listfile, "w", encoding="utf-8") as lf:
            for p in files:
                lf.write(str(p) + "\n")
        try:
            subprocess.run([rar, "a", "-r", "-ep1", str(out_path), f"@{listfile}"], check=True)
        finally:
            try:
                listfile.unlink()
            except Exception:
                pass
        return
    if Path(winrar).exists():
        with open(listfile, "w", encoding="utf-8") as lf:
            for p in files:
                lf.write(f"\"{p}\"\n")
        try:
            subprocess.run([winrar, "a", "-r", "-ep1", str(out_path), f"@{listfile}"], check=True)
        finally:
            try:
                listfile.unlink()
            except Exception:
                pass
        return

    print("[WARN] RAR tools not found and patool unavailable; skipping RAR build", file=sys.stderr)


def main() -> int:
    root = Path(__file__).resolve().parent
    name = ask_bundle_name()
    out_dir = ensure_release_dir(root)
    files = collect_files(root)

    # Ensure output directory excluded from inputs
    files = [p for p in files if not str(p).lower().startswith(str(out_dir).lower())]

    zip_path = out_dir / f"{name}.zip"
    seven_path = out_dir / f"{name}.7z"
    rar_path = out_dir / f"{name}.rar"

    print(f"[INFO] Building ZIP → {zip_path}")
    build_zip(files, root, zip_path)

    print(f"[INFO] Building 7Z  → {seven_path}")
    build_7z(files, root, seven_path)

    print(f"[INFO] Building RAR → {rar_path}")
    build_rar(files, root, rar_path)

    print("[DONE] Artifacts in:", out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
