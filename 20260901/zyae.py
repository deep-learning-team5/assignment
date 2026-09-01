import numpy as np
import pandas as pd

df = pd.read_csv("로그배치1.csv", encoding="utf-8-sig")
# 파일을 읽어서 df 로 저장
지표 = ["CPU온도", "전력", "응답시간", "메모리"]

# ----------------------------------------
# 문제 1. 받은 파일을 열고 상태를 파악한다
# ----------------------------------------

print(df.shape)
miss = df.isnull().sum()
print(miss[miss > 0].to_dict())
print(type(df["전력"].iloc[0]).__name__)
print(df["상태"].value_counts().to_dict())

# ----------------------------------------
# 문제 2. 숫자로 저장되지 않은 열 고치기
# ----------------------------------------

df["전력"] = pd.to_numeric(df["전력"], errors="coerce")
# to_numeric 함수를 사용하여 '전력' 열을 숫자로 변환, 변환 불가 시 NaN으로 처리
print(df["전력"].isnull().sum())
print(round(df["전력"].mean(), 2))

# ----------------------------------------
# 문제 3. 중복 행 제거
# ----------------------------------------

print(df.duplicated().sum())  # 중복행 개수 세기
df = df.drop_duplicates().reset_index(drop=True)  # 중복 행 제거
print(df.shape)

# ----------------------------------------
# 문제 4. 결측 채우기
# ----------------------------------------

cpu_avg = df["CPU온도"].mean()  # cpu 평균
memory_med = df["메모리"].median()  # 메모리 중앙값
power_avg = df["전력"].mean()  # 전력 평균

df["CPU온도"] = df["CPU온도"].fillna(cpu_avg)
df["메모리"] = df["메모리"].fillna(memory_med)
df["전력"] = df["전력"].fillna(power_avg)

print(df[지표].isnull().sum().sum())

print(round(cpu_avg, 2), round(memory_med, 2))


# ----------------------------------------
# 문제 5. 구역별 요약
# ----------------------------------------
area_avg = df.groupby("구역")[지표].mean().round(2)
print(area_avg)
counts = df["구역"].value_counts()
print(counts.sort_index().to_dict())

# ----------------------------------------
# 문제 6. z-점수로 CPU온도 이상 찾기
# ----------------------------------------

print(round(cpu_avg, 2), round(df["CPU온도"].std(ddof=0), 2))
z = (df["CPU온도"] - cpu_avg) / df["CPU온도"].std(ddof=0)

print((z.abs() > 3).sum(), (z.abs() > 2).sum())

# ----------------------------------------
# 문제 7. IQR로 메모리 이상 찾기
# ----------------------------------------

Q1 = df["메모리"].quantile(0.25)
Q3 = df["메모리"].quantile(0.75)
IQR = Q3 - Q1

down = Q1 - 1.5 * IQR
up = Q3 + 1.5 * IQR

print(round(down, 2), round(up, 2))

count = (df["메모리"] < down) | (df["메모리"] > up)

print(count.sum())
print(df.loc[count]["구역"].value_counts().to_dict())

# ----------------------------------------
# 문제 8. 이상으로 판정된 행 제거
# ----------------------------------------
print(df["구역"].value_counts().sort_index().to_dict())


df = df[~count].reset_index(drop=True)
print(df["구역"].value_counts().sort_index().to_dict())


# ----------------------------------------
# 문제 9. 0~1로 스케일 맞추고 파일로 남기기
# ----------------------------------------

small = df[지표].min()
big = df[지표].max()

minmax = (df[지표] - small) / (big - small)

print(minmax.min().round(3).to_dict())
print(minmax.max().round(3).to_dict())
print(minmax.mean().round(3).to_dict())

new = df[["수집시각", "구역"]].copy()
new[지표] = minmax

new.to_csv("정규화_멘티.csv", index=False, encoding="utf-8-sig")

new = pd.read_csv("정규화_멘티.csv", encoding="utf-8-sig")

print(new.shape)

# ----------------------------------------
# 문제 10. 구역 인코딩하고 저장하기
# ----------------------------------------

df["구역코드"] = df["구역"].map({"Z1-알파": 0, "Z2-브라보": 1, "Z3-찰리": 2})

final = df[
    ["수집시각", "구역", "구역코드", "CPU온도", "전력", "응답시간", "메모리", "상태"]
]
final.to_csv("정제결과_멘트.csv", index=False, encoding="utf-8-sig")

final = pd.read_csv("정제결과_멘트.csv", encoding="utf-8-sig")
print(final.shape)
print(final.isnull().sum().sum(), final.duplicated().sum())
print(final.columns.to_list())
