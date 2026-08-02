"""
core/task_manager.py

할 일(Task)을 추가/삭제/완료/복원/검색/정렬하는 핵심 로직을 담당합니다.
이 파일은 화면(UI)을 전혀 알지 못합니다 (Streamlit 코드가 없습니다).

그래서 나중에 UI를 바꾸거나, 엑셀 연동/클라우드 동기화 같은
새로운 기능을 추가할 때도 이 파일의 함수를 그대로 재사용할 수 있습니다.
"""

from __future__ import annotations

from datetime import datetime, date
from typing import Optional

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


def add_task(
    title: str,
    priority: str,
    due_date: Optional[str] = None,
    memo: str = "",
) -> None:
    """새 할 일을 추가합니다. 마감일(YYYY-MM-DD)과 메모는 선택 사항입니다."""
    tasks = get_all_tasks()
    tasks.append(
        Task(title=title.strip(), priority=priority, due_date=due_date, memo=memo.strip())
    )
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


def update_due_date(task_id: str, due_date: Optional[str]) -> None:
    """할 일의 마감일을 변경합니다. None을 넣으면 마감일이 제거됩니다."""
    tasks = get_all_tasks()
    for t in tasks:
        if t.id == task_id:
            t.due_date = due_date
    _persist(tasks)


def update_memo(task_id: str, memo: str) -> None:
    """할 일의 메모를 변경합니다. 빈 문자열을 넣으면 메모가 제거됩니다."""
    tasks = get_all_tasks()
    for t in tasks:
        if t.id == task_id:
            t.memo = memo.strip()
    _persist(tasks)


def get_days_left(task: Task) -> Optional[int]:
    """
    마감일까지 남은 일수를 계산합니다.
    - 양수: 아직 여유가 있음 (예: 3 -> D-3)
    - 0: 오늘이 마감일 (D-DAY)
    - 음수: 마감일이 지남 (예: -2 -> 2일 지남)
    - None: 마감일이 설정되지 않음
    """
    if not task.due_date:
        return None
    try:
        due = date.fromisoformat(task.due_date)
    except ValueError:
        return None
    return (due - date.today()).days


def _sort_key(task: Task):
    """
    Todo 목록 정렬 기준:
    1) Pin 된 항목이 먼저 오도록
    2) 그다음 우선순위(High > Medium > Low) 순서로
    3) 같은 우선순위면 마감일이 빠른 항목이 먼저 오도록 (마감일 없으면 뒤로)
    4) 마지막으로 먼저 생성된 항목이 먼저 오도록
    """
    priority_rank = PRIORITY_ORDER.index(task.priority) if task.priority in PRIORITY_ORDER else 99
    # 마감일이 없는 항목은 "9999-12-31"로 취급해서 항상 뒤로 보냅니다
    due = task.due_date or "9999-12-31"
    return (not task.pinned, priority_rank, due, task.created_at)


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

    # 오늘이 마감이거나 이미 지난 미완료 할 일 (days_left가 0 이하)
    due_today = [
        t for t in tasks
        if not t.completed and get_days_left(t) is not None and get_days_left(t) <= 0
    ]

    return {
        "total": total,
        "completed": completed_count,
        "progress": progress,
        "recent_completed": recent_completed,
        "high_priority": sorted(high_priority, key=_sort_key),
        "due_today": sorted(due_today, key=_sort_key),
    }
