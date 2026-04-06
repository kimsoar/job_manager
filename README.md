
import { onMounted, onBeforeUnmount } from 'vue'

let timer: number | null = null

const handleResize = () => {
  if (timer) clearTimeout(timer)

  timer = window.setTimeout(() => {
    refreshTable()
  }, 150)
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
})



<template>
  <div class="p-6">
    <!-- 버튼 -->
    <div class="mb-4 flex gap-2">
      <a-button type="primary" @click="openModal">Add Row</a-button>
      <a-button danger :disabled="!selectedRow" @click="markDelete">Delete</a-button>
      <a-button :disabled="!hasDeleted" @click="applyDelete">Apply Delete</a-button>
      <a-button @click="clearSelection">Clear</a-button>
    </div>

    <!-- 테이블 -->
    <a-table
      :columns="columns"
      :data-source="dataSource"
      :row-selection="rowSelection"
      :row-class-name="getRowClassName"
      :custom-row="onRowClick"
      rowKey="key"
      :pagination="false"
    >
      <!-- 🔍 검색 필터 UI -->
      <template #customFilterDropdown="{ setSelectedKeys, selectedKeys, confirm, clearFilters, column }">
         <div style="padding: 8px">
        <a-input
          ref="searchInput"
          :placeholder="`Search ${column.dataIndex}`"
          :value="selectedKeys[0]"
          style="width: 188px; margin-bottom: 8px; display: block"
          @pressEnter="handleSearch(selectedKeys, confirm, column.dataIndex)"
          @change="(e: Event) => handleInputChange(e, setSelectedKeys)"
        />
        <a-button
          type="primary"
          size="small"
          style="width: 90px; margin-right: 8px"
          @click="handleSearch(selectedKeys, confirm, column.dataIndex)"
        >
          <template #icon><SearchOutlined /></template>
          Search
        </a-button>
        <a-button size="small" style="width: 90px" @click="handleReset(clearFilters)">
          Reset
        </a-button>
      </div>
      </template>

      <!-- 🔍 필터 아이콘 -->
      <template #customFilterIcon="{ filtered }">
        <SearchOutlined :style="{ color: filtered ? '#108ee9' : undefined }" />
      </template>
    </a-table>

    <!-- 모달 -->
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
const searchInput = ref<any>(null)
interface TableRow {
  key: string
  name: string
  age: number
  address: string
  status?: RowStatus
}

const handleInputChange = (
  e: Event,
  setSelectedKeys: (keys: string[]) => void
) => {
  const target = e.target as HTMLInputElement
  setSelectedKeys(target.value ? [target.value] : [])
}

/**
 * 데이터
 */
const dataSource = ref<TableRow[]>([
  { key: '1', name: 'John Brown', age: 28, address: 'Seoul', status: 'normal' },
  { key: '3', name: 'Jane sdf', age: 32, address: 'aa', status: 'normal' },
    { key: '4', name: 'Jane sfadfds', age: 32, address: 'aa ban', status: 'normal' },
      { key: '5', name: 'Jansfdfssfe Doe', age: 32, address: 'aaa', status: 'normal' },
        { key: '6', name: 'asfdfsa Doe', age: 32, address: 'aaaa', status: 'normal' },
          { key: '7', name: 'asdffds Doe', age: 32, address: 'ee', status: 'normal' },
            { key: '8', name: 'sadf Doe', age: 32, address: 'sss', status: 'normal' },

])

/**
 * 검색 상태
 */
const searchState = reactive({
  searchText: '',
  searchedColumn: '',
})


const handleSearch = (
  selectedKeys: string[],
  confirm: () => void,
  dataIndex: string
) => {
  confirm()
  searchState.searchText = selectedKeys[0]
  searchState.searchedColumn = dataIndex
}

type ClearFilters = (param?: { confirm?: boolean; closeDropdown?: boolean }) => void

const handleReset = (clearFilters?: ClearFilters) => {
  clearFilters?.({ confirm: true })
  searchState.searchText = ''
}

/**
 * 선택
 */
const selectedRowKeys = ref<string[]>([])

const selectedRow = computed(() =>
  dataSource.value.find(r => r.key === selectedRowKeys.value[0])
)

const rowSelection = computed(() => ({
  type: 'radio' as const,
  selectedRowKeys: selectedRowKeys.value,
  onChange: (keys: string[]) => (selectedRowKeys.value = keys),
}))

const onRowClick = (record: TableRow) => ({
  onClick: () => (selectedRowKeys.value = [record.key]),
})

const clearSelection = () => (selectedRowKeys.value = [])

/**
 * 삭제
 */
const markDelete = () => {
  if (!selectedRow.value) return

  selectedRow.value.status =
    selectedRow.value.status === 'new' ? 'new_deleted' : 'deleted'
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
      setTimeout(() => {
        searchInput.value?.focus()
      }, 100)
    }
  },
    onFilter: (value: string, record: TableRow) =>
      record.name.toLowerCase().includes(value.toLowerCase()),
  },
  {
    title: 'Age',
    dataIndex: 'age',
    sorter: (a: TableRow, b: TableRow) => a.age - b.age,
  },
  {
    title: 'Address',
    dataIndex: 'address',
    key: 'address',
    customFilterDropdown: true,
     onFilterDropdownOpenChange: (visible: boolean) => {
    if (visible) {
      setTimeout(() => {
        searchInput.value?.focus()
      }, 100)
    }
  },
    onFilter: (value: string, record: TableRow) =>
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
    onFilter: (value: string, record: TableRow) => record.status === value,
  },
]

/**
 * 스타일 class
 */
const getRowClassName = (record: TableRow) => {
  const isSelected = selectedRowKeys.value.includes(record.key)

  let cls = ''

  if (record.status === 'deleted') cls = 'row-deleted'
  else if (record.status === 'new_deleted') cls = 'row-new-deleted'
  else if (record.status === 'new') cls = 'row-new'

  if (isSelected) cls += ' row-selected'

  return cls.trim()
}
</script>

<style lang="scss" scoped>
:deep(.ant-table-tbody > tr > td) {
  transition: none !important;
}

/* 상태별 */
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
  padding: 0;
}
</style>
