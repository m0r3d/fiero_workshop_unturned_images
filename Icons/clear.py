#!/usr/bin/env python3
"""
Переименовывает все файлы в папке,
оставляя в имени только последнее число перед расширением.
Если файл с таким именем уже существует, операция пропускается,
а событие фиксируется в лог-файле rename.log.
"""

import os
import re
import logging
import sys
from pathlib import Path

# ── 1. Настройка логирования ───────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
    handlers=[
        logging.FileHandler("rename.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

# ── 2. Определяем текущую папку и имя самого скрипта ───────────────────────────
current_dir = Path(__file__).resolve().parent
script_name = Path(__file__).name

# ── 3. Перебираем файлы в каталоге ──────────────────────────────────────────────
for entry in current_dir.iterdir():
    # пропускаем папки и сам скрипт
    if not entry.is_file() or entry.name == script_name:
        continue

    base, ext = os.path.splitext(entry.name)

    # ищем все числа в имени и берём последнее
    numbers = re.findall(r"\d+", base)
    if not numbers:
        logging.info("⏩ Пропуск «%s» — в имени нет чисел", entry.name)
        continue

    new_name = f"{numbers[-1]}{ext}"
    target_path = current_dir / new_name

    if target_path.exists():
        logging.warning(
            "⚠️  Не переименовано «%s» → «%s» — такое имя уже занято",
            entry.name,
            new_name,
        )
        continue

    try:
        entry.rename(target_path)
        logging.info("✅ %s → %s", entry.name, new_name)
    except OSError as e:
        logging.error(
            "❌ Ошибка при переименовании «%s»: %s", entry.name, e
        )
