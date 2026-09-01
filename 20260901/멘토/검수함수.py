# (2) 멘티 제출물이 도착하기 전에, 제출물을 검사할 함수를 먼저 작성합니다.
#     멘티 과제 지시문(정제결과_멘티.csv 명세)은 이미 알고 있으니 멘티 파일
#     없이도 만들 수 있습니다.
#
#       def 검수(경로):          # 항목별 통과/실패를 출력하고 전체 통과 여부를 돌려준다
#
#     검사 항목: 열 이름·순서 / 결측 0 / 완전중복 0 / 키(수집시각·구역) 중복 0 /
#     메모리 > 0 / 구역코드와 구역 1:1.
#     자기 자신의 정제결과_최종.csv 를 넣어 전부 통과하는지 확인하세요.
#     검수함수.py 로 저장합니다. 멘티 파일 검사는 문제 5에서 합니다.
import numpy as np
import pandas as pd


def 검수(경로):
    check_4 = pd.read_csv(경로, encoding="utf-8-sig")

    mentee_columns_4 = [
        "수집시각",
        "구역",
        "구역코드",
        "CPU온도",
        "전력",
        "응답시간",
        "메모리",
        "상태",
    ]
    # 멘티 정제결과의 열 이름과 순서

    mentor_columns_4 = [
        "수집시각",
        "구역",
        "구역코드",
        "센서ID",
        "CPU온도",
        "전력",
        "응답시간",
        "메모리",
        "상태",
    ]
    # 멘토 정제결과의 열 이름과 순서

    all_pass_4 = True
    # 모든 검사를 통과했는지 저장 -> 하나라도 실패하면 False로 변경

    if (
        check_4.columns.tolist() == mentee_columns_4
        or check_4.columns.tolist() == mentor_columns_4
    ):
        print("통과 열 이름·순서")
    else:
        print("실패 열 이름·순서")
        all_pass_4 = False

    missing_4 = check_4.isnull().sum().sum()
    # 전체 결측값 개수

    if missing_4 == 0:
        print("통과 결측 0")
    else:
        print(f"실패 결측 0 ({missing_4}건)")
        all_pass_4 = False
    # 결측값이 하나도 없는지 확인

    duplicate_4 = check_4.duplicated().sum()
    # 모든 열이 완전히 똑같은 행의 개수

    if duplicate_4 == 0:
        print("통과 완전중복 0")
    else:
        print(f"실패 완전중복 0 ({duplicate_4}건)")
        all_pass_4 = False
    # 완전 중복 행이 없는지 확인

    key_duplicate_4 = check_4.duplicated(subset=["수집시각", "구역"]).sum()
    # 수집시각, 구역이 같은 행이 있는지 확인

    if key_duplicate_4 == 0:
        print("통과 키 중복 0")
    else:
        print(f"실패 키 중복 0 ({key_duplicate_4}건)")
        all_pass_4 = False
    # 키 중복이 없는지 확인

    memory_4 = (check_4["메모리"] > 0).all()
    # 모든 메모리 값이 0보다 큰지 확인

    if memory_4:
        print("통과 메모리 > 0")
    else:
        print("실패 메모리 > 0")
        all_pass_4 = False

    code_check_4 = check_4.groupby("구역")["구역코드"].nunique()
    # 한 구역에 구역코드가 몇 종류씩 연결?

    area_check_4 = check_4.groupby("구역코드")["구역"].nunique()
    # 하나의 구역코드에 구역이 몇 종류씩 연결?

    if (code_check_4 == 1).all() and (area_check_4 == 1).all():
        print("통과 구역코드 1:1")
    else:
        print("실패 구역코드 1:1")
        all_pass_4 = False
    # 구역 하나에는 구역코드 하나? 구역코드 하나에는 구역 하나만 연결?

    return all_pass_4
    # 불리언 결과 반환


# result_4 = 검수("정제결과_최종.csv")

# print("전체 통과:", result_4)
