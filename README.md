💾 Heap 관련 설정

-Xms12g
* 초기 힙(Heap) 크기를 12GB로 설정합니다.
* 애플리케이션이 시작될 때 이 크기만큼 힙을 미리 확보하여 메모리 확장에 따른 GC 부하를 줄입니다.

-Xmx20g
* 최대 힙 크기를 20GB로 제한합니다.
* 이 값을 초과하면 OutOfMemoryError: Java heap space 발생.
* GC가 이 범위 내에서만 동작하므로, 과도한 메모리 사용을 방지합니다.
* (현재 RAM 64GB 기준으로 3개 서비스라면 20GB씩은 적절한 상한선입니다.)

🧠 Metaspace

-XX:MaxMetaspaceSize=1024m
* 클래스 메타데이터를 저장하는 Metaspace 최대 크기를 1GB로 설정.
* 클래스 로딩이 많지 않은 일반 Spring Boot 서비스라면 256~512MB도 충분하지만, JPA Entity나 많은 Bean을 사용하는 경우 1GB로 여유 있게 설정하는 게 안정적입니다.

⚙️ GC (Garbage Collection) 설정

-XX:+UseG1GC
* G1(Garbage First) GC를 사용.
* 대규모 힙(>4GB) 환경에서 짧은 stop-the-world 시간을 보장합니다.

-XX:MaxGCPauseMillis=200
* GC 일시 정지 시간을 200ms 이하로 목표로 조정.
* 완전한 보장은 아니지만, G1이 이 목표를 기준으로 내부 튜닝을 수행합니다.

-XX:InitiatingHeapOccupancyPercent=45
* 힙이 45% 찼을 때 Concurrent GC(동시 수집) 시작.
* GC를 미리 수행하여 Full GC를 방지하고 응답 지연을 줄입니다.

-XX:+UseStringDeduplication
* 같은 문자열 리터럴을 중복 제거하여 메모리 절약.
* 특히 JSON 직렬화나 반복된 문자열이 많은 경우 효과적입니다.

-XX:+HeapDumpOnOutOfMemoryError
* OutOfMemoryError 발생 시 힙덤프(.hprof)를 생성.
* 이후 문제 분석에 사용합니다.

🧵 Spring 비동기 / 쓰레드풀 설정

-Dspring.task.execution.pool.max-size=10
* 비동기 @Async나 TaskExecutor 사용 시 최대 쓰레드 수를 10개로 제한.
* CPU 코어 수에 맞춰 조정 (예: 8코어 → 8~12개 권장).

-Dspring.task.execution.pool.queue-capacity=50
* 대기열 크기 설정 (대기 중인 비동기 작업 수).
* 큐가 가득 차면 RejectedExecutionException 발생 → 백프레셔 역할 수행.

📦 파일 업로드 제한

-Dspring.servlet.multipart.max-file-size=1GB
-Dspring.servlet.multipart.max-request-size=1GB
* 업로드 파일과 요청 전체 크기 모두 1GB 이하로 제한.
* 대용량 업로드 시 메모리 폭주를 방지.

🌐 Tomcat (내장 서버) 설정

-Dserver.tomcat.max-threads=200
* 요청을 처리하는 최대 워커 쓰레드 수.
* 요청이 200개를 초과하면 큐에 대기하게 됩니다.

-Dserver.tomcat.accept-count=100
* 연결 대기열(큐) 크기.
* 200개 쓰레드가 모두 사용 중일 때 추가로 100개의 요청을 대기시킵니다.
* 그 이상이면 503(Service Unavailable) 발생.

-Dserver.tomcat.connection-timeout=20000
* 클라이언트가 요청을 보낸 후 응답이 없을 때 연결을 끊는 시간(ms).
* 20초로 설정되어 있으므로, 너무 오래 걸리는 요청은 끊어줍니다.

✅ 정리
구분	주요 옵션	역할
JVM 메모리	-Xms, -Xmx	힙 크기 조정, 안정적인 GC 동작
GC	UseG1GC, MaxGCPauseMillis 등	짧은 지연시간 유지
Metaspace	MaxMetaspaceSize	클래스 메타데이터 메모리 제한
비동기	spring.task.execution.*	백프레셔, 비동기 처리 조절
업로드	multipart.*	대용량 요청 방어
Tomcat	max-threads, accept-count	동시 요청 및 큐 조절





🟩 start.bat (안정화 버전)

@echo off
REM ===========================================================
REM Spring Boot 2.x - 64GB 환경 / 2개 인스턴스 실행 (안정화 버전)
REM 위치: D:\test
REM 각 인스턴스당: 힙 20GB, Metaspace 1GB
REM 스레드 풀 + 백프레셔 설정 포함
REM ===========================================================

REM 1️⃣ 콘솔 UTF-8 설정
chcp 65001 > nul

REM 2️⃣ 작업 폴더 이동
cd /d D:\test

REM 3️⃣ 로그 폴더 확인 / 없으면 생성
if not exist logs mkdir logs

REM 4️⃣ 공통 JVM 옵션
set JAVA_OPTS=-Xms12g -Xmx20g ^
 -XX:MaxMetaspaceSize=1024m ^
 -XX:+UseG1GC ^
 -XX:MaxGCPauseMillis=200 ^
 -XX:InitiatingHeapOccupancyPercent=45 ^
 -XX:+UseStringDeduplication ^
 -XX:+HeapDumpOnOutOfMemoryError ^
 -Dspring.task.execution.pool.max-size=10 ^
 -Dspring.task.execution.pool.queue-capacity=50 ^
 -Dspring.servlet.multipart.max-file-size=1GB ^
 -Dspring.servlet.multipart.max-request-size=1GB ^
 -Dserver.tomcat.max-threads=200 ^
 -Dserver.tomcat.accept-count=100 ^
 -Dserver.tomcat.connection-timeout=20000

REM ===========================================================
REM APP1 실행 (포트 8080)
REM ===========================================================
echo Starting app1 on port 8080...
start "app1" cmd /c java %JAVA_OPTS% ^
 -verbose:gc ^
 -Xlog:gc*:logs\app1_gc.log:time,uptime,level,tags ^
 -XX:HeapDumpPath=logs\app1_heapdump.hprof ^
 -jar app.jar --server.port=8080 --spring.profiles.active=server1 ^
 > logs\app1.log 2>&1

REM ===========================================================
REM APP2 실행 (포트 8081)
REM ===========================================================
echo Starting app2 on port 8081...
start "app2" cmd /c java %JAVA_OPTS% ^
 -verbose:gc ^
 -Xlog:gc*:logs\app2_gc.log:time,uptime,level,tags ^
 -XX:HeapDumpPath=logs\app2_heapdump.hprof ^
 -jar app.jar --server.port=8081 --spring.profiles.active=server2 ^
 > logs\app2.log 2>&1

echo ===========================================================
echo Both instances (app1 & app2) are starting in D:\test...
echo ThreadPool + Backpressure configuration applied.
echo Check logs in the "logs" folder for details.
echo ===========================================================
pause

🟥 stop.bat (변경 없음)

@echo off
REM ===========================================================
REM Stop Spring Boot 2.x instances (app1 & app2)
REM ===========================================================
echo Stopping app1 and app2...

taskkill /FI "WINDOWTITLE eq app1" /T /F
taskkill /FI "WINDOWTITLE eq app2" /T /F

echo ===========================================================
echo Both instances stopped.
echo ===========================================================
pause

