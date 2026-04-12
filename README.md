front에서 backend로 airflow dag가 실행 중인지 확인하고 실행중이면 실행 하지않고 실행 중이지않으면 실행 하는 것을 만들려고 하는데. 응답을 어떻게 구성하면 좋을까?

이건 핵심이 **“상태 조회 + 실행 요청을 분리할지 / 합칠지”**를 먼저 결정해야 합니다.
결론부터 말하면, 한 번의 API로 처리 (idempotent하게) 만드는 게 가장 안전합니다.

✅ 추천 방식 (Best Practice)

👉 “실행 요청 + 상태 판단”을 서버에서 같이 처리

API 설계
POST /api/dag/run
Request
{
  "dag_id": "example_dag"
}
Response 케이스
1️⃣ 이미 실행 중
{
  "status": "running",
  "message": "DAG is already running",
  "dag_run_id": "manual__2026-04-12T10:00:00",
  "started_at": "2026-04-12T10:00:00"
}
2️⃣ 새로 실행됨
{
  "status": "started",
  "message": "DAG triggered successfully",
  "dag_run_id": "manual__2026-04-12T10:05:00",
  "started_at": "2026-04-12T10:05:00"
}
3️⃣ 실패
{
  "status": "error",
  "message": "Failed to trigger DAG",
  "error": "Airflow API timeout"
}
✅ 왜 이게 좋은가
1. 프론트 단순화

프론트는 그냥:

const res = await api.runDag("example_dag")

if (res.status === "running") {
  // 이미 실행중
} else if (res.status === "started") {
  // 새로 실행됨
}

👉 상태 체크 API 따로 호출 안 해도 됨

2. Race Condition 방지

프론트에서 이렇게 하면 문제 생김:

상태 조회 → "not running"
실행 요청 → 동시에 다른 요청도 실행

👉 중복 실행 발생 가능

➡️ 서버에서 atomic하게 처리해야 안전

3. Airflow 구조상 자연스러움

Apache Airflow 는
기본적으로 dag_run 단위로 실행되기 때문에

👉 서버에서:

running 상태 조회
없으면 trigger

이 흐름이 맞음

✅ 백엔드 로직 (FastAPI 기준 예시)
@router.post("/dag/run")
async def run_dag(dag_id: str):

    running = await airflow.is_dag_running(dag_id)

    if running:
        return {
            "status": "running",
            "message": "DAG is already running",
            "dag_run_id": running.id,
            "started_at": running.start_date
        }

    dag_run = await airflow.trigger_dag(dag_id)

    return {
        "status": "started",
        "message": "DAG triggered successfully",
        "dag_run_id": dag_run.id,
        "started_at": dag_run.start_date
    }
✅ 추가로 넣으면 좋은 것들
🔹 상태 ENUM 명확히
type DagRunStatus =
  | "started"
  | "running"
  | "queued"
  | "success"
  | "failed"
  | "error"
🔹 HTTP Status 코드도 활용
200 → 정상 (started / running)
409 → 이미 실행 중 (선호하는 팀도 있음)
500 → 에러

👉 개인적으로는 200 + status field 방식 추천

🔹 UX 개선 포인트
버튼 클릭 후 disable
polling or websocket으로 상태 갱신
🚀 정리

👉 핵심은 이거 하나

“실행 여부 판단을 프론트가 아니라 백엔드가 하게 만들어라”

그리고 응답은:

status: started | running | error

이 3개만 명확하게 나누면 충분합니다.

원하면
👉 Airflow REST API 기준으로 실제 DAG 상태 체크 (/dagRuns?state=running)까지 포함해서
실제 구현 코드 (FastAPI + async) 더 구체적으로 짜줄게.

------------------------------------------------------------------------------------------------------------------------



<service>
  <id>spring-service</id>

  <executable>java</executable>

  <arguments>
    -Dfile.encoding=UTF-8
    -Dsun.jnu.encoding=UTF-8
    -Duser.timezone=Asia/Seoul
    -jar app.jar
  </arguments>

  <log mode="roll"/>
