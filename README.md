# JobManager

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
# print("\n'extended_sensor_data.csv' 파일이 성공적으로 저장되었습니다.")




