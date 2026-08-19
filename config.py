"""
config.py

프로젝트 전체에서 공통으로 사용하는 설정값을 모아두는 파일입니다.
색상, 우선순위 종류, 파일 경로 등을 여기서 관리하면
나중에 디자인이나 값을 바꿀 때 이 파일만 수정하면 됩니다.
"""

from pathlib import Path

# ----------------------------
# 파일 경로 설정
# ----------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"

TASKS_FILE = DATA_DIR / "tasks.json"
SETTINGS_FILE = DATA_DIR / "settings.json"
TODAY_LIST_FILE = DATA_DIR / "today_list.json"
STYLE_FILE = ASSETS_DIR / "style.css"

# ----------------------------
# 우선순위(Priority) 설정
# ----------------------------
PRIORITY_HIGH = "high"
PRIORITY_MEDIUM = "medium"
PRIORITY_LOW = "low"

# 화면에 표시할 순서 (High가 먼저 오도록)
PRIORITY_ORDER = [PRIORITY_HIGH, PRIORITY_MEDIUM, PRIORITY_LOW]

# 화면에 보여줄 라벨
PRIORITY_LABELS = {
    PRIORITY_HIGH: "High",
    PRIORITY_MEDIUM: "Medium",
    PRIORITY_LOW: "Low",
}

# 우선순위별 색상 (뱃지, 강조 표시에 사용)
PRIORITY_COLORS = {
    PRIORITY_HIGH: "#EF4444",    # 레드
    PRIORITY_MEDIUM: "#F59E0B",  # 앰버
    PRIORITY_LOW: "#22C55E",     # 그린
}

# ----------------------------
# 마감일(Due Date) 설정
# ----------------------------
# 마감일 배지 색상: 지남(빨강) / 오늘(앰버) / 남음(회색)
DUE_COLORS = {
    "overdue": "#EF4444",   # 마감일이 지난 경우
    "today": "#F59E0B",     # 오늘이 마감일인 경우
    "upcoming": "#64748B",  # 아직 여유가 있는 경우
}

# ----------------------------
# 오늘의 작업 (Today's Tasks) 추천 설정
# ----------------------------
# 우선순위별 기본 점수 (중요할수록 높게)
RECOMMEND_PRIORITY_SCORES = {
    PRIORITY_HIGH: 30,
    PRIORITY_MEDIUM: 20,
    PRIORITY_LOW: 10,
}

# 자동 추천 개수의 "목표치" (소프트 타깃) - 지난/오늘 마감인 급한 할 일은
# 이 개수를 넘더라도 전부 포함하고, 나머지 자리를 점수 순으로 채웁니다.
TODAY_SOFT_TARGET = 5

# 요청일(request_date)이 오래될수록 주는 가산점.
# (기준 일수, 가산점) 목록 - 큰 기준부터 확인해서 한 번만 적용합니다.
REQUEST_AGE_BONUS_THRESHOLDS = [
    (14, 20),  # 요청한 지 14일 이상 지난 경우
    (7, 10),   # 요청한 지 7일 이상 지난 경우
]

# ----------------------------
# 테마(Theme) 설정
# ----------------------------
THEME_LIGHT = "light"
THEME_DARK = "dark"
DEFAULT_THEME = THEME_LIGHT

# 테마별 색상 팔레트
THEME_COLORS = {
    THEME_LIGHT: {
        "background": "#F5F7FA",
        "card_bg": "#FFFFFF",
        "text": "#1E293B",
        "text_secondary": "#64748B",
        "border": "#E2E8F0",
        "primary": "#6366F1",
        "shadow": "rgba(0, 0, 0, 0.08)",
    },
    THEME_DARK: {
        "background": "#0F172A",
        "card_bg": "#1E293B",
        "text": "#E2E8F0",
        "text_secondary": "#94A3B8",
        "border": "#334155",
        "primary": "#818CF8",
        "shadow": "rgba(0, 0, 0, 0.45)",
    },
}

# ----------------------------
# 기타 설정
# ----------------------------
RECENT_COMPLETED_COUNT = 5  # 대시보드에 보여줄 최근 완료 작업 개수
DATETIME_FORMAT = "%Y-%m-%d %H:%M"
