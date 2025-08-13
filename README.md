ㅏ# JobManager

## 실행 방법

ENV=development python main.py run --all
ENV=production python main.py run --all
python main.py run --all (development 기본 선택)

## 명령어

python main.py list (실행 가능한 job의 항목들을 보여줌)
python main.py run --all (실행 가능한 job들을 실행 시켜줌)
python main.py run --only [job이름] (원하는 job만 실행 시켜줌)
python main.py run --only [job1] --only [job2](job1, job2를 실행 import pandas as pd
import numpy as np

# 1. 기본 설정
start_date = '2025-01-01'
num_days = 1000
equipment = ['SPA001', 'QQS002', 'CCA011']
sensors = ['TEMP_01', 'PRES_01', 'VIB_01', 'FLOW_01']
min_count = 1000
max_count = 2500000

# 2. 1000일의 날짜 데이터 생성
dates = pd.to_datetime(pd.date_range(start=start_date, periods=num_days, freq='D'))

# 3. 날짜, 장비, 센서의 모든 조합 생성
# pd.MultiIndex.from_product를 사용하여 모든 경우의 수를 효율적으로 생성
idx = pd.MultiIndex.from_product([dates, equipment, sensors], names=['Date', 'eqp', 'sensor'])
df = pd.DataFrame(index=idx).reset_index()

# 4. 랜덤 count 값 생성
# 생성해야 할 총 행의 개수를 계산
num_rows = len(df)
# np.random.randint를 사용하여 지정된 범위의 랜덤 정수 생성
random_counts = np.random.randint(min_count, max_count + 1, size=num_rows)
df['count'] = random_counts

# 5. 날짜 형식 변경 (YYYY. MM. DD.)
df['Date'] = df['Date'].dt.strftime('%Y. %m. %d.')

# 6. 결과 확인 및 파일 저장
print("--- 데이터 샘플 (상위 10개) ---")
print(df.head(10))
print("\n--- 데이터 정보 ---")
print(df.info())

# CSV 파일로 저장 (필요시 주석 해제)
# df.to_csv('extended_sensor_data.csv', index=False, encoding='utf-8-sig')
# print("\n'extended_sensor_data.csv' 파일이 성공적으로 import glob
import csv
from collections import Counter, defaultdict
from datetime import datetime
import matplotlib.pyplot as plt
import os

LOG_PATH = "./logs/*.log"  # IIS 로그 파일 패턴
OUTPUT_DIR = "./tps_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

tps_counter = Counter()
endpoint_tps = defaultdict(Counter)
status_tps = defaultdict(Counter)

# 모든 로그 파일 순회
for file_path in glob.glob(LOG_PATH):
    print(f"처리중: {file_path}")
    with open(file_path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue

            parts = line.split()
            if len(parts) < 7:
                continue

            date_str, time_str = parts[0], parts[1]
            uri = parts[4]       # cs-uri-stem
            status = parts[6]    # sc-status

            try:
                dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue

            # 초 단위 TPS 집계
            tps_counter[dt] += 1
            endpoint_tps[uri][dt] += 1
            status_tps[status][dt] += 1

# Peak TPS 계산
if tps_counter:
    peak_time, peak_value = max(tps_counter.items(), key=lambda x: x[1])
else:
    peak_time, peak_value = None, 0

# 공통 출력 함수
def print_tps_report(title, counter_dict):
    print(f"\n=== {title} ===")
    for key, counter in sorted(counter_dict.items(), key=lambda x: -sum(x[1].values())):
        total = sum(counter.values())
        avg = total / len(counter) if counter else 0
        peak = max(counter.values()) if counter else 0
        print(f"{key} -> 총 요청: {total}, 평균 TPS: {avg:.2f}, 피크 TPS: {peak}")

# 전체 TPS 계산
total_requests = sum(tps_counter.values())
total_seconds = len(tps_counter)
avg_tps = total_requests / total_seconds if total_seconds > 0 else 0

print("\n=== 전체 TPS (모든 로그 합산, 초 단위) ===")
print(f"총 요청 수: {total_requests}")
print(f"측정 구간: {total_seconds}초")
print(f"평균 TPS: {avg_tps:.2f}")
print(f"피크 TPS: {peak_value} (시간: {peak_time})")

# 엔드포인트별 TPS
print_tps_report("엔드포인트별 TPS", endpoint_tps)

# 상태코드별 TPS
print_tps_report("상태코드별 TPS", status_tps)

# ========================
# CSV 저장
# ========================

# 전체 TPS CSV
overall_csv_path = os.path.join(OUTPUT_DIR, "overall_tps.csv")
with open(overall_csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["시간(초)", "TPS"])
    for t in sorted(tps_counter.keys()):
        writer.writerow([t, tps_counter[t]])
print(f"전체 TPS CSV 저장 완료: {overall_csv_path}")

# Peak TPS CSV
peak_csv_path = os.path.join(OUTPUT_DIR, "peak_tps.csv")
with open(peak_csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["시간", "TPS"])
    writer.writerow([peak_time, peak_value])
print(f"Peak TPS CSV 저장 완료: {peak_csv_path}")

# ========================
# 그래프 시각화
# ========================

# 시간대별 TPS 변화
times = sorted(tps_counter.keys())
tps_values = [tps_counter[t] for t in times]

plt.figure(figsize=(12, 6))
plt.plot(times, tps_values, label="TPS", color="blue")
plt.axvline(peak_time, color="red", linestyle="--", label=f"Peak: {peak_time}")
plt.title("시간대별 TPS 변화")
plt.xlabel("시간")
plt.ylabel("TPS (초당 요청 수)")
plt.grid(True)
plt.legend()

# 상태코드 비율 파이차트
status_totals = {code: sum(c.values()) for code, c in status_tps.items()}
plt.figure(figsize=(6, 6))
plt.pie(status_totals.values(), labels=status_totals.keys(), autopct="%1.1f%%", startangle=90)
plt.title("상태코드 비율")

plt.WITH DailyCounts AS (
  -- 1. 날짜별로 모든 센서 값의 합계를 계산합니다.
  SELECT
    "Date",
    SUM("count") AS total_count
  FROM
    sensor_data -- 테이블 이름은 실제 사용하는 이름으로 변경해주세요.
  WHERE
    "Date" < '2027-09-27' -- '2027-09-27' 이전 날짜만 필터링합니다.
    AND "eqp" IN ('SPA001', 'QQS002', 'CCA011')
    AND "sensor" IN ('TEMP_01', 'PRES_01', 'VIB_01', 'FLOW_01')
  GROUP BY
    "Date"
)
-- 2. 일일 합계가 500,000 이하인 날짜들 중에서 가장 최근 날짜를 선택합니다.
SELECT
  MAX("Date") AS max_date
FROM
  DailyCounts
WHERE
  total_count <= WITH cte AS (
    SELECT
        date,
        name,
        count,
        SUM(count) OVER (PARTITION BY name ORDER BY date) AS cum_sum
    FROM your_table
    WHERE date < '2025-07-05'
)
SELECT date
FROM cte
WHERE cum_sum < 1000
ORDER BY date DESC
LIMIT WITH cte AS (
    SELECT
        date,
        eqpname,
        sensorname,
        count,
        SUM(count) OVER (
            PARTITION BY eqpname, sensorname
            ORDER BY date
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cum_sum
    FROM your_table
    WHERE date < '2025-07-05'
      AND eqpname = 'A01'
      AND sensorname = 'QU1'
)
SELECT date, eqpname, sensorname, cum_sum
FROM cte
WHERE cum_sum < 1000
ORDER BY date DESC
LIMIT WITH daily_sum AS (
    SELECT
        date,
        SUM(count) AS total_count
    FROM your_table
    WHERE date < '2025-07-05'
      AND (
           (eqpname = 'A1'  AND sensorname IN ('QU1', 'QU2'))
        OR (eqpname = 'A02' AND sensorname IN ('QU1', 'QU2'))
      )
    GROUP BY date
),
cum_reverse AS (
    SELECT
        date,
        SUM(total_count) OVER (
            ORDER BY date DESC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cum_sum
    FROM daily_sum
    ORDER BY date DESC
)
SELECT date, cum_sum
FROM cum_reverse
WHERE cum_sum < 1000
ORDER BY date DESC
LIMIT 1;












