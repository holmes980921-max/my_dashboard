"""
core/models.py

할 일(Task) 하나의 데이터 구조를 정의하는 파일입니다.
나중에 마감일(due_date), 카테고리(category), 메모(memo) 같은
새로운 항목을 추가하고 싶다면 이 파일에 필드만 추가하면 됩니다.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional

from config import PRIORITY_MEDIUM


@dataclass
class Task:
    """할 일 하나를 표현하는 데이터 클래스입니다."""

    title: str
    priority: str = PRIORITY_MEDIUM
    completed: bool = False
    pinned: bool = False
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    due_date: Optional[str] = None  # 마감일 ("YYYY-MM-DD" 형식, 없으면 None)
    memo: str = ""                  # 상세 메모 (없으면 빈 문자열)

    # --- v1.0: 업무 정보 필드 ---
    requester: str = ""             # 요청자 (자유 텍스트, 없으면 빈 문자열)
    lot: str = ""                   # LOT 번호 (자유 텍스트, 없으면 빈 문자열)
    slot: str = ""                  # SLOT 번호 (자유 텍스트, 없으면 빈 문자열)
    request_date: Optional[str] = None  # 요청일 ("YYYY-MM-DD" 형식, 없으면 None)

    # --- v1.0: 수동 정렬 순서 ---
    # None이면 "아직 순서가 배정되지 않음"을 의미합니다. task_manager.py가
    # 처음 불러올 때 기존 데이터(순서 없음)를 created_at 순서로 한 번만
    # 자동 배정합니다 - 0은 "실제로 맨 앞"이라는 유효한 값이라 기본값으로
    # 쓰면 안 되므로, 배정 여부를 구분할 수 있도록 None을 기본값으로 둡니다.
    order: Optional[int] = None

    # --- 향후 확장 예정 필드 (필요할 때 아래처럼 추가하면 됩니다) ---
    # category: Optional[str] = None      # 카테고리
    # is_recurring: bool = False           # 반복 작업 여부

    def to_dict(self) -> dict:
        """Task 객체를 JSON 저장이 가능한 dict로 변환합니다."""
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "Task":
        """
        dict(JSON에서 읽은 데이터)를 Task 객체로 변환합니다.
        .get()을 사용해서, 예전 데이터에 새 필드가 없어도
        기본값으로 채워지도록 하여 에러 없이 동작하게 합니다.
        """
        return Task(
            id=data.get("id", uuid.uuid4().hex[:8]),
            title=data.get("title", ""),
            completed=data.get("completed", False),
            priority=data.get("priority", PRIORITY_MEDIUM),
            pinned=data.get("pinned", False),
            created_at=data.get("created_at", datetime.now().isoformat()),
            completed_at=data.get("completed_at"),
            due_date=data.get("due_date"),
            memo=data.get("memo", ""),
            requester=data.get("requester", ""),
            lot=data.get("lot", ""),
            slot=data.get("slot", ""),
            request_date=data.get("request_date"),
            order=data.get("order"),
        )
