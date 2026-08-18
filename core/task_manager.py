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

from config import (
    RECENT_COMPLETED_COUNT,
    PRIORITY_HIGH,
    RECOMMEND_COUNT,
    RECOMMEND_PRIORITY_SCORES,
    RECOMMEND_PIN_BONUS,
)
from core.models import Task
from utils.storage import load_tasks, save_tasks


def _backfill_missing_order(tasks: list) -> bool:
    """
    order가 아직 배정되지 않은(None) 할 일에 한해, created_at 순서대로
    order 값을 새로 부여합니다. v1.0 이전 데이터를 위한 1회성 보정
    로직입니다 - 이미 order가 있는 할 일은 절대 건드리지 않습니다.

    반환값: 실제로 값을 채운 태스크가 하나라도 있으면 True (호출한 쪽에서
    이 경우에만 파일에 다시 저장하면 됩니다).
    """
    missing = [t for t in tasks if t.order is None]
    if not missing:
        return False

    existing_orders = [t.order for t in tasks if t.order is not None]
    next_order = (max(existing_orders) + 1) if existing_orders else 0

    # 순서가 없는 태스크끼리는 만들어진 시각(created_at) 순서를 그대로 유지합니다.
    for t in sorted(missing, key=lambda t: t.created_at):
        t.order = next_order
        next_order += 1
    return True


def _next_order(tasks: list) -> int:
    """새 할 일에 부여할 다음 순서 값을 계산합니다. (항상 목록 맨 아래로 추가됨)"""
    orders = [t.order for t in tasks if t.order is not None]
    return (max(orders) + 1) if orders else 0


def get_all_tasks() -> list:
    """저장된 모든 할 일을 Task 객체 리스트로 불러옵니다."""
    raw_tasks = load_tasks()
    tasks = [Task.from_dict(t) for t in raw_tasks]

    # v1.0 이전 데이터(순서 없음)를 만나면 한 번만 순서를 배정하고 저장합니다.
    if _backfill_missing_order(tasks):
        _persist(tasks)

    return tasks


def _persist(tasks: list) -> None:
    """Task 객체 리스트를 JSON 파일에 저장합니다."""
    save_tasks([t.to_dict() for t in tasks])


def add_task(
    title: str,
    priority: str,
    due_date: Optional[str] = None,
    memo: str = "",
    requester: str = "",
    lot: str = "",
    slot: str = "",
    request_date: Optional[str] = None,
) -> None:
    """
    새 할 일을 추가합니다. 마감일/메모/요청자/LOT/SLOT/요청일은 모두 선택
    사항입니다. 새 할 일은 항상 수동 정렬 목록의 맨 아래에 추가됩니다.
    """
    tasks = get_all_tasks()
    tasks.append(
        Task(
            title=title.strip(),
            priority=priority,
            due_date=due_date,
            memo=memo.strip(),
            requester=requester.strip(),
            lot=lot.strip(),
            slot=slot.strip(),
            request_date=request_date,
            order=_next_order(tasks),
        )
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


def update_requester(task_id: str, requester: str) -> None:
    """할 일의 요청자를 변경합니다. 빈 문자열을 넣으면 제거됩니다."""
    tasks = get_all_tasks()
    for t in tasks:
        if t.id == task_id:
            t.requester = requester.strip()
    _persist(tasks)


def update_lot(task_id: str, lot: str) -> None:
    """할 일의 LOT 번호를 변경합니다. 빈 문자열을 넣으면 제거됩니다."""
    tasks = get_all_tasks()
    for t in tasks:
        if t.id == task_id:
            t.lot = lot.strip()
    _persist(tasks)


def update_slot(task_id: str, slot: str) -> None:
    """할 일의 SLOT 번호를 변경합니다. 빈 문자열을 넣으면 제거됩니다."""
    tasks = get_all_tasks()
    for t in tasks:
        if t.id == task_id:
            t.slot = slot.strip()
    _persist(tasks)


def update_request_date(task_id: str, request_date: Optional[str]) -> None:
    """할 일의 요청일을 변경합니다. None을 넣으면 요청일이 제거됩니다."""
    tasks = get_all_tasks()
    for t in tasks:
        if t.id == task_id:
            t.request_date = request_date
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


def _recommend_score(task: Task) -> tuple:
    """
    할 일 하나의 '추천 점수'와 '추천 이유'를 계산합니다.

    점수 구성:
    - 우선순위 점수: High 30 / Medium 20 / Low 10
    - 마감일 점수: 지남 +50, 오늘 +40, 1일 전 +30, 2일 전 +20, 3일 전 +10
    - Pin 보너스: +5

    예) High 우선순위 + 오늘 마감 = 30 + 40 = 70점
    """
    score = RECOMMEND_PRIORITY_SCORES.get(task.priority, 0)
    reasons = []

    if task.priority == PRIORITY_HIGH:
        reasons.append("우선순위 High")

    days_left = get_days_left(task)
    if days_left is not None:
        if days_left < 0:
            score += 50
            reasons.append(f"마감 {-days_left}일 지남")
        elif days_left == 0:
            score += 40
            reasons.append("오늘 마감")
        elif days_left <= 3:
            # D-1이면 +30, D-2면 +20, D-3이면 +10
            score += (4 - days_left) * 10
            reasons.append(f"마감 {days_left}일 전")

    if task.pinned:
        score += RECOMMEND_PIN_BONUS
        reasons.append("고정된 할 일")

    return score, reasons


def get_recommended_tasks(count: int = RECOMMEND_COUNT) -> list:
    """
    '오늘 먼저 하면 좋은 할 일' 추천 목록을 반환합니다.
    미완료 할 일을 점수순으로 정렬해서 상위 count개를 골라줍니다.

    반환 형식: [{"task": Task, "score": 점수, "reasons": [이유 문자열들]}, ...]
    """
    todos = [t for t in get_all_tasks() if not t.completed]

    scored = []
    for t in todos:
        score, reasons = _recommend_score(t)
        scored.append({"task": t, "score": score, "reasons": reasons})

    # 점수 높은 순 -> 마감일 빠른 순 -> 먼저 만든 순으로 정렬
    scored.sort(
        key=lambda item: (
            -item["score"],
            item["task"].due_date or "9999-12-31",
            item["task"].created_at,
        )
    )
    return scored[:count]


def _sort_key(task: Task):
    """
    Todo 목록 정렬 기준 (v1.0): 오직 사용자가 지정한 수동 순서(order)만 사용합니다.
    우선순위나 Pin 여부로 자동 정렬하지 않습니다 - 우선순위는 배지 등으로
    "정보"만 보여주고, 실제 목록 순서는 사용자가 직접 조정합니다.

    order가 같은 값일 경우(정상적으로는 발생하지 않아야 하지만 방어적으로)
    먼저 만들어진 항목이 앞에 오도록 created_at을 보조 기준으로 둡니다.
    """
    return (task.order if task.order is not None else 0, task.created_at)


def get_todo_tasks(search_keyword: str = "") -> list:
    """
    미완료 할 일 목록을 반환합니다.
    검색어가 있으면 제목에 검색어가 포함된 항목만 반환합니다.
    사용자가 지정한 수동 순서(order)대로 정렬되어 있습니다.
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
