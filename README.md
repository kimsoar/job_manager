web.config
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <rewrite>
      <rules>
        <rule name="VueRouter" stopProcessing="true">
          <match url=".*" />
          <conditions logicalGrouping="MatchAll">
            <add input="{REQUEST_FILENAME}" matchType="IsFile" negate="true" />
            <add input="{REQUEST_FILENAME}" matchType="IsDirectory" negate="true" />
          </conditions>
          <action type="Rewrite" url="/" />
        </rule>
      </rules>
    </rewrite>
  </system.webServer>
</configuration>



<!-- C:\deploy\myapp\frontend\dist\web.config -->
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <rewrite>
      <rules>
        <rule name="VueRouterHistory" stopProcessing="true">
          <match url=".*" />
          <conditions logicalGrouping="MatchAll">
            <add input="{REQUEST_FILENAME}" matchType="IsFile" negate="true" />
            <add input="{REQUEST_FILENAME}" matchType="IsDirectory" negate="true" />
          </conditions>
          <action type="Rewrite" url="/index.html" />
        </rule>
      </rules>
    </rewrite>
  </system.webServer>
</configuration>




uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 --log-config log_config.yaml



version: 1
disable_existing_loggers: False
formatters:
  default:
    format: "%(levelprefix)s %(asctime)s %(message)s"
handlers:
  console:
    class: logging.StreamHandler
    formatter: default
  file:
    class: concurrent_log_handler.ConcurrentRotatingFileHandler
    filename: "app.log"
    maxBytes: 10485760
    backupCount: 5
    formatter: default
loggers:
  uvicorn:
    handlers: [console, file]
    level: INFO
root:
  level: INFO
  handlers: [console, file]




pip install concurrent-log-handler


from concurrent_log_handler import ConcurrentRotatingFileHandler
import logging

logger = logging.getLogger("my_logger")
logger.setLevel(logging.INFO)

handler = ConcurrentRotatingFileHandler(
    "app.log", maxBytes=10*1024*1024, backupCount=5
)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info("FastAPI 시작")




python 
-m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 --log-level info


using System.Net.Http;
using Microsoft.IdentityModel.Clients.ActiveDirectory;

// ADAL의 IHttpClientFactory 구현
public class NoProxyHttpClientFactory : Microsoft.IdentityModel.Clients.ActiveDirectory.IHttpClientFactory
{
    public HttpClient GetHttpClient()
    {
        var handler = new HttpClientHandler
        {
            UseProxy = false,   // 프록시 사용 안 함
            Proxy = null
        };

#if DEBUG
        // 테스트 전용: 인증서 검사 완화 (운영금지)
        handler.ServerCertificateCustomValidationCallback = HttpClientHandler.DangerousAcceptAnyServerCertificateValidator;
#endif

        return new HttpClient(handler, disposeHandler: true);
    }
}










using System.Net.Http;
using Microsoft.IdentityModel.Clients.ActiveDirectory;

// ADAL의 IHttpClientFactory 구현
public class NoProxyHttpClientFactory : Microsoft.IdentityModel.Clients.ActiveDirectory.IHttpClientFactory
{
    public HttpClient GetHttpClient()
    {
        var handler = new HttpClientHandler
        {
            UseProxy = false,   // 프록시 사용 안 함
            Proxy = null
        };

#if DEBUG
        // 테스트 전용: 인증서 검사 완화 (운영금지)
        handler.ServerCertificateCustomValidationCallback = HttpClientHandler.DangerousAcceptAnyServerCertificateValidator;
#endif

        return new HttpClient(handler, disposeHandler: true);
    }
}





using System.Net.Http;
using Microsoft.IdentityModel.Clients.ActiveDirectory;

