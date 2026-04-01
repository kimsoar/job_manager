// utils/url.ts
export function extractPageId(url: string): number | null {
  const patterns = [
    /pageId=(\d+)/,
    /\/pages\/(\d+)\//
  ];

  for (const pattern of patterns) {
    const match = url.match(pattern);
    if (match) return Number(match[1]);
  }

  return null; // throw 대신 안전하게
}


<style lang="scss" scoped>
:deep(.ant-table-tbody) {

  > tr {

    /* 기본 transition 제거 (중요) */
    > td {
      transition: none !important;
    }

    /* 🔴 삭제 */
    &.row-deleted > td {
      background-color: #fee2e2 !important;
      color: #ef4444;
      text-decoration: line-through;
    }

    &.row-deleted:hover > td {
      background-color: #fecaca !important;
    }

    /* 🟠 신규삭제 */
    &.row-new-deleted > td {
      background-color: #ffedd5 !important;
      color: #f97316;
      text-decoration: line-through;
    }

    &.row-new-deleted:hover > td {
      background-color: #fed7aa !important;
    }

    /* 🟢 신규 */
    &.row-new > td {
      background-color: #ecfdf5 !important;
      border-left: 4px solid #4ade80;
    }

    &.row-new:hover > td {
      background-color: #d1fae5 !important;
    }

    /* 🔵 선택 */
    &.row-selected > td {
      background-color: #dbeafe !important;
    }

    &.row-selected:hover > td {
      background-color: #bfdbfe !important;
    }

    /* 기본 hover */
    &:not(.row-new):not(.row-deleted):not(.row-new-deleted):hover > td {
      background-color: #f9fafb !important;
    }
  }
}

/* 🔥 Antd 기본 완전 제거 */
:deep(.ant-table-tbody > tr:hover > td) {
  background: unset !important;
}

:deep(.ant-table-tbody > tr.ant-table-row-selected > td) {
  background: unset !important;
}
</style>

const getRowClassName = (record: TableRow) => {
  const isSelected = selectedRowKeys.value.includes(record.key)

  let cls = ''

  if (record.status === 'deleted') cls = 'row-deleted'
  else if (record.status === 'new_deleted') cls = 'row-new-deleted'
  else if (record.status === 'new') cls = 'row-new'

  if (isSelected) cls += ' row-selected'

  return cls.trim()
}












<style lang="scss" scoped>
:deep(.ant-table-tbody) {
  > tr {
    transition: all 0.15s ease;

    /* 🔵 선택 상태 */
    &.selected-row > td {
      background-color: #dbeafe !important; // blue-100
    }

    &:hover.selected-row > td {
      background-color: #bfdbfe !important; // blue-200
    }

    /* 🟢 신규 */
    &.new-row > td {
      background-color: #ecfdf5 !important; // green-50
      border-left: 4px solid #4ade80;
    }

    &:hover.new-row > td {
      background-color: #d1fae5 !important; // green-100
    }

    /* 🔴 삭제 */
    &.deleted-row > td {
      background-color: #fee2e2 !important; // red-100
      color: #ef4444;
      text-decoration: line-through;
    }

    &:hover.deleted-row > td {
      background-color: #fecaca !important; // red-200
    }

    /* 🟠 신규 후 삭제 */
    &.new-deleted-row > td {
      background-color: #ffedd5 !important; // orange-100
      color: #f97316;
      text-decoration: line-through;
    }

    &:hover.new-deleted-row > td {
      background-color: #fed7aa !important; // orange-200
    }

    /* 기본 hover */
    &:hover > td {
      background-color: #f9fafb;
    }
  }
}

/* 🔥 Antd 기본 hover 제거 */
:deep(.ant-table-tbody > tr:hover > td) {
  background: transparent !important;
}

/* 🔥 선택 색 제거 */
:deep(.ant-table-tbody > tr.ant-table-row-selected > td) {
  background: transparent !important;
}
</style>



<style lang="scss" scoped>
:deep(.ant-table) {
  border: 1px solid #e5e7eb; // Tailwind gray-200

  .ant-table-container {
    border-inline-start: 1px solid #e5e7eb;
    border-top: 1px solid #e5e7eb;
  }

  .ant-table-cell {
    border-inline-end: 1px solid #e5e7eb;
    border-bottom: 1px solid #e5e7eb;
  }
}
</style>

