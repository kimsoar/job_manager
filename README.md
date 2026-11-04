import { createApp } from "vue";
import {
  Button,
  Checkbox,
  ConfigProvider,
  Empty,
  Form,
  Input,
  Modal,
  Radio,
  Select,
  Spin,
  Tooltip,
} from "ant-design-vue";
import "vue-virtual-scroller/dist/vue-virtual-scroller.css";
import "./style.css";
import App from "./App.vue";

const app = createApp(App);
[
  Button,
  Checkbox,
  ConfigProvider,
  Empty,
  Form,
  Input,
  Modal,
  Radio,
  Select,
  Spin,
  Tooltip,
].forEach((component) => app.use(component));
app.mount("#app");








<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { RecycleScroller } from "vue-virtual-scroller";
import { Empty } from "ant-design-vue";
import {
  HistoryOutlined,
  SearchOutlined,
  UnorderedListOutlined,
} from "@ant-design/icons-vue";
import WorkspacePane from "./WorkspacePane.vue";
import { REVIEW_LABEL } from "../constants/dsa";
import { shortDateTime } from "../utils/date";
import { abbreviateDivision } from "../utils/division";
import { getStatus, recordKey } from "../utils/records";
import type { DsaSummary, MoveDirection, StatusFilter } from "../types/dsa";

const ITEM_HEIGHT = 56;
const STATUS_OPTIONS: { value: StatusFilter; label: string }[] = [
  { value: "REVIEW", label: REVIEW_LABEL },
  { value: "COMPLETED", label: "완료" },
  { value: "ALL", label: "전체" },
];

const props = defineProps<{
  records: DsaSummary[];
  totalCount: number;
  statusCounts: Record<StatusFilter, number>;
  searching: boolean;
  searchFailed: boolean;
  selectedKey: string | null;
}>();

const emit = defineEmits<{
  select: [key: string];
  move: [direction: MoveDirection];
  "retry-search": [];
  "show-all": [];
  "show-history": [];
}>();

const statusFilter = defineModel<StatusFilter>("statusFilter", {
  required: true,
});

const keyword = defineModel<string>("keyword", { required: true });

type VirtualRecord = { key: string; record: DsaSummary };

const listElement = ref<any>(null);

const virtualRecords = computed<VirtualRecord[]>(() =>
  props.records.map((record) => ({
    key: recordKey(record),
    record,
  }))
);

watch(
  () => [props.selectedKey, props.records],
  () => {
    const index = props.records.findIndex(
      (record) => recordKey(record) === props.selectedKey
    );

    if (index >= 0) listElement.value?.scrollToItem(index);
  },
  { flush: "post" }
);

const hiddenCount = computed(() => props.totalCount - props.records.length);

// Focus stays on the list because the virtualizer can unmount a focused row
function selectItem(key: string) {
  emit("select", key);
  listElement.value?.$el.focus({ preventScroll: true });
}
</script>