// ADAL의 IHttpClientFactory 구현
public class NoProxyHttpClientFactory : Microsoft.IdentityModel.Clients.ActiveDirectory.IHttpClientFactory
{
    public HttpClient GetHttpClient()
    {
        var handler = new HttpClientHandler
        {
            UseProxy = false,   // 프록시 사용 안 함
            Proxy = null
        };

#if DEBUG
        // 테스트 전용: 인증서 검사 완화 (운영금지)
        handler.ServerCertificateCustomValidationCallback = HttpClientHandler.DangerousAcceptAnyServerCertificateValidator;
#endif

        return new HttpClient(handler, disposeHandler: var httpFactory = new NoProxyHttpClientFactory();
var authContext = new AuthenticationContext(authority, validateAuthority: true, tokenCache: null, httpClientFactory: httpFactory);

var result = await authContext.AcquireTokenAsync(resource, clientId, new Uri("https://your-return-uri"), new PlatformParameters(PromptBehavior.Auto));







using System;
using System.Net.Http;
using Microsoft.Identity.Client;         // Microsoft.Identity.Client v4+
using Microsoft.Identity.Client.Platforms.Shared; // 필요시

// IMsalHttpClientFactory 구현
public class NoProxyHttpClientFactory : IMsalHttpClientFactory
{
    public HttpClient GetHttpClient()
    {
        var handler = new HttpClientHandler
        {
            UseProxy = false,  // 프록시 사용 금지
            Proxy = null
        };

#if DEBUG
        // 테스트용: 인증서 검증을 완화 (절대 운영에 사용 금지)
        handler.ServerCertificateCustomValidationCallback = (req, cert, chain, errors) => true;
#endif

        return new HttpClient(handler, disposeHandler: true);
    }
}

// MSAL 앱 생성 및 토큰 획득 (Interactive 예시)
var clientId = "your-client-id";
var authority = "https://login.microsoftonline.com/your-tenant-id"; // 또는 "common"
var redirectUri = "http://localhost"; // 앱에 맞게 변경

var httpFactory = new NoProxyHttpClientFactory();

var app = PublicClientApplicationBuilder.Create(clientId)
    .WithAuthority(authority)
    .WithRedirectUri(redirectUri)
    .WithHttpClientFactory(httpFactory)   // 여기에 커스텀 HttpClient 공급
    .Build();

// 요청할 scope 목록 — 실제 사용하려는 리소스/권한으로 교체하세요.
string[] scopes = new[] { "User.Read" }; // 예: Microsoft Graph 권한 예시

var result = await app.AcquireTokenInteractive(scopes)
    .ExecuteAsync();

Console.WriteLine("Access token: " + result.AccessToken);






String regex = "^/api/v1/app/mbeat(/.*)?$";

boolean matched = Pattern.compile(regex).matcher(text).matches();

System.out.println(matched ? "경로 패턴 일치" : "일치하지 않음");



using System;
using System.Collections.Generic;
using System.Linq;

class Program
{
    static void Main()
    {
        var items = new List<string>
        {
            "apple orange banana",
            "apple banana",
            "orange mango",
            "apple orange",
            "grape apple juice"
        };

        string input = "apple,orange"; // 검색 입력값
        var keywords = input
            .Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);

        // 부분 일치하는 모든 키워드를 포함하는 항목만 필터링
        var filtered = items
            .Where(item => keywords.All(k => item.Contains(k, StringComparison.OrdinalIgnoreCase)))
            .ToList();

        // 결과 출력
        foreach (var result in filtered)
        {
            Console.WriteLine(result);
        }
    }
}



🧩 최종 FastAPI API 설계안
1️⃣ 기본 정보 (공용)
GET /models                     # 지원하는 LLM 모델 목록 조회
GET /prompts                    # 샘플 프롬프트 목록 조회


공용 리소스 — 로그인 없이 접근 가능

2️⃣ 대화 (Conversation)
GET    /conversations                 # 사용자의 전체 대화 목록 조회
POST   /conversations                 # 새 대화 생성 (첫 메시지 포함 가능)
GET    /conversations/{id}            # 특정 대화 상세 조회
PUT    /conversations/{id}            # 대화 제목 또는 속성 수정
DELETE /conversations/{id}            # 대화 삭제

POST   /conversations/{id}/messages   # 메시지 추가 및 LLM 응답 요청
GET    /conversations/{id}/messages   # 대화 메시지 전체 히스토리 조회

GET    /conversations/{id}/stream     # LLM 응답을 SSE로 실시간 스트리밍
POST   /conversations/{id}/feedback   # 대화 또는 메시지 피드백 제출


💬 ChatGPT와 유사한 구조로 “대화 → 메시지” 관계 명확
💡 실시간 응답(SSE)은 /stream 하위로 통합

3️⃣ 공유 (Share)
GET    /shares                        # 공유된 대화 목록 (관리자용 또는 내 공유)
POST   /shares                        # 새로운 공유 생성 (body: conversation_id)
GET    /shares/{id}                   # 공유된 대화 조회 (읽기 전용)
POST   /shares/{id}/clone             # 공유된 대화로부터 새 대화 생성
DELETE /shares/{id}                   # 공유 취소 또는 삭제


샘플 (Sample)
GET    /samples                       # 샘플 대화 목록 조회
POST   /samples                       # 새로운 샘플 생성 (body: conversation_id)
GET    /samples/{id}                  # 샘플 대화 조회
POST   /samples/{id}/clone            # 샘플 대화로부터 새 대화 생성


📤 공유는 “스냅샷 → 복제 → 새 대화 생성” 흐름으로 설계

4️⃣ 사용자 수집 자료 (Collector)
GET    /collector/items         # 수집 자료 목록 조회
POST   /collector/items         # 수집 자료 등록
DELETE /collector/items/{id}    # 수집 자료 삭제

📚 사용자가 참고용으로 업로드/저장한 자료 관리용

5️⃣ 사용자 설정 (User Settings)
GET    /user/settings                 # 전체 설정 조회
PUT    /user/settings                 # 설정 전체 수정

GET    /user/settings/subscription    # 구독 설정 조회
PUT    /user/settings/subscription    # 구독 설정 변경

GET    /user/settings/theme           # UI 테마 조회
PUT    /user/settings/theme           # UI 테마 변경

GET    /user/settings/notification    # 알림 설정 조회
PUT    /user/settings/notification    # 알림 설정 변경


⚙️ 향후 theme, notification 등 세부 설정이 추가되어도 확장 용이
/user는 단수형으로 유지 → 로그인된 사용자 한 명 기준

6️⃣ 인증 (Auth)
POST   /auth/login
POST   /auth/logout
POST   /auth/refresh
POST   /auth/register


🔐 JWT 기반 인증을 가정한 표준 구성

🧱 라우터 구성 예시
# main.py
app.include_router(model_router, prefix="/models", tags=["Models"])
app.include_router(prompt_router, prefix="/prompts", tags=["Prompts"])
app.include_router(conversation_router, prefix="/conversations", tags=["Conversations"])
app.include_router(share_router, prefix="/share", tags=["Share"])
app.include_router(collector_router, prefix="/collector", tags=["Collector"])
app.include_router(user_settings_router, prefix="/user/settings", tags=["User Settings"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])

✅ 요약
구분	Prefix	주요 기능	형태
기본 정보	/models, /prompts	모델 및 샘플 프롬프트 조회	공용
대화	/conversations	대화 CRUD 및 메시지 관리	복수형
공유	/share	대화 공유 및 복제	복수형
수집 자료	/collector	사용자가 등록한 자료 관리	복수형
사용자 설정	/user/settings	구독 및 기타 개인 설정	단수형
인증	/auth	로그인/회원가입/JWT 갱신	복수형

이 구성이 확장성·가독성·운영 편의성을 모두 고려한
“운영환경 기준의 실전형 REST API 구조”입니다.

원하신다면 이걸 기반으로
📁 routers/ 디렉토리 구조 + 각 router 기본 템플릿 코드 (conversation_router.py 등)까지 바로 만들어드릴 수도 있습니다.
그걸 원하시나요?



----------------

🧩 최종 FastAPI API 설계안 (v1)
1️⃣ 기본 정보 (공용)
GET /models                     # 지원하는 LLM 모델 목록 조회
GET /prompts                    # 샘플 프롬프트 목록 조회


공용 리소스 (로그인 불필요 가능)
ex) 모델 선택, 프롬프트 추천 등 기본 데이터 제공

2️⃣ 대화 (Conversations)
GET    /conversations                 # 사용자의 전체 대화 목록 조회
POST   /conversations                 # 새 대화 생성 (첫 메시지 포함 가능)
GET    /conversations/{id}            # 특정 대화 상세 조회
PUT    /conversations/{id}            # 대화 제목 또는 속성 수정
DELETE /conversations/{id}            # 대화 삭제

POST   /conversations/{id}/messages   # 메시지 추가 및 LLM 응답 요청
GET    /conversations/{id}/messages   # 대화 메시지 전체 히스토리 조회

GET    /conversations/{id}/stream     # LLM 응답을 SSE로 실시간 스트리밍
POST   /conversations/{id}/feedback   # 대화 또는 메시지 피드백 제출


💬 “대화”와 “메시지”의 계층 구조 명확
💡 SSE 응답은 /stream 하위에서 구분
💡 Feedback은 conversation 단위로 관리 가능

3️⃣ 공유 (Shares)
GET    /shares                        # 내가 생성한 공유 목록 조회
POST   /shares                        # 새 공유 생성 (body: conversation_id)
GET    /shares/{id}                   # 공유된 대화 조회 (읽기 전용)
POST   /shares/{id}/clone             # 공유된 대화로부터 새 대화 생성
DELETE /shares/{id}                   # 공유 삭제 또는 비활성화


📤 공유 리소스는 /shares로 복수형 관리
💡 “복제(clone)”는 명시적 액션으로 표현해 명확성 확보

4️⃣ 샘플 (Samples)
GET    /samples                       # 샘플 대화 목록 조회
POST   /samples                       # 새로운 샘플 등록 (body: conversation_id)
GET    /samples/{id}                  # 샘플 대화 상세 조회
POST   /samples/{id}/clone            # 샘플 대화로부터 새 대화 생성


🧠 /shares와 동일한 구조 유지 — 일관성 극대화
💡 관리자가 제공하는 샘플 프롬프트나 대화 예시용

5️⃣ 사용자 수집 자료 (Collector)
GET    /collector/items               # 사용자가 수집한 자료 목록 조회
POST   /collector/items               # 자료 등록
DELETE /collector/items/{id}          # 자료 삭제


📚 /collector는 기능 그룹, 실제 리소스는 /items
💡 나중에 /collector/tags, /collector/search 등 확장 가능

6️⃣ 사용자 설정 (User Settings)
GET    /user/settings                 # 사용자 설정 전체 조회
PUT    /user/settings                 # 사용자 설정 전체 수정

GET    /user/settings/subscription    # 구독 설정 조회
PUT    /user/settings/subscription    # 구독 설정 변경


관리자
GET  /users/{user_id}/settings                 # 특정 사용자의 설정 조회
PUT  /users/{user_id}/settings                 # 특정 사용자의 설정 수정
GET  /users/{user_id}/settings/subscription    # 특정 사용자의 구독 설정 조회
PUT  /users/{user_id}/settings/subscription    # 특정 사용자의 구독 설정 수정


GET    /users/{user_id}/conversations          # 특정 사용자의 대화 목록 조회
GET    /users/{user_id}/conversations/{id}     # 특정 사용자의 특정 대화 상세 조회
DELETE /users/{user_id}/conversations/{id}     # 특정 사용자의 대화 삭제 (관리자 권한)


⚙️ /user는 단수형 — 현재 로그인한 사용자 기준
💡 /user/settings 하위로 세부 설정 확장 용이
ex) /user/settings/notifications, /user/settings/theme