:deep(.ant-table) {
  border: 1px solid #d1d5db;

  .ant-table-cell {
    border: 1px solid #d1d5db;
  }
}

:deep(.ant-table) {
  border: 1px solid #e5e7eb;

  .ant-table-cell {
    border-color: #e5e7eb;
  }
}



const getRowClassName = (record: TableRow) => {
  const isSelected = selectedRowKeys.value.includes(record.key)

  const base = 'transition-all duration-200'

  switch (record.status) {
    case 'new':
      return `
        bg-green-50 hover:bg-green-100 
        border-l-4 border-green-400 ${base}
      `

    case 'deleted':
      return `
        bg-red-100 hover:bg-red-200 
        text-red-500 line-through ${base}
      `

    case 'new_deleted':
      return `
        bg-orange-100 hover:bg-orange-200 
        text-orange-600 line-through ${base}
      `

    default:
      if (isSelected) {
        return `bg-blue-100 hover:bg-blue-200 ${base}`
      }
      return `hover:bg-gray-50 ${base}`
  }
}


<style lang="scss" scoped>
:deep(.ant-table-tbody) {
  > tr {
    &:hover > td {
      background: transparent !important;
    }

    &.ant-table-row-selected > td {
      background-color: transparent !important;
    }
  }
}
</style>

---------------------------------------------------------------------------

<style lang="scss" scoped>
/* 🔥 Antd hover 제거 */
:deep(.ant-table-tbody > tr:hover > td) {
  background: transparent !important;
}

/* 🔥 Antd 선택 색 제거 */
:deep(.ant-table-tbody > tr.ant-table-row-selected > td) {
  background-color: transparent !important;
}
</style>


------------------------------------------------------------


<template>
  <a-form
    ref="formRef"
    :model="form"
    :rules="rules"
    layout="vertical"
  >
    <!-- 이름 -->
    <a-form-item label="Name" name="name">
      <a-input v-model:value="form.name" />
    </a-form-item>

    <!-- 🔥 멀티 셀렉트 -->
    <a-form-item label="Tags" name="tags">
      <a-select
        v-model:value="form.tags"
        mode="multiple"
        placeholder="태그 선택"
        :options="options"
        allow-clear
      />
    </a-form-item>

    <!-- 버튼 -->
    <a-button type="primary" @click="handleSubmit">
      Submit
    </a-button>
  </a-form>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { FormInstance } from 'ant-design-vue'

// form
const formRef = ref<FormInstance>()

const form = ref({
  name: '',
  tags: [] as string[],
})

// 옵션
const options = [
  { label: 'Frontend', value: 'frontend' },
  { label: 'Backend', value: 'backend' },
  { label: 'DevOps', value: 'devops' },
]

// 🔥 validation rules
const rules = {
  name: [
    { required: true, message: '이름을 입력하세요' },
  ],
  tags: [
    {
      required: true,
      type: 'array',
      min: 1,
      message: '최소 1개 이상 선택하세요',
      trigger: 'change',
    },
  ],
}

// 제출
const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    console.log('성공:', form.value)
  } catch (err) {
    console.log('검증 실패')
  }
}
</script>





<template>
  <div class="p-6">
    <!-- 버튼 영역 -->
    <div class="mb-4 flex gap-2">
      <a-button type="primary" @click="openModal">
        Add Row
      </a-button>

      <a-button
        danger
        :disabled="!selectedRow"
        @click="markDelete"
      >
        Delete Selected
      </a-button>

      <a-button
        :disabled="!hasDeleted"
        @click="applyDelete"
      >
        Apply Delete
      </a-button>
    </div>

    <!-- 선택된 row 표시 -->
    <div class="mb-4 text-sm text-gray-600">
      Selected:
      <span v-if="selectedRow">
        {{ selectedRow.name }} ({{ selectedRow.age }})
      </span>
      <span v-else>None</span>
    </div>

    <!-- 테이블 -->
    <a-table
    bordered
      :columns="columns"
      :data-source="dataSource"
      :row-selection="rowSelection"
      :row-class-name="getRowClassName"
      :custom-row="onRowClick"
      :pagination="false"
      rowKey="key"
    />

    <!-- 모달 -->
    <a-modal
      v-model:open="isModalOpen"
      title="Add New User"
      @ok="handleOk"
      @cancel="handleCancel"
    >
      <a-form layout="vertical">
        <a-form-item label="Name">
          <a-input v-model:value="form.name" />
        </a-form-item>

        <a-form-item label="Age">
          <a-input-number
            v-model:value="form.age"
            :min="0"
            style="width: 100%"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface TableRow {
  key: string
  name: string
  age: number
  isNew?: boolean
  isDeleted?: boolean
}

