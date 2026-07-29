<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref } from "vue";

import { message } from "ant-design-vue";

import {
  parseChamberInfo,
  parseMarkdownTable,
  parseWaferHeaders,
  type MarkdownTable,
  type MarkdownTableRow,
} from "./markdownTable";

interface Props {
  modelValue: string;
}

const props = defineProps<Props>();

/**
 * =========================================================
 * TABLE
 * =========================================================
 */

const tableContainer = ref<HTMLElement | null>(null);

const table = computed<MarkdownTable>(() =>
  parseMarkdownTable(props.modelValue)
);

function isEmptyRow(row: MarkdownTableRow): boolean {
  return row.cells.every((cell) => !cell.value?.trim());
}

const dataRows = computed<MarkdownTableRow[]>(() => {
  return table.value.rows.filter((row) => !isEmptyRow(row));
});
/**
 * =========================================================
 * HEADER
 * =========================================================
 *
 * 예:
 *
 * RTAMM.1_g1_w1
 * RTAMM.1_g1_w2
 * RTAMM.1_g1_w3
 * CAMT.1_g1_w1
 * RTAMM.1_g2_w5
 * CAMT.1_g2_w2
 *
 * parseWaferHeaders()
 *
 * -> group
 * -> lot
 * -> wafer
 *
 * 구조로 변환
 */

const waferHeader = computed(() => parseWaferHeaders(table.value.headers));

/**
 * =========================================================
 * REMARK
 * =========================================================
 *
 * 원본:
 *
 * | step | category | ... | 비고 |
 *
 * 비고는 화면에 표시하지 않는다.
 *
 * 하지만 Chamber 정보를 읽기 위해
 * 원본 row에는 유지한다.
 */

const remarkColumnIndex = computed(() => table.value.headers.length - 1);

/**
 * =========================================================
 * CHAMBER INFO
 * =========================================================
 *
 * 예:
 *
 * chamber: group1={2,6}, group2={2}
 *
 * 현재 요구사항:
 *
 * group1 -> 무시
 * group2 -> 사용
 *
 * 따라서:
 *
 * g1 = [2, 6]
 * g2 = [2]
 */

const chamberInfo = computed(() => {
  for (const row of dataRows.value) {
    const remark = row.cells[remarkColumnIndex.value]?.value ?? "";

    if (remark.toLowerCase().includes("chamber:")) {
      return parseChamberInfo(remark);
    }
  }

  return {};
});

/**
 * =========================================================
 * STEP ROWSPAN
 * =========================================================
 *
 * 예:
 *
 * XP50000 | PPID
 *         | EQP
 *         | Chamber
 *
 * step cell:
 *
 * rowspan="3"
 */

interface RowSpanInfo {
  startRow: number;
  endRow: number;
}

const stepRowSpans = computed<RowSpanInfo[]>(() => {
  const result: RowSpanInfo[] = [];

  let rowIndex = 0;

  while (rowIndex < dataRows.value.length) {
    const step = dataRows.value[rowIndex]?.cells[0]?.value?.trim() ?? "";

    /**
     * step이 비어 있으면
     * 이전 step의 하위 row
     */
    if (!step) {
      rowIndex++;
      continue;
    }

    let endRow = rowIndex;

    while (
      endRow + 1 < dataRows.value.length &&
      !dataRows.value[endRow + 1]?.cells[0]?.value?.trim()
    ) {
      endRow++;
    }

    result.push({
      startRow: rowIndex,
      endRow,
    });

    rowIndex = endRow + 1;
  }

  return result;
});

function getRowSpan(rowIndex: number): number {
  const info = stepRowSpans.value.find((item) => item.startRow === rowIndex);

  if (!info) {
    return 1;
  }

  return info.endRow - info.startRow + 1;
}

function shouldRenderStepCell(rowIndex: number): boolean {
  const info = stepRowSpans.value.find(
    (item) => rowIndex >= item.startRow && rowIndex <= item.endRow
  );

  if (!info) {
    return true;
  }

  return info.startRow === rowIndex;
}

/**
 * =========================================================
 * CHAMBER HIGHLIGHT
 * =========================================================
 *
 * 핵심 규칙:
 *
 * chamber: group1={2,6}, group2={2}
 *
 * group1:
 *   2 -> 무시
 *   6 -> 무시
 *
 * group2:
 *   2 -> highlight
 *   6 -> 일반
 *
 * 즉 "불량(g2) Chamber"만 강조한다.
 */

