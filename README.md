<template>
  <div class="min-h-screen bg-slate-100 p-6 text-slate-800">
    <div class="max-w-7xl mx-auto space-y-4">
      <!-- ========================================== -->
      <!-- 1. 상단 컨트롤 바 (검색 및 전체 펼치기/접기) -->
      <!-- ========================================== -->
      <div
        class="bg-white p-4 rounded-none shadow-2xs border border-slate-200/80 flex flex-wrap items-center justify-between gap-4"
      >
        <!-- 검색 및 건수 -->
        <div class="flex items-center gap-3 flex-1 min-w-[300px]">
          <h1 class="text-lg font-bold text-slate-900 whitespace-nowrap">
            Recipe 관리
          </h1>
          <a-input-search
            v-model:value="searchQuery"
            placeholder="Recipe명, Title, Target Key 검색..."
            allow-clear
            class="max-w-md rounded-none"
          />
          <a-tag color="blue" class="font-semibold m-0 rounded-none"
            >총 {{ filteredRecipes.length }}건</a-tag
          >
        </div>

        <!-- 일괄 조작 및 신규 생성 -->
        <div class="flex items-center gap-2">
          <a-button-group>
            <a-button class="rounded-none" @click="expandAll">전체 펼치기</a-button>
            <a-button class="rounded-none" @click="collapseAll">전체 접기</a-button>
          </a-button-group>
          <a-button type="primary" class="rounded-none">+ 신규 Recipe</a-button>
        </div>
      </div>

      <!-- ========================================== -->
      <!-- 2. 아코디언 (Collapse) 목록 영역 -->
      <!-- ========================================== -->
      <a-collapse
        v-model:activeKey="activeKeys"
        ghost
        class="space-y-3 recipe-collapse"
      >
        <a-collapse-panel
          v-for="recipe in filteredRecipes"
          :key="recipe.id"
          class="bg-white rounded-none border border-slate-200/80 shadow-2xs overflow-hidden transition-all hover:border-indigo-300"
        >
          <!-- (A) 아코디언 헤더 Slot -->
          <template #header>
            <div
              class="flex flex-wrap items-center justify-between w-full pr-4 py-1 gap-2"
            >
              <!-- 레시피 식별 정보 -->
              <div class="flex items-center gap-3 min-w-[280px]">
                <span class="font-bold text-slate-400 text-xs w-20">{{
                  recipe.id
                }}</span>
                <span class="font-bold text-slate-900 text-sm">{{
                  recipe.title
                }}</span>
                <a-tag color="purple" class="font-mono text-2xs m-0 rounded-none">{{
                  recipe.recipeName
                }}</a-tag>
              </div>

              <!-- 주요 사양 요약 정보 -->
              <div
                class="hidden md:flex items-center gap-6 text-xs text-slate-500 font-mono"
              >
                <div>
                  Target:
                  <span class="font-semibold text-slate-800">{{
                    recipe.targetKeyName
                  }}</span>
                </div>
                <div>
                  Keys:
                  <span class="font-semibold text-slate-800"
                    >{{ recipe.totalKeys }}ea</span
                  >
                </div>
                <div>
                  G-Opt Points:
                  <span class="font-semibold text-indigo-600"
                    >{{ recipe.gOptimality.length }}pts</span
                  >
                </div>
              </div>

              <!-- 상태 태그 & 최종 수정일 -->
              <div class="flex items-center gap-3">
                <span class="text-2xs text-slate-400 hidden lg:inline">{{
                  recipe.updatedAt
                }}</span>
                <a-tag
                  :color="recipe.status === 'Active' ? 'green' : 'default'"
                  class="m-0 rounded-none"
                >
                  {{ recipe.status }}
                </a-tag>
              </div>
            </div>
          </template>

          <!-- (B) 아코디언 내부 상세 내용 -->
          <div
            :ref="(el) => setCardRef(el, recipe.id)"
            class="pt-2 pb-4 space-y-6 bg-white p-4 rounded-none"
          >
            <!-- 1. 상세 사양 (Specifications) -->
            <div class="bg-slate-50/70 p-4 rounded-none border border-slate-100">
              <h4
                class="text-xs font-bold text-slate-500 mb-3 uppercase tracking-wider"
              >
                Basic Specifications
              </h4>
              <a-descriptions
                bordered
                size="small"
                :column="{ xxl: 4, xl: 3, lg: 2, md: 2, sm: 1 }"
              >
                <a-descriptions-item label="Target Key Name">
                  <span class="font-semibold text-indigo-600">{{
                    recipe.targetKeyName
                  }}</span>
                </a-descriptions-item>
                <a-descriptions-item label="총 Key 개수"
                  >{{ recipe.totalKeys }} ea</a-descriptions-item
                >
                <a-descriptions-item label="Field당 Key 개수"
                  >{{ recipe.keysPerField }} ea</a-descriptions-item
                >
                <a-descriptions-item label="Edge Clearance">{{
                  recipe.edgeClearance
                }}</a-descriptions-item>
                <a-descriptions-item label="Key Size">{{
                  recipe.keySize
                }}</a-descriptions-item>
                <a-descriptions-item label="TIS Correction" :span="2">
                  <a-tag color="purple" class="font-mono rounded-none">{{
                    recipe.tisCorrection
                  }}</a-tag>
                </a-descriptions-item>
              </a-descriptions>
            </div>

            <!-- 2. 2-Column 그리드 (계측 조건 & 개선된 G-Optimality 영역) -->
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
              <!-- (좌) 계측 조건 테이블 -->
              <div class="lg:col-span-4">
                <div
                  class="border border-slate-200 rounded-none overflow-hidden bg-white shadow-2xs h-full"
                >
                  <div
                    class="bg-slate-100/80 px-4 py-2.5 border-b border-slate-200 text-xs font-bold text-slate-700"
                  >
                    계측 조건 (Measurement Conditions)
                  </div>
                  <a-table
                    :dataSource="recipe.measurementConditions"
                    :columns="measurementColumns"
                    :pagination="false"
                    size="small"
                    bordered
                  >
                    <template #bodyCell="{ column, text }">
                      <template v-if="column.dataIndex === 'direction'">
                        <span class="font-bold text-slate-700">{{ text }}</span>
                      </template>
                      <template v-else-if="column.dataIndex === 'dose'">
                        <a-tag color="green" class="m-0 text-2xs rounded-none">{{
                          text
                        }}</a-tag>
                      </template>
                    </template>
                  </a-table>
                </div>
              </div>

              <!-- (우) 개선된 G-Optimality (고정 스크롤 + KPI 요약 + 이상치 필터) -->
              <div class="lg:col-span-8">
                <div
                  class="border border-slate-200 rounded-none overflow-hidden bg-white shadow-2xs"
                >
                  <!-- [G-Opt 헤더]: KPI 요약 + 필터 컨트롤 -->
                  <div
                    class="bg-slate-50 p-2.5 px-3 border-b border-slate-200 flex flex-wrap items-center justify-between gap-2"
                  >
                    <!-- KPI 요약 수치 -->
                    <div class="flex items-center gap-3 text-xs">
                      <span class="font-bold text-slate-800">G-Optimality</span>
                      <div class="h-3 w-[1px] bg-slate-300"></div>
                      <div class="text-slate-500">
                        Max:
                        <span class="font-mono font-bold text-red-600">{{
                          getStats(recipe.gOptimality).max
                        }}</span>
                      </div>
                      <div class="text-slate-500">
                        Min:
                        <span class="font-mono font-bold text-slate-700">{{
                          getStats(recipe.gOptimality).min
                        }}</span>
                      </div>
                      <div class="text-slate-500">
                        Avg:
                        <span class="font-mono font-bold text-slate-700">{{
                          getStats(recipe.gOptimality).avg
                        }}</span>
                      </div>
                    </div>

                    <!-- 빠른 필터 (전체 / Outlier 전용) -->
                    <div class="flex items-center gap-2">
                      <a-radio-group
                        :value="recipeFilterMode[recipe.id] || 'all'"
                        @change="
                          (e) => setFilterMode(recipe.id, e.target.value)
                        "
                        size="small"
                        button-style="solid"
                      >
                        <a-radio-button value="all" class="rounded-none"
                          >전체 ({{
                            recipe.gOptimality.length
                          }})</a-radio-button
                        >
                        <a-radio-button value="outlier" class="rounded-none">
                          <span class="text-red-500 font-semibold">
                            Outliers ({{
                              getStats(recipe.gOptimality).outlierCount
                            }})
                          </span>
                        </a-radio-button>
                      </a-radio-group>
                    </div>
                  </div>

                  <!-- [G-Opt 테이블]: 고정 세로 스크롤 (:scroll="{ y: 250 }") -->
                  <a-table
                    :dataSource="getFilteredGOptimality(recipe)"
                    :columns="gOptimalityColumns"
                    :pagination="false"
                    :scroll="{ y: 250 }"
                    size="small"
                    bordered
                    class="dense-scroll-table"
                  >
                    <template #bodyCell="{ column, text, record, index }">
                      <template v-if="column.dataIndex === 'no'">
                        <span class="text-2xs font-mono text-slate-400"
                          >#{{ index + 1 }}</span
                        >
                      </template>

                      <template v-else-if="column.dataIndex === 'ovlDirection'">
                        <a-tag
                          :color="text === 'O' ? 'blue' : 'orange'"
                          class="m-0 font-bold text-2xs rounded-none"
                        >
                          {{ text }}
                        </a-tag>
                      </template>

                      <template v-else-if="column.dataIndex === 'ref'">
                        <a-badge
                          :status="
                            record.ref === 'Recipe' ? 'success' : 'warning'
                          "
                          :text="record.ref"
                          class="text-2xs"
                        />
                      </template>

                      <!-- 이상치(Value > 0.25) 붉은색 강조 -->
                      <template v-else-if="column.dataIndex === 'value'">
                        <span
                          class="font-mono font-semibold"
                          :class="
                            text > 0.25
                              ? 'text-red-600 bg-red-50 px-1.5 py-0.5 rounded-none border border-red-200'
                              : 'text-slate-700'
                          "
                        >
                          {{ text.toFixed(4) }}
                        </span>
                      </template>
                    </template>
                  </a-table>
                </div>
              </div>
            </div>

            <!-- 3. 푸터 하단 액션 버튼 -->
            <div
              class="flex justify-end items-center gap-2 pt-2 border-t border-slate-100"
            >
              <a-button
                size="small"
                class="rounded-none"
                :loading="downloadingId === recipe.id"
                @click="downloadAsImage(recipe)"
              >
                <template #icon><DownloadOutlined /></template>
                이미지로 저장
              </a-button>
              <a-button size="small" class="rounded-none">복사 생성</a-button>
              <a-button size="small" class="rounded-none">수정</a-button>
              <a-button size="small" type="primary" class="rounded-none"
                >설비 전송 (Deploy)</a-button
              >
            </div>
          </div>
        </a-collapse-panel>
      </a-collapse>

      <!-- 검색 결과 없음 예외 처리 -->
      <div
        v-if="filteredRecipes.length === 0"
        class="bg-white p-12 rounded-none text-center text-slate-400"
      >
        검색 조건에 맞는 Recipe가 없습니다.
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from "vue";

