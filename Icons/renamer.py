#!/usr/bin/env python3
import os
import re
import sys


NUMBER_AT_END_RE = re.compile(r'(\d+)(\.[^.]+)?$')  # число в конце + необязательное расширение


def extract_new_name(filename: str) -> str | None:
    """
    Возвращает новое имя файла вида '5733.png' (или '5733' если без расширения),
    если в конце имени есть число. Иначе None.
    """
    m = NUMBER_AT_END_RE.search(filename)
    if not m:
        return None

    number = m.group(1)
    ext = m.group(2) or ""
    return f"{number}{ext}"


def safe_replace_rename(src_path: str, dst_path: str) -> None:
    """
    Переименовывает/перемещает src_path в dst_path.
    Если dst_path уже существует — удаляет его и делает замену.
    """
    if os.path.exists(dst_path):
        os.remove(dst_path)
    os.rename(src_path, dst_path)


def main() -> int:
    folder = sys.argv[1] if len(sys.argv) > 1 else "."
    folder = os.path.abspath(folder)

    if not os.path.isdir(folder):
        print(f"Folder not found: {folder}")
        return 1

    renamed = 0
    skipped = 0
    collisions = 0
    errors = 0

    for entry in os.listdir(folder):
        src_path = os.path.join(folder, entry)

        # только файлы (не папки)
        if not os.path.isfile(src_path):
            continue

        new_name = extract_new_name(entry)
        if not new_name:
            skipped += 1
            continue

        # если имя уже такое же — пропускаем
        if new_name == entry:
            skipped += 1
            continue

        dst_path = os.path.join(folder, new_name)

        try:
            if os.path.exists(dst_path):
                collisions += 1
            safe_replace_rename(src_path, dst_path)
            renamed += 1
            print(f"{entry}  ->  {new_name}")
        except Exception as e:
            errors += 1
            print(f"ERROR: {entry} -> {new_name}: {e}")

    print("\nDone.")
    print(f"Renamed:    {renamed}")
    print(f"Skipped:    {skipped}")
    print(f"Replaced:   {collisions}  (existing files overwritten)")
    print(f"Errors:     {errors}")
    return 0 if errors == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
