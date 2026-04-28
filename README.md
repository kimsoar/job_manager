<template>
  <a-tooltip v-if="isOverflow" :title="text">
    <span
      ref="elRef"
      class="truncate block w-full"
      @mouseenter="check"
    >
      {{ text }}
    </span>
  </a-tooltip>

  <span
    v-else
    ref="elRef"
    class="truncate block w-full"
    @mouseenter="check"
  >
    {{ text }}
  </span>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue';

const props = defineProps<{
  text: string | number;
}>();

const elRef = ref<HTMLElement | null>(null);
const isOverflow = ref(false);

const check = async () => {
  await nextTick();
  const el = elRef.value;
  if (!el) return;

  isOverflow.value = el.scrollWidth > el.clientWidth;
};
</script>

<style scoped>
.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>


------------------

<template>
  <div
    class="p-6 outline-none h-full"
    tabindex="0"
  >
    <div class="mb-4 flex items-center justify-between">
      <div class="text-sm font-mono bg-slate-50 p-3 rounded border border-slate-200 shadow-sm flex-1 mr-4">
        <span>Active Key: <b class="text-blue-600">{{ activeRowKey || 'None' }}</b></span>
      </div>
      
      <div class="flex gap-2">
        <a-button type="primary" @click="addRow">
          <template #icon><PlusOutlined /></template>행 추가
        </a-button>
        <a-button danger :disabled="!activeRowKey" @click="removeRow">
          <template #icon><DeleteOutlined /></template>행 삭제
        </a-button>
      </div>
    </div>

    <a-table
    @resizeColumn="handleResizeColumn"
      :columns="columns"
      :data-source="dataSource"
      :expandable="expandableSettings"
      :custom-row="onRowClick"
      @expand="onExpand"
      rowKey="key"
      :pagination="false"
      class="excel-table overflow-hidden border border-slate-200 rounded"
      bordered
    >

  <template #expandIcon="{ expanded, expandable, record, onExpand }">
    <div class="flex items-center justify-center">
    <template v-if="expandable && record.key !== '1'">
      <span
        class="hierarchical-expand-icon"
        :class="{ 'is-expanded': expanded }"
        @click="e => onExpand(record, e)"
      >
        <transition name="icon-rotate" mode="out-in">
          <PlusOutlined v-if="!expanded" key="plus" />
          <MinusOutlined v-else key="minus" />
        </transition>
      </span>
    </template>
    <template v-else>
      <span class="inline-block w-5"></span>
    </template>
    </div>
  </template>

     <template #bodyCell="{ text, record, column }">
      <div
        v-if="column.dataIndex"
        class="cell-wrapper"
        :class="getCellClass('main', record.key, column.dataIndex as string)"
        @mousedown="startSelect('main', record.key, column.dataIndex as string)"
        @mouseenter="moveSelect('main', record.key, column.dataIndex as string)"
      >
        <EllipsisCell :text="text" />
      </div>
    </template>

      <template #expandedRowRender="{ record: mainRecord }">
        <a-spin :spinning="mainRecord.loading">
          <div class="p-4 bg-slate-50 border-y border-slate-200">
            <h4 class="text-xs font-bold text-slate-500 mb-2">DETAILS (Table ID: {{ mainRecord.key }})</h4>
            <a-table
              v-if="mainRecord.details"
              :columns="detailColumns"
              :data-source="mainRecord.details"
              :pagination="false"
              rowKey="id"
              size="small"
              bordered
            >
              <template #bodyCell="{ text, record, column }">
                <div
                  v-if="column.dataIndex"
                  class="cell-wrapper"
                  :class="getCellClass(mainRecord.key, String(record.id), column.dataIndex as string)"
                  @mousedown="startSelect(mainRecord.key, String(record.id), column.dataIndex as string)"
                  @mouseenter="moveSelect(mainRecord.key, String(record.id), column.dataIndex as string)"
                >
                  <EllipsisCell :text="text" />
                </div>
              </template>
            </a-table>
          </div>
        </a-spin>
      </template>
    </a-table>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { message } from 'ant-design-vue'

import type { TableColumnsType } from 'ant-design-vue';
import EllipsisCell from './EllipsisCell.vue'