// 컬럼
const columns = [
  { title: 'Name', dataIndex: 'name', key: 'name' },
  { title: 'Age', dataIndex: 'age', key: 'age' },
]

// 데이터
const dataSource = ref<TableRow[]>([
  { key: '1', name: 'John', age: 28 },
  { key: '2', name: 'Jane', age: 32 },
])

// 선택 상태
const selectedRowKeys = ref<string[]>([])

const selectedRow = computed(() =>
  dataSource.value.find(row => row.key === selectedRowKeys.value[0])
)

// 🔥 selection (반드시 computed)
const rowSelection = computed(() => ({
  type: 'radio' as const,
  selectedRowKeys: selectedRowKeys.value,
  onChange: (keys: string[]) => {
    selectedRowKeys.value = keys
  },
}))

// row 클릭 선택
const onRowClick = (record: TableRow) => ({
  onClick: () => {
    selectedRowKeys.value = [record.key]
  },
})

/**
 * 🔴 Soft Delete
 */
const markDelete = () => {
  if (!selectedRow.value) return
  selectedRow.value.isDeleted = true
}

const hasDeleted = computed(() =>
  dataSource.value.some(row => row.isDeleted)
)

const applyDelete = () => {
  dataSource.value = dataSource.value.filter(row => !row.isDeleted)
  selectedRowKeys.value = []
}

/**
 * 🟢 Modal
 */
const isModalOpen = ref(false)

const form = ref({
  name: '',
  age: 0,
})

const openModal = () => {
  form.value = { name: '', age: 0 }
  isModalOpen.value = true
}

const handleOk = () => {
  if (!form.value.name) return

  const newRow: TableRow = {
    key: Date.now().toString(),
    name: form.value.name,
    age: form.value.age,
    isNew: true,
  }

  dataSource.value.unshift(newRow)

  // 자동 선택
  selectedRowKeys.value = [newRow.key]

  isModalOpen.value = false
}

const handleCancel = () => {
  isModalOpen.value = false
}

/**
 * 🎨 row 스타일 (hover 포함)
 */
const getRowClassName = (record: TableRow) => {
  const isSelected = selectedRowKeys.value.includes(record.key)

  // 🔴 삭제 (hover 유지)
  if (record.isDeleted) {
    return `
      bg-red-100 
      hover:bg-red-200 
      text-red-500 
      line-through 
      transition-all duration-200
    `
  }

  // 🟢 신규 + 선택
  if (record.isNew && isSelected) {
    return `
      bg-green-200 
      hover:bg-green-300 
      border-l-4 border-green-500 
      transition-all duration-200
    `
  }

  // 🟢 신규
  if (record.isNew) {
    return `
      bg-green-50 
      hover:bg-green-100 
      border-l-4 border-green-400 
      transition-all duration-200
    `
  }

  // 🔵 선택
  if (isSelected) {
    return `
      bg-blue-100 
      hover:bg-blue-200 
      transition-all duration-200
    `
  }

  // 기본
  return 'hover:bg-gray-50 transition-all duration-200'
}
</script>

<style>
/* 🔥 Antd 기본 hover 제거 */
.ant-table-tbody > tr:hover > td {
  background: transparent !important;
}

/* 🔥 Antd 선택 색 제거 */
.ant-table-tbody > tr.ant-table-row-selected > td {
  background-color: transparent !important;
}
</style>