7️⃣ 인증 (Auth)
POST   /auth/login                    # 로그인
POST   /auth/logout                   # 로그아웃
POST   /auth/refresh                  # 토큰 갱신
POST   /auth/register                 # 회원가입


🔐 JWT 기반 인증을 가정
💡 /user와는 별도의 책임 영역

🧱 FastAPI 라우터 구성 예시
# main.py
app.include_router(model_router, prefix="/models", tags=["Models"])
app.include_router(prompt_router, prefix="/prompts", tags=["Prompts"])
app.include_router(conversation_router, prefix="/conversations", tags=["Conversations"])
app.include_router(share_router, prefix="/shares", tags=["Shares"])
app.include_router(sample_router, prefix="/samples", tags=["Samples"])
app.include_router(collector_router, prefix="/collector", tags=["Collector"])
app.include_router(user_settings_router, prefix="/user/settings", tags=["User Settings"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])

✅ 요약 테이블
구분	Prefix	주요 기능	특징
기본 정보	/models, /prompts	모델/프롬프트 목록	공용
대화	/conversations	대화 CRUD + 메시지/SSE	핵심 서비스
공유	/shares	대화 공유 및 복제	일관된 구조
샘플	/samples	샘플 대화 관리	/shares와 동일 패턴
수집 자료	/collector/items	사용자 저장 자료	확장성 높음
사용자 설정	/user/settings	구독/테마/알림 등	단수형 user
인증	/auth	로그인/회원가입	독립 영역

