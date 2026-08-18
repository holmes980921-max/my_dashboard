"""
utils/validators.py

사용자 입력값이 올바른지 검사하는 함수들을 모아둔 파일입니다.
task_manager(데이터 처리)와 역할을 분리해서,
검증 규칙이 바뀌어도 이 파일만 수정하면 되도록 합니다.
"""

from typing import Optional


def is_blank(title: str) -> bool:
    """빈 문자열이거나 공백만 입력했는지 확인합니다."""
    return title is None or title.strip() == ""


def validate_new_task(title: str) -> Optional[str]:
    """
    새 할 일 제목을 검증합니다.
    문제가 있으면 에러 메시지를 반환하고, 문제가 없으면 None을 반환합니다.

    v1.0: 중복 제목 검사는 제거했습니다. 이메일 제목을 그대로 복사해서
    쓰는 경우 등, 같은 제목이라도 LOT/SLOT이 다른 별개의 업무일 수 있기
    때문입니다.
    """
    if is_blank(title):
        return "할 일 내용을 입력해주세요."

    return None