</service>

<env name="PYTHONIOENCODING" value="utf-8"/>
<env name="PYTHONUTF8" value="1"/>



<service>
  <id>fastapi-service</id>
  <name>FastAPI Service</name>

  <executable>C:\app\venv\Scripts\python.exe</executable>

  <arguments>
    -m uvicorn main:app --host 0.0.0.0 --port 8000
  </arguments>

  <workingdirectory>C:\app</workingdirectory>

  <log mode="roll"/>
</service>



<service>
  <id>springboot-app</id>
  <name>SpringBoot App</name>

  <executable>java</executable>

  <arguments>
    -Xms512m 
    -Xmx1024m 
    -XX:+UseG1GC 
    -Dspring.profiles.active=prod 
    -Dfile.encoding=UTF-8 
    -jar app.jar
  </arguments>

  <log mode="roll" />
</service>



<template>
  <div class="p-6">

    <!-- 🔹 상태 표시 -->
    <div class="mb-4 text-sm">
      <div>
        Active (삭제 대상):
        <span v-if="activeRowKey">{{ activeRowKey }}</span>
        <span v-else>None</span>
      </div>

      <div>
        Checked Keys:
        <span v-if="checkedRowKeys.length">
          {{ checkedRowKeys.join(', ') }}
        </span>
        <span v-else>None</span>
      </div>
    </div>

    <!-- 🔹 버튼 -->
    <div class="mb-4 flex gap-2">
      <a-button type="primary" @click="openModal">Add Row</a-button>

      <a-button danger :disabled="!activeRow" @click="markDelete">
        Delete
      </a-button>

      <a-button :disabled="!hasDeleted" @click="applyDelete">
        Apply Delete
      </a-button>

      <a-button @click="clearSelection">
        Clear
      </a-button>
    </div>

    <!-- 🔹 테이블 -->
    <a-table
      :columns="columns"
      :data-source="dataSource"
      :row-selection="rowSelection"
      :row-class-name="getRowClassName"
      :custom-row="onRowClick"
      rowKey="key"
      :pagination="false"
    >


      <!-- 🔍 필터 dropdown -->
      <template #customFilterDropdown="{ setSelectedKeys, selectedKeys, confirm, clearFilters, column }">
        <div class="p-2">
          <a-input
            ref="searchInput"
            :placeholder="`Search ${column.dataIndex}`"
            :value="selectedKeys[0]"
            @update:value="val => setSelectedKeys(val ? [val] : [])"
            @pressEnter="handleSearch(selectedKeys, confirm, column.dataIndex)"
          />

          <div class="flex gap-2 mt-2">
            <a-button size="small" type="primary"
              @click="handleSearch(selectedKeys, confirm, column.dataIndex)">
              Search
            </a-button>

            <a-button size="small"
              @click="handleReset(clearFilters)">
              Reset
            </a-button>
          </div>
        </div>
      </template>

      <!-- 🔍 아이콘 -->
      <template #customFilterIcon="{ filtered }">
        <SearchOutlined :style="{ color: filtered ? '#108ee9' : undefined }" />
      </template>

      <!-- 🔥 highlight -->
      <template #bodyCell="{ text, column }">
        
        <span v-if="searchState.searchText && searchState.searchedColumn === column.dataIndex">
          <template
            v-for="(fragment, i) in text
              ?.toString()
              .split(new RegExp(`(?<=${searchState.searchText})|(?=${searchState.searchText})`, 'i'))"
          >
            <mark
              v-if="fragment.toLowerCase() === searchState.searchText.toLowerCase()"
              :key="i"
              class="highlight"
            >
              {{ fragment }}
            </mark>
            <template v-else>{{ fragment }}</template>
          </template>
        </span>

        <template v-else>
          {{ text }}
        </template>
      </template>

    </a-table>

    <!-- 🔹 모달 -->
    <a-modal v-model:open="isModalOpen" title="Add User" @ok="handleOk">
      <a-form layout="vertical">
        <a-form-item label="Name">
          <a-input v-model:value="form.name" />
        </a-form-item>

        <a-form-item label="Age">
          <a-input-number v-model:value="form.age" style="width:100%" />
        </a-form-item>

        <a-form-item label="Address">
          <a-input v-model:value="form.address" />
        </a-form-item>
      </a-form>
    </a-modal>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { SearchOutlined } from '@ant-design/icons-vue'

