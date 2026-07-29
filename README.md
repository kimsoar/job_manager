function isEmptyRow(
  row: MarkdownTableRow,
): boolean {
  return row.cells.every(
    (cell) =>
      !cell.value?.trim(),
  )
}

const dataRows = computed<MarkdownTableRow[]>(
  () => {
    return table.value.rows.filter(
      (row) => !isEmptyRow(row),
    )
  },
)


------------------------------------------------------------------------------------




<script setup lang="ts">
import { reactive } from "vue";
import {
  SearchOutlined,
  PictureOutlined,
  UnorderedListOutlined,
} from "@ant-design/icons-vue";

interface SearchForm {
  photoOnly: boolean;
  stepFrom?: string;
  stepTo?: string;
  lotId: string;
}

const form = reactive<SearchForm>({
  photoOnly: false,
  stepFrom: undefined,
  stepTo: undefined,
  lotId: "",
});

const stepOptions = [
  { label: "STEP 01", value: "STEP01" },
  { label: "STEP 02", value: "STEP02" },
  { label: "STEP 03", value: "STEP03" },
  { label: "STEP 04", value: "STEP04" },
  { label: "STEP 05", value: "STEP05" },
];

const handleSearch = () => {
  console.log({
    photoOnly: form.photoOnly,
    stepFrom: form.stepFrom,
    stepTo: form.stepTo,
    lotId: form.lotId,
  });
};
</script>

<template>
  <div class="w-full rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
    <!-- 1. 최상단: 핵심 기능 분기 (Photo Only Mode) -->
    <div
      class="mb-3 flex items-center justify-between rounded-lg bg-slate-50 px-3 py-1.5 border border-slate-100"
    >
      <div class="flex items-center gap-2">
        <span class="text-xs font-bold text-slate-600">조회 모드:</span>
        <a-checkbox
          v-model:checked="form.photoOnly"
          class="select-none text-xs font-semibold text-blue-600"
        >
          <span class="inline-flex items-center gap-1">
            <PictureOutlined v-if="form.photoOnly" class="text-blue-500" />
            <UnorderedListOutlined v-else class="text-gray-400" />
            Photo Only 모드 적용
          </span>
        </a-checkbox>
      </div>

      <span class="text-[11px] text-gray-400">
        {{
          form.photoOnly
            ? "이미지 위주 결과 출력"
            : "전체 데이터 및 테이블 출력"
        }}
      </span>
    </div>

    <!-- 2. 주 입력 영역 (Step, Lot ID) + 조회 버튼 -->
    <div class="grid grid-cols-[1fr_auto] items-stretch gap-x-3">
      <!-- [왼쪽] Step & Lot ID 입력 폼 (2줄) -->
      <div class="space-y-2">
        <!-- Step 선택 -->
        <div class="flex items-center gap-2">
          <label class="w-14 shrink-0 text-xs font-semibold text-gray-600">
            Step
          </label>
          <div class="flex flex-1 items-center gap-1.5">
            <a-select
              v-model:value="form.stepFrom"
              :options="stepOptions"
              placeholder="시작 Step"
              allow-clear
              class="flex-1"
            />
            <span class="shrink-0 text-xs text-gray-400">~</span>
            <a-select
              v-model:value="form.stepTo"
              :options="stepOptions"
              placeholder="종료 Step"
              allow-clear
              class="flex-1"
            />
          </div>
        </div>

        <!-- Lot ID 입력 -->
        <div class="flex items-center gap-2">
          <label class="w-14 shrink-0 text-xs font-semibold text-gray-600">
            Lot ID
          </label>
          <a-input
            v-model:value="form.lotId"
            placeholder="Lot ID 입력 (Enter로 조회)"
            allow-clear
            class="flex-1"
            @press-enter="handleSearch"
          />
        </div>
      </div>

      <!-- [오른쪽] Step + Lot ID 2줄 높이에 딱 떨어지는 조회 버튼 -->
      <a-button
        type="primary"
        class="flex h-auto! min-w-[80px] flex-col items-center justify-center gap-1 px-4 text-xs font-bold shadow-sm"
        @click="handleSearch"
      >
        <SearchOutlined class="text-base" />
        <span>조회</span>
      </a-button>
    </div>
  </div>
</template>
