"""
components/dashboard.py

Dashboard 탭 화면을 그리는 파일입니다.
전체 현황(Total/Completed/Progress/High Priority)과
최근 완료된 작업을 카드 형태로 보여줍니다.
"""

import streamlit as st

from components.common import format_datetime, priority_badge_html, due_badge_html
from core.task_manager import get_dashboard_stats, get_recommended_tasks


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


def _render_recommend_card(item: dict, rank: int) -> None:
    """추천 할 일 카드 하나를 그립니다. (순위 메달 + 제목 + 배지 + 추천 이유)"""
    task = item["task"]
    rank_icons = ["🥇", "🥈", "🥉"]
    icon = rank_icons[rank] if rank < len(rank_icons) else "⭐"

    reasons = " · ".join(item["reasons"]) if item["reasons"] else "여유 있을 때 미리 해두세요"

    st.markdown(
        f"""
        <div class="dashboard-card recommend-card">
            <div>{icon} <span class="task-title">{task.title}</span></div>
            <div style="margin: 0.4rem 0 0.3rem 0;">
                {priority_badge_html(task.priority)}{due_badge_html(task)}
            </div>
            <div class="task-meta">💡 {reasons}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_recommendations() -> None:
    """'오늘의 추천' 섹션을 그립니다. 마감일 + 중요도 점수 상위 3개를 보여줍니다."""
    st.markdown("#### 🎯 오늘의 추천")

    recommended = get_recommended_tasks()

    if not recommended:
        st.info("추천할 할 일이 없습니다. Todo 탭에서 새 할 일을 추가해보세요!")
        return

    cols = st.columns(len(recommended))
    for rank, (col, item) in enumerate(zip(cols, recommended)):
        with col:
            _render_recommend_card(item, rank)


def render_dashboard() -> None:
    """Dashboard 탭 전체를 그립니다."""
    stats = get_dashboard_stats()

    # 오늘 뭐부터 할지 바로 보이도록 추천 섹션을 가장 위에 배치
    _render_recommendations()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📊 현재 현황")

    # 5개의 지표 카드를 한 줄에 배치
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        _render_stat_card("Total Tasks", stats["total"])
    with col2:
        _render_stat_card("Completed", stats["completed"])
    with col3:
        _render_stat_card("Progress", f"{stats['progress']}%")
    with col4:
        _render_stat_card("High Priority", len(stats["high_priority"]))
    with col5:
        # 오늘 마감이거나 이미 지난 할 일 개수
        _render_stat_card("Due Today", len(stats["due_today"]))

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
                        <span class="task-meta">완료: {format_datetime(task.completed_at)}</span>
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
                        {priority_badge_html(task.priority)}{due_badge_html(task)}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