import { toPng } from "html-to-image";
import { DownloadOutlined } from "@ant-design/icons-vue"; // Ant Design 아이콘 (선택)

// 레시피별 DOM Element Reference 저장
const cardRefs = ref<Record<string, HTMLElement>>({});
const setCardRef = (el: any, id: string) => {
  if (el) cardRefs.value[id] = el as HTMLElement;
};

// 다운로드 중 로딩 상태 관리
const downloadingId = ref<string | null>(null);
// 📸 이미지 다운로드 함수 수정
const downloadAsImage = async (recipe: RecipeItem) => {
  const targetEl = cardRefs.value[recipe.id];
  if (!targetEl) return;

  try {
    downloadingId.value = recipe.id;

    // html-to-image를 사용하여 PNG 생성
    const dataUrl = await toPng(targetEl, {
      cacheBust: true, // 캐시 방지
      backgroundColor: "#ffffff", // 배경색 흰색 지정 (투명 배경 방지)
      pixelRatio: 2, // 2배 선명한 고해상도 출력
    });

    // 다운로드 링크 생성 및 실행
    const link = document.createElement("a");
    link.download = `${recipe.recipeName}_${recipe.id}.png`;
    link.href = dataUrl;
    link.click();
  } catch (error) {
    console.error("이미지 저장 중 오류가 발생했습니다:", error);
  } finally {
    downloadingId.value = null;
  }
};

