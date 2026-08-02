"""
components/dashboard.py

Dashboard 탭 화면을 그리는 파일입니다.
전체 현황(Total/Completed/Progress/High Priority)과
최근 완료된 작업을 카드 형태로 보여줍니다.
"""

from datetime import datetime

import streamlit as st

from config import PRIORITY_COLORS, PRIORITY_LABELS, DATETIME_FORMAT
from core.task_manager import get_dashboard_stats


def _format_datetime(iso_string) -> str:
    """ISO 형식 문자열을 보기 좋은 날짜/시간 문자열로 변환합니다."""
    if not iso_string:
        return "-"
    try:
        return datetime.fromisoformat(iso_string).strftime(DATETIME_FORMAT)
    except ValueError:
        return "-"


def _render_stat_card(label: str, value) -> None:
    """지표 카드 하나를 그립니다. (Total, Completed 등)"""
    st.markdown(
        f"""
        <div class="dashboard-card stat-card">
            <div class="stat-value">{value}</div>
            <div class="stat-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _priority_badge_html(priority: str) -> str:
    """우선순위 뱃지 HTML 조각을 만듭니다."""
    color = PRIORITY_COLORS.get(priority, "#94A3B8")
    label = PRIORITY_LABELS.get(priority, priority)
    return f'<span class="priority-badge" style="background-color:{color};">{label}</span>'


def render_dashboard() -> None:
    """Dashboard 탭 전체를 그립니다."""
    stats = get_dashboard_stats()

    st.markdown("#### 📊 현재 현황")

    # 4개의 지표 카드를 한 줄에 배치
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        _render_stat_card("Total Tasks", stats["total"])
    with col2:
        _render_stat_card("Completed", stats["completed"])
    with col3:
        _render_stat_card("Progress", f"{stats['progress']}%")
    with col4:
        _render_stat_card("High Priority", len(stats["high_priority"]))

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    # 최근 완료된 작업 5개
    with col_left:
        st.markdown("#### 🕘 Recent Completed")
        if not stats["recent_completed"]:
            st.info("아직 완료된 작업이 없습니다.")
        else:
            for task in stats["recent_completed"]:
                st.markdown(
                    f"""
                    <div class="dashboard-card">
                        <span class="task-title">✔ {task.title}</span><br>
                        <span class="task-meta">완료: {_format_datetime(task.completed_at)}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # 우선순위 높은 작업들
    with col_right:
        st.markdown("#### 🔥 High Priority Tasks")
        if not stats["high_priority"]:
            st.info("긴급한 할 일이 없습니다.")
        else:
            for task in stats["high_priority"]:
                st.markdown(
                    f"""
                    <div class="dashboard-card">
                        <span class="task-title">{task.title}</span>
                        {_priority_badge_html(task.priority)}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
