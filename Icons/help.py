#!/usr/bin/env python3
# rename_to_number.py
# Переименовывает файлы вида NAME_1234.png -> 1234.png

from pathlib import Path
import argparse
import re
import sys
import os

def iter_files(root: Path, exts, recursive: bool):
    pattern_exts = tuple("." + e.lower() for e in exts)
    if recursive:
        for p in root.rglob("*"):
            if p.is_file() and p.suffix.lower() in pattern_exts:
                yield p
    else:
        for p in root.iterdir():
            if p.is_file() and p.suffix.lower() in pattern_exts:
                yield p

def unique_target(target: Path) -> Path:
    """Если файл существует, подбираем уникальное имя: 1234_1.png, 1234_2.png, ..."""
    if not target.exists():
        return target
    base = target.stem
    suffix = target.suffix
    parent = target.parent
    i = 1
    while True:
        cand = parent / f"{base}_{i}{suffix}"
        if not cand.exists():
            return cand
        i += 1

def main():
    parser = argparse.ArgumentParser(
        description="Переименовать изображения NAME_1234.png -> 1234.png (берём число после последнего '_')."
    )
    parser.add_argument("path", nargs="?", default=".", help="Папка с файлами (по умолчанию текущая).")
    parser.add_argument("--ext", nargs="+", default=["png"],
                        help="Список расширений без точки: png jpg jpeg webp gif bmp tiff (по умолчанию: png).")
    parser.add_argument("-r", "--recursive", action="store_true", help="Искать файлы рекурсивно по подпапкам.")
    parser.add_argument("--on-conflict", choices=["skip", "overwrite", "unique"], default="unique",
                        help="Что делать, если целевое имя уже существует: skip/overwrite/unique (по умолчанию unique).")
    parser.add_argument("-n", "--dry-run", action="store_true", help="Только показать, что будет сделано.")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.exists() or not root.is_dir():
        print(f"[ERR] Папка не найдена: {root}")
        sys.exit(1)

    regex = re.compile(r"_(\d+)$")  # число после последнего "_"
    renamed = skipped = conflicts = 0

    for f in iter_files(root, args.ext, args.recursive):
        name = f.stem
        m = regex.search(name)
        if not m:
            # нет числа после последнего "_"
            skipped += 1
            continue

        num = m.group(1)
        if name == num:
            # уже в нужном формате
            skipped += 1
            continue

        target = f.with_name(num + f.suffix)

        if target.exists():
            conflicts += 1
            if args.on_conflict == "skip":
                print(f"[SKIP] {f.name} -> {target.name} (уже существует)")
                continue
            elif args.on_conflict == "overwrite":
                print(f"[OVERWRITE] {f.name} -> {target.name}")
                if not args.dry_run:
                    # os.replace перезапишет цель надёжно
                    os.replace(f, target)
                renamed += 1
            else:  # unique
                new_target = unique_target(target)
                print(f"[RENAME] {f.name} -> {new_target.name}")
                if not args.dry_run:
                    f.rename(new_target)
                renamed += 1
        else:
            print(f"[RENAME] {f.name} -> {target.name}")
            if not args.dry_run:
                f.rename(target)
            renamed += 1

    print("\nИтог:")
    print(f"  Переименовано: {renamed}")
    print(f"  Пропущено:     {skipped}")
    print(f"  Конфликтов:    {conflicts}")
    if args.dry_run:
        print("  Режим: dry-run (ничего не менял)")

if __name__ == "__main__":
    main()