이 구조는 ChatGPT류 서비스에서

운영 시 API 관리가 쉽고

버전 확장(v2, v3 등)도 단순하며

Swagger/OpenAPI 문서 구조도 깔끔하게 유지됩니다.

원하신다면 다음 단계로
📁 /routers 폴더 구조 + 각 라우터 기본 코드 템플릿 (예: conversation_router.py, collector_router.py)
까지 자동 생성 형태로 구성해드릴까요?
→ 이 설계를 실제 FastAPI 프로젝트 스켈레톤 코드로 옮길 수 있습니다.



-------------


✅ 2️⃣ FastAPI에서 토큰 재발급 방식 (권장)

외부 인증이 성공하면 프론트엔드가 FastAPI에 외부 토큰을 전달,
FastAPI는 이를 검증 후 내부용 JWT를 발급하는 구조입니다.

🔹 흐름

Frontend가 외부 로그인 성공 후 외부 토큰을 획득

FastAPI /auth/exchange 엔드포인트에 외부 토큰 전달

FastAPI가 외부 서버에 토큰 검증 요청

검증 성공 시 FastAPI가 내부 JWT 발급 (ID 포함)

이후 모든 요청은 내부 토큰(Authorization: Bearer <fastapi_token>) 사용

🔹 FastAPI 예시 코드
from fastapi import FastAPI, HTTPException, Header
from jose import jwt
import httpx
import os

SECRET_KEY = os.getenv("FASTAPI_SECRET_KEY", "dev-secret")
ALGORITHM = "HS256"

app = FastAPI()

@app.post("/auth/exchange")
async def exchange_token(external_token: str = Header(..., alias="X-External-Token")):
    # 1️⃣ 외부 인증 서버에 토큰 검증 요청
    async with httpx.AsyncClient() as client:
        res = await client.get(
            "https://auth.example.com/userinfo",
            headers={"Authorization": f"Bearer {external_token}"}
        )
        if res.status_code != 200:
            raise HTTPException(401, "Invalid external token")

        userinfo = res.json()
        user_id = userinfo.get("id")
        if not user_id:
            raise HTTPException(400, "User ID not found in external response")

    # 2️⃣ 내부 JWT 발급
    payload = {"user_id": user_id}
    internal_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": internal_token, "token_type": "bearer"}

🔹 Vue3 프론트엔드 예시
const externalToken = externalAuthToken; // 외부 API 로그인 결과
const { data } = await api.post('/auth/exchange', null, {
  headers: { 'X-External-Token': externalToken },
});
localStorage.setItem('internal_token', data.access_token);