import { 
  PlusSquareOutlined, 
  MinusSquareOutlined,
  PlusOutlined, 
  MinusOutlined,
  DeleteOutlined 
} from '@ant-design/icons-vue'

/** 타입 정의 */
interface DetailRow { id: number; item: string; qty: number }
interface TableRow {
  key: string; name: string; age: number; address: string; description: string; url: string;
  details?: DetailRow[];
  loading?: boolean; loaded?: boolean;
}

function handleResizeColumn(w: any, col: any) {
  col.width = w;
}

type ColumnKey = keyof TableRow
type DetailColumnKey = keyof DetailRow

/** 데이터 */
const dataSource = ref<TableRow[]>([
  { key: '1', name: 'John', age: 28, address: 'Seoul', description: 'SoftwareEngineerEngineerEngineer', url: 'https://example.com/example.com/example.com/john' },
  { key: '2', name: 'Jane', age: 32, address: 'Busan', description: 'Product Manager', url: 'https://example.com/jane' },
])

const columns = ref<TableColumnsType>([
  { title: 'Name', dataIndex: 'name', resizable: true, width: 150, },
  { title: 'Age', dataIndex: 'age', resizable: true, width: 100 },
  { title: 'Address', dataIndex: 'address', resizable: true, width: 200 },
  { title: 'Description', dataIndex: 'description', resizable: true, width: 200, ellipsis: true },
  { title: 'URL', dataIndex: 'url', resizable: true, width: 200, ellipsis: true },
]);

const detailColumns: { title: string; dataIndex: DetailColumnKey }[] = [
  { title: 'Item', dataIndex: 'item' },
  { title: 'Qty', dataIndex: 'qty' },
]

/** rowKey 안전 처리 */
const getRowKey = (row: any) => ('key' in row ? row.key : String(row.id))

/** 행 선택 */
const activeRowKey = ref<string | null>(null)

const addRow = () => {
  const newKey = Date.now().toString()
  dataSource.value.unshift({
    key: newKey,
    name: 'New User',
    age: 20,
    address: 'New City',
    description: 'New Description',
    url: 'https://example.com/new-user',
  })
  activeRowKey.value = newKey
  message.success('새로운 행이 추가되었습니다.')
}

const removeRow = () => {
  if (!activeRowKey.value) return
  dataSource.value = dataSource.value.filter(r => r.key !== activeRowKey.value)
  activeRowKey.value = null
  message.info('선택한 행이 삭제되었습니다.')
}

const onRowClick = (record: TableRow) => ({
  onClick: () => { activeRowKey.value = record.key }
})

/** 선택 로직 */
const isSelecting = ref(false)
const activeTableId = ref<string | null>(null)
const startCell = ref<{ row: string; col: string } | null>(null)
const endCell = ref<{ row: string; col: string } | null>(null)

const startSelect = (tableId: string, row: string, col: string) => {
  isSelecting.value = true
  activeTableId.value = tableId
  startCell.value = { row, col }
  endCell.value = { row, col }
}

const moveSelect = (tableId: string, row: string, col: string) => {
  if (isSelecting.value && activeTableId.value === tableId) {
    endCell.value = { row, col }
  }
}

const stopSelect = () => { isSelecting.value = false }

onMounted(() => {
  window.addEventListener('mouseup', stopSelect)
  window.addEventListener('keydown', handleCopy)
})

onUnmounted(() => {
  window.removeEventListener('mouseup', stopSelect)
  window.removeEventListener('keydown', handleCopy)
})

/** 셀 선택 스타일 */
const getCellClass = (tableId: string, rowKey: string, colKey: string) => {
  if (!startCell.value || !endCell.value || activeTableId.value !== tableId) return {}

  let targetData: any[] = []
  let targetCols: any[] = []

  if (tableId === 'main') {
    targetData = dataSource.value
    targetCols = columns.value
  } else {
    const parent = dataSource.value.find(r => r.key === tableId)
    targetData = parent?.details || []
    targetCols = detailColumns
  }

  const rowIdxMap = new Map(targetData.map((r, i) => [getRowKey(r), i]))
  const colIdxMap = new Map(targetCols.map((c, i) => [c.dataIndex, i]))

  const r1 = rowIdxMap.get(startCell.value.row)
  const r2 = rowIdxMap.get(endCell.value.row)
  const c1 = colIdxMap.get(startCell.value.col)
  const c2 = colIdxMap.get(endCell.value.col)
  const currR = rowIdxMap.get(rowKey)
  const currC = colIdxMap.get(colKey)

  if ([r1, r2, c1, c2, currR, currC].some(v => v === undefined)) return {}

  const isSelected =
    currR! >= Math.min(r1!, r2!) &&
    currR! <= Math.max(r1!, r2!) &&
    currC! >= Math.min(c1!, c2!) &&
    currC! <= Math.max(c1!, c2!)

  return { 'selected-cell': isSelected }
}

