// composables/useEllipsis.ts
import { ref, onMounted, onBeforeUnmount, nextTick, type Ref } from 'vue'

export function useEllipsis(target: Ref<HTMLElement | null>) {
  const isEllipsis = ref(false)

  const check = () => {
    if (!target.value) return
    const el = target.value

    isEllipsis.value = el.scrollWidth > el.clientWidth
  }

  let observer: ResizeObserver

  onMounted(async () => {
    await nextTick()
    check()

    if (target.value) {
      observer = new ResizeObserver(check)
      observer.observe(target.value)
    }
  })

  onBeforeUnmount(() => {
    observer?.disconnect()
  })

  return { isEllipsis, check }
}



<!-- components/EllipsisCell.vue -->
<template>
  <a-tooltip v-if="isEllipsis" :title="text">
    <div ref="el" class="truncate">
      {{ text }}
    </div>
  </a-tooltip>

  <div v-else ref="el" class="truncate">
    {{ text }}
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useEllipsis } from '@/composables/useEllipsis'

const props = defineProps<{
  text: string
}>()

const el = ref<HTMLElement | null>(null)
const { isEllipsis } = useEllipsis(el)
</script>

truncate = overflow-hidden text-ellipsis whitespace-nowrap

<a-table :columns="columns" :data-source="data">
  <template #bodyCell="{ column, record }">
    <template v-if="column.dataIndex === 'name'">
      <EllipsisCell :text="record.name" />
    </template>
  </template>
</a-table>




<template>
  <a-button @click="changeFruitFilter">Change Fruit Filter</a-button>
  <a-button @click="changeNameFilter">Change Name Filter</a-button>

  <a-table
    :columns="columns"
    :data-source="data"
    @resizeColumn="handleResizeColumn"
  >
    <!-- Header -->
    <template #headerCell="{ column }">
      <template v-if="column.key === 'name'">
        <span>
          <smile-outlined />
          Name
        </span>
      </template>
    </template>

    <!-- Body -->
    <template #bodyCell="{ column, record }">
      <template v-if="column.key === 'name'">
        <a>{{ record.name }}</a>
      </template>

      <template v-else-if="column.key === 'tags'">
        <span>
          <a-tag
            v-for="tag in record.tags"
            :key="tag"
            :color="tag === 'loser' ? 'volcano' : tag.length > 5 ? 'geekblue' : 'green'"
          >
            {{ tag.toUpperCase() }}
          </a-tag>
        </span>
      </template>

      <template v-else-if="column.key === 'action'">
        <span>
          <a>Invite 一 {{ record.name }}</a>
          <a-divider type="vertical" />
          <a>Delete</a>
          <a-divider type="vertical" />
          <a class="ant-dropdown-link">
            More actions
            <down-outlined />
          </a>
        </span>
      </template>
    </template>
  </a-table>
</template>

<script lang="ts" setup>
import { ref, computed, watch } from 'vue';
import { SmileOutlined, DownOutlined } from '@ant-design/icons-vue';
import type { TableColumnsType } from 'ant-design-vue';

/* =========================
 * 데이터
 * ========================= */
const data = [
  {
    key: '1',
    name: 'John Brown',
    age: 32,
    address: 'New York No. 1 Lake Park',
    tags: ['nice', 'developer'],
    fruit: 'Apple',
  },
  {
    key: '2',
    name: 'Jim Green',
    age: 42,
    address: 'London No. 1 Lake Park',
    tags: ['loser'],
    fruit: 'Banana',
  },
  {
    key: '3',
    name: 'Joe Black',
    age: 32,
    address: 'Sidney No. 1 Lake Park',
    tags: ['cool', 'teacher'],
    fruit: 'Cherry',
  },
];

/* =========================
 * Filter 상태
 * ========================= */
const fruitData = ref<string[]>([]);
const nameData = ref<string[]>([]);

const fruitFilter = computed(() =>
  fruitData.value.map(fruit => ({ text: fruit, value: fruit }))
);

const nameFilter = computed(() =>
  nameData.value.map(name => ({ text: name, value: name }))
);

/* =========================
 * Column 정의 (정적)
 * ========================= */

type ColumnItem = {
  key?: string;
  dataIndex?: string;
  title?: string;
  width?: number;
  minWidth?: number;
  maxWidth?: number;
  resizable?: boolean;
  filterSearch?: boolean;
  onFilter?: (value: any, record: any) => boolean;
  filters?: { text: string; value: string }[];
};

const columnsData = ref<ColumnItem[]>([
  {
    dataIndex: 'name',
    key: 'name',
    resizable: true,
    width: 150,
    filterSearch: true,
    onFilter: (value, record: any) => record.name === value,
  },
  {
    title: 'Age',
    dataIndex: 'age',
    key: 'age',
    resizable: true,
    width: 100,
    minWidth: 100,
    maxWidth: 200,
  },
  {
    title: 'Address',
    dataIndex: 'address',
    key: 'address',
  },
  {
    title: 'Fruit',
    dataIndex: 'fruit',
    key: 'fruit',
    filterSearch: true,
    onFilter: (value, record: any) => record.fruit === value,
  },
  {
    title: 'Tags',
    key: 'tags',
    dataIndex: 'tags',
  },
  {
    title: 'Action',
    key: 'action',
  },
]);

/* =========================
 * 동적 Filter 매핑 (확장 가능 구조)
 * ========================= */
const filterMap = {
  fruit: fruitFilter,
  name: nameFilter,
};

/* =========================
 * Columns (최종)
 * ========================= */
const columns = ref<TableColumnsType>([]);

const buildColumns = () => {
  const cols = columnsData.value.map(col => {
    const c = { ...col };

    const key = c.key as keyof typeof filterMap;
    if (filterMap[key]) {
      c.filters = filterMap[key].value;
    }

    return c;
  });

  columns.value = cols as TableColumnsType;
};

/* =========================
 * 반응성 연결
 * ========================= */
watch([fruitFilter, nameFilter], buildColumns, { immediate: true });

/* =========================
 * 이벤트
 * ========================= */
function handleResizeColumn(w: number, col: any) {
  col.width = w;
}

const changeFruitFilter = () => {
  fruitData.value = ['Apple', 'Banana', 'Cherry'];
};

const changeNameFilter = () => {
  nameData.value = ['John Brown', 'Jim Green', 'Joe Black'];
};
</script>