이후 모든 요청은:

api.interceptors.request.use(config => {
  const token = localStorage.getItem('internal_token');
  if (token) config.headers['Authorization'] = `Bearer ${token}`;
  return config;
});


이 구조는 OAuth 2.0의 token exchange (RFC 8693) 표준과 유사하며,
외부 인증 → 내부 서비스 간 토큰 교환이 필요한 상황에서 가장 안정적입니다.



✅ 1️⃣ Vue3 (Frontend) — 사용자 ID 전달

외부 인증 완료 후, FastAPI에 사용자 ID를 전송해 JWT를 받습니다.

import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

export async function loginToBackend(userId: string) {
  const res = await api.post('/auth/token', { user_id: userId });
  const token = res.data.access_token;
  localStorage.setItem('jwt', token);
}

// 이후 요청 시 자동으로 JWT 포함
api.interceptors.request.use(config => {
  const token = localStorage.getItem('jwt');
  if (token) config.headers['Authorization'] = `Bearer ${token}`;
  return config;
});

✅ 2️⃣ FastAPI (Backend) — JWT 생성 및 검증
🔹 auth/token 엔드포인트 — JWT 발급
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from jose import jwt
from datetime import datetime, timedelta

app = FastAPI()

SECRET_KEY = "your-very-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1일 유효

class TokenRequest(BaseModel):
    user_id: str

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/auth/token")
async def issue_token(request: TokenRequest):
    if not request.user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    # 🔹 사용자 ID를 기반으로 자체 JWT 생성
    token_data = {"sub": request.user_id}
    access_token = create_access_token(token_data)
    return {"access_token": access_token, "token_type": "bearer"}

🔹 보호된 API 예시 (JWT 검증)
from fastapi import Depends, HTTPException, Header
from jose import jwt, JWTError

def verify_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(401, "Invalid token: missing user_id")
        return user_id
    except JWTError:
        raise HTTPException(401, "Invalid or expired token")

@app.get("/user/me")
async def get_me(user_id: str = Depends(verify_token)):
    return {"user_id": user_id}

✅ 3️⃣ 흐름 요약

Frontend가 외부 인증을 통해 user_id를 획득

/auth/token으로 {"user_id": "<사용자ID>"} POST 요청

FastAPI가 JWT를 생성하여 반환

이후 모든 요청 시 Authorization: Bearer <JWT> 헤더 포함

FastAPI가 JWT를 검증해 사용자 식별 수행

✅ 4️⃣ 확장 포인트
항목	설명
🔐 보안 강화	user_id 전달 시, 외부 인증 서버의 서명값 or 해시값을 함께 전달하면 위변조 방지 가능
⏱ 토큰 만료	exp 만료시간 외에 iat, iss 등 클레임 추가 가능
🧩 역할(Role) 추가	JWT payload에 roles, permissions 추가 가능
🌐 도메인 제한	FastAPI CORS 설정에서 신뢰된 도메인만 허용
✅ 5️⃣ FastAPI CORS 설정 (필수)
from fastapi.middleware.cors import CORSMiddleware

origins = ["https://your-frontend.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


이 구조면 Frontend가 ID만 전달해도 안전하게 FastAPI에서 자체 토큰을 발급하고,
이후 통신은 표준적인 JWT 인증 체계로 돌아갑니다.
또한 FastAPI는 외부 인증 서버에 의존하지 않고 자체적으로 사용자 식별을 처리할 수 있습니다.

원하신다면 다음 중 하나로 코드를 확장해드릴 수 있어요:

🔄 Refresh Token 추가 버전

🧑‍💻 사용자 Role(권한) 포함 JWT 발급 버전

🧩 외부 인증서의 서명값(HMAC 등)을 검증하는 버전
Frontend]
  └─ 로그인 후 user_id 전송 → /auth/token
[FastAPI]
  ├─ access_token + refresh_token 발급
  ├─ access_token(15분) → 요청 보호
  └─ refresh_token(7일) → /auth/refresh 로 재발급
✅ 1️⃣ 설정값 정의
python
코드 복사
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, List

# 환경설정
SECRET_KEY = "super-secret-key"
REFRESH_SECRET_KEY = "another-refresh-secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

app = FastAPI()

