"""
components/todo.py

Todo 탭 화면을 그리는 파일입니다.
할 일 추가, 검색, 진행률 표시, 목록(하이브리드 카드) 기능을 담당합니다.

v1.0 카드 구조 (3단계 정보 밀도):
- Level 1 (항상 보임): 순서 이동 / 우선순위(배지+왼쪽 강조선) / 제목 / 마감일 배지 / 완료 버튼
- Level 2 (항상 보임, 값이 있을 때만): 요청자 · LOT · SLOT · 요청일 요약 줄
- Level 3 (접이식): 메모, 편집 폼, 복사, 삭제

Pin 기능은 v1.0에서 UI상 제거되었습니다 (수동 정렬이 그 역할을 대신합니다).
기존 데이터의 pinned 필드 자체는 하위 호환을 위해 그대로 남아있습니다.
"""

from datetime import date

import streamlit as st

from config import PRIORITY_ORDER, PRIORITY_LABELS, PRIORITY_MEDIUM
from components.common import build_copy_text, due_badge_html, metadata_line_html, priority_accent_style, priority_badge_html
from core.task_manager import (
    add_task,
    complete_task,
    delete_task,
    update_title,
    update_priority,
    update_due_date,
    update_memo,
    update_requester,
    update_lot,
    update_slot,
    update_request_date,
    get_todo_tasks,
    get_all_tasks,
    move_task_up,
    move_task_down,
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

        # 선택 항목들은 expander(접이식 영역) 안에 넣어서 화면을 깔끔하게 유지
        with st.expander("📅 추가 정보 입력 (선택)"):
            col_due, col_request_date = st.columns(2)
            with col_due:
                new_due = st.date_input(
                    "마감일", value=None, format="YYYY-MM-DD", key="add_due_date"
                )
            with col_request_date:
                new_request_date = st.date_input(
                    "요청일", value=None, format="YYYY-MM-DD", key="add_request_date"
                )

            col_requester, col_lot, col_slot = st.columns(3)
            with col_requester:
                new_requester = st.text_input("요청자", key="add_requester")
            with col_lot:
                new_lot = st.text_input("LOT", key="add_lot")
            with col_slot:
                new_slot = st.text_input("SLOT", key="add_slot")

            new_memo = st.text_area(
                "메모", placeholder="상세 내용을 적어두세요... (선택)", key="add_memo"
            )

        if submitted:
            error_message = validate_new_task(new_title)
            if error_message:
                st.warning(error_message)
            else:
                # date 객체는 JSON에 저장할 수 없으므로 "YYYY-MM-DD" 문자열로 변환
                add_task(
                    new_title,
                    new_priority,
                    due_date=new_due.isoformat() if new_due else None,
                    memo=new_memo,
                    requester=new_requester,
                    lot=new_lot,
                    slot=new_slot,
                    request_date=new_request_date.isoformat() if new_request_date else None,
                )
                st.rerun()


def _render_progress_bar() -> None:
    """전체 대비 완료 진행률을 프로그레스 바로 보여줍니다. (오늘의 작업 진행률은 Today 탭에서 확인)"""
    all_tasks = get_all_tasks()
    total = len(all_tasks)
    completed = len([t for t in all_tasks if t.completed])
    ratio = (completed / total) if total > 0 else 0

    st.progress(ratio, text=f"전체 진행률 {int(ratio * 100)}% ({completed}/{total})")


def _render_delete_control(task) -> None:
    """
    가벼운 2단계 확인 후 삭제합니다. session_state에 "확인 대기중" 상태를
    잠깐 기억해두는 방식이라, 별도 라이브러리 없이도 실수로 삭제하는 것을
    막을 수 있습니다.
    """
    confirm_key = f"confirm_delete_{task.id}"

    if st.session_state.get(confirm_key):
        st.warning("정말 삭제할까요? 되돌릴 수 없습니다.")
        col_yes, col_no = st.columns(2)
        with col_yes:
            if st.button("네, 삭제", key=f"delete_yes_{task.id}", use_container_width=True):
                delete_task(task.id)
                st.session_state.pop(confirm_key, None)
                st.rerun()
        with col_no:
            if st.button("취소", key=f"delete_no_{task.id}", use_container_width=True):
                st.session_state.pop(confirm_key, None)
                st.rerun()
    else:
        if st.button("🗑️ 삭제", key=f"delete_{task.id}", use_container_width=True):
            st.session_state[confirm_key] = True
            st.rerun()


def _render_detail_expander(task) -> None:
    """Level 3: 접이식 상세/편집 영역 - 메모 미리보기, 전체 필드 편집, 복사, 삭제."""
    expander_label = "📋 상세 / 편집"
    if task.memo:
        preview = task.memo if len(task.memo) <= 20 else task.memo[:20] + "..."
        expander_label += f"  —  🗒️ {preview}"

    with st.expander(expander_label):
        edited_title = st.text_input("제목", value=task.title, key=f"edit_title_{task.id}")

        col_priority, col_due = st.columns(2)
        with col_priority:
            edited_priority = st.selectbox(
                "우선순위",
                options=PRIORITY_ORDER,
                format_func=lambda p: PRIORITY_LABELS[p],
                index=PRIORITY_ORDER.index(task.priority),
                key=f"edit_priority_{task.id}",
            )
        with col_due:
            current_due = date.fromisoformat(task.due_date) if task.due_date else None
            edited_due = st.date_input(
                "마감일", value=current_due, format="YYYY-MM-DD", key=f"edit_due_{task.id}"
            )

        col_requester, col_lot, col_slot = st.columns(3)
        with col_requester:
            edited_requester = st.text_input("요청자", value=task.requester, key=f"edit_requester_{task.id}")
        with col_lot:
            edited_lot = st.text_input("LOT", value=task.lot, key=f"edit_lot_{task.id}")
        with col_slot:
            edited_slot = st.text_input("SLOT", value=task.slot, key=f"edit_slot_{task.id}")

        current_request_date = date.fromisoformat(task.request_date) if task.request_date else None
        edited_request_date = st.date_input(
            "요청일", value=current_request_date, format="YYYY-MM-DD", key=f"edit_request_date_{task.id}"
        )

        edited_memo = st.text_area("메모", value=task.memo, key=f"edit_memo_{task.id}")

        col_save, col_copy, col_delete = st.columns([1, 1, 1])
        with col_save:
            if st.button("💾 저장", key=f"save_{task.id}", use_container_width=True):
                error_message = validate_new_task(edited_title)
                if error_message:
                    st.warning(error_message)
                else:
                    update_title(task.id, edited_title)
                    update_priority(task.id, edited_priority)
                    update_due_date(task.id, edited_due.isoformat() if edited_due else None)
                    update_requester(task.id, edited_requester)
                    update_lot(task.id, edited_lot)
                    update_slot(task.id, edited_slot)
                    update_request_date(
                        task.id, edited_request_date.isoformat() if edited_request_date else None
                    )
                    update_memo(task.id, edited_memo)
                    st.rerun()
        with col_copy:
            with st.popover("📋 복사", use_container_width=True):
                st.code(build_copy_text(task), language=None)
        with col_delete:
            _render_delete_control(task)


def _render_task_card(task, is_first: bool, is_last: bool) -> None:
    """
    Todo 목록의 카드 하나를 그립니다 (Level 1 + Level 2 + Level 3).

    is_first/is_last: 검색어로 화면에 안 보이는 항목이 있어도, 항상 "전체
    미완료 목록" 기준의 맨 위/맨 아래 여부입니다 (render_todo 참고).
    """
    col_order, col_title, col_complete = st.columns([0.5, 4.4, 1.2])

    with col_order:
        # ▲▼를 세로로 쌓아서 한 칸에 배치 - 컬럼을 늘리지 않고 정렬 기능을 유지합니다.
        if st.button("▲", key=f"up_{task.id}", disabled=is_first, use_container_width=True):
            move_task_up(task.id)
            st.rerun()
        if st.button("▼", key=f"down_{task.id}", disabled=is_last, use_container_width=True):
            move_task_down(task.id)
            st.rerun()

    with col_title:
        # Level 1: 우선순위(배지+왼쪽 강조선, 색+텍스트 병행) + 제목(줄바꿈 허용) + 마감일 배지
        accent = priority_accent_style(task.priority)
        memo_icon = " 🗒️" if task.memo else ""
        st.markdown(
            f"<div style='{accent}'>"
            f"{priority_badge_html(task.priority)} <span class='task-title'>{task.title}</span>"
            f"{memo_icon} {due_badge_html(task)}"
            f"</div>"
            # Level 2: 요청자/LOT/SLOT/요청일 - 값이 하나도 없으면 아예 표시 안 됨
            f"{metadata_line_html(task)}",
            unsafe_allow_html=True,
        )

    with col_complete:
        if st.button("✅ 완료하기", key=f"complete_{task.id}", use_container_width=True):
            complete_task(task.id)
            st.toast(f"'{task.title}' 완료했습니다! 🎉", icon="✅")
            st.rerun()

    # Level 3: 접이식 상세/편집 영역
    _render_detail_expander(task)


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

    # 검색어로 필터링되기 전, 전체 미완료 목록 안에서의 위치를 미리 계산합니다.
    # 순서 이동(위/아래)의 맨 위/맨 아래 판정은 화면에 보이는 목록이 아니라
    # 항상 이 전체 순서를 기준으로 해야 하기 때문입니다.
    all_todo_ids = [t.id for t in get_todo_tasks()]
    last_index = len(all_todo_ids) - 1

    for task in tasks:
        position = all_todo_ids.index(task.id)
        with st.container(border=True):
            _render_task_card(task, is_first=(position == 0), is_last=(position == last_index))
