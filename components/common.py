"""
components/common.py

여러 탭에서 공통으로 사용하는 작은 화면 조각들을 모아둔 파일입니다.
(우선순위 배지, D-day 배지, 날짜 포맷 등)

같은 코드를 탭마다 복사하지 않고 여기서 가져다 쓰면,
디자인이 바뀌어도 이 파일 하나만 수정하면 됩니다.
"""

from datetime import datetime

from config import DATETIME_FORMAT, DUE_COLORS, PRIORITY_COLORS, PRIORITY_LABELS
from core.task_manager import get_days_left


def format_datetime(iso_string) -> str:
    """ISO 형식 문자열을 보기 좋은 날짜/시간 문자열로 변환합니다."""
    if not iso_string:
        return "-"
    try:
        return datetime.fromisoformat(iso_string).strftime(DATETIME_FORMAT)
    except ValueError:
        return "-"


def priority_badge_html(priority: str) -> str:
    """우선순위 뱃지 HTML 조각을 만듭니다."""
    color = PRIORITY_COLORS.get(priority, "#94A3B8")
    label = PRIORITY_LABELS.get(priority, priority)
    return f'<span class="priority-badge" style="background-color:{color};">{label}</span>'


def due_badge_html(task) -> str:
    """
    마감일 상태를 나타내는 배지 HTML을 만듭니다.
    - 마감일 지남: 빨간색 "N일 지남"
    - 오늘 마감: 앰버색 "D-DAY"
    - 여유 있음: 회색 "D-N"
    - 마감일 없음: 빈 문자열 (배지 표시 안 함)
    """
    days_left = get_days_left(task)
    if days_left is None:
        return ""

    if days_left < 0:
        color, label = DUE_COLORS["overdue"], f"{-days_left}일 지남"
    elif days_left == 0:
        color, label = DUE_COLORS["today"], "D-DAY"
    else:
        color, label = DUE_COLORS["upcoming"], f"D-{days_left}"

    return f'<span class="priority-badge" style="background-color:{color};">📅 {label}</span>'


def priority_accent_style(priority: str) -> str:
    """
    v1.0: 우선순위 색상의 왼쪽 강조선(accent) 인라인 스타일을 만듭니다.
    배지(텍스트+색)와 함께 써서, 색만으로 우선순위를 구분하지 않도록 합니다.
    """
    color = PRIORITY_COLORS.get(priority, "#94A3B8")
    return f"border-left: 4px solid {color}; padding-left: 0.6rem;"


def metadata_line_html(task) -> str:
    """
    v1.0: 요청자/LOT/SLOT/요청일을 한 줄의 보조 정보로 만듭니다.
    값이 없는 항목은 표시하지 않고("-" 채우지 않음), 값이 하나도 없으면
    빈 문자열을 반환해서 아예 줄 자체가 생기지 않게 합니다.
    """
    parts = []
    if task.requester:
        parts.append(f"👤 {task.requester}")
    if task.lot:
        parts.append(f"LOT {task.lot}")
    if task.slot:
        parts.append(f"SLOT {task.slot}")
    if task.request_date:
        parts.append(f"요청일 {task.request_date}")

    if not parts:
        return ""

    return f"<div class='task-meta' style='margin-top:0.25rem;'>{' · '.join(parts)}</div>"


def build_copy_text(task) -> str:
    """
    v1.0: 할 일 정보를 이메일/메신저 등에 붙여넣기 좋은 텍스트로 만듭니다.
    값이 없는 선택 항목(요청자/LOT/SLOT/요청일/마감일/메모)은 제외합니다.
    """
    lines = [f"Title: {task.title}"]

    if task.requester:
        lines.append(f"Requester: {task.requester}")
    if task.lot:
        lines.append(f"LOT: {task.lot}")
    if task.slot:
        lines.append(f"SLOT: {task.slot}")
    if task.request_date:
        lines.append(f"Request Date: {task.request_date}")
    if task.due_date:
        lines.append(f"Due Date: {task.due_date}")

    lines.append(f"Priority: {PRIORITY_LABELS.get(task.priority, task.priority)}")

    if task.memo:
        lines.append(f"Memo: {task.memo}")

    return "\n".join(lines)
