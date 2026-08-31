# ============================================================
# [멘티 과제] 설비 점검 데이터 정제 · 전처리
# ============================================================

import numpy as np
import pandas as pd

df = pd.read_csv("설비배치1.csv", encoding="utf-8-sig")
센서 = ["온도", "진동", "회전수", "압력"]

# ----------------------------------------
# 문제 1. 받은 파일을 열고 상태를 파악한다
# ----------------------------------------

print(df.shape)
miss = df.isnull().sum() # 결측 수 세기
print(miss[miss>0].to_dict())
print(type(df['진동'].iloc[0]).__name__) # 진동 열 첫번째 값 타입
print(df["판정"].value_counts().to_dict()) # 판정 결과 별 수세기

# ----------------------------------------
# 문제 2. 숫자로 저장되지 않은 열 고치기
# ----------------------------------------

df["진동"] = pd.to_numeric(df["진동"], errors="coerce")
# to_numeric : 숫자로 변환 / errors='coerce' -> 숫자 변경시 에러나면 결측값 처리해라
print(df["진동"].isnull().sum())
print(round(df['진동'].mean(),2))

# ----------------------------------------
# 문제 3. 중복 행 제거
# ----------------------------------------

print(df.duplicated().sum()) # 중복행 개수세기
df = df.drop_duplicates().reset_index(drop =True) # 중복행 제거 / 인덱스 0부터 하기
print(df.shape) # 제거 후 모양
# index reset하기 - 기존 index 제거 O -> True
#                - 기존 index 제거 X -> False

# ----------------------------------------
# 문제 4. 결측 채우기
# ----------------------------------------
t_avg = df['온도'].mean() # 온도 열 평균
p_mid = df['압력'].median() # 압력 열 중앙값
v_avg = df['진동'].mean() # 진동 열 평균

df['온도']= df["온도"].fillna(t_avg)
df['압력']=df['압력'].fillna(p_mid)
df['진동']= df["진동"].fillna(v_avg)

print(df[센서].isnull().sum().sum()) # sum() 한번하면 센서 별 결측 개수 나옴 -> 한번 더 해서 총합 구하기
print(round(t_avg,2),round(p_mid,2))

# ----------------------------------------
# 문제 5. 생산라인별 요약
# ----------------------------------------

# groupby : 데이터를 그룹화하여 연산을 수행
# df.groupby('기준열')['계산할열'].mean() 

print(round(df.groupby('생산라인')[센서].mean(),2))

counts = df['생산라인'].value_counts()
# valye_counts() : 값이 몇번 등장하는지 카운트함
print(counts.sort_index().to_dict())
# sort_index() : 인덱스를 기준으로 정렬 -> 이름 순 'a' ..

# ----------------------------------------
# 문제 6. z-점수로 온도 이상 찾기
# ----------------------------------------

# ddof=0 
# 전체 데이터를 사용한다는 뜻임
pyo = df['온도'].std(ddof=0) # 온도 표준편차
print(round(t_avg,2), round(pyo,2))

z = (df['온도']-t_avg)/pyo
print((z.abs()>3).sum(),(z.abs()>2).sum())

# ----------------------------------------
# 문제 7. IQR로 압력 이상 찾기
# ----------------------------------------


# quantile() : 분위수에 맞는 값 구하는 함수
q1 = df['압력'].quantile(0.25)
q3 = df['압력'].quantile(0.75)
iqr = q3-q1

down = q1 - 1.5*iqr # 아래 울타리
up = q3 + 1.5* iqr # 위 울타리

print(round(down,2), round(up,2))
strange = ((df["압력"]<down)|(df['압력']>up))
print(strange.sum())
print(df.loc[strange]['생산라인'].value_counts().to_dict())
# 이상한 값이 어느 생산라인에서 몇개가 나왔는지 찾고 딕셔너리로

# ----------------------------------------
# 문제 8. 이상으로 판정된 행 제거
# ----------------------------------------

st_hang= (df.loc[strange]) # 이상 판정 행
print(df['생산라인'].value_counts().sort_index().to_dict())

# print(strange) -> bool

df = df[~strange]  # 이상값이 True -> True가 아닌 것만 다시 저장
print(df['생산라인'].value_counts().sort_index().reset_index(drop =True).to_dict())
print(df.shape)

# ----------------------------------------
# 문제 9. 0~1로 스케일 맞추고 파일로 남기기
# ----------------------------------------

sen_min = df[센서].min()
sen_max = df[센서].max()

minmax = (df[센서]-sen_min)/(sen_max-sen_min) # 열별로 정규화 됨
print(minmax.min().to_dict()) # 정규화 된 열의 최소값 
print(minmax.max().to_dict())
print(round(minmax.mean(),3).to_dict())

new_df = df[['검사일시','생산라인']].copy()
new_df[센서]=round(minmax,4)

new_df.to_csv("정규화_멘티.csv", index=False, encoding="utf-8-sig")

new_df = pd.read_csv("정규화_멘티.csv",encoding='utf-8-sig')

print(new_df.shape)

# ----------------------------------------
# 문제 10. 라인 인코딩하고 저장하기
# ----------------------------------------

df["라인코드"] = df["생산라인"].map({"A라인":0,"B라인":1,"C라인":2})
# map : 대응시켜라 a라인이면 0 , b라인이면 1
final = df[["검사일시",'생산라인','라인코드','온도','진동','회전수','압력','판정']]
final.to_csv('정제결과_멘티.csv',index=False,encoding='utf-8-sig')
final = pd.read_csv("정제결과_멘티.csv",encoding='utf-8-sig')
print(final.shape, final.isnull().sum().sum(),final.duplicated().sum())
print(final.columns.tolist())
# columns 만 사용시 Index(['검사일시'..] dtype='str') 으로나옴
# tolist() 사용해 리스트만 