# CORS (필수)
origins = ["https://your-frontend.com", "http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
✅ 2️⃣ 토큰 생성 함수
python
코드 복사
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
✅ 3️⃣ 요청 모델 및 역할(Role) 정보
python
코드 복사
class TokenRequest(BaseModel):
    user_id: str
    roles: Optional[List[str]] = []  # 예: ["admin", "user"]
✅ 4️⃣ /auth/token — 토큰 발급 API
python
코드 복사
@app.post("/auth/token")
async def issue_token(request: TokenRequest):
    if not request.user_id:
        raise HTTPException(400, "user_id required")

    # JWT payload (sub = subject, roles = 권한)
    payload = {"sub": request.user_id, "roles": request.roles}

    access_token = create_access_token(payload)
    refresh_token = create_refresh_token({"sub": request.user_id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }
✅ 5️⃣ /auth/refresh — 토큰 재발급 API
python
코드 복사
class RefreshRequest(BaseModel):
    refresh_token: str

@app.post("/auth/refresh")
async def refresh_token(req: RefreshRequest):
    try:
        payload = jwt.decode(req.refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(401, "Invalid refresh token")

        # 새 Access Token 발급
        new_access_token = create_access_token({"sub": user_id})
        return {"access_token": new_access_token, "token_type": "bearer"}
    except JWTError:
        raise HTTPException(401, "Invalid or expired refresh token")
✅ 6️⃣ 인증 의존성 (토큰 검증)
python
코드 복사
def verify_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Invalid Authorization header")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        roles = payload.get("roles", [])
        if not user_id:
            raise HTTPException(401, "Invalid token")
        return {"user_id": user_id, "roles": roles}
    except JWTError:
        raise HTTPException(401, "Invalid or expired token")
✅ 7️⃣ 보호된 API (Role 검증 포함)
python
코드 복사
@app.get("/user/me")
async def get_me(user=Depends(verify_token)):
    return {"user_id": user["user_id"], "roles": user["roles"]}

@app.get("/admin/only")
async def admin_only(user=Depends(verify_token)):
    if "admin" not in user["roles"]:
        raise HTTPException(403, "Admin role required")
    return {"message": f"Welcome, admin {user['user_id']}!"}
✅ 8️⃣ Vue3 프론트엔드 연동 예시
typescript
코드 복사
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

api.interceptors.request.use(async config => {
  const token = localStorage.getItem('access_token');
  const exp = localStorage.getItem('access_exp');
  const refresh = localStorage.getItem('refresh_token');

  if (token) config.headers['Authorization'] = `Bearer ${token}`;

  // (선택) 만료 감지 후 자동 재발급 로직
  // exp 시간 계산 후 재발급 호출 가능

  return config;
});

export async function login(userId: string, roles: string[]) {
  const { data } = await api.post('/auth/token', { user_id: userId, roles });
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
}
✅ 9️⃣ 정리
항목	설명
Access Token	사용자 ID + Role + 만료시간 (15분)
Refresh Token	사용자 ID만 포함, 7일 유효
재발급	/auth/refresh 에서 Refresh Token으로 새 Access Token
Role 검증	JWT payload 내 roles 필드
Vue	Axios interceptor로 자동 헤더 주입 및 갱신

이 구조는 JWT + Refresh Token + Role 기반 인증의 완성형 템플릿이에요.
실서비스에서도 거의 그대로 적용 가능합니다 ✅



🔄 자동 만료 감지 후 Access Token 재발급 (Vue3 Axios용 코드)

✅ 목표 구조
[Vue3 Axios Interceptor]
 ├─ 모든 요청에 Access Token 자동 포함
 ├─ 응답이 401이면 Refresh Token으로 재발급 시도
 └─ 재발급 성공 시 원래 요청 재시도

✅ 1️⃣ Axios 설정 (토큰 관리용 util)

src/api/auth.ts

import axios, { AxiosRequestConfig, AxiosError } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL;

// FastAPI 백엔드 인스턴스
const api = axios.create({
  baseURL: API_BASE_URL,
});

// === localStorage helper ===
function getAccessToken() {
  return localStorage.getItem('access_token');
}
function getRefreshToken() {
  return localStorage.getItem('refresh_token');
}
function saveTokens(access: string, refresh?: string) {
  localStorage.setItem('access_token', access);
  if (refresh) localStorage.setItem('refresh_token', refresh);
}
function clearTokens() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
}

// === JWT 만료 여부 확인 ===
function isTokenExpired(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const now = Math.floor(Date.now() / 1000);
    return payload.exp < now;
  } catch {
    return true;
  }
}

// === Refresh Token으로 재발급 ===
async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return null;

  try {
    const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
      refresh_token: refreshToken,
    });
    const newAccess = response.data.access_token;
    if (newAccess) {
      saveTokens(newAccess); // refresh_token은 그대로 유지
      return newAccess;
    }
  } catch (error) {
    console.warn('Failed to refresh token:', error);
    clearTokens();
    return null;
  }
  return null;
}

✅ 2️⃣ Axios Request Interceptor — 자동 토큰 주입 + 만료 감지
api.interceptors.request.use(async (config: AxiosRequestConfig) => {
  const token = getAccessToken();

  if (token) {
    // 요청 전에 만료 여부 확인
    if (isTokenExpired(token)) {
      const newAccess = await refreshAccessToken();
      if (!newAccess) throw new Error('Unable to refresh access token');
      config.headers!['Authorization'] = `Bearer ${newAccess}`;
    } else {
      config.headers!['Authorization'] = `Bearer ${token}`;
    }
  }

  return config;
});

