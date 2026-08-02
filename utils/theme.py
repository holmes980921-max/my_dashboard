"""
utils/theme.py

다크 모드 / 라이트 모드에 맞는 색상을 계산하고,
CSS를 만들어서 화면에 적용하는 역할을 담당합니다.
"""

import streamlit as st

from config import THEME_COLORS, STYLE_FILE, DEFAULT_THEME
from utils.storage import load_settings, save_settings


def get_current_theme() -> str:
    """저장된 설정에서 현재 테마 값을 읽어옵니다."""
    settings = load_settings()
    return settings.get("theme", DEFAULT_THEME)


def set_theme(theme: str) -> None:
    """테마를 변경하고 settings.json에 저장합니다."""
    settings = load_settings()
    settings["theme"] = theme
    save_settings(settings)


def apply_theme(theme: str) -> None:
    """
    현재 테마에 맞는 색상을 CSS 변수로 만들어
    st.markdown을 통해 화면 전체에 적용합니다.
    assets/style.css의 공통 스타일(카드, 애니메이션 등)도 함께 불러옵니다.
    """
    colors = THEME_COLORS.get(theme, THEME_COLORS[DEFAULT_THEME])

    # 테마 색상을 CSS 변수(:root)로 주입합니다.
    # -> style.css에서는 var(--card-bg) 처럼 이 값들을 그대로 사용합니다.
    theme_css = f"""
    <style>
    :root {{
        --background: {colors['background']};
        --card-bg: {colors['card_bg']};
        --text-color: {colors['text']};
        --text-secondary: {colors['text_secondary']};
        --border-color: {colors['border']};
        --primary-color: {colors['primary']};
        --shadow-color: {colors['shadow']};
    }}
    </style>
    """
    st.markdown(theme_css, unsafe_allow_html=True)

    # 공통 스타일(style.css)을 불러와 적용합니다.
    if STYLE_FILE.exists():
        with open(STYLE_FILE, "r", encoding="utf-8") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
