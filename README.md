<template>
  <div class="flex flex-col gap-2">
    <a-input
      v-model:value="searchText"
      placeholder="file_name 검색 (예: 001_002 → IN001 또는 OUT002)"
      allow-clear
      size="small"
    />

    <AgGridVue
      class="rounded border border-slate-300 [&_.ag-row]:cursor-pointer"
      style="
        height: 280px;
        width: 100%;
        --ag-font-size: 12px;
        --ag-header-height: 28px;
        --ag-row-height: 28px;
        --ag-cell-horizontal-padding: 10px;
      "
      :row-data="rowData"
      :column-defs="columnDefs"
      :row-selection="rowSelection"
      :get-row-id="getRowId"
      :loading="loading"
      :overlay-no-rows-template="overlayNoRowsTemplate"
      :locale-text="{ loadingOoo: '불러오는 중…' }"
      @grid-ready="onGridReady"
      @selection-changed="onSelectionChanged"
      @row-data-updated="syncSelectionToGrid"
      @row-clicked="onRowClicked"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { AgGridVue } from "ag-grid-vue3";
import type {
  ColDef,
  GetRowIdParams,
  GridApi,
  GridReadyEvent,
  RowClickedEvent,
  RowSelectionOptions,
  SelectionChangedEvent,
} from "ag-grid-community";
import { Input as AInput } from "ant-design-vue";
import type { FileRecord } from "../types/query";

const props = defineProps<{
  fileRecords: FileRecord[];
  selected: string[];
  loading?: boolean;
  hasCriteria?: boolean;
}>();

const emit = defineEmits<{
  (e: "update:selected", value: string[]): void;
}>();

const searchText = defineModel<string>("searchText", { default: "" });

// preset/검색어는 서버에 넘겨 이미 필터링된 결과를 그대로 보여줌 (클라이언트에서 다시 거르지 않음).
const rowData = computed(() => props.fileRecords);

const overlayNoRowsTemplate = computed(() =>
  props.hasCriteria
    ? "검색 조건에 맞는 file_name이 없습니다"
    : "검색어를 입력하거나 Preset을 선택하면 목록을 불러옵니다"
);

const columnDefs: ColDef<FileRecord>[] = [
  { field: "file_name", headerName: "File Name", flex: 1, minWidth: 180 },
];
const rowSelection: RowSelectionOptions = {
  mode: "multiRow",
  headerCheckbox: true,
  selectAll: "filtered",
};

const gridApi = ref<GridApi<FileRecord> | null>(null);

function getRowId(params: GetRowIdParams<FileRecord>): string {
  return params.data.file_name;
}

function onGridReady(event: GridReadyEvent<FileRecord>) {
  gridApi.value = event.api;
  syncSelectionToGrid();
}

// 체크박스 자체 클릭은 ag-grid 기본 동작에 맡기고, row의 나머지 영역 클릭 시 그 row만 토글.
function onRowClicked(event: RowClickedEvent<FileRecord>) {
  const target = event.event?.target as HTMLElement | null;
  if (target?.closest(".ag-selection-checkbox") || !event.node.data) return;

  event.node.setSelected(!event.node.isSelected(), false, "rowClicked");
}

// 사용자가 직접 바꾼 선택만 부모에 올림. 부모의 selected가 단일 진실 공급원이고 grid 체크 상태는 그 투영일 뿐이라,
// 프로그램적 변경(api: 동기화, rowDataChanged: 행 교체로 인한 선택 해제 등)은 되돌려 보내지 않음 -> 타이밍에 의존하지 않음.
const USER_SELECTION_SOURCES = new Set<string>([
  "checkboxSelected",
  "rowClicked",
  "spaceKey",
  "uiSelectAll",
  "uiSelectFiltered",
  "uiSelectAllCurrentPage",
]);

// 선택은 preset/검색을 넘나들어도 유지되는 전역 목록 — 화면 밖(다른 조건) 선택은 두고 보이는 행만 반영.
function onSelectionChanged(event: SelectionChangedEvent<FileRecord>) {
  if (!gridApi.value || !USER_SELECTION_SOURCES.has(event.source)) return;

  const visibleFileNames = new Set(props.fileRecords.map((r) => r.file_name));
  const selectedElsewhere = props.selected.filter(
    (f) => !visibleFileNames.has(f)
  );
  const selectedInView = gridApi.value
    .getSelectedRows()
    .map((r) => r.file_name);

  emit("update:selected", [...selectedElsewhere, ...selectedInView]);
}

// 부모 selected -> grid 체크 상태 반영. 멱등이라 여러 번 불려도 안전함.
// 호출 시점: selected 변경 시 + grid가 새 행을 실제로 반영했을 때(row-data-updated) — 어느 쪽이 먼저 와도 결과가 같음.
function syncSelectionToGrid() {
  if (!gridApi.value) return;

  const selectedSet = new Set(props.selected);
  gridApi.value.forEachNode((node) => {
    const isSelected = !!node.data && selectedSet.has(node.data.file_name);
    if (node.isSelected() !== isSelected) node.setSelected(isSelected, false);
  });
}

watch(() => props.selected, syncSelectionToGrid);
</script>
