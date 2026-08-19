"""
app.py

My Dashboard 앱의 진입점(entry point)입니다.
페이지 설정, 상단 타이틀/날짜, 테마 적용, 탭 구성을 담당하며
실제 화면 내용은 components/ 폴더의 함수들을 호출해서 그립니다.

실행 방법: streamlit run app.py
"""

from datetime import datetime

import streamlit as st

from components.sidebar import render_sidebar
from components.dashboard import render_dashboard
from components.todo import render_todo
from components.today import render_today
from components.completed import render_completed
from utils.theme import apply_theme

# 1. 페이지 기본 설정 (Streamlit 규칙상 가장 먼저 호출되어야 합니다)
st.set_page_config(
    page_title="My Dashboard",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. 사이드바 렌더링 + 현재 테마 값 가져오기
current_theme = render_sidebar()

# 3. 테마(CSS) 적용
apply_theme(current_theme)

# 4. 상단 타이틀 + 현재 날짜
col_title, col_date = st.columns([3, 1])
with col_title:
    st.markdown("## 📋 My Dashboard")
with col_date:
    st.markdown(
        f"<div style='text-align:right; padding-top:1.3rem; color:var(--text-secondary);'>"
        f"{datetime.now().strftime('%Y년 %m월 %d일')}</div>",
        unsafe_allow_html=True,
    )

st.markdown("---")

# 5. 4개의 탭 구성 (v1.0: Today 탭 추가)
tab_dashboard, tab_todo, tab_today, tab_completed = st.tabs(
    ["📊 Dashboard", "📝 Todo", "🎯 Today", "✅ Completed"]
)

with tab_dashboard:
    render_dashboard()

with tab_todo:
    render_todo()

with tab_today:
    render_today()

with tab_completed:
    render_completed()