interface GOptimalityItem {
  key: string;
  x: number;
  y: number;
  ovlDirection: string;
  value: number;
  ref: string;
}

interface MeasurementCondition {
  key: string;
  direction: string;
  wavelengthLabel: string;
  wavelength: string;
  polarization: string;
  dose: string;
  rowSpan?: number;
}

interface RecipeItem {
  id: string;
  title: string;
  recipeName: string;
  status: "Active" | "Draft" | "Archived";
  updatedAt: string;
  totalKeys: number;
  keysPerField: number;
  edgeClearance: string;
  keySize: string;
  tisCorrection: string;
  targetKeyName: string;
  gOptimality: GOptimalityItem[];
  measurementConditions: MeasurementCondition[];
}

// --- 레시피별 다량의 G-Optimality 데이터 (각 50개 이상) 포함 샘플 데이터 생성 ---
const recipeList = ref<RecipeItem[]>(
  Array.from({ length: 10 }).map((_, index) => {
    const idNum = 337 + index;

    // 각 레시피마다 50개의 G-Optimality 포인트 생성
    const gOptItems: GOptimalityItem[] = Array.from({ length: 50 }).map(
      (_, gIdx) => {
        const isOutlier = (gIdx + index) % 8 === 0;
        const val = isOutlier
          ? 0.255 + Math.random() * 0.04
          : 0.14 + Math.random() * 0.09;
        return {
          key: `gopt-${index}-${gIdx}`,
          x: parseFloat((-8 + Math.random() * 16).toFixed(4)),
          y: parseFloat((-8 + Math.random() * 16).toFixed(4)),
          ovlDirection: gIdx % 2 === 0 ? "O" : "V",
          value: parseFloat(val.toFixed(4)),
          ref: gIdx % 3 === 0 ? "ADV" : "Recipe",
        };
      }
    );

    return {
      id: `rcp-${idNum}`,
      title: `${idNum}.recipe Content`,
      recipeName: `SVD${39 + index}DSL.recipe`,
      status: index % 4 === 0 ? "Draft" : "Active",
      updatedAt: `2026-08-${10 + (index % 5)}`,
      totalKeys: 500 + index * 10,
      keysPerField: 90 + (index % 10),
      edgeClearance: `${7 - (index % 3)}mm`,
      keySize: "10um * 10um",
      tisCorrection: `AC 19${21 + index}TFS`,
      targetKeyName: `target label ${String.fromCharCode(65 + (index % 5))}`,
      gOptimality: gOptItems,
      measurementConditions: [
        {
          key: "1",
          direction: "X",
          wavelengthLabel: "WL1.",
          wavelength: "193nm",
          polarization: "H",
          dose: "100%",
          rowSpan: 2,
        },
        {
          key: "2",
          direction: "X",
          wavelengthLabel: "WL2.",
          wavelength: "193nm",
          polarization: "H",
          dose: "100%",
          rowSpan: 0,
        },
        {
          key: "3",
          direction: "Y",
          wavelengthLabel: "WL1.",
          wavelength: "193nm",
          polarization: "H",
          dose: "100%",
          rowSpan: 1,
        },
      ],
    };
  })
);

