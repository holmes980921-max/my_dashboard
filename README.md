# My Dashboard

Python과 Streamlit으로 만든 개인용 할 일 관리(Todo) 대시보드입니다.
JSON 파일 기반으로 데이터를 저장하며, 앱을 종료했다가 다시 실행해도
할 일 목록과 테마 설정이 그대로 유지됩니다.

## ✨ 프로젝트 소개

- **Dashboard 탭**: 🎯 오늘의 추천 TOP 3, 전체 할 일 현황(Total / Completed / Progress / High Priority / Due Today), 최근 완료 항목을 한눈에 확인
- **Todo 탭**: 할 일 추가/검색/우선순위 변경/Pin 고정/삭제, 마감일(D-day 배지)과 메모 관리
- **Completed 탭**: 완료된 할 일 확인, 복원(Restore), 삭제
- **Dark / Light 테마**: 선택한 테마는 재실행 후에도 유지
- 카드 레이아웃, 둥근 모서리, 그림자, hover 애니메이션 등 모던한 UI

## 🛠 설치 방법

1. Python 3.9 이상이 설치되어 있어야 합니다.
2. 프로젝트 폴더로 이동한 뒤, 필요한 패키지를 설치합니다.

```bash
cd my_dashboard
pip install -r requirements.txt
```

## 🚀 실행 방법

```bash
streamlit run app.py
```

실행 후 터미널에 표시되는 주소(기본값 `http://localhost:8501`)를 브라우저로 열면 됩니다.

## 📁 폴더 구조

```
my_dashboard/
│
├── app.py                     # 앱 진입점 (페이지 설정, 탭 구성)
├── config.py                  # 색상/우선순위/경로 등 전역 설정값
│
├── core/                      # 핵심 로직 (UI와 분리된 데이터 처리)
│   ├── models.py               # Task 데이터 구조 정의
│   └── task_manager.py         # 추가/삭제/완료/복원/검색/정렬 로직
│
├── components/                # 화면(UI) 렌더링
│   ├── common.py                # 공통 UI 조각 (배지, 날짜 포맷)
│   ├── sidebar.py               # 사이드바 (테마 선택)
│   ├── dashboard.py             # Dashboard 탭
│   ├── todo.py                  # Todo 탭
│   └── completed.py             # Completed 탭
│
├── utils/                     # 공통 보조 기능
│   ├── storage.py                # JSON 읽기/쓰기
│   ├── validators.py             # 입력값 검증
│   └── theme.py                   # 테마 CSS 적용
│
├── data/                      # 데이터 저장 폴더
│   ├── tasks.json
│   └── settings.json
│
├── assets/
│   └── style.css               # 카드/애니메이션/반응형 스타일
│
├── requirements.txt
└── README.md
```

## 📌 기능 설명

### Dashboard
- **🎯 오늘의 추천**: 마감일과 중요도를 점수로 계산해 "오늘 먼저 할 일" TOP 3를 자동 추천
  - 점수 = 우선순위(High 30 / Medium 20 / Low 10) + 마감 임박도(지남 50 / 오늘 40 / 1~3일 전 30~10) + Pin 보너스(5)
  - 각 카드에 추천 이유 표시 (예: "우선순위 High · 오늘 마감")
- Total Tasks, Completed Tasks, Progress(%), High Priority Tasks, Due Today 지표 카드
- 최근 완료된 할 일 5개 표시

### Todo
- 입력창 + Add 버튼 (Enter 키로도 추가 가능)
- 실시간 검색
- 진행률 프로그레스 바
- 각 항목: 체크박스(완료 처리) / 제목 / 우선순위 변경 / Pin 고정 / 삭제
- 체크박스를 선택하면 완료 처리되어 Completed 탭에서 확인 가능
- Pin 된 항목은 항상 목록 최상단에 표시

### Completed
- 완료된 할 일과 완료 시각 표시
- Restore 버튼: 다시 Todo 탭으로 이동
- Delete 버튼: 완전 삭제

### Priority
- High / Medium / Low 3단계, 색상으로 구분
- 언제든지 변경 가능

### Due Date (마감일)
- 할 일 추가 시 또는 나중에 항목의 "✏️ 마감일 / 메모" 영역에서 설정
- 목록에 D-day 배지 표시: 여유 있음(회색 D-N) / 오늘 마감(앰버 D-DAY) / 지남(빨강 N일 지남)
- 같은 우선순위 안에서는 마감일이 빠른 항목이 위로 정렬
- Dashboard에 "Due Today"(오늘 마감 + 지난 항목) 지표 카드 표시

### Memo (메모)
- 각 할 일에 상세 메모를 첨부 가능
- 메모가 있는 항목은 제목 옆에 🗒️ 아이콘 표시, 접이식 영역에 미리보기 제공

### 테마
- 사이드바에서 Light / Dark 모드 선택
- 선택한 테마는 `data/settings.json`에 저장되어 재실행 후에도 유지

### 데이터 검증
- 빈 문자열 / 공백만 입력 시 추가 불가
- 중복된 할 일 입력 시 "이미 존재하는 할 일입니다." 메시지 표시

## 🔮 향후 개발 계획

아래 기능들을 쉽게 추가할 수 있도록 `core/models.py`(데이터 구조)와
`core/task_manager.py`(로직)를 UI와 분리해두었습니다.

- 캘린더 뷰
- Category (카테고리) 분류
- Recurring Task (반복 작업)
- Notification (알림)
- Excel Integration (엑셀 내보내기/가져오기)
- Google Calendar 연동
- Login (사용자 로그인)
- Cloud Sync (클라우드 동기화)