type RowStatus = 'normal' | 'new' | 'deleted' | 'new_deleted'

interface TableRow {
  key: string
  name: string
  age: number
  address: string
  status?: RowStatus
}

/**
 * 데이터
 */
const dataSource = ref<TableRow[]>([
  { key: '1', name: 'John Brown', age: 28, address: 'Seoul', status: 'normal' },
  { key: '2', name: 'Jane Doe', age: 32, address: 'Busan', status: 'normal' },
   { key: '3', name: 'John Brown', age: 28, address: 'Seoul', status: 'normal' },
  { key: '4', name: 'Jane Doe', age: 32, address: 'Busan', status: 'normal' },
   { key: '5', name: 'John Brown', age: 28, address: 'Seoul', status: 'normal' },
  { key: '6', name: 'Jane Doe', age: 32, address: 'Busan', status: 'normal' },
])

/**
 * 🔍 검색 상태
 */
const searchState = reactive({
  searchText: '',
  searchedColumn: '',
})

const handleSearch = (selectedKeys, confirm, dataIndex) => {
  confirm()
  searchState.searchText = selectedKeys[0]
  searchState.searchedColumn = dataIndex
}

const handleReset = (clearFilters?: (param?: { confirm?: boolean }) => void) => {
  clearFilters?.({ confirm: true })
  searchState.searchText = ''
}

/**
 * ✅ 선택 구조
 */
const checkedRowKeys = ref<string[]>([])   // checkbox
const activeRowKey = ref<string | null>(null) // 삭제 대상

const activeRow = computed(() =>
  dataSource.value.find(r => r.key === activeRowKey.value)
)

/**
 * checkbox 선택
 */
const rowSelection = computed(() => ({
  type: 'checkbox' as const,
  selectedRowKeys: checkedRowKeys.value,
  onChange: (keys: string[]) => {
    checkedRowKeys.value = keys
  },
   // 🔥 핵심
  getCheckboxProps: (record: TableRow) => ({
  disabled: record.status !== 'normal',
  title: record.status !== 'normal'
    ? 'normal 상태만 선택 가능합니다'
    : '',
})
}))

/**
 * row 클릭 → 삭제 대상
 */
const onRowClick = (record: TableRow) => ({
  onClick: () => {
    activeRowKey.value = record.key
  },
})

const clearSelection = () => {
  checkedRowKeys.value = []
  activeRowKey.value = null
}

/**
 * 삭제
 */
const markDelete = () => {
  if (!activeRow.value) return

  activeRow.value.status =
    activeRow.value.status === 'new' ? 'new_deleted' : 'deleted'
}

const hasDeleted = computed(() =>
  dataSource.value.some(r => r.status === 'deleted' || r.status === 'new_deleted')
)

const applyDelete = () => {
  dataSource.value = dataSource.value.filter(
    r => r.status !== 'deleted' && r.status !== 'new_deleted'
  )
  clearSelection()
}

/**
 * 추가
 */
const isModalOpen = ref(false)

const form = ref({
  name: '',
  age: 0,
  address: '',
})

const openModal = () => {
  form.value = { name: '', age: 0, address: '' }
  isModalOpen.value = true
}

const handleOk = () => {
  if (!form.value.name) return

  dataSource.value.unshift({
    key: Date.now().toString(),
    ...form.value,
    status: 'new',
  })

  isModalOpen.value = false
}