<template>
  <WorkspacePane title="Results" :icon="UnorderedListOutlined">
    <template #actions>
      <a-tooltip
        placement="bottomRight"
        :title="`표시 ${records.length.toLocaleString()}건 / 검색 ${totalCount.toLocaleString()}건`"
      >
        <span class="cursor-help text-xs text-slate-500 tabular-nums">
          <b class="font-semibold text-slate-900">
            {{ records.length.toLocaleString() }}
          </b>
          / {{ totalCount.toLocaleString() }}
        </span>
      </a-tooltip>
    </template>

    <div class="flex flex-col gap-2 border-b border-slate-100 px-4 py-3">
      <a-radio-group
        v-model:value="statusFilter"
        button-style="solid"
        class="flex! w-full"
      >
        <a-radio-button
          v-for="option in STATUS_OPTIONS"
          :key="option.value"
          :value="option.value"
          class="flex-1 text-center text-xs! leading-[22px]!"
        >
          {{ option.label }}
          <span class="ml-0.5 tabular-nums opacity-75">
            {{ statusCounts[option.value].toLocaleString() }}
          </span>
        </a-radio-button>
      </a-radio-group>

      <a-input
        v-model:value="keyword"
        allow-clear
        placeholder="EQP ID, Wafer, Category 검색"
        aria-label="검색 결과 필터"
        @keydown.esc="keyword = ''"
      >
        <template #prefix>
          <SearchOutlined class="text-slate-400" />
        </template>
      </a-input>
    </div>

    <div
      class="relative h-64 max-h-64 min-h-0 overflow-hidden xl:h-auto xl:max-h-none xl:flex-1"
    >
      <div
        v-if="searching && !records.length"
        class="grid h-40 place-items-center"
      >
        <a-spin />
      </div>

      <a-empty
        v-else-if="searchFailed && !totalCount"
        class="py-6"
        :image="Empty.PRESENTED_IMAGE_SIMPLE"
        description="검사 데이터를 불러오지 못했습니다."
      >
        <a-button @click="emit('retry-search')">
          다시 시도
        </a-button>
      </a-empty>

      <a-empty
        v-else-if="!records.length"
        class="py-6"
        :image="Empty.PRESENTED_IMAGE_SIMPLE"
        :description="
          hiddenCount
            ? `필터에 가려진 검사 데이터 ${hiddenCount.toLocaleString()}건이 있습니다.`
            : '표시할 검사 데이터가 없습니다.'
        "
      >
        <a-button v-if="hiddenCount" @click="emit('show-all')">
          전체 보기
        </a-button>
      </a-empty>

      <RecycleScroller
        v-else
        ref="listElement"
        :items="virtualRecords"
        :item-size="ITEM_HEIGHT"
        key-field="key"
        :buffer="200"
        tabindex="0"
        aria-label="검색 결과 목록"
        class="wafer-recycle-scroller group relative h-full min-h-0 outline-none [scrollbar-width:thin]"
        @keydown.up.prevent="emit('move', -1)"
        @keydown.down.prevent="emit('move', 1)"
      >
        <template #default="{ item }: { item: VirtualRecord }">
          <button
            type="button"
            class="flex h-14 w-full cursor-pointer flex-col justify-center gap-1 border-b border-slate-100 px-4 text-left"
            :class="
              item.key === selectedKey
                ? 'bg-blue-50 shadow-[inset_2px_0_0_var(--color-blue-600)] group-focus:shadow-[inset_3px_0_0_var(--color-blue-600)]'
                : 'hover:bg-slate-50'
            "
            :aria-current="item.key === selectedKey"
            tabindex="-1"
            @click="selectItem(item.key)"
          >
            <span class="flex items-center justify-between gap-2">
              <span
                class="truncate font-mono text-xs font-medium text-slate-900"
                :title="`${item.record.eqpid} · W${item.record.wafer} · ${item.record.division}`"
              >
                {{ item.record.eqpid }}

                <span class="font-sans text-slate-500">
                  · W{{ item.record.wafer }}
                </span>

                <span
                  class="ml-1.5 rounded border border-slate-200 bg-slate-50 px-1 font-sans text-[10px] leading-4 font-medium text-slate-600"
                >
                  {{ abbreviateDivision(item.record.division) }}
                </span>
              </span>

              <span
                class="max-w-32 shrink-0 truncate rounded border px-1.5 text-[11px] leading-[18px]"
                :class="
                  getStatus(item.record) === 'COMPLETED'
                    ? 'border-emerald-200 bg-emerald-50 text-emerald-700'
                    : 'border-amber-200 bg-amber-50 text-amber-700'
                "
                :title="item.record.pc_category ?? undefined"
              >
                {{ item.record.pc_category ?? REVIEW_LABEL }}
              </span>
            </span>

            <span class="truncate text-[11px] text-slate-600">
              {{ item.record.equ_category }} ·
              {{ shortDateTime(item.record.created_at) }} · 불량
              <span class="tabular-nums">
                {{ item.record.detection_ctn }}
              </span>

              <template
                v-if="
                  item.record.pc_category === null && item.record.pred_label
                "
              >
                ·
                <span class="text-violet-700">
                  예측 {{ item.record.pred_label }}
                </span>
              </template>
            </span>
          </button>
        </template>
      </RecycleScroller>
    </div>

    <div class="shrink-0 border-t border-slate-100 px-4 py-2.5">
      <a-button
        block
        :disabled="searching || !totalCount"
        @click="emit('show-history')"
      >
        <template #icon>
          <HistoryOutlined />
        </template>
        판정 이력
      </a-button>
    </div>
  </WorkspacePane>
</template>