function isChamberHighlighted(rowIndex: number, columnIndex: number): boolean {
  /**
   * -------------------------------------------------------
   * 1. Chamber row인지 확인
   * -------------------------------------------------------
   */

  const category = dataRows.value[rowIndex]?.cells[1]?.value
    ?.trim()
    .toLowerCase();

  if (category !== "chamber") {
    return false;
  }

  /**
   * -------------------------------------------------------
   * 2. 현재 wafer column 정보
   * -------------------------------------------------------
   */

  const column = waferHeader.value.columns.find(
    (item) => item.index === columnIndex
  );

  if (!column) {
    return false;
  }

  /**
   * -------------------------------------------------------
   * 3. g2 = 불량만 사용
   * -------------------------------------------------------
   */

  if (column.groupId.toLowerCase() !== "g2") {
    return false;
  }

  /**
   * -------------------------------------------------------
   * 4. group2 Chamber 정보
   * -------------------------------------------------------
   */

  const targetChambers = chamberInfo.value.g2;

  if (!targetChambers || targetChambers.length === 0) {
    return false;
  }

  /**
   * -------------------------------------------------------
   * 5. 현재 Chamber 값
   * -------------------------------------------------------
   */

  const value = dataRows.value[rowIndex]?.cells[columnIndex]?.value?.trim();

  if (!value) {
    return false;
  }

  const chamber = Number(value);

  if (!Number.isFinite(chamber)) {
    return false;
  }

  /**
   * -------------------------------------------------------
   * 6. group2 Chamber와 일치하면 강조
   * -------------------------------------------------------
   */

  return targetChambers.includes(chamber);
}

/**
 * =========================================================
 * CELL SELECTION
 * =========================================================
 */

interface CellPosition {
  row: number;
  col: number;
}

interface SelectionRange {
  startRow: number;
  endRow: number;
  startCol: number;
  endCol: number;
}

const selectionStart = ref<CellPosition | null>(null);

const selectionEnd = ref<CellPosition | null>(null);

const isDragging = ref(false);

/**
 * 선택 영역 정규화
 */

const normalizedSelection = computed<SelectionRange | null>(() => {
  if (!selectionStart.value || !selectionEnd.value) {
    return null;
  }

  return {
    startRow: Math.min(selectionStart.value.row, selectionEnd.value.row),

    endRow: Math.max(selectionStart.value.row, selectionEnd.value.row),

    startCol: Math.min(selectionStart.value.col, selectionEnd.value.col),

    endCol: Math.max(selectionStart.value.col, selectionEnd.value.col),
  };
});

/**
 * =========================================================
 * SELECTION START
 * =========================================================
 */

async function startSelection(row: number, col: number, event: MouseEvent) {
  event.preventDefault();

  selectionStart.value = {
    row,
    col,
  };

  selectionEnd.value = {
    row,
    col,
  };

  isDragging.value = true;

  await nextTick();

  tableContainer.value?.focus();
}

/**
 * =========================================================
 * SELECTION MOVE
 * =========================================================
 */

function moveSelection(row: number, col: number) {
  if (!isDragging.value) {
    return;
  }

  selectionEnd.value = {
    row,
    col,
  };
}

/**
 * =========================================================
 * SELECTION END
 * =========================================================
 */

function stopSelection() {
  isDragging.value = false;
}

/**
 * =========================================================
 * IS SELECTED
 * =========================================================
 */

function isSelected(row: number, col: number): boolean {
  const selection = normalizedSelection.value;

  if (!selection) {
    return false;
  }

  return (
    row >= selection.startRow &&
    row <= selection.endRow &&
    col >= selection.startCol &&
    col <= selection.endCol
  );
}

/**
 * =========================================================
 * STEP CELL SELECTED
 * =========================================================
 */

function isStepCellSelected(rowIndex: number): boolean {
  const selection = normalizedSelection.value;

  if (!selection) {
    return false;
  }

  const span = stepRowSpans.value.find((item) => item.startRow === rowIndex);

  if (!span) {
    return isSelected(rowIndex, 0);
  }

  return (
    span.startRow <= selection.endRow &&
    span.endRow >= selection.startRow &&
    selection.startCol <= 0 &&
    selection.endCol >= 0
  );
}

