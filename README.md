<template>
  <div class="flex flex-col gap-2">
    <a-input
      v-model:value="searchText"
      placeholder="file_name 검색"
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
      @row-clicked="onRowClicked"
    />

    <div class="text-xs text-slate-500">{{ selected.length }}개 선택됨</div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, ref, watch } from "vue";
import { AgGridVue } from "ag-grid-vue3";
import type {
  ColDef,
  GetRowIdParams,
  GridApi,
  GridReadyEvent,
  RowClickedEvent,
  RowSelectionOptions,
  ValueFormatterParams,
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
  // 지금 화면에 보이는, 체크된 행들의 preset만 중복 없이 뽑아서 전달 (다른 preset에서 선택된 파일은 반영 안 됨).
  (e: "selected-presets-change", value: (string | null)[]): void;
}>();

const searchText = defineModel<string>("searchText", { default: "" });

// preset/검색어는 서버에 넘겨 이미 필터링된 결과를 그대로 보여줌 (클라이언트에서 다시 거르지 않음).
const rowData = computed(() => props.fileRecords);

const overlayNoRowsTemplate = computed(() =>
  props.hasCriteria
    ? "검색 조건에 맞는 file_name이 없습니다"
    : "검색어를 입력하거나 Preset을 선택하면 목록을 불러옵니다"
);

function formatNullable(params: ValueFormatterParams<FileRecord>): string {
  return params.value == null ? "-" : String(params.value);
}

function formatDate(params: ValueFormatterParams<FileRecord>): string {
  return params.value ? new Date(params.value).toLocaleDateString() : "-";
}

// null 가능 필드 공통 컬럼 정의 (field 외엔 동일한 패턴이라 팩토리로 정리).
function nullableColumn(
  field: keyof FileRecord,
  headerName: string,
  minWidth: number
): ColDef<FileRecord> {
  return { field, headerName, flex: 1, minWidth, valueFormatter: formatNullable };
}

const columnDefs: ColDef<FileRecord>[] = [
  { field: "file_name", headerName: "File Name", flex: 2, minWidth: 180 },
  nullableColumn("preset", "Preset", 90),
  nullableColumn("Edge_Top(nm)", "Edge Top (nm)", 110),
  nullableColumn("Edge_Left(nm)", "Edge Left (nm)", 110),
  nullableColumn("Edge_Right(nm)", "Edge Right (nm)", 110),
  nullableColumn("Edge_Bottom(nm)", "Edge Bottom (nm)", 120),
  { field: "createdAt", headerName: "Created At", flex: 1, minWidth: 110, valueFormatter: formatDate },
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

  event.node.setSelected(!event.node.isSelected());
}

// 선택은 preset/검색을 넘나들어도 유지되는 전역 목록 — 화면 밖(다른 조건) 선택은 두고 보이는 행만 반영.
function onSelectionChanged() {
  if (!gridApi.value) return;

  const visibleFileNames = new Set(props.fileRecords.map((r) => r.file_name));
  const selectedElsewhere = props.selected.filter(
    (f) => !visibleFileNames.has(f)
  );
  const selectedRows = gridApi.value.getSelectedRows();
  const selectedInView = selectedRows.map((r) => r.file_name);

  emit("update:selected", [...selectedElsewhere, ...selectedInView]);
  emit("selected-presets-change", [...new Set(selectedRows.map((r) => r.preset))]);
}

// 부모가 selected를 바꾸면(세트 추가 후 초기화 등) 그리드 체크 상태를 맞춤.
function syncSelectionToGrid() {
  if (!gridApi.value) return;

  const selectedSet = new Set(props.selected);
  gridApi.value.forEachNode((node) => {
    const isSelected = !!node.data && selectedSet.has(node.data.file_name);
    if (node.isSelected() !== isSelected) node.setSelected(isSelected, false);
  });
}

// selected뿐 아니라 fileRecords가 바뀔 때도 재동기화 — rowData 갱신 후 체크해야 해서 nextTick으로 순서 보장.
watch(
  [() => props.selected, () => props.fileRecords],
  () => void nextTick(syncSelectionToGrid)
);
</script>