// --- 반응형 상태 ---
const searchQuery = ref<string>("");
const activeKeys = ref<string[]>(["rcp-337"]); // 기본 1개 펼침
const recipeFilterMode = reactive<Record<string, "all" | "outlier">>({});

// 레시피별 필터 모드 변경
const setFilterMode = (recipeId: string, mode: "all" | "outlier") => {
  recipeFilterMode[recipeId] = mode;
};

// 레시피별 필터링된 G-Optimality 반환
const getFilteredGOptimality = (recipe: RecipeItem) => {
  const mode = recipeFilterMode[recipe.id] || "all";
  if (mode === "outlier") {
    return recipe.gOptimality.filter((item) => item.value > 0.25);
  }
  return recipe.gOptimality;
};

// 레시피별 G-Optimality KPI 통계 자동 계산
const getStats = (items: GOptimalityItem[]) => {
  if (!items || items.length === 0)
    return { max: "0", min: "0", avg: "0", outlierCount: 0 };
  const values = items.map((d) => d.value);
  const max = Math.max(...values);
  const min = Math.min(...values);
  const avg = values.reduce((a, b) => a + b, 0) / values.length;
  const outlierCount = items.filter((i) => i.value > 0.25).length;
  return {
    max: max.toFixed(4),
    min: min.toFixed(4),
    avg: avg.toFixed(4),
    outlierCount,
  };
};