/**
 * 컬럼
 */
const columns = [
  {
    title: 'Name',
    dataIndex: 'name',
    key: 'name',
    customFilterDropdown: true,
    onFilterDropdownOpenChange: (visible: boolean) => {
      if (visible) {
        requestAnimationFrame(() => {
          searchInput.value?.focus()
        })
      }
    },
    onFilter: (value, record) =>
      record.name.toLowerCase().includes(value.toLowerCase()),
  },
  {
    title: 'Age',
    dataIndex: 'age',
    sorter: (a, b) => a.age - b.age,
  },
  {
    title: 'Address',
    dataIndex: 'address',
    key: 'address',
    customFilterDropdown: true,
    onFilter: (value, record) =>
      record.address.toLowerCase().includes(value.toLowerCase()),
  },
  {
    title: 'Status',
    dataIndex: 'status',
    filters: [
      { text: 'Normal', value: 'normal' },
      { text: 'New', value: 'new' },
      { text: 'Deleted', value: 'deleted' },
      { text: 'New Deleted', value: 'new_deleted' },
    ],
    onFilter: (value, record) => record.status === value,
  },
]

const searchInput = ref<any>(null)

/**
 * 스타일
 */
const getRowClassName = (record: TableRow) => {
  const isActive = record.key === activeRowKey.value

  let cls = ''

  if (record.status === 'deleted') cls = 'row-deleted'
  else if (record.status === 'new_deleted') cls = 'row-new-deleted'
  else if (record.status === 'new') cls = 'row-new'

  if (isActive) cls += ' row-selected'

 
  return cls.trim()
}
</script>

<style lang="scss" scoped>

:deep(.ant-table-tbody > tr > td) {
  transition: none !important;
}

/* 상태 */
:deep(.row-deleted > td) {
  background: #fee2e2 !important;
}
:deep(.row-deleted:hover > td) {
  background: #fecaca !important;
}

:deep(.row-new-deleted > td) {
  background: #ffedd5 !important;
}
:deep(.row-new-deleted:hover > td) {
  background: #fed7aa !important;
}

:deep(.row-new > td) {
  background: #ecfdf5 !important;
}
:deep(.row-new:hover > td) {
  background: #d1fae5 !important;
}

:deep(.row-selected > td) {
  background: #dbeafe !important;
}
:deep(.row-selected:hover > td) {
  background: #bfdbfe !important;
}

/* 기본 hover 제거 */
:deep(.ant-table-tbody > tr:hover > td) {
  background: unset !important;
}

/* highlight */
.highlight {
  background-color: #ffc069;
}
</style>



----------------------------------------------------------------------

focus

<template>
  <div class="p-6">

    <!-- 상태 표시 -->
    <div class="mb-4 text-sm">
      <div>
        Active:
        <span v-if="activeRowKey">{{ activeRowKey }}</span>
        <span v-else>None</span>
      </div>

      <div>
        Checked:
        <span v-if="checkedRowKeys.length">
          {{ checkedRowKeys.join(', ') }}
        </span>
        <span v-else>None</span>
      </div>
    </div>

    <!-- 버튼 -->
    <div class="mb-4 flex gap-2">
      <a-button type="primary" >Add Row</a-button>
      <a-button danger :disabled="!activeRow" @click="markDelete">Delete</a-button>
      <a-button @click="clearSelection">Clear</a-button>
    </div>

    <!-- 테이블 -->
    <a-table
      :columns="columns"
      :data-source="dataSource"
      :row-selection="rowSelection"
      :custom-row="onRowClick"
      rowKey="key"
      :pagination="false"
    >

      <!-- 🔍 필터 dropdown -->
      <template #customFilterDropdown="{ setSelectedKeys, selectedKeys, confirm, clearFilters, column }">
        <div class="p-2">

          <a-input
            :ref="el => {
              if (el) searchInputs[column.dataIndex] = el
            }"
            :placeholder="`Search ${column.dataIndex}`"
            :value="selectedKeys[0]"
            @update:value="val => setSelectedKeys(val ? [val] : [])"
            @pressEnter="handleSearch(selectedKeys, confirm, column.dataIndex)"
          />

          <div class="flex gap-2 mt-2">
            <a-button size="small" type="primary"
              @click="handleSearch(selectedKeys, confirm, column.dataIndex)">
              Search
            </a-button>

            <a-button size="small"
              @click="handleReset(clearFilters)">
              Reset
            </a-button>
          </div>

        </div>
      </template>

      <!-- 아이콘 -->
      <template #customFilterIcon="{ filtered }">
        <SearchOutlined
          :style="{
            fontSize: '18px',
            color: filtered ? '#1677ff' : '#999'
          }"
        />
      </template>

    </a-table>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, nextTick } from 'vue'
