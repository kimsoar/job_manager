[역할] 너는 python 개발 전문가야
[배경] 의식의 흐름대로 개발하다 보니 코드 정리가 필요해.
[요청] 아래 내가 작성한 코드를 줄태니 리팩터링 부탁해.

import re
from collections import defaultdict
from typing import Dict, List, Any
import numpy as np

import csv
from io import StringIO

raw_text = """
process_id  step_seq    eqp_id  lot_id  root_lot_id ppid    wafer_id    mcc_name    process_time    start_time
KVI XP40000 EQP#1   RTAM.01 RTAM    61521VP 18  Wafer   27.56   2026. 1. 1. 오후 12:11:10
KVI XP40000 EQP#1   RTAM.01 RTAM    61521VP 19  Wafer   45.468  2026. 1. 1. 오후 12:11:11
KVI XP40000 EQP#1   RTAM.01 RTAM    61521VP 19  TRS231  51.117  2026. 1. 1. 오후 12:11:12
KVI XP40000 EQP#1   RTAM.01 RTAM    61521VP 18  TRS232  19.152  2026. 1. 1. 오후 12:11:13
KVI XP40000 EQP#1   RTAM.01 RTAM    61521VP 18  SCPL1134    72.177  2026. 1. 1. 오후 12:11:14
KVI XP40000 EQP#1   RTAM.01 RTAM    61521VP 18  SCPL1134    38.081  2026. 1. 1. 오후 12:11:15
KVI XP40000 EQP#1   RTAM.01 RTAM    61521VP 19  SCPL1135    35.113  2026. 1. 1. 오후 12:11:16
KVI XP40000 EQP#1   RTAM.01 RTAM    61521VP 19  SCPL2111    2.392   2026. 1. 1. 오후 12:11:17
KVI XP40000 EQP#1   RTAM.01 RTAM    61521VP 19  TES121  60.336  2026. 1. 1. 오후 12:11:18
KVI XP40000 EQP#1   RTAM.01 RTAM    61521VP 18  TES101  35.333  2026. 1. 1. 오후 12:11:19
KVI XP40000 EQP#1   RTAM.01 RTAM    61521VP 18  ABCT1102    88.368  2026. 1. 1. 오후 12:11:20
KVI XP40000 EQP#1   RTAM.01 RTAM    61521VP 18  RSWP1616    31.099  2026. 1. 1. 오후 12:11:21
KVI XP40000 EQP#1   RTAM.01 RTAM    61521VP 18  TRS1000 15.649  2026. 1. 1. 오후 12:11:22
KVI XP40000 EQP#1   RTAM.01 RTAM    61521VP 19  ABCT1102    14.757  2026. 1. 1. 오후 12:11:23
KVI XP40000 EQP#1   RTAM.01 RTAM    61521VP 19  RSWP1616    38.835  2026. 1. 1. 오후 12:11:24
KVI XP40000 EQP#1   RTAM.01 RTAM    61521VP 19  TRS1000 5.96    2026. 1. 1. 오후 12:11:25
KVI XP40000 EQP#1   RTAM.01 RTAM    61521VP 18  Wafer   47.509  2026. 1. 1. 오후 12:11:26
KVI XP40000 EQP#1   RTAM.01 RTAM    61521VP 19  Wafer   95.966  2026. 1. 1. 오후 12:11:27
KVI XP40000 EQP#1   RTAM.01 RTAM    61521VP 18  SCPL1134    79.77   2026. 1. 1. 오후 12:11:28
KVI XP40000 EQP#1   RTAM.01 RTAM    61521VP 19  SCPL1135    9.092   2026. 1. 1. 오후 12:11:29
KVI XP40000 EQP#1   RTAM.01 RTAM    61521VP 18  TRS234  19.421  2026. 1. 1. 오후 12:11:30
KVI XP40000 EQP#1   RTAM.01 RTAM    61521VP 19  TRS233  82.511  2026. 1. 1. 오후 12:11:31
KVI XP49000 EQP#2   RTAM.01 RTAM    CP01    18  TRS232  51.852  2026. 1. 1. 오후 12:11:32
KVI XP49000 EQP#2   RTAM.01 RTAM    CP01    19  TRS232  59.284  2026. 1. 1. 오후 12:11:33
KVI XP49000 EQP#2   RTAM.01 RTAM    CP01    18  SCPL1134    33.672  2026. 1. 1. 오후 12:11:34
KVI XP49000 EQP#2   RTAM.01 RTAM    CP01    19  SCPL1135    62.597  2026. 1. 1. 오후 12:11:35
KVI XP49000 EQP#2   RTAM.01 RTAM    CP01    18  RSWP1616    91.713  2026. 1. 1. 오후 12:11:36
KVI XP49000 EQP#2   RTAM.01 RTAM    CP01    19  RSWP2616    37.954  2026. 1. 1. 오후 12:11:37
KVI XP49000 EQP#2   RTAM.01 RTAM    CP01    19  CPS3333 27.369  2026. 1. 1. 오후 12:11:38
KVI XP49000 EQP#2   RTAM.01 RTAM    CP01    18  CPS2222 78.093  2026. 1. 1. 오후 12:11:39
KVI XP49000 EQP#2   RTAM.01 RTAM    CP01    18  SCPL1134    94.388  2026. 1. 1. 오후 12:11:40
KVI XP49000 EQP#2   RTAM.01 RTAM    CP01    19  SCPL1134    96.113  2026. 1. 1. 오후 12:11:41
KVI XP49000 EQP#2   RTAM.01 RTAM    CP01    18  SCPL1134    18.953  2026. 1. 1. 오후 12:11:42
KVI XP49000 EQP#2   RTAM.01 RTAM    CP01    19  SCPL1135    1.181   2026. 1. 1. 오후 12:11:43
KVI XP49000 EQP#2   RTAM.01 RTAM    CP01    18  CPS1022 15.111  2026. 1. 1. 오후 12:11:44
KVI XP49000 EQP#2   RTAM.01 RTAM    CP01    19  CPS1022 63.818  2026. 1. 1. 오후 12:11:45
KVI XP50000 EQP#3   RTAM.01 RTAM    SVC11CP 18  Wafer   55.739  2026. 1. 1. 오후 12:11:46
KVI XP50000 EQP#3   RTAM.01 RTAM    SVC11CP 19  Wafer   53.413  2026. 1. 1. 오후 12:11:47
KVI XP50000 EQP#3   RTAM.01 RTAM    SVC11CP 18  TRS1010 2.428   2026. 1. 1. 오후 12:11:48
KVI XP50000 EQP#3   RTAM.01 RTAM    SVC11CP 19  TRS2010 74.234  2026. 1. 1. 오후 12:11:49
KVI XP50000 EQP#3   RTAM.01 RTAM    SVC11CP 18  TRS1010 54.853  2026. 1. 1. 오후 12:11:50
KVI XP50000 EQP#3   RTAM.01 RTAM    SVC11CP 19  TRS1010 45.618  2026. 1. 1. 오후 12:11:51
KVI XP50000 EQP#3   RTAM.01 RTAM    SVC11CP 18  SCPL1134    55.901  2026. 1. 1. 오후 12:11:52
KVI XP50000 EQP#3   RTAM.01 RTAM    SVC11CP 19  SCPL1134    59.661  2026. 1. 1. 오후 12:11:53
KVI XP50000 EQP#4   RTAM.01 RTAM    SVC11CP 18  Wafer   46.438  2026. 1. 2. 오후 12:10:39
KVI XP50000 EQP#4   RTAM.01 RTAM    SVC11CP 19  Wafer   70.971  2026. 1. 2. 오후 12:10:40
KVI XP50000 EQP#4   RTAM.01 RTAM    SVC11CP 18  TRS1010 79.348  2026. 1. 2. 오후 12:10:41
KVI XP50000 EQP#4   RTAM.01 RTAM    SVC11CP 19  TRS1010 41.187  2026. 1. 2. 오후 12:10:42
KVI XP50000 EQP#4   RTAM.01 RTAM    SVC11CP 18  TRS2010 47.5    2026. 1. 2. 오후 12:10:43
KVI XP50000 EQP#4   RTAM.01 RTAM    SVC11CP 19  TRS1010 90.606  2026. 1. 2. 오후 12:10:44
KVI XP50000 EQP#4   RTAM.01 RTAM    SVC11CP 18  SCPL1135    39.477  2026. 1. 2. 오후 12:10:45
KVI XP50000 EQP#4   RTAM.01 RTAM    SVC11CP 19  SCPL1134    95.594  2026. 1. 2. 오후 12:10:46
KVI XP50000 EQP#4   RTAM.01 RTAM    SVC11CP 18  TES101  69.141  2026. 1. 2. 오후 12:10:47
KVI XP50000 EQP#4   RTAM.01 RTAM    SVC11CP 18  ABCT1102    88.107  2026. 1. 2. 오후 12:10:49
KVI XP50000 EQP#4   RTAM.01 RTAM    SVC11CP 19  ABCT1102    84.062  2026. 1. 2. 오후 12:10:50
KVI XP40000 EQP#1   MACA1.1 MACA    61521VP 6   Wafer   8.034   2026. 1. 2. 오후 12:10:05
KVI XP40000 EQP#1   MACA1.1 MACA    61521VP 7   Wafer   1.837   2026. 1. 2. 오후 12:10:06
KVI XP40000 EQP#1   MACA1.1 MACA    61521VP 6   TRS232  48.293  2026. 1. 2. 오후 12:10:07
KVI XP40000 EQP#1   MACA1.1 MACA    61521VP 7   TRS233  61.467  2026. 1. 2. 오후 12:10:08
KVI XP40000 EQP#1   MACA1.1 MACA    61521VP 6   SCPL1134    43.994  2026. 1. 2. 오후 12:10:09
KVI XP40000 EQP#1   MACA1.1 MACA    61521VP 7   SCPL1122    80.873  2026. 1. 2. 오후 12:10:10
KVI XP40000 EQP#1   MACA1.1 MACA    61521VP 6   SCPL1134    1.73    2026. 1. 2. 오후 12:10:11
KVI XP40000 EQP#1   MACA1.1 MACA    61521VP 7   SCPL1134    29.394  2026. 1. 2. 오후 12:10:12
KVI XP40000 EQP#1   MACA1.1 MACA    61521VP 6   TES121  96.3    2026. 1. 2. 오후 12:10:13
KVI XP40000 EQP#1   MACA1.1 MACA    61521VP 7   TES101  53.15   2026. 1. 2. 오후 12:10:14
KVI XP40000 EQP#1   MACA1.1 MACA    61521VP 6   Wafer   85.408  2026. 1. 2. 오후 12:10:15
KVI XP40000 EQP#1   MACA1.1 MACA    61521VP 7   Wafer   44.51   2026. 1. 2. 오후 12:10:16
KVI XP40000 EQP#1   MACA1.1 MACA    61521VP 6   SCPL1135    88.003  2026. 1. 2. 오후 12:10:17
KVI XP40000 EQP#1   MACA1.1 MACA    61521VP 7   SCPL1134    9.823   2026. 1. 2. 오후 12:10:18
KVI XP40000 EQP#1   MACA1.1 MACA    61521VP 6   TRS234  64.178  2026. 1. 2. 오후 12:10:19
KVI XP40000 EQP#1   MACA1.1 MACA    61521VP 6   XCP120  29.184  2026. 1. 2. 오후 12:10:20
KVI XP40000 EQP#1   MACA1.1 MACA    61521VP 7   TRS233  73.45   2026. 1. 2. 오후 12:10:21
KVI XP40000 EQP#1   MACA1.1 MACA    61521VP 7   XCP120  33.801  2026. 1. 2. 오후 12:10:22
KVI XP40000 EQP#1   MACA1.1 MACA    61521VP 6   CAS124  25.515  2026. 1. 2. 오후 12:10:23
KVI XP40000 EQP#1   MACA1.1 MACA    61521VP 7   CAS123  31.451  2026. 1. 2. 오후 12:10:24
KVI XP49000 EQP#2   MACA1.1 MACA    CP01    6   TRS232  78.017  2026. 1. 2. 오후 12:10:25
KVI XP49000 EQP#2   MACA1.1 MACA    CP01    6   SCPL1134    23.704  2026. 1. 2. 오후 12:10:26
KVI XP49000 EQP#2   MACA1.1 MACA    CP01    7   TRS232  49.964  2026. 1. 2. 오후 12:10:27
KVI XP49000 EQP#2   MACA1.1 MACA    CP01    7   SCPL1134    47.639  2026. 1. 2. 오후 12:10:28
KVI XP49000 EQP#2   MACA1.1 MACA    CP01    6   RSWP1616    69.165  2026. 1. 2. 오후 12:10:29
KVI XP49000 EQP#2   MACA1.1 MACA    CP01    7   RSWP1616    68.835  2026. 1. 2. 오후 12:10:30
KVI XP49000 EQP#2   MACA1.1 MACA    CP01    6   CPS2222 40.183  2026. 1. 2. 오후 12:10:31
KVI XP49000 EQP#2   MACA1.1 MACA    CP01    7   CPS2222 33.404  2026. 1. 2. 오후 12:10:32
KVI XP49000 EQP#2   MACA1.1 MACA    CP01    6   SCPL1135    79.612  2026. 1. 2. 오후 12:10:33
KVI XP49000 EQP#2   MACA1.1 MACA    CP01    7   SCPL1134    33.493  2026. 1. 2. 오후 12:10:34
KVI XP49000 EQP#2   MACA1.1 MACA    CP01    6   SCPL1134    89.514  2026. 1. 2. 오후 12:10:35
KVI XP49000 EQP#2   MACA1.1 MACA    CP01    7   SCPL1134    89.286  2026. 1. 2. 오후 12:10:36
KVI XP49000 EQP#2   MACA1.1 MACA    CP01    6   CPS1022 18.704  2026. 1. 2. 오후 12:10:37
KVI XP49000 EQP#2   MACA1.1 MACA    CP01    7   CPS1022 34.667  2026. 1. 2. 오후 12:10:38
KVI XP50000 EQP#3   MACA1.1 MACA    SVC11CP 6   Wafer   16.556  2026. 1. 2. 오후 12:10:39
KVI XP50000 EQP#3   MACA1.1 MACA    SVC11CP 7   Wafer   4.997   2026. 1. 2. 오후 12:10:40
KVI XP50000 EQP#3   MACA1.1 MACA    SVC11CP 6   TRS1010 11.996  2026. 1. 2. 오후 12:10:41
KVI XP50000 EQP#3   MACA1.1 MACA    SVC11CP 7   TRS1010 19.524  2026. 1. 2. 오후 12:10:42
KVI XP50000 EQP#3   MACA1.1 MACA    SVC11CP 7   TRS1010 37.769  2026. 1. 2. 오후 12:10:43
KVI XP50000 EQP#3   MACA1.1 MACA    SVC11CP 6   TRS2010 55.21   2026. 1. 2. 오후 12:10:44
KVI XP50000 EQP#3   MACA1.1 MACA    SVC11CP 6   SCPL1135    10.499  2026. 1. 2. 오후 12:10:45
KVI XP50000 EQP#3   MACA1.1 MACA    SVC11CP 6   TES101  85.126  2026. 1. 2. 오후 12:10:46
KVI XP50000 EQP#3   MACA1.1 MACA    SVC11CP 7   SCPL1134    26.521  2026. 1. 2. 오후 12:10:47
KVI XP50000 EQP#3   MACA1.1 MACA    SVC11CP 6   ABCT1102    52.098  2026. 1. 2. 오후 12:10:48
KVI XP50000 EQP#3   MACA1.1 MACA    SVC11CP 7   TES101  3.717   2026. 1. 2. 오후 12:10:49
KVI XP50000 EQP#3   MACA1.1 MACA    SVC11CP 7   ABCT1102    79.798  2026. 1. 2. 오후 12:10:50
KVI XP50000 EQP#5   MACA1.1 MACA    SVC11CP 6   Wafer   9.892   2026. 1. 2. 오후 12:10:51
KVI XP50000 EQP#5   MACA1.1 MACA    SVC11CP 7   Wafer   96.68   2026. 1. 2. 오후 12:10:52
KVI XP50000 EQP#5   MACA1.1 MACA    SVC11CP 6   RSWP1616    82.087  2026. 1. 2. 오후 12:10:53
KVI XP50000 EQP#5   MACA1.1 MACA    SVC11CP 7   RSWP1616    61.663  2026. 1. 2. 오후 12:10:54
KVI XP50000 EQP#5   MACA1.1 MACA    SVC11CP 6   CPS1001 15.035  2026. 1. 2. 오후 12:10:55
KVI XP50000 EQP#5   MACA1.1 MACA    SVC11CP 7   CPS1001 57.612  2026. 1. 2. 오후 12:10:56
KVI XP50000 EQP#5   MACA1.1 MACA    SVC11CP 6   CPS2223 36.547  2026. 1. 2. 오후 12:10:57
KVI XP50000 EQP#5   MACA1.1 MACA    SVC11CP 7   CPS2222 3.186   2026. 1. 2. 오후 12:10:58
KVI XP50000 EQP#5   MACA1.1 MACA    SVC11CP 6   TES101  45.006  2026. 1. 2. 오후 12:10:59
KVI XP50000 EQP#5   MACA1.1 MACA    SVC11CP 7   TES101  56.62   2026. 1. 2. 오후 12:11:00
KVI XP50000 EQP#5   MACA1.1 MACA    SVC11CP 6   SCPL1135    0.724   2026. 1. 2. 오후 12:11:01
KVI XP50000 EQP#5   MACA1.1 MACA    SVC11CP 7   SCPL1134    21.074  2026. 1. 2. 오후 12:11:02
"""

