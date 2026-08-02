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


def is_duplicate_task(title: str, existing_tasks: list) -> bool:
    """
    이미 같은 제목의 할 일이 있는지 확인합니다.
    앞뒤 공백은 무시하고, 대소문자도 구분하지 않습니다.
    existing_tasks는 core.models.Task 객체 리스트입니다.
    """
    normalized_title = title.strip().lower()
    return any(task.title.strip().lower() == normalized_title for task in existing_tasks)


def validate_new_task(title: str, existing_tasks: list) -> Optional[str]:
    """
    새 할 일 제목을 검증합니다.
    문제가 있으면 에러 메시지를 반환하고, 문제가 없으면 None을 반환합니다.
    """
    if is_blank(title):
        return "할 일 내용을 입력해주세요."

    if is_duplicate_task(title, existing_tasks):
        return "이미 존재하는 할 일입니다."

    return None
