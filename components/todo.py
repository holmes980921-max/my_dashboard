"""
components/todo.py

Todo 탭 화면을 그리는 파일입니다.
할 일 추가, 검색, 진행률 표시, 목록(체크/우선순위/Pin/삭제) 기능을 담당합니다.
"""

from datetime import date

import streamlit as st

from config import PRIORITY_ORDER, PRIORITY_LABELS, PRIORITY_MEDIUM, DUE_COLORS
from core.task_manager import (
    add_task,
    complete_task,
    delete_task,
    toggle_pin,
    update_priority,
    update_due_date,
    update_memo,
    get_days_left,
    get_todo_tasks,
    get_all_tasks,
)
from utils.validators import validate_new_task


def _render_add_form() -> None:
    """할 일 입력창 + Add 버튼을 그립니다. st.form이라 Enter 키로도 제출됩니다."""
    with st.form(key="add_task_form", clear_on_submit=True):
        col_input, col_priority, col_button = st.columns([3, 1, 1])

        with col_input:
            new_title = st.text_input(
                "할 일을 입력하세요",
                label_visibility="collapsed",
                placeholder="새로운 할 일을 입력하세요...",
            )
        with col_priority:
            new_priority = st.selectbox(
                "우선순위",
                options=PRIORITY_ORDER,
                format_func=lambda p: PRIORITY_LABELS[p],
                index=PRIORITY_ORDER.index(PRIORITY_MEDIUM),
                label_visibility="collapsed",
            )
        with col_button:
            submitted = st.form_submit_button("➕ Add", use_container_width=True)

        # 마감일/메모는 선택 사항이라 expander(접이식 영역) 안에 넣어서 화면을 깔끔하게 유지
        with st.expander("📅 마감일 / 🗒️ 메모 추가 (선택)"):
            new_due = st.date_input(
                "마감일",
                value=None,  # 기본값 없음 -> 선택하지 않으면 None이 반환됩니다
                format="YYYY-MM-DD",
                key="add_due_date",
            )
            new_memo = st.text_area(
                "메모",
                placeholder="상세 내용을 적어두세요... (선택)",
                key="add_memo",
            )

        if submitted:
            error_message = validate_new_task(new_title, get_all_tasks())
            if error_message:
                st.warning(error_message)
            else:
                # date 객체는 JSON에 저장할 수 없으므로 "YYYY-MM-DD" 문자열로 변환
                due_str = new_due.isoformat() if new_due else None
                add_task(new_title, new_priority, due_date=due_str, memo=new_memo)
                st.rerun()


def _render_progress_bar() -> None:
    """전체 대비 완료 진행률을 프로그레스 바로 보여줍니다."""
    all_tasks = get_all_tasks()
    total = len(all_tasks)
    completed = len([t for t in all_tasks if t.completed])
    ratio = (completed / total) if total > 0 else 0

    st.progress(ratio, text=f"진행률 {int(ratio * 100)}% ({completed}/{total})")


def _due_badge_html(task) -> str:
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


def _render_edit_expander(task) -> None:
    """항목 아래 접이식 영역에서 마감일과 메모를 수정할 수 있게 합니다."""
    # 메모가 있으면 제목에 미리보기를 살짝 보여줌
    expander_label = "✏️ 마감일 / 메모"
    if task.memo:
        preview = task.memo if len(task.memo) <= 20 else task.memo[:20] + "..."
        expander_label += f"  —  🗒️ {preview}"

    with st.expander(expander_label):
        current_due = date.fromisoformat(task.due_date) if task.due_date else None
        edited_due = st.date_input(
            "마감일",
            value=current_due,
            format="YYYY-MM-DD",
            key=f"due_{task.id}",
        )
        edited_memo = st.text_area(
            "메모",
            value=task.memo,
            placeholder="메모를 입력하세요...",
            key=f"memo_{task.id}",
        )

        col_save, col_clear, _ = st.columns([1, 1, 2])
        with col_save:
            if st.button("💾 저장", key=f"save_{task.id}", use_container_width=True):
                update_due_date(task.id, edited_due.isoformat() if edited_due else None)
                update_memo(task.id, edited_memo)
                st.rerun()
        with col_clear:
            # 마감일이 있을 때만 "제거" 버튼을 보여줌
            if task.due_date and st.button(
                "📅 마감일 제거", key=f"clear_due_{task.id}", use_container_width=True
            ):
                update_due_date(task.id, None)
                st.rerun()


def _render_task_item(task) -> None:
    """Todo 목록의 항목 하나(체크박스/제목/우선순위/Pin/삭제)를 그립니다."""
    col_check, col_title, col_priority, col_pin, col_delete = st.columns(
        [0.5, 3, 1.3, 0.6, 0.6]
    )

    with col_check:
        checked = st.checkbox("완료", key=f"check_{task.id}", label_visibility="collapsed")
        if checked:
            # 체크박스를 선택하면 완료 처리 후 새로고침 -> 자동으로 Completed 탭 목록에 나타남
            complete_task(task.id)
            st.rerun()

    with col_title:
        pin_icon = "📌 " if task.pinned else ""
        memo_icon = " 🗒️" if task.memo else ""
        st.markdown(
            f"<span class='task-title'>{pin_icon}{task.title}</span>"
            f"{memo_icon} {_due_badge_html(task)}",
            unsafe_allow_html=True,
        )

    with col_priority:
        new_priority = st.selectbox(
            "우선순위",
            options=PRIORITY_ORDER,
            format_func=lambda p: PRIORITY_LABELS[p],
            index=PRIORITY_ORDER.index(task.priority),
            key=f"priority_{task.id}",
            label_visibility="collapsed",
        )
        if new_priority != task.priority:
            update_priority(task.id, new_priority)
            st.rerun()

    with col_pin:
        pin_label = "📌" if task.pinned else "📍"
        if st.button(pin_label, key=f"pin_{task.id}"):
            toggle_pin(task.id)
            st.rerun()

    with col_delete:
        if st.button("🗑️", key=f"delete_{task.id}"):
            delete_task(task.id)
            st.rerun()

    # 항목 아래에 마감일/메모 수정 영역 표시
    _render_edit_expander(task)


def render_todo() -> None:
    """Todo 탭 전체를 그립니다."""
    st.markdown("#### 📝 새로운 할 일 추가")
    _render_add_form()

    st.markdown("<br>", unsafe_allow_html=True)

    search_keyword = st.text_input("🔍 할 일 검색", placeholder="검색어를 입력하세요...")

    _render_progress_bar()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📋 할 일 목록")

    tasks = get_todo_tasks(search_keyword)

    if not tasks:
        st.info("할 일이 없습니다. 새로운 할 일을 추가해보세요!")
        return

    for task in tasks:
        with st.container(border=True):
            _render_task_item(task)
