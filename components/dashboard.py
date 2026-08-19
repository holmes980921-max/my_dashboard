"""
components/dashboard.py

Dashboard 탭 화면을 그리는 파일입니다.
전체 요약/통계를 한눈에 보여주는 자리이며, 실제 "오늘의 작업"을
추천받고 직접 추가/제외하는 상호작용은 Today 탭(components/today.py)이
담당합니다 - Dashboard는 읽기 전용 요약 정보에 집중합니다.

v1.0: 메인 진행률(Progress)은 이제 "오늘의 작업" 기준입니다. 전체
할 일 기준 완료율은 보조 정보로 캡션에 작게 표시합니다.
"""

import streamlit as st

from components.common import format_datetime, priority_badge_html, due_badge_html
from core.task_manager import get_dashboard_stats
from core.today_manager import get_today_progress


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


def render_dashboard() -> None:
    """Dashboard 탭 전체를 그립니다."""
    stats = get_dashboard_stats()
    today_stats = get_today_progress()

    st.markdown("#### 📊 오늘의 현황")

    # 5개의 지표 카드를 한 줄에 배치 - 진행률은 "오늘의 작업" 기준입니다.
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        _render_stat_card("오늘의 작업", today_stats["total"])
    with col2:
        _render_stat_card("오늘 완료", today_stats["completed"])
    with col3:
        _render_stat_card("오늘 진행률", f"{today_stats['progress']}%")
    with col4:
        _render_stat_card("High Priority", len(stats["high_priority"]))
    with col5:
        # 오늘 마감이거나 이미 지난 할 일 개수 (전체 기준)
        _render_stat_card("Due Today", len(stats["due_today"]))

    # 전체 할 일 기준 완료율은 보조 정보로만 작게 표시 (요청사항: 클러터 방지)
    st.caption(
        f"전체 할 일 기준 진행률: {stats['progress']}% "
        f"(총 {stats['total']}개 중 {stats['completed']}개 완료) · "
        "오늘의 작업 추천/관리는 🎯 Today 탭에서 확인하세요."
    )

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