✅ 3️⃣ Axios Response Interceptor — 401 자동 처리 및 재시도
api.interceptors.response.use(
  response => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      console.warn('Access token expired, attempting refresh...');
      const newAccess = await refreshAccessToken();

      if (newAccess && error.config) {
        error.config.headers!['Authorization'] = `Bearer ${newAccess}`;
        // 원래 요청 재시도
        return api.request(error.config);
      }

      // 재발급 실패 → 로그인 페이지로 이동 or 로그아웃
      clearTokens();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

✅ 4️⃣ 로그인 함수 예시
export async function login(userId: string, roles: string[]) {
  const { data } = await api.post('/auth/token', { user_id: userId, roles });
  saveTokens(data.access_token, data.refresh_token);
  return data;
}

✅ 5️⃣ FastAPI 대응 엔드포인트 요약 (참고)
엔드포인트	메서드	설명
/auth/token	POST	Access + Refresh Token 발급
/auth/refresh	POST	Refresh Token으로 Access 재발급
/user/me	GET	JWT 인증 테스트용
✅ 6️⃣ 실제 동작 흐름

로그인 성공 → /auth/token → Access + Refresh 저장

요청 시 Axios가 Access Token 자동 추가

만료 감지 시 자동 /auth/refresh 요청

재발급 성공 → Access 갱신 → 원래 API 재시도

Refresh Token도 만료 시 자동 로그아웃 처리

✅ 7️⃣ 추가 팁
상황	대응
Refresh Token도 만료됨	401 발생 시 로그인 페이지로 이동
여러 탭 동시 로그인	Refresh Token은 localStorage 공유됨 — 동작 일관
짧은 Access Token 주기	10~15분 추천 (보안 + UX 밸런스)

이 코드는 Axios + FastAPI JWT 인증의 베스트 프랙티스 구조로,
실제 운영 서비스에서도 거의 그대로 사용 가능한 형태입니다 ⚙️


좋아요 👍
이제 Vue3 + TypeScript + Pinia + Axios 조합으로
JWT 기반 인증 (Access + Refresh 토큰)과 자동 재발급 로직을 완전히 통합한 버전을 보여드릴게요.

🧩 구조 개요
src/
 ├─ stores/
 │   └─ auth.ts           # 인증 관련 Pinia 스토어
 ├─ api/
 │   └─ axios.ts          # Axios 인스턴스 + 인터셉터
 ├─ views/
 │   └─ LoginView.vue     # 로그인 화면 예시
 ├─ main.ts

1️⃣ stores/auth.ts (Pinia 스토어)
// stores/auth.ts
import { defineStore } from 'pinia'
import axios from '@/api/axios'

interface User {
  id: string
  role: string
}

interface AuthState {
  accessToken: string | null
  refreshToken: string | null
  user: User | null
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    accessToken: localStorage.getItem('accessToken'),
    refreshToken: localStorage.getItem('refreshToken'),
    user: JSON.parse(localStorage.getItem('user') || 'null'),
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken,
  },

  actions: {
    async login(id: string) {
      const res = await axios.post('/auth/login', { id })
      const { access_token, refresh_token, user } = res.data

      this.accessToken = access_token
      this.refreshToken = refresh_token
      this.user = user

      localStorage.setItem('accessToken', access_token)
      localStorage.setItem('refreshToken', refresh_token)
      localStorage.setItem('user', JSON.stringify(user))
    },

    async refreshAccessToken() {
      if (!this.refreshToken) throw new Error('No refresh token')

      const res = await axios.post('/auth/refresh', {
        refresh_token: this.refreshToken,
      })
      const { access_token } = res.data

      this.accessToken = access_token
      localStorage.setItem('accessToken', access_token)
      return access_token
    },

    logout() {
      this.accessToken = null
      this.refreshToken = null
      this.user = null
      localStorage.clear()
    },
  },
})

2️⃣ api/axios.ts (Axios 인스턴스 + 인터셉터)
// api/axios.ts
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000,
})

// ✅ 요청 인터셉터
api.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.accessToken) {
    config.headers.Authorization = `Bearer ${auth.accessToken}`
  }
  return config
})