/** 복사 */
const handleCopy = async (e: KeyboardEvent) => {
  if (!(e.ctrlKey || e.metaKey) || e.key !== 'c') return
  if (!activeTableId.value || !startCell.value || !endCell.value) return

  e.preventDefault()

  let targetData: any[] = []
  let targetCols: any[] = []

  if (activeTableId.value === 'main') {
    targetData = dataSource.value
    targetCols = columns.value
  } else {
    const parent = dataSource.value.find(r => r.key === activeTableId.value)
    targetData = parent?.details || []
    targetCols = detailColumns
  }

  const rowIdxMap = new Map(targetData.map((r, i) => [getRowKey(r), i]))
  const colIdxMap = new Map(targetCols.map((c, i) => [c.dataIndex, i]))

  const r1 = rowIdxMap.get(startCell.value.row)!
  const r2 = rowIdxMap.get(endCell.value.row)!
  const c1 = colIdxMap.get(startCell.value.col)!
  const c2 = colIdxMap.get(endCell.value.col)!

  const rMin = Math.min(r1, r2)
  const rMax = Math.max(r1, r2)
  const cMin = Math.min(c1, c2)
  const cMax = Math.max(c1, c2)

  let text = ''
  for (let r = rMin; r <= rMax; r++) {
    const row = []
    for (let c = cMin; c <= cMax; c++) {
      row.push(targetData[r][targetCols[c].dataIndex] ?? '')
    }
    text += row.join('\t') + (r === rMax ? '' : '\n')
  }

  try {
    await navigator.clipboard.writeText(text)
    message.success('복사 완료')
  } catch {
    message.error('복사 실패 (권한 문제)')
  }
}

/** expandable 수정 (버그 fix) */
const expandableSettings = {}

const onExpand = async (expanded: boolean, record: TableRow) => {
  if (expanded && !record.loaded) {
    record.loading = true
    setTimeout(() => {
      record.details = [
        { id: 101, item: 'Item A', qty: 1 },
        { id: 102, item: 'Item B', qty: 3 },
      ]
      record.loaded = true
      record.loading = false
    }, 600)
  }
}
</script>

<style scoped lang="scss">

.excel-table :deep(.ant-table-tbody > tr > td.ant-table-cell:not(.ant-table-row-expand-icon-cell)) {
  padding: 0 !important;
}

.excel-table :deep(.ant-table-cell) {
  position: relative;
  overflow: hidden;
  // padding: 8px 16px !important;
  // padding: 0px !important;
}


.cell-wrapper {
  //  cursor: cell;
  // user-select: none;
  // display: flex;
  // align-items: center;
 cursor: cell;
  user-select: none;
  display: flex;
  align-items: center;
  // overflow: hidden; // ⭐ 중요


  
  &.selected-cell {
    background-color: rgba(24, 144, 255, 0.15) !important;
    box-shadow: inset 0 0 0 1px #1890ff;
    z-index: 1;
    position: relative;
  }
}


////////
/// /* 아이콘 컨테이너 */
.hierarchical-expand-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 17px;
  cursor: pointer;
  color: #8c8c8c;
  transition: color 0.3s;
  width: 20px;
  height: 20px;

  &:hover {
    color: #1890ff;
  }

  &.is-expanded {
    // color: #1890ff; // 마이너스일 때도 블루 유지 (취향에 따라 변경)
  }
}

/* 아이콘 교체 애니메이션 (Icon Rotate Transition) */
.icon-rotate-enter-active,
.icon-rotate-leave-active {
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.icon-rotate-enter-from {
  opacity: 0;
  transform: rotate(-90deg) scale(0.5);
}

.icon-rotate-leave-to {
  opacity: 0;
  transform: rotate(90deg) scale(0.5);
}
</style>