// 검색 필터
const filteredRecipes = computed(() => {
  if (!searchQuery.value.trim()) return recipeList.value;
  const query = searchQuery.value.toLowerCase();
  return recipeList.value.filter(
    (r) =>
      r.title.toLowerCase().includes(query) ||
      r.recipeName.toLowerCase().includes(query) ||
      r.targetKeyName.toLowerCase().includes(query)
  );
});

// 전체 펼치기 / 접기
const expandAll = () => {
  activeKeys.value = filteredRecipes.value.map((r) => r.id);
};
const collapseAll = () => {
  activeKeys.value = [];
};

// 테이블 컬럼 정의
const measurementColumns = [
  {
    title: "Dir",
    dataIndex: "direction",
    width: 50,
    align: "center",
    customCell: (record: MeasurementCondition) => ({ rowSpan: record.rowSpan }),
  },
  { title: "WL 구분", dataIndex: "wavelengthLabel", align: "center" },
  { title: "Wavelength", dataIndex: "wavelength", align: "center" },
  { title: "Polarization", dataIndex: "polarization", align: "center" },
  { title: "Dose", dataIndex: "dose", align: "center" },
];

const gOptimalityColumns = [
  { title: "No", dataIndex: "no", width: 50, align: "center" },
  { title: "X 좌표 (mm)", dataIndex: "x", align: "right" },
  { title: "Y 좌표 (mm)", dataIndex: "y", align: "right" },
  { title: "Ovl Dir", dataIndex: "ovlDirection", align: "center", width: 85 },
  { title: "Value", dataIndex: "value", align: "right" },
  { title: "Ref", dataIndex: "ref", align: "center", width: 80 },
];
</script>

<style scoped>
/* Ant Design Vue 컴포넌트 모서리 곡률(border-radius) 일괄 직각화 */
:deep(.ant-btn),
:deep(.ant-btn-group),
:deep(.ant-collapse),
:deep(.ant-collapse-item),
:deep(.ant-collapse-header),
:deep(.ant-descriptions-view),
:deep(.ant-table-wrapper),
:deep(.ant-table-container),
:deep(.ant-input),
:deep(.ant-input-affix-wrapper),
:deep(.ant-tag),
:deep(.ant-radio-button-wrapper),
:deep(.ant-select-selector) {
  border-radius: 0px !important;
}

/* Ant Design Collapse 커스텀 스타일 */
:deep(.recipe-collapse .ant-collapse-header) {
  align-items: center !important;
  padding: 12px 16px !important;
}
:deep(.recipe-collapse .ant-collapse-content-box) {
  padding: 0 20px 16px 20px !important;
}

/* 고정 스크롤 테이블 스크롤바 디자인 */
:deep(.dense-scroll-table .ant-table-body::-webkit-scrollbar) {
  width: 5px;
}
:deep(.dense-scroll-table .ant-table-body::-webkit-scrollbar-thumb) {
  background: #cbd5e1;
  border-radius: 0px;
}
:deep(.dense-scroll-table .ant-table-body::-webkit-scrollbar-thumb:hover) {
  background: #94a3b8;
}
</style>