/**
 * =========================================================
 * COPY
 * =========================================================
 *
 * Ctrl+C / Cmd+C
 *
 * TSV 형식으로 복사
 *
 * Ctrl+V는 지원하지 않는다.
 */

function createSelectedTSV(): string {
  const selection = normalizedSelection.value;

  if (!selection) {
    return "";
  }

  /**
   * 마지막 column = 비고
   *
   * 따라서 복사 대상 마지막 column은
   *
   * headers.length - 2
   */

  const maxCol = table.value.headers.length - 2;

  const result: string[] = [];

  for (let row = selection.startRow; row <= selection.endRow; row++) {
    const values: string[] = [];

    const endCol = Math.min(selection.endCol, maxCol);

    for (let col = selection.startCol; col <= endCol; col++) {
      const value = dataRows.value[row]?.cells[col]?.value ?? "";

      values.push(value.replace(/\t/g, " ").replace(/\r?\n/g, " "));
    }

    result.push(values.join("\t"));
  }

  return result.join("\n");
}

/**
 * =========================================================
 * CLIPBOARD COPY
 * =========================================================
 *
 * ClipboardEvent를 사용한다.
 *
 * @copy 이벤트이므로
 * KeyboardEvent 타입 충돌이 없다.
 */

function handleCopy(event: ClipboardEvent) {
  const selection = normalizedSelection.value;

  if (!selection) {
    return;
  }

  const tsv = createSelectedTSV();

  if (!tsv) {
    return;
  }

  /**
   * 기본 copy 방지
   */
  event.preventDefault();

  /**
   * TSV 저장
   */
  event.clipboardData?.setData("text/plain", tsv);

  /**
   * 복사 완료 메시지
   */
  message.success("선택한 셀을 클립보드에 복사했습니다.");
}

/**
 * =========================================================
 * WINDOW MOUSE UP
 * =========================================================
 */

function handleWindowMouseUp() {
  stopSelection();
}

window.addEventListener("mouseup", handleWindowMouseUp);

onBeforeUnmount(() => {
  window.removeEventListener("mouseup", handleWindowMouseUp);
});
</script>

