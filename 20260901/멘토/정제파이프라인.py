# ----------------------------------------
# 문제 4. 손으로 두 번 하면 두 번 다르다 - 자동화
# ----------------------------------------
# (1) 문제 1~2에서 한 일(키 중복 제거 -> 구역별 이상 탐지 -> 이상값 제외 통계로
#     결측 채우기 -> 반복 탐지·치환)을 함수 하나로 묶으세요.
#
#       def 정제(df):            # 원본 표를 받아 정제된 표를 돌려준다
#
#     로그배치1.csv 를 넣어 나온 결과가 정제결과_최종.csv 와 같은지 True/False,
#     두 번 실행해도 같은지 True/False 를 출력하세요. 정제파이프라인.py 로 저장합니다.

import numpy as np
import pandas as pd


지표 = ["CPU온도", "전력", "응답시간", "메모리"]
키열 = ["수집시각", "구역", "센서ID"]


def 정제(df):
    cleaned_4 = df.copy()  # 원본 변경되면 안 됨

    cleaned_4["전력"] = pd.to_numeric(cleaned_4["전력"], errors="coerce")
    # to_numuric()으로 문자열 있으면 에러 내지 말고 NaN 처리하는 과정 역시 동일

    cleaned_4 = cleaned_4.drop_duplicates().copy()
    # 완전 중복 열 제거

    cleaned_4 = cleaned_4.drop_duplicates(subset=키열, keep="first").reset_index(
        drop=True
    )
    # 수집시각,구역,센서ID(키열)가 같은 행은 같은 기록으로 판단해서 첫 번째 행만 남기고 나머지는 제거

    mean_cpu_4 = cleaned_4.groupby("구역")["CPU온도"].transform("mean")
    # 각 행이 속한 구역의 CPU온도 평균

    std_cpu_4 = cleaned_4.groupby("구역")["CPU온도"].transform(lambda x: x.std(ddof=0))
    # 각 행이 속한 구역의 CPU온도 표준편차
    # 문제 조건이 ddof=0

    z_cpu_4 = (cleaned_4["CPU온도"] - mean_cpu_4) / std_cpu_4
    # 구역별 CPU온도 z-score 계산

    out_cpu_4 = z_cpu_4.abs() > 2.5  # 임계값 2.5

    normal_cpu_4 = cleaned_4[~out_cpu_4]  # CPU온도 이상값이 아닌 행만 가져옴

    mean_normal_4 = normal_cpu_4.groupby("구역")["CPU온도"].mean()
    # 이상값을 제외 구역별 CPU온도 평균

    cleaned_4["CPU온도"] = cleaned_4.groupby("구역")["CPU온도"].transform(
        lambda x: x.fillna(mean_normal_4[x.name])
    )
    # CPU온도 결측값 이상값 제외 평균으로 채움

    cleaned_4["메모리"] = cleaned_4.groupby("구역")["메모리"].transform(
        lambda x: x.fillna(x.median())
    )
    # 메모리 결측값은 해당 구역의 중앙값

    cleaned_4["전력"] = cleaned_4.groupby("구역")["전력"].transform(
        lambda x: x.fillna(x.median())
    )
    # 전력 결측값도 해당 구역의 중앙값

    while True:
        mean_memory_4 = cleaned_4.groupby("구역")["메모리"].transform("mean")
        # 현재 상태에서 구역별 메모리 평균

        std_memory_4 = cleaned_4.groupby("구역")["메모리"].transform(
            lambda x: x.std(ddof=0)
        )
        # 현재 상태에서 구역별 메모리 표준편차

        z_memory_4 = (cleaned_4["메모리"] - mean_memory_4) / std_memory_4
        # 구역 기준 메모리 z-score

        out_memory_4 = z_memory_4.abs() > 3
        # 메모리 z-score 절댓값이 3보다 큰 행을 이상값으로 판단

        if out_memory_4.sum() == 0:
            break
        # 더 이상 이상값이 없으면 반복 종료

        median_memory_4 = cleaned_4.groupby("구역")["메모리"].transform("median")
        # 각 행이 속한 구역의 메모리 중앙값

        cleaned_4.loc[out_memory_4, "메모리"] = median_memory_4[out_memory_4]
        # 이번 반복에서 발견된 이상값을 해당 구역의 중앙값으로
        # 교체 후 while문 처음으로 돌아가 다시 이상값을 찾음

    code_4 = {"Z1-알파": 0, "Z2-브라보": 1, "Z3-찰리": 2}
    # 기존 배치1에서 사용한 구역코드

    cleaned_4.insert(2, "구역코드", cleaned_4["구역"].map(code_4))
    # 세 번째 열에 구역코드 추가

    return cleaned_4


원본_4 = pd.read_csv("로그배치1.csv", encoding="utf-8-sig")

result_4 = 정제(원본_4)

final_4 = pd.read_csv("정제결과_최종.csv", encoding="utf-8-sig")

print(result_4.round(10).equals(final_4.round(10)))
# round안 하니까 미세한 차이 때문에 자꾸 false로 리턴 되어서 추가함
# True

result_again_4 = 정제(원본_4)

print(result_4.equals(result_again_4))
# 첫 번째 실행 결과와 두 번째 실행 결과가 같은지 확인 항상 같은 결과가 나와야 함
# True