reader = csv.DictReader(
    StringIO(raw_text.strip()),
    delimiter="\t"
)

raw_rows = []

for row in reader:
    raw_rows.append(row)
    
    
def normalize_mcc_name(name: str) -> str:
    """
    그룹핑용 Key 생성
    """

    if name.upper().startswith("WAFER"):
        return "Wafer"

    # 숫자 제거
    key = re.sub(r"\d+", "", name)

    # 중간에 숫자가 제거되면서 남은 '-' 제거
    key = key.replace("--", "-")

    # 끝에 남은 '-' 제거
    key = re.sub(r"-+$", "", key)

    return key

def extract_key(lot_id:str, wafer_id:str) -> str:
    return f"{lot_id}_{wafer_id}"

additional_columns = {}

for row in raw_rows:
    key = extract_key(row['lot_id'], row['wafer_id'])
    if key not in additional_columns:
        additional_columns[key] = key
        
additional_column_list = list(additional_columns)

def get_target_column(df, target_columns, target_idx):
    """
    특정 행에서 NaN이 아닌 컬럼명을 반환
    """
    # target_col = get_target_column(df, additional_column_list, target_idx)
    target_cols = target_columns

    # # 2. 0번 행에서 해당 컬럼들이 NaN이 아닌지 확인 (True/False 시리즈 반환)
    not_null_series = df.loc[target_idx, target_cols].notna()

    # # 3. True인 컬럼명만 리스트로 추출
    valid_columns = not_null_series[not_null_series].index.tolist()

    print(valid_columns)
    return valid_columns[0] if valid_columns else None

