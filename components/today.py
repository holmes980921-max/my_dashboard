"""
components/today.py

Today 탭 화면을 그리는 파일입니다.

역할:
- 자동 추천 + 사용자가 직접 추가/이월된 "오늘의 작업" 목록을 보여줍니다.
- 완료 처리(완료해도 오늘 하루는 흐리게 표시되어 목록에 남아있습니다),
  되돌리기, "오늘 목록에서 빼기"(원본 할 일은 삭제하지 않음)를 제공합니다.
- Todo 탭의 할 일 중 아직 오늘 목록에 없는 것을 수동으로 추가할 수 있습니다.
- 오늘의 작업 기준 진행률을 보여줍니다.
"""

import streamlit as st

from components.common import due_badge_html, metadata_line_html, priority_accent_style, priority_badge_html
from core.task_manager import complete_task, restore_task, get_todo_tasks
from core.today_manager import (
    SOURCE_CARRIED_OVER,
    SOURCE_MANUAL,
    SOURCE_RECOMMENDED,
    add_to_today,
    exclude_from_today,
    get_today_progress,
    get_today_tasks,
)

_SOURCE_LABELS = {
    SOURCE_RECOMMENDED: "🎯 추천",
    SOURCE_MANUAL: "🙋 직접 추가",
    SOURCE_CARRIED_OVER: "↩️ 이월됨",
}


def _render_progress() -> None:
    """오늘의 작업 기준 진행률을 보여줍니다."""
    stats = get_today_progress()
    if stats["total"] == 0:
        st.info("오늘의 작업이 아직 없습니다. 아래에서 추가해보세요!")
        return
    ratio = stats["completed"] / stats["total"]
    st.progress(ratio, text=f"오늘의 진행률 {stats['progress']}% ({stats['completed']}/{stats['total']})")


def _render_today_item(item: dict) -> None:
    """오늘의 작업 항목 하나를 그립니다."""
    task = item["task"]
    source_label = _SOURCE_LABELS.get(item["source"], "")

    with st.container(border=True):
        col_info, col_action = st.columns([4, 1.4])

        with col_info:
            accent = priority_accent_style(task.priority)
            if task.completed:
                # 완료된 항목은 흐리게 + 취소선 - 오늘 하루는 계속 목록에 남아
                # 진행률 계산에 반영됩니다.
                title_html = f"<s style='color: var(--text-secondary);'>{task.title}</s>"
            else:
                title_html = f"<span class='task-title'>{task.title}</span>"

            st.markdown(
                f"<div style='{accent}'>"
                f"{priority_badge_html(task.priority)} {title_html} {due_badge_html(task)}"
                f" <span class='task-meta'>{source_label}</span>"
                f"</div>{metadata_line_html(task)}",
                unsafe_allow_html=True,
            )

        with col_action:
            if task.completed:
                if st.button("↩ 되돌리기", key=f"today_restore_{task.id}", use_container_width=True):
                    restore_task(task.id)
                    st.rerun()
            else:
                if st.button("✅ 완료하기", key=f"today_complete_{task.id}", use_container_width=True):
                    complete_task(task.id)
                    st.toast(f"'{task.title}' 완료했습니다! 🎉", icon="✅")
                    st.rerun()

            if st.button("➖ 오늘 목록에서 빼기", key=f"today_exclude_{task.id}", use_container_width=True):
                exclude_from_today(task.id)
                st.rerun()


def _render_add_manual() -> None:
    """Todo 목록 중 아직 오늘의 작업에 없는 항목을 골라서 수동으로 추가합니다."""
    todo_tasks = get_todo_tasks()
    today_ids = {item["task"].id for item in get_today_tasks()}
    candidates = [t for t in todo_tasks if t.id not in today_ids]

    with st.expander("➕ Todo에서 오늘의 작업으로 추가"):
        if not candidates:
            st.caption("추가할 수 있는 할 일이 없습니다 (모든 미완료 할 일이 이미 오늘 목록에 있습니다).")
            return

        options = {t.id: t.title for t in candidates}
        selected_id = st.selectbox(
            "추가할 할 일 선택",
            options=list(options.keys()),
            format_func=lambda tid: options[tid],
            key="today_add_select",
            label_visibility="collapsed",
        )
        if st.button("추가", key="today_add_button"):
            add_to_today(selected_id)
            st.rerun()


def render_today() -> None:
    """Today 탭 전체를 그립니다."""
    st.markdown("#### 🎯 오늘의 작업")
    _render_progress()

    st.markdown("<br>", unsafe_allow_html=True)

    items = get_today_tasks()
    if not items:
        st.info("오늘의 작업이 없습니다.")
    else:
        for item in items:
            _render_today_item(item)

    st.markdown("<br>", unsafe_allow_html=True)
    _render_add_manual()