import { SearchOutlined } from '@ant-design/icons-vue'

type RowStatus = 'normal' | 'new' | 'deleted' | 'new_deleted'

interface TableRow {
  key: string
  name: string
  age: number
  address: string
  status?: RowStatus
}

/**
 * 데이터
 */
const dataSource = ref<TableRow[]>([
  { key: '1', name: 'John', age: 28, address: 'Seoul', status: 'normal' },
  { key: '2', name: 'Jane', age: 32, address: 'Busan', status: 'normal' },
])

/**
 * 검색 상태
 */
const searchState = reactive({
  searchText: '',
  searchedColumn: '',
})

const handleSearch = (selectedKeys, confirm, dataIndex) => {
  confirm()
  searchState.searchText = selectedKeys[0]
  searchState.searchedColumn = dataIndex
}

const handleReset = (clearFilters?: (param?: { confirm?: boolean }) => void) => {
  clearFilters?.({ confirm: true })
  searchState.searchText = ''
}

/**
 * ✅ 핵심: 컬럼별 input ref
 */
const searchInputs = ref<Record<string, any>>({})

/**
 * ✅ focus 함수 (핵심)
 */
const focusInput = (key: string) => {
  nextTick(() => {
    setTimeout(() => {
      const input = searchInputs.value[key]
      input?.input?.focus()
    }, 50)
  })
}
/**
 * 선택
 */
const checkedRowKeys = ref<string[]>([])
const activeRowKey = ref<string | null>(null)

const activeRow = computed(() =>
  dataSource.value.find(r => r.key === activeRowKey.value)
)

const rowSelection = computed(() => ({
  type: 'checkbox' as const,
  selectedRowKeys: checkedRowKeys.value,
  onChange: (keys: string[]) => {
    checkedRowKeys.value = keys
  },
  getCheckboxProps: (record: TableRow) => ({
    disabled: record.status !== 'normal',
  }),
}))

const onRowClick = (record: TableRow) => ({
  onClick: () => {
    activeRowKey.value = record.key
  },
})

const clearSelection = () => {
  checkedRowKeys.value = []
  activeRowKey.value = null
}

/**
 * 삭제
 */
const markDelete = () => {
  if (!activeRow.value) return
  activeRow.value.status = 'deleted'
}

/**
 * 컬럼 (🔥 핵심 focus 적용)
 */
const columns = [
  {
    title: 'Name',
    dataIndex: 'name',
    key: 'name',
    customFilterDropdown: true,
    onFilterDropdownOpenChange: (visible: boolean) => {
      if (visible) focusInput('name')
    },
    onFilter: (value, record) =>
      record.name.toLowerCase().includes(value.toLowerCase()),
  },
  {
    title: 'Age',
    dataIndex: 'age',
  },
  {
    title: 'Address',
    dataIndex: 'address',
    key: 'address',
    customFilterDropdown: true,
    onFilterDropdownOpenChange: (visible: boolean) => {
      if (visible) focusInput('address')
    },
    onFilter: (value, record) =>
      record.address.toLowerCase().includes(value.toLowerCase()),
  },
]
</script>
