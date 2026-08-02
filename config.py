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
