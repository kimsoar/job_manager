<igDP:XamDataGrid
    DataSource="{Binding Items}"
    AutoGenerateFields="False">

    <igDP:XamDataGrid.FieldLayouts>
        <igDP:FieldLayout>

            <igDP:FieldLayout.Fields>
                <igDP:Field Name="Name" Label="이름" />
                <igDP:Field Name="Age" Label="나이" />

                <!-- 버튼 필드 -->
                <igDP:TemplateField Name="Action" Label="작업">
                    <igDP:TemplateField.CellValuePresenterStyle>
                        <Style TargetType="igDP:CellValuePresenter">
                            <Setter Property="Template">
                                <Setter.Value>
                                    <ControlTemplate TargetType="igDP:CellValuePresenter">
                                        <Button Content="삭제"
                                                Command="{Binding DataContext.DeleteCommand, 
                                                                  RelativeSource={RelativeSource AncestorType=igDP:XamDataGrid}}"
                                                CommandParameter="{Binding Data}"
                                                Padding="5,2"
                                                Margin="5,0" />
                                    </ControlTemplate>
                                </Setter.Value>
                            </Setter>
                        </Style>
                    </igDP:TemplateField.CellValuePresenterStyle>
                </igDP:TemplateField>

            </igDP:FieldLayout.Fields>
        </igDP:FieldLayout>
    </igDP:XamDataGrid.FieldLayouts>
</igDP:XamDataGrid>



<igDP:XamDataGrid
    x:Name="DataGrid"
    DataSource="{Binding Items}"
    AutoGenerateFields="False">

    <igDP:XamDataGrid.FieldLayouts>
        <igDP:FieldLayout>
            <igDP:FieldLayout.Fields>

                <!-- 일반 텍스트 필드 -->
                <igDP:Field Name="Name" Label="이름" />

                <igDP:Field Name="Age" Label="나이" />

                <!-- 버튼이 들어가는 필드 -->
                <igDP:TemplateField Name="Action" Label="작업">
                    <igDP:TemplateField.CellValuePresenterStyle>
                        <Style TargetType="igDP:CellValuePresenter">
                            <Setter Property="Template">
                                <Setter.Value>
                                    <DataTemplate>
                                        <Button Content="삭제"
                                                Command="{Binding DataContext.DeleteCommand, RelativeSource={RelativeSource AncestorType=igDP:XamDataGrid}}"
                                                CommandParameter="{Binding Data}"
                                                Padding="5,2"
                                                Margin="5,0"
                                                />
                                    </DataTemplate>
                                </Setter.Value>
                            </Setter>
                        </Style>
                    </igDP:TemplateField.CellValuePresenterStyle>
                </igDP:TemplateField>

            </igDP:FieldLayout.Fields>
        </igDP:FieldLayout>
    </igDP:XamDataGrid.FieldLayouts>
</igDP:XamDataGrid>

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

 -Dserver.tomcat.connection-timeout=20000 ^
 -Dspring.servlet.multipart.max-file-size=1GB ^
 -Dspring.servlet.multipart.max-request-size=1GB


REM  -Dserver.tomcat.max-threads=200 ^ 에서 10으로 조정
REM   -Dserver.tomcat.connection-timeout=20000 에서 500000으로 조정


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


————————————————————————
발생 원인



🧠 GC loop(Stop-the-world) 발생 메커니즘
JVM은 heap이 꽉 차면 Full GC를 실행합니다. 그런데 Full GC로도 메모리가 해제되지 않으면, 다시 GC → 메모리 부족 → GC… 무한 반복이 일어나죠. 이게 GC loop (GC thrashing) 상태입니다. CPU는 대부분 GC에 쓰이고, 애플리케이션 로직은 멈춘 듯 보입니다.



🚨 JVM 설정을 안 했을 때의 위험
* JVM은 OS의 여유 메모리를 “가능한 한 다 쓰려는 경향”이 있습니다.
* 캐싱이 켜진 상태에서는 GC가 주기적으로 full cycle 수행 → CPU 100% loop 발생
* Heap이 동적으로 확장되면서 GC 스레드와 애플리케이션 스레드가 경쟁 → 응답 멈춤 현상
따라서 캐싱만 끄면 불완전하고, JVM 힙 크기를 명시적으로 제한해야 안전하게 동작합니다.



