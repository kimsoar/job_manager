조회 조건 영역과 결과 영역을 완전히 독립적인 MF(Micro Frontend) 컴포넌트로 재사용할 계획이면, 이름을 “화면 기준”이 아니라 “역할 기준”으로 나누는게 유지보수에 훨씬 좋습니다.

지금 구조를 보면 실제 역할은:

조회 조건 입력
분석 실행
분석 결과 표시

이 3가지입니다.

추천 구조는 아래처럼 가는 걸 권장합니다.

추천 네이밍 구조
1. 조회 조건 MF
추천 이름
LotAnalysisFilter
LotAnalysisCriteria
LotAnalysisQuery

그 중 가장 추천:

LotAnalysisFilter

이유:

검색 조건 UI라는 의미가 가장 직관적
다른 화면에서도 재사용하기 좋음
백엔드 query/filter 의미와도 자연스럽게 연결됨
2. 결과 테이블 MF
추천 이름
LotAnalysisResult
LotAnalysisResultTable
LotAnalysisComparisonTable

그 중 가장 추천:

LotAnalysisResultTable

이유:

결과 + 테이블 역할이 명확
추후 chart/card 추가 시 Result와 구분 가능
실제 UI 책임이 드러남
최종 추천 구조
mf-lot-analysis-filter
mf-lot-analysis-result-table

Vue 컴포넌트명:

LotAnalysisFilter.vue
LotAnalysisResultTable.vue
내부 구조 추천
조회 조건 MF
lot-analysis-filter/
├── components/
│   ├── LotConditionCard.vue
│   └── WaferSelector.vue
│
├── composables/
│   ├── useLotAnalysisFilter.ts
│   └── useLotCondition.ts
│
├── services/
│   └── lot-analysis-filter.service.ts
│
├── api/
│   └── lot-analysis-filter.api.ts
│
├── types/
│   └── lot-analysis-filter.type.ts
│
└── LotAnalysisFilter.vue
결과 테이블 MF
lot-analysis-result-table/
├── components/
│   ├── AnalysisTable.vue
│   ├── AnalysisDetailPanel.vue
│   └── WaferCell.vue
│
├── composables/
│   ├── useAnalysisTable.ts
│   ├── useWaferSelection.ts
│   └── useMismatchHighlight.ts
│
├── services/
│   └── lot-analysis-result.service.ts
│
├── api/
│   └── lot-analysis-result.api.ts
│
├── types/
│   └── analysis-result.type.ts
│
└── LotAnalysisResultTable.vue
중요한 포인트

현재 코드 기준으로는:

LotAnalysisCondition

보다

LotAnalysisFilter

가 훨씬 좋은 이름입니다.

왜냐면 Condition은 너무 추상적입니다.

실제 역할은:

검색
필터링
조회 범위 지정

이므로 Filter/Query가 더 명확합니다.

내가 가장 추천하는 최종 이름
MF 이름
mf-lot-analysis-filter
mf-lot-analysis-result-table
Vue Root Component
LotAnalysisFilter.vue
LotAnalysisResultTable.vue
composable
useLotAnalysisFilter
useLotAnalysisResult
service
lotAnalysisFilter.service.ts
lotAnalysisResult.service.ts
api
lotAnalysisFilter.api.ts
lotAnalysisResult.api.ts
추가 추천

조회 조건 MF와 결과 MF를 완전히 분리한다면
둘 사이 연결은 props/event 보다 아래 방식이 더 좋습니다.

Shell(Page)
 ├─ LotAnalysisFilter MF
 └─ LotAnalysisResultTable MF

그리고 shell에서:

const condition = ref()
const result = ref()

onSearch = async (filter) => {
  result.value = await fetchResult(filter)
}

즉:

Filter MF → 검색 조건 emit
Shell → API 호출 orchestration
Result MF → 결과만 렌더링

이 구조가 MF에서는 가장 안정적입니다.

특히:

독립 배포
독립 테스트
독립 라우팅
독립 상태관리

할 때 강력합니다.
