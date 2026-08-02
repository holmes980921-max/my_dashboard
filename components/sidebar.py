"""
components/sidebar.py

사이드바 화면을 그리는 파일입니다.
현재는 테마(다크/라이트) 선택 기능만 있지만,
나중에 로그인, 카테고리 필터 등을 추가할 자리이기도 합니다.
"""

import streamlit as st

from config import THEME_LIGHT, THEME_DARK
from utils.theme import get_current_theme, set_theme


def render_sidebar() -> str:
    """사이드바를 그리고, 사용자가 선택한 테마 값을 반환합니다."""
    with st.sidebar:
        st.markdown("### ⚙️ 설정")

        current_theme = get_current_theme()
        options = [THEME_LIGHT, THEME_DARK]
        labels = {THEME_LIGHT: "☀️ Light Mode", THEME_DARK: "🌙 Dark Mode"}

        selected_theme = st.radio(
            "테마 선택",
            options=options,
            format_func=lambda t: labels[t],
            index=options.index(current_theme),
            label_visibility="collapsed",
        )

        # 사용자가 테마를 바꾸면 즉시 저장하고 화면을 새로고침합니다.
        if selected_theme != current_theme:
            set_theme(selected_theme)
            st.rerun()

        return selected_theme