import pandas as pd

pd.set_option('display.max_rows', None)

columns_list = ['step', 'eqp', 'ppid', 'normalize_mcc_name', 'start_time' ]  + additional_column_list

df = pd.DataFrame(columns=columns_list)

for row in raw_rows:
    df.loc[len(df)] = {'step': row['step_seq'], 'eqp': row['eqp_id'], 'ppid': row['ppid'], extract_key(row['lot_id'], row['wafer_id']): row['mcc_name'], 'normalize_mcc_name': normalize_mcc_name(row['mcc_name']), 'start_time': row['start_time']}

temp_time = df['start_time'].str.replace('오전', 'AM').str.replace('오후', 'PM')
df['_temp_dt'] = pd.to_datetime(temp_time, format='%Y. %m. %d. %p %I:%M:%S', errors='coerce')

# inplace=True 옵션 사용
df.sort_values(by=['step', 'eqp', '_temp_dt'], inplace=True)
df.reset_index(drop=True, inplace=True)

df.drop(columns=['_temp_dt'], inplace=True)

print(df.head(20))
print("-" *100)

current_index = 0
complete_rows = []

target_idx = 0  # 이동시킬 데이터가 있는 행

for loop_count in range(len(df) - 1):
    target_idx = target_idx + 1
    target_info = df.loc[target_idx, ["step", "eqp", "ppid", "normalize_mcc_name"]]
    
    target_col = get_target_column(df, additional_column_list, target_idx)

    # 2. 위로 올라가면서 기준 정보가 같고, 해당 컬럼이 NaN인 '가장 첫 행' 찾기
    destination_idx = None

    # 현재 행 바로 위부터 0번 행까지 역순으로 탐색
    for i in range(target_idx - 1, -1, -1):
        # 인덱스가 유효한지 확인 (이미 삭제된 인덱스일 수 있으므로 구문 예방)
        if i in df.index:
            current_info = df.loc[i, ["step", "eqp", "ppid", "normalize_mcc_name"]]

            # 기준 정보가 일치하는지 확인
            if current_info.equals(target_info):
                # 조건을 만족하는 행을 발견하면 우선 저장 (위로 갈수록 더 상단 행으로 갱신됨)
                if pd.isna(df.at[i, target_col]):
                    destination_idx = i
            else:
                if pd.isna(df.at[i, target_col]):
                    print(
                        f"기준 정보는 다르지만 상위 행 정보가 NaN이라 계속 진행. (현재 행: {i}, target_idx: {target_idx})"
                    )
                else:
                    # 연속된 동일 그룹 범위를 벗어나면 탐색 종료
                    break

    # 3. 매칭된 목적지(여기서는 4번)가 있으면 값을 이동하고 원래 행(6번) 삭제
    if destination_idx is not None:
        print(
            f"🎯 {target_idx}번의 값을 동일 그룹의 가장 상단인 {destination_idx}번으로 이동합니다."
        )
        df.at[destination_idx, target_col] = df.at[target_idx, target_col]
        df = df.drop(index=target_idx)
    else:
        print(f"❌ {target_idx}번 {target_col}컬럼은 이동할 수 있는 조건의 상위 행이 없습니다.")
        