// ✅ 응답 인터셉터 (AccessToken 자동 갱신)
let isRefreshing = false
let refreshQueue: (() => void)[] = []

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const auth = useAuthStore()
    const originalRequest = error.config

    // 토큰 만료로 인한 401 에러 감지
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // 이미 갱신 중이면, 큐에 추가
        return new Promise((resolve) => {
          refreshQueue.push(() => resolve(api(originalRequest)))
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const newAccessToken = await auth.refreshAccessToken()
        // 대기 중이던 요청 재시도
        refreshQueue.forEach((cb) => cb())
        refreshQueue = []
        return api(originalRequest)
      } catch (err) {
        auth.logout()
        window.location.href = '/login'
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

export default api

3️⃣ FastAPI 백엔드 (요약)
# auth_router.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt

SECRET_KEY = "secret"
ALGORITHM = "HS256"

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    id: str

@router.post("/login")
def login(req: LoginRequest):
    user = {"id": req.id, "role": "admin"}  # 외부에서 받은 사용자정보 기반
    access_token = jwt.encode(
        {"sub": user["id"], "role": user["role"], "exp": datetime.utcnow() + timedelta(minutes=30)},
        SECRET_KEY, algorithm=ALGORITHM
    )
    refresh_token = jwt.encode(
        {"sub": user["id"], "exp": datetime.utcnow() + timedelta(days=7)},
        SECRET_KEY, algorithm=ALGORITHM
    )
    return {"access_token": access_token, "refresh_token": refresh_token, "user": user}

class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/refresh")
def refresh(req: RefreshRequest):
    try:
        payload = jwt.decode(req.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        new_access = jwt.encode(
            {"sub": payload["sub"], "exp": datetime.utcnow() + timedelta(minutes=30)},
            SECRET_KEY, algorithm=ALGORITHM
        )
        return {"access_token": new_access}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")

4️⃣ LoginView.vue (예시)
<template>
  <div class="flex flex-col items-center justify-center h-screen">
    <div class="bg-white shadow-lg p-8 rounded-xl w-80">
      <h2 class="text-2xl font-semibold mb-6 text-center">Login</h2>
      <input
        v-model="userId"
        type="text"
        placeholder="User ID"
        class="border p-2 w-full rounded mb-4"
      />
      <button
        @click="login"
        class="bg-blue-500 hover:bg-blue-600 text-white py-2 rounded w-full"
      >
        Login
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const userId = ref('')
const auth = useAuthStore()
const router = useRouter()

async function login() {
  try {
    await auth.login(userId.value)
    router.push('/')
  } catch {
    alert('Login failed')
  }
}
</script>

✅ 동작 요약
상황	처리 방식
로그인	/auth/login → Access + Refresh Token 저장
API 호출 시	Axios가 Authorization: Bearer 자동 추가
Access Token 만료 시	401 감지 → Refresh Token으로 자동 재발급 후 재요청
Refresh Token 만료 시	로그아웃 처리 + /login으로 리다이렉트

원하신다면 다음 단계로

🔐 AccessToken을 localStorage 대신 메모리 저장 + RefreshToken만 안전하게 HttpOnly 쿠키로 관리하는 고보안 버전
도 이어서 만들어드릴 수 있어요.

그럴까요?

아주 좋은 질문이에요 👍
FastAPI에서 JWT 토큰 안의 사용자 정보(예: id, role 등) 를 읽는 표준적인 방법은 다음 단계로 진행됩니다.

🧩 기본 개념

1️⃣ Frontend → 요청 시 JWT를 Authorization: Bearer <access_token> 헤더에 담아 전송
2️⃣ Backend(FastAPI) → 요청을 받을 때 JWT를 디코딩(jwt.decode())하여 사용자 정보를 확인
3️⃣ Dependency 주입 방식으로 get_current_user() 함수를 공통으로 사용

✅ 예시 코드
1️⃣ auth.py – JWT 검증 및 사용자 정보 추출
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime
from typing import Optional

SECRET_KEY = "secret"
ALGORITHM = "HS256"

# Authorization 헤더에서 Bearer 토큰을 자동으로 추출
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# JWT payload 스키마
class TokenData:
    def __init__(self, sub: str, role: Optional[str] = None):
        self.sub = sub
        self.role = role

def get_current_user(token: str = Depends(oauth2_scheme)):
    """요청 헤더의 JWT를 검증하고 사용자 정보를 반환"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        exp: int = payload.get("exp")
        if user_id is None:
            raise credentials_exception
        if datetime.utcfromtimestamp(exp) < datetime.utcnow():
            raise credentials_exception
        return TokenData(sub=user_id, role=role)
    except JWTError:
        raise credentials_exception

2️⃣ 라우터에서 사용 예시
from fastapi import APIRouter, Depends
from .auth import get_current_user, TokenData

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me")
def read_users_me(current_user: TokenData = Depends(get_current_user)):
    return {
        "user_id": current_user.sub,
        "role": current_user.role,
    }


➡️ 클라이언트가 Authorization: Bearer <access_token> 을 보냈다면,
해당 엔드포인트에서 자동으로 토큰이 파싱되어 아래와 같은 응답을 받게 됩니다:

{
  "user_id": "abc123",
  "role": "admin"
}

3️⃣ (선택) 실제 DB 사용자 조회 예시

JWT payload에는 **기본 식별자(id)**만 넣고,
실제 데이터는 DB에서 가져오고 싶다면 이렇게 확장할 수 있습니다:

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

✅ 정리
항목	설명
Authorization	Bearer <token> 형식
OAuth2PasswordBearer	FastAPI가 자동으로 헤더에서 토큰 추출
jwt.decode()	토큰 검증 및 payload 읽기
Depends(get_current_user)	인증 미들웨어처럼 공통으로 사용 가능
role 포함 시	권한 분기 처리도 가능 (if user.role != "admin": ...)
