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
