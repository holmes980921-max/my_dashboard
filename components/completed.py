"""
components/completed.py

Completed 탭 화면을 그리는 파일입니다.
완료된 할 일 목록과 완료 시각, Restore/Delete 버튼을 보여줍니다.
"""

from datetime import datetime

import streamlit as st

from config import DATETIME_FORMAT
from core.task_manager import get_completed_tasks, restore_task, delete_task


def _format_datetime(iso_string) -> str:
    """ISO 형식 문자열을 보기 좋은 날짜/시간 문자열로 변환합니다."""
    if not iso_string:
        return "-"
    try:
        return datetime.fromisoformat(iso_string).strftime(DATETIME_FORMAT)
    except ValueError:
        return "-"


def render_completed() -> None:
    """Completed 탭 전체를 그립니다."""
    st.markdown("#### ✅ 완료된 할 일")

    tasks = get_completed_tasks()

    if not tasks:
        st.info("아직 완료된 할 일이 없습니다.")
        return

    for task in tasks:
        with st.container(border=True):
            col_title, col_time, col_restore, col_delete = st.columns([3, 1.6, 1, 1])

            with col_title:
                st.markdown(f"<span class='task-title'>✔ {task.title}</span>", unsafe_allow_html=True)
            with col_time:
                st.markdown(
                    f"<span class='task-meta'>완료: {_format_datetime(task.completed_at)}</span>",
                    unsafe_allow_html=True,
                )
            with col_restore:
                if st.button("↩ Restore", key=f"restore_{task.id}", use_container_width=True):
                    restore_task(task.id)
                    st.rerun()
            with col_delete:
                if st.button("🗑️ Delete", key=f"del_completed_{task.id}", use_container_width=True):
                    delete_task(task.id)
                    st.rerun()