<template>
  <!--
    =======================================================
    ROOT
    =======================================================

    width / height를 props로 받지 않는다.

    부모가:

      w-full
      h-full

    을 지정하면 그대로 100%를 사용한다.

    Module Federation 환경을 고려하여
    position / sticky / z-index를 사용하지 않는다.
  -->

  <div
    ref="tableContainer"
    tabindex="0"
    class="w-full h-full min-w-0 min-h-0 max-w-full max-h-full overflow-auto rounded-xl border border-slate-200 bg-white shadow-sm outline-none select-none"
    @copy="handleCopy"
  >
    <table class="w-full min-w-max border-collapse text-sm">
      <!-- ================================================= -->
      <!-- HEADER -->
      <!-- ================================================= -->

      <thead>
        <!-- ================================================= -->
        <!-- GROUP HEADER -->
        <!-- ================================================= -->

        <tr>
          <!-- STEP -->
          <th
            rowspan="3"
            class="min-w-[110px] border border-slate-300 bg-slate-100 px-3 py-2 text-center font-semibold whitespace-nowrap"
          >
            step
          </th>

          <!-- CATEGORY -->
          <th
            rowspan="3"
            class="min-w-[110px] border border-slate-300 bg-slate-100 px-3 py-2 text-center font-semibold whitespace-nowrap"
          >
            category
          </th>

          <!-- GROUP -->
          <th
            v-for="(group, index) in waferHeader.groupHeaders"
            :key="`group-${index}`"
            :colspan="group.colspan"
            class="border border-slate-300 px-3 py-2 text-center font-bold whitespace-nowrap"
            :class="
              group.groupId === 'g1'
                ? 'bg-emerald-50 text-emerald-700'
                : group.groupId === 'g2'
                  ? 'bg-rose-50 text-rose-700'
                  : 'bg-slate-100 text-slate-700'
            "
          >
            <span class="inline-flex items-center gap-1.5">
              <!-- Group 상태 dot -->
              <span
                class="h-2.5 w-2.5 rounded-full"
                :class="
                  group.groupId === 'g1'
                    ? 'bg-emerald-500'
                    : group.groupId === 'g2'
                      ? 'bg-rose-500'
                      : 'bg-slate-400'
                "
              />

              {{ group.label }}
            </span>
          </th>
        </tr>

        <!-- ================================================= -->
        <!-- LOT HEADER -->
        <!-- ================================================= -->

        <tr>
          <th
            v-for="(lot, index) in waferHeader.lotHeaders"
            :key="`lot-${index}`"
            :colspan="lot.colspan"
            class="border border-slate-300 px-3 py-2 text-center font-semibold whitespace-nowrap"
            :class="
              lot.groupId === 'g1'
                ? 'bg-emerald-100/70 text-emerald-800'
                : lot.groupId === 'g2'
                  ? 'bg-rose-100/70 text-rose-800'
                  : 'bg-slate-50 text-slate-700'
            "
          >
            {{ lot.lotId }}
          </th>
        </tr>

        <!-- ================================================= -->
        <!-- WAFER HEADER -->
        <!-- ================================================= -->

        <tr>
          <th
            v-for="column in waferHeader.columns"
            :key="`wafer-${column.index}`"
            class="border border-slate-300 px-3 py-2 text-center font-medium whitespace-nowrap"
            :class="
              column.groupId === 'g1'
                ? 'bg-emerald-50/60 text-emerald-800'
                : column.groupId === 'g2'
                  ? 'bg-rose-50/60 text-rose-800'
                  : 'bg-slate-50 text-slate-700'
            "
          >
            {{ column.waferId }}
          </th>
        </tr>
      </thead>

      <!-- ================================================= -->
      <!-- BODY -->
      <!-- ================================================= -->

      <tbody>
        <tr v-for="(row, rowIndex) in dataRows" :key="`row-${rowIndex}`">
          <!-- ================================================= -->
          <!-- STEP -->
          <!-- ================================================= -->

          <td
            v-if="shouldRenderStepCell(rowIndex)"
            :rowspan="getRowSpan(rowIndex)"
            class="border border-slate-200 bg-slate-50 px-3 py-2 align-top font-semibold whitespace-nowrap cursor-cell"
            :class="{
              'bg-blue-100 ring-2 ring-inset ring-blue-400':
                isStepCellSelected(rowIndex),
            }"
            @mousedown="startSelection(rowIndex, 0, $event)"
            @mouseenter="moveSelection(rowIndex, 0)"
          >
            {{ row.cells[0]?.value ?? "" }}
          </td>

          <!-- ================================================= -->
          <!-- CATEGORY -->
          <!-- ================================================= -->

          <td
            class="border border-slate-200 px-3 py-2 whitespace-nowrap cursor-cell"
            :class="{
              'bg-blue-100 ring-2 ring-inset ring-blue-400': isSelected(
                rowIndex,
                1
              ),
            }"
            @mousedown="startSelection(rowIndex, 1, $event)"
            @mouseenter="moveSelection(rowIndex, 1)"
          >
            {{ row.cells[1]?.value ?? "" }}
          </td>

          <!-- ================================================= -->
          <!-- WAFER CELLS -->
          <!-- ================================================= -->

          <td
            v-for="column in waferHeader.columns"
            :key="`cell-${rowIndex}-${column.index}`"
            class="border border-slate-200 px-3 py-2 whitespace-nowrap cursor-cell transition-colors"
            :class="[
              /**
               * =============================================
               * 기본 Group 배경
               *
               * Header보다 훨씬 연하게 표시
               * =============================================
               */

              column.groupId === 'g1'
                ? 'bg-emerald-50/30'
                : column.groupId === 'g2'
                  ? 'bg-rose-50/30'
                  : 'bg-white',

              {
                /**
                 * ===========================================
                 * 불량 Chamber Highlight
                 * ===========================================
                 *
                 * group2={2}
                 *
                 * g2 + Chamber=2
                 *
                 * 만 강조
                 */
                'bg-rose-100 text-rose-900 font-bold': isChamberHighlighted(
                  rowIndex,
                  column.index
                ),

                /**
                 * ===========================================
                 * 셀 선택
                 * ===========================================
                 */
                'bg-blue-100 text-blue-900 ring-2 ring-inset ring-blue-400':
                  isSelected(rowIndex, column.index),
              },
            ]"
            @mousedown="startSelection(rowIndex, column.index, $event)"
            @mouseenter="moveSelection(rowIndex, column.index)"
          >
            {{ row.cells[column.index]?.value ?? "" }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
