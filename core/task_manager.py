"""
core/task_manager.py

할 일(Task)을 추가/삭제/완료/복원/검색/정렬하는 핵심 로직을 담당합니다.
이 파일은 화면(UI)을 전혀 알지 못합니다 (Streamlit 코드가 없습니다).

그래서 나중에 UI를 바꾸거나, 엑셀 연동/클라우드 동기화 같은
새로운 기능을 추가할 때도 이 파일의 함수를 그대로 재사용할 수 있습니다.
"""

from __future__ import annotations

from datetime import datetime

from config import PRIORITY_ORDER, RECENT_COMPLETED_COUNT, PRIORITY_HIGH
from core.models import Task
from utils.storage import load_tasks, save_tasks


def get_all_tasks() -> list:
    """저장된 모든 할 일을 Task 객체 리스트로 불러옵니다."""
    raw_tasks = load_tasks()
    return [Task.from_dict(t) for t in raw_tasks]


def _persist(tasks: list) -> None:
    """Task 객체 리스트를 JSON 파일에 저장합니다."""
    save_tasks([t.to_dict() for t in tasks])


def add_task(title: str, priority: str) -> None:
    """새 할 일을 추가합니다."""
    tasks = get_all_tasks()
    tasks.append(Task(title=title.strip(), priority=priority))
    _persist(tasks)


def delete_task(task_id: str) -> None:
    """할 일을 목록에서 완전히 삭제합니다."""
    tasks = get_all_tasks()
    tasks = [t for t in tasks if t.id != task_id]
    _persist(tasks)


def complete_task(task_id: str) -> None:
    """할 일을 완료 처리합니다. (Todo 탭에서 체크박스를 선택했을 때 호출)"""
    tasks = get_all_tasks()
    for t in tasks:
        if t.id == task_id:
            t.completed = True
            t.completed_at = datetime.now().isoformat()
    _persist(tasks)


def restore_task(task_id: str) -> None:
    """완료된 할 일을 다시 미완료 상태로 되돌립니다. (Completed 탭의 Restore 버튼)"""
    tasks = get_all_tasks()
    for t in tasks:
        if t.id == task_id:
            t.completed = False
            t.completed_at = None
    _persist(tasks)


def toggle_pin(task_id: str) -> None:
    """Pin 상태를 켜고 끕니다."""
    tasks = get_all_tasks()
    for t in tasks:
        if t.id == task_id:
            t.pinned = not t.pinned
    _persist(tasks)


def update_priority(task_id: str, priority: str) -> None:
    """할 일의 우선순위를 변경합니다."""
    tasks = get_all_tasks()
    for t in tasks:
        if t.id == task_id:
            t.priority = priority
    _persist(tasks)


def _sort_key(task: Task):
    """
    Todo 목록 정렬 기준:
    1) Pin 된 항목이 먼저 오도록
    2) 그다음 우선순위(High > Medium > Low) 순서로
    3) 마지막으로 먼저 생성된 항목이 먼저 오도록
    """
    priority_rank = PRIORITY_ORDER.index(task.priority) if task.priority in PRIORITY_ORDER else 99
    return (not task.pinned, priority_rank, task.created_at)


def get_todo_tasks(search_keyword: str = "") -> list:
    """
    미완료 할 일 목록을 반환합니다.
    검색어가 있으면 제목에 검색어가 포함된 항목만 반환합니다.
    Pin -> 우선순위 순으로 정렬되어 있습니다.
    """
    tasks = [t for t in get_all_tasks() if not t.completed]

    if search_keyword.strip():
        keyword = search_keyword.strip().lower()
        tasks = [t for t in tasks if keyword in t.title.lower()]

    return sorted(tasks, key=_sort_key)


def get_completed_tasks() -> list:
    """완료된 할 일 목록을 최근 완료 순으로 반환합니다."""
    tasks = [t for t in get_all_tasks() if t.completed]
    return sorted(tasks, key=lambda t: t.completed_at or "", reverse=True)


def get_dashboard_stats() -> dict:
    """Dashboard 탭에 필요한 통계 정보를 계산해서 반환합니다."""
    tasks = get_all_tasks()
    total = len(tasks)
    completed = [t for t in tasks if t.completed]
    completed_count = len(completed)
    progress = round((completed_count / total) * 100) if total > 0 else 0

    recent_completed = sorted(
        completed, key=lambda t: t.completed_at or "", reverse=True
    )[:RECENT_COMPLETED_COUNT]

    high_priority = [t for t in tasks if not t.completed and t.priority == PRIORITY_HIGH]

    return {
        "total": total,
        "completed": completed_count,
        "progress": progress,
        "recent_completed": recent_completed,
        "high_priority": sorted(high_priority, key=_sort_key),
    }