df.reset_index(drop=True, inplace=True)

print("-" * 100)
print("-" * 50, "데이터 정리 완료", "-" * 50)
print("-" * 50, "차수 설정 진행 준비", "-" * 50)
print("-" * 100)
print(df)

# 차수 만들기
df['degree'] = np.nan

complete_rows = []

target_idx = -1

degree_count = 1  # 차수 카운트 초기화

for loop_count in range(len(df)):
    print(loop_count, "차수 설정 진행 중...")
    
    
    target_idx = target_idx + 1
    target_info = df.loc[target_idx, ["step", "ppid"]]
    
    
    upside_idx = target_idx - 1
    if upside_idx in df.index:
        upside_info = df.loc[upside_idx, ["step", "ppid"]]
    else:
        upside_info = None
    
    
    if upside_info is None:
        # 최상단 row 데이터
        df.at[target_idx, 'degree'] = degree_count
    elif upside_info.equals(target_info): 
        # 바로 위 row 데이터와 같을때
        if df.at[target_idx, 'normalize_mcc_name'] == 'Wafer':
            target_col = get_target_column(df, additional_column_list, target_idx)
            
            destination_idx = upside_idx
            
            # 현재 행 바로 위부터 0번 행까지 역순으로 탐색
            for i in range(target_idx - 1, -1, -1):
                # 인덱스가 유효한지 확인 (이미 삭제된 인덱스일 수 있으므로 구문 예방)
                if i in df.index:
                    current_info = df.loc[i, ["step", "ppid"]]

                    # 기준 정보가 일치하는지 확인
                    if current_info.equals(target_info):
                        # 조건을 만족하는 행을 발견하면 우선 저장 (위로 갈수록 더 상단 행으로 갱신됨)
                        if not pd.isna(df.at[i, target_col]):
                            destination_idx = i
                    else:
                        break
            
            df.at[target_idx, 'degree'] = int(df.at[destination_idx, 'degree']) + 1
        else:
            df.at[target_idx, 'degree'] = df.at[upside_idx, 'degree']
    else:
        # 바로 위 row 데이터와 다를때
        degree_count = 1
        df.at[target_idx, 'degree'] = degree_count

    
print(df)