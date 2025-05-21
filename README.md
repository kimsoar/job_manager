# JobManager

## 실행 방법

ENV=development python main.py run --all
ENV=production python main.py run --all
python main.py run --all (development 기본 선택)

## 명령어

python main.py list (실행 가능한 job의 항목들을 보여줌)
python main.py run --all (실행 가능한 job들을 실행 시켜줌)
python main.py run --only [job이름] (원하는 job만 실행 시켜줌)
python main.py run --only [job1] --only [job2](job1, job2를 실행 시켜줌)