➡ JVM Heap이 4GB보다 작다면 (예: -Xmx2G)
* Eden 영역이 금세 꽉 찼다가 Young GC 발생
* Survivor로 복사 불가 → Old 영역으로 Promotion
* Old 영역도 곧 포화 → Full GC 발생
* Full GC 후에도 여전히 데이터가 존재 → GC loop (즉, GC가 계속 돌며 처리 멈춤)
즉, 캐시가 없더라도 **“대용량 데이터를 한 번에 들고 있는 구조”**라면 GC loop가 발생합니다.




——————

원하시면 제가 Heap 20GB 기준 동시 요청별 메모리 시뮬레이션을 계산해서 몇 건까지 안전하게 처리 가능한지도 보여드릴 수 있어요.
그걸 해드릴까요?


좋아요. 지금 조건을 정리하고, Heap 20GB 기준 단일 요청 4GB 처리 시 동시 요청별 메모리 상황을 계산해보겠습니다.

1️⃣ 가정
* 서버 RAM: 64GB (다른 서비스 + OS 24GB 가정 → 사용 가능 RAM 40GB)
* JVM Heap: -Xms12g -Xmx20g
* 단일 요청 데이터: 4GB (객체 + JSON 직렬화 버퍼 포함)
* G1GC: Concurrent GC 진행
* 안전 마진: Heap 최대 20GB 사용 중 약 20~25%는 GC overhead + JVM internal 사용
즉, 실질적으로 단일 요청이 4~5GB Heap을 사용한다고 가정

2️⃣ 요청별 Heap 점유 예상
동시 요청 수	요청당 메모리	총 Heap 점유	주석
1	4~5GB	4~5GB	Heap 20GB 여유 충분, 안전
2	4~5GB	8~10GB	Heap 20GB 여유 충분, GC 부담 있음
3	4~5GB	12~15GB	Heap 20GB 중 ~75% 점유 → Full GC 발생 가능
4	4~5GB	16~20GB	Heap 거의 최대 → Full GC 반복 가능, 성능 급격히 저하
5	4~5GB	20~25GB	Heap 초과 → OOM 발생 가능
결론: 동시 2건 정도까지 안전, 3건 이상 위험

3️⃣ Full GC 발생 시점
* G1GC: InitiatingHeapOccupancyPercent=40%
* Heap 20GB → 40% = 8GB 사용 시 Concurrent GC 시작
* 동시 2건 → 총 8~10GB 사용 → GC 시작 → 처리 가능
* 동시 3건 → 총 12~15GB → GC가 계속 수행되면서 Full GC 발생 → 응답 지연

4️⃣ 안전 전략
1. Tomcat maxThreads 제한 → 동시 요청 2~3건 유지

-Dserver.tomcat.max-threads=3
-Dserver.tomcat.accept-count=10
1. Task Executor 제한 → @Async, Scheduler 동시 실행 제한

-Dspring.task.execution.pool.max-size=2
-Dspring.task.execution.pool.queue-capacity=5
1. Heap 점유 모니터링
* GC 로그를 통해 요청 처리 중 OldGen 점유율 확인
* 필요 시 InitiatingHeapOccupancyPercent 낮춰서 GC 조기 시작

5️⃣ 요약
항목	권장
JVM Heap	-Xms12g -Xmx20g
단일 요청	4GB
동시 요청	2건 안전, 3건 이상 GC 위험
Tomcat maxThreads	2~3
Task Executor	2
GC 튜닝	G1GC, InitiatingHeapOccupancyPercent=40~45, MaxGCPauseMillis=250



using System;
using System.Collections.Generic;

public class DateTimeSplitter
{
    public static List<(DateTime Start, DateTime End)> SplitByDays(DateTime start, DateTime end, int intervalDays)
    {
        var result = new List<(DateTime Start, DateTime End)>();

        var currentStart = start;

        while (currentStart <= end)
        {
            // 구간 종료일 = 시작일 + (intervalDays - 1)
            var currentEnd = currentStart.AddDays(intervalDays - 1);

            // 종료일이 전체 end보다 크면 end로 조정
            if (currentEnd > end)
                currentEnd = end;

            result.Add((currentStart, currentEnd));

            // 다음 구간 시작일
            currentStart = currentEnd.AddDays(1);
        }

        return result;
    }
}
핵심: Heap 제한 때문에 동시 요청 수 제어가 필수입니다. IIS Load Balancer가 여러 Jar에 요청 분산 → 전체 동시 요청 관리 가능


