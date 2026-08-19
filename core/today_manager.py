"""
core/today_manager.py

"오늘의 작업(Today's Tasks)" 목록을 관리합니다.

중요한 설계 원칙 (Single Source of Truth):
- 할 일의 실제 정보(제목/완료 여부 등)는 항상 tasks.json에만 존재합니다.
- today_list.json에는 task_id와 "오늘 목록에서의 상태"만 저장하고,
  할 일 정보를 절대 복제하지 않습니다. 화면에 보여줄 때마다 tasks.json에서
  다시 조회(join)합니다.

날짜가 바뀌면(어제 저장된 date != 오늘) 딱 한 번, 아래 순서로 목록을
새로 계산합니다:
1) 어제 목록에서 제외(excluded)되지 않았고 아직 미완료인 항목 -> 이월(carried_over)
2) 나머지 미완료 할 일을 대상으로 자동 추천(recommended) 계산
"excluded"는 "그날 하루만" 유효합니다 - 다음날에는 조건이 맞으면 다시
추천될 수 있습니다 (영구 차단이 아닙니다).
"""

from __future__ import annotations

from datetime import date

from config import TODAY_SOFT_TARGET
from core.task_manager import get_all_tasks, get_days_left, score_task_for_recommendation
from utils.storage import load_today_list, save_today_list

SOURCE_RECOMMENDED = "recommended"
SOURCE_MANUAL = "manual"
SOURCE_CARRIED_OVER = "carried_over"


def _today_str() -> str:
    return date.today().isoformat()


def _auto_recommend_ids(candidate_tasks: list, exclude_ids: set) -> list:
    """
    자동으로 추천할 task_id 목록을 계산합니다.
    1) 마감이 지났거나 오늘 마감인 할 일 -> 무조건 포함
    2) 나머지는 점수 높은 순으로 정렬해서, 소프트 타깃(TODAY_SOFT_TARGET)이
       될 때까지 채웁니다. 1번만으로 이미 소프트 타깃을 넘으면 억지로
       자르지 않고 전부 포함합니다.
    exclude_ids에 들어있는 태스크(이미 이월된 태스크)는 후보에서 뺍니다 -
    같은 태스크가 "이월"과 "추천"에 중복으로 들어가지 않도록 합니다.
    """
    pool = [t for t in candidate_tasks if t.id not in exclude_ids]

    urgent = [t for t in pool if (dl := get_days_left(t)) is not None and dl <= 0]
    urgent_ids = {t.id for t in urgent}

    rest = [t for t in pool if t.id not in urgent_ids]
    rest_sorted = sorted(rest, key=lambda t: -score_task_for_recommendation(t))

    remaining_slots = max(0, TODAY_SOFT_TARGET - len(urgent))
    selected = urgent + rest_sorted[:remaining_slots]
    return [t.id for t in selected]


def _rollover_if_needed(data: dict) -> dict:
    """
    저장된 날짜가 오늘과 다르면, 이월 + 새 추천을 계산해서 today_list를
    갱신하고 저장합니다. 이미 오늘 날짜라면 아무 것도 하지 않고 그대로
    반환합니다 (하루에 한 번만 추천이 계산됩니다).
    """
    today = _today_str()
    if data.get("date") == today:
        return data

    all_tasks = get_all_tasks()
    tasks_by_id = {t.id: t for t in all_tasks}

    # 1) 이월 대상: 어제 목록에서 제외되지 않았고, tasks.json 기준 아직 미완료인 것.
    #    삭제된 태스크(tasks_by_id에 없음)는 자연스럽게 이월 대상에서 빠집니다.
    carried_over_ids = [
        item["task_id"]
        for item in data.get("items", [])
        if not item.get("excluded", False)
        and (task := tasks_by_id.get(item["task_id"])) is not None
        and not task.completed
    ]

    # 2) 나머지 미완료 할 일을 대상으로 새 추천 계산 (이월된 것은 후보 제외)
    incomplete_tasks = [t for t in all_tasks if not t.completed]
    recommended_ids = _auto_recommend_ids(incomplete_tasks, exclude_ids=set(carried_over_ids))

    new_items = [
        {"task_id": tid, "source": SOURCE_CARRIED_OVER, "excluded": False} for tid in carried_over_ids
    ] + [
        {"task_id": tid, "source": SOURCE_RECOMMENDED, "excluded": False} for tid in recommended_ids
    ]

    new_data = {"date": today, "items": new_items}
    save_today_list(new_data)
    return new_data


def get_today_list_raw() -> dict:
    """날짜 롤오버 처리를 마친 today_list.json의 원본 데이터를 반환합니다."""
    return _rollover_if_needed(load_today_list())


def get_today_tasks() -> list:
    """
    오늘의 작업 목록을 반환합니다 (제외되지 않은 항목만).
    반환 형식: [{"task": Task, "source": "recommended"/"manual"/"carried_over"}, ...]

    today_list.json이 가리키는 task_id가 이미 삭제된 경우, 화면에서
    조용히 건너뜁니다 (에러 없이 방어적으로 처리).
    """
    data = get_today_list_raw()
    tasks_by_id = {t.id: t for t in get_all_tasks()}

    result = []
    for item in data["items"]:
        if item.get("excluded", False):
            continue
        task = tasks_by_id.get(item["task_id"])
        if task is None:
            continue  # 삭제된 할 일을 가리키는 참조 - 안전하게 건너뜀
        result.append({"task": task, "source": item["source"]})
    return result


def is_in_today_list(task_id: str) -> bool:
    """해당 할 일이 오늘의 작업(제외되지 않은 상태)에 포함되어 있는지 확인합니다."""
    return any(item["task"].id == task_id for item in get_today_tasks())


def add_to_today(task_id: str) -> None:
    """
    할 일을 오늘의 작업에 수동으로 추가합니다.
    이전에 같은 태스크를 제외했었다면, 새로 추가하지 않고 제외 상태만
    풀어줍니다 (같은 task_id가 목록에 중복으로 들어가지 않도록 함).
    """
    data = get_today_list_raw()
    existing = next((item for item in data["items"] if item["task_id"] == task_id), None)

    if existing is not None:
        existing["excluded"] = False
    else:
        data["items"].append({"task_id": task_id, "source": SOURCE_MANUAL, "excluded": False})

    save_today_list(data)


def exclude_from_today(task_id: str) -> None:
    """
    할 일을 오늘의 작업에서 뺍니다. 원본 할 일(tasks.json)은 전혀
    건드리지 않고, 오늘 목록에서의 표시 여부만 바꿉니다.
    이 제외는 "오늘 하루만" 유효합니다 - 다음 날 다시 조건이 맞으면
    자동 추천에 다시 나타날 수 있습니다.
    """
    data = get_today_list_raw()
    for item in data["items"]:
        if item["task_id"] == task_id:
            item["excluded"] = True
    save_today_list(data)


def get_today_progress() -> dict:
    """오늘의 작업 기준 진행률을 계산합니다."""
    items = get_today_tasks()
    total = len(items)
    completed = len([i for i in items if i["task"].completed])
    progress = round((completed / total) * 100) if total > 0 else 0
    return {"total": total, "completed": completed, "progress": progress}
