"""
utils/storage.py

JSON 파일을 읽고 쓰는 공용 함수들을 모아둔 파일입니다.
tasks.json, settings.json을 다루는 모든 코드는 이 파일을 거쳐갑니다.

나중에 저장 방식을 (예: 클라우드 DB로) 바꾸더라도
이 파일의 함수 이름과 반환 형태만 유지하면 다른 코드는 수정할 필요가 없습니다.
"""

import json

from config import TASKS_FILE, SETTINGS_FILE, DATA_DIR, DEFAULT_THEME


def _ensure_data_dir() -> None:
    """data 폴더가 없으면 새로 만듭니다."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_tasks() -> list:
    """
    tasks.json 파일을 읽어서 할 일 목록(list)을 반환합니다.
    파일이 없으면 빈 목록으로 새로 만들어줍니다.
    """
    _ensure_data_dir()

    if not TASKS_FILE.exists():
        save_tasks([])
        return []

    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # tasks.json은 {"tasks": [...]} 형태로 저장되어 있습니다.
    return data.get("tasks", [])


def save_tasks(tasks: list) -> None:
    """할 일 목록(list of dict)을 tasks.json 파일에 저장합니다."""
    _ensure_data_dir()

    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump({"tasks": tasks}, f, ensure_ascii=False, indent=2)


def load_settings() -> dict:
    """
    settings.json 파일을 읽어서 설정값(dict)을 반환합니다.
    파일이 없으면 기본 설정(라이트 모드)으로 새로 만들어줍니다.
    """
    _ensure_data_dir()

    if not SETTINGS_FILE.exists():
        default_settings = {"theme": DEFAULT_THEME}
        save_settings(default_settings)
        return default_settings

    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_settings(settings: dict) -> None:
    """설정값(dict)을 settings.json 파일에 저장합니다."""
    _ensure_data_dir()

    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)
