<template>
  <div class="flex flex-col gap-4 p-4 bg-slate-50 min-h-screen">
    <div class="flex flex-col lg:flex-row gap-4 items-start">
      <div
        class="flex flex-col gap-4 p-4 border border-slate-200 rounded-xl bg-white shadow-sm max-w-4xl w-full"
      >
        <div
          class="flex items-center justify-between border-b border-slate-200 pb-3"
        >
          <div class="flex items-center gap-2">
            <span class="text-base">⚙️</span>
            <h2 class="text-sm font-bold text-slate-800">조회 조건 설정</h2>
          </div>

          <a-button
            type="primary"
            size="middle"
            :disabled="conditionSets.length === 0"
            :loading="querying"
            class="!font-semibold"
            @click="runQuery"
          >
            🔍 전체 조회 ({{ conditionSets.length }}개 세트)
          </a-button>
        </div>

        <div class="flex items-center gap-3">
          <div class="w-64">
            <label class="block text-[11px] font-semibold text-slate-500 mb-1"
              >Preset 필터</label
            >
            <a-select
              v-model:value="selectedPreset"
              show-search
              allow-clear
              placeholder="Preset 선택 (생략 가능)"
              class="w-full"
              :options="presetOptions"
              :loading="options.presetsLoading.value"
              :virtual="false"
              @dropdown-visible-change="
                (open: boolean) => open && options.loadPresets()
              "
            />
          </div>
          <div class="w-40">
            <label class="block text-[11px] font-semibold text-slate-500 mb-1"
              >Site 필터</label
            >
            <a-tooltip
              :title="
                isComplexSearch
                  ? 'file_name 검색어가 숫자_숫자 형식이라 Site와 의미가 겹쳐 선택할 수 없습니다'
                  : undefined
              "
            >
              <a-select
                v-model:value="selectedSite"
                allow-clear
                :disabled="isComplexSearch"
                placeholder="Site 선택 (생략 가능)"
                class="w-full"
                :options="siteOptions"
              />
            </a-tooltip>
          </div>
          <div class="text-xs text-slate-400 mt-4">
            * Preset을 선택하거나 아래 Grid에서 파일명을 검색하면 목록이
            표출됩니다. (Site는 단독 선택만으로는 조회되지 않고 검색어와 함께
            적용됩니다)
          </div>
        </div>

        <div
          v-if="options.presetsError.value || options.fileRecordsError.value"
          class="border border-red-300 bg-red-50 text-red-600 text-xs rounded-lg px-3 py-2"
        >
          {{ options.presetsError.value ?? options.fileRecordsError.value }}
        </div>

        <div class="flex flex-col gap-2">
          <FileNameGrid
            :file-records="displayedFileRecords"
            v-model:selected="selectedFileNames"
            v-model:search-text="searchText"
            :loading="options.fileRecordsLoading.value"
            :has-criteria="hasCriteria"
          />

          <div
            class="flex items-center justify-between bg-slate-100 p-2.5 rounded-lg border border-slate-200"
          >
            <span class="text-xs text-slate-600">
              현재
              <strong class="text-blue-600 font-bold"
                >{{ selectedFileNames.length }}개</strong
              >의 파일이 선택되었습니다.
            </span>
            <a-button
              type="primary"
              ghost
              size="small"
              :disabled="!canAdd"
              class="text-xs! font-medium!"
              @click="handleAdd"
            >
              + 조건 세트로 추가
            </a-button>
          </div>

          <div
            v-if="selectedFileNames.length"
            class="flex flex-wrap gap-1 max-h-24 overflow-y-auto pr-1"
          >
            <span
              v-for="file in selectedFileNames"
              :key="file"
              class="inline-flex items-center gap-1 text-[10px] bg-white border border-slate-300 rounded px-1.5 py-0.5 text-slate-600"
            >
              {{ file }}
              <button
                class="text-slate-300 hover:text-red-500 cursor-pointer leading-none"
                @click="removeSelectedFileName(file)"
              >
                ✕
              </button>
            </span>
          </div>
        </div>
      </div>

      <div
        v-if="conditionSets.length"
        class="w-full lg:flex-1 lg:sticky lg:top-4 border border-slate-200 rounded-xl bg-white shadow-sm p-4"
      >
        <ConditionSetList
          :condition-sets="conditionSets"
          @remove-set="removeConditionSet"
          @remove-file="removeFileFromSet"
        />
      </div>
    </div>

    <div
      v-if="queryError"
      class="border border-red-300 bg-red-50 text-red-600 text-xs rounded-lg px-3 py-2"
    >
      조회 실패: {{ queryError }}
    </div>

    <!-- 조회는 세트 전체가 한 번에 요청/응답되므로 카드별이 아닌 전체 스피너 하나로 표시 -->
    <div v-if="querying" class="flex items-center justify-center py-16">
      <a-spin tip="차트 데이터 조회 중..." size="large" />
    </div>

    <div v-else-if="results.length" class="flex flex-wrap gap-4">
      <div
        v-for="result in results"
        :key="result.conditionSet.id"
        class="border border-slate-200 flex flex-col"
      >
        <div
          v-if="result.status === 'error'"
          class="h-96 flex items-center justify-center text-red-500 text-xs"
        >
          데이터를 불러오지 못했습니다.
        </div>
        <div
          v-else-if="result.status === 'missing'"
          class="h-96 flex items-center justify-center text-amber-600 text-xs"
        >
          서버 응답에 이 세트의 데이터가 없습니다.
        </div>
        <div v-else class="w-full">
          <CircuitRulerChart
            :objects="result.objects"
            :layout="{ width: 480, height: 480 }"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { refDebounced } from "@vueuse/core";
import {
  Button as AButton,
  Select as ASelect,
  Spin as ASpin,
  Tooltip as ATooltip,
} from "ant-design-vue";
import FileNameGrid from "./FileNameGrid.vue";
import ConditionSetList from "./ConditionSetList.vue";
import CircuitRulerChart from "./CircuitRulerChart.vue";
import { useQueryOptions } from "../composables/useQueryOptions";
import { useConditionSets } from "../composables/useConditionSets";
import { SITE_OPTIONS, type Site } from "../types/query";
import { COMPLEX_SEARCH_PATTERN } from "../api/queryApi";

const options = useQueryOptions();
const {
  conditionSets,
  results,
  querying,
  queryError,
  addConditionSet,
  removeConditionSet,
  removeFileFromSet,
  runQuery,
} = useConditionSets();

// a-select의 "선택 안 함"(undefined)과 실제 null preset을 구분하기 위한 sentinel 값.
const NULL_PRESET_OPTION = "__null_preset__";

const selectedPreset = ref<string | undefined>(undefined); // undefined = 아무것도 선택 안 함
const selectedSite = ref<Site | undefined>(undefined); // undefined = 아무것도 선택 안 함
const selectedFileNames = ref<string[]>([]);
const searchText = ref("");
const debouncedSearchText = refDebounced(searchText, 300); // 타이핑마다 서버 호출하지 않도록

const presetOptions = computed(() =>
  options.presets.value.map((p) => ({
    label: p ?? "(preset 없음)",
    value: p ?? NULL_PRESET_OPTION,
  }))
);

const siteOptions = SITE_OPTIONS.map((s) => ({ label: s, value: s }));

// complex 검색(숫자_숫자)은 자체적으로 IN/OUT을 지정하므로 Site 필터와 의미가 겹침 — 입력 중엔 Site 선택을 막음.
const isComplexSearch = computed(() => COMPLEX_SEARCH_PATTERN.test(searchText.value.trim()));

// a-select의 sentinel 값을 실제 도메인 값(string | null | undefined)으로 변환.
function resolvePreset(value: string | undefined): string | null | undefined {
  if (value === undefined) return undefined;
  return value === NULL_PRESET_OPTION ? null : value;
}

const canAdd = computed(() => selectedFileNames.value.length > 0);

// preset 또는 검색어가 있어야 조회 — Site는 단독으로 조회를 트리거하지 않고 검색/preset과 함께 적용됨.
const hasCriteria = computed(
  () => selectedPreset.value !== undefined || !!debouncedSearchText.value
);
const displayedFileRecords = computed(() =>
  hasCriteria.value ? options.fileRecords.value : []
);

// 선택은 preset/site/검색어를 넘나들어도 유지되는 전역 목록 — 조건이 바뀌면 그 조건으로 재조회.
// Site는 검색어와 결합될 때만 의미가 있어, 검색어 없이는 조회에 반영하지 않음.
watch([selectedPreset, debouncedSearchText], ([presetValue, search]) => {
  // complex 검색(숫자_숫자)은 자체적으로 IN/OUT을 지정하므로 Site 필터와 의미가 겹침 — 선택 해제.
  if (
    selectedSite.value !== undefined &&
    search &&
    COMPLEX_SEARCH_PATTERN.test(search.trim())
  ) {
    selectedSite.value = undefined; // 아래 selectedSite watcher가 이어서 올바른 조건으로 재조회함
    return;
  }

  const preset = resolvePreset(presetValue);
  if (preset === undefined && !search) return;

  const site = search ? selectedSite.value : undefined;
  options.loadFileRecords({ preset, site, search });
});

// Site 변경은 검색어가 있을 때만 재조회 — 검색어 없이 site만 바뀌면 결과에 영향이 없으므로 무시.
watch(selectedSite, (site) => {
  if (!debouncedSearchText.value) return;

  const preset = resolvePreset(selectedPreset.value);
  options.loadFileRecords({ preset, site, search: debouncedSearchText.value });
});

// complex 검색(숫자_숫자) 결과는 도착하는 대로 전부 선택 — 다른 조건에서 이미 고른 선택은 유지하고 합침.
// fileRecords는 최신 요청의 결과만 반영되므로(useQueryOptions의 레이스 가드), 이 시점의 debouncedSearchText가 그 요청의 검색어와 같음.
watch(options.fileRecords, (records) => {
  if (!COMPLEX_SEARCH_PATTERN.test(debouncedSearchText.value.trim())) return;

  selectedFileNames.value = [
    ...new Set([...selectedFileNames.value, ...records.map((r) => r.file_name)]),
  ];
});

function handleAdd() {
  addConditionSet(
    resolvePreset(selectedPreset.value) ?? null,
    selectedFileNames.value
  );
  selectedFileNames.value = [];
}

function removeSelectedFileName(fileName: string) {
  selectedFileNames.value = selectedFileNames.value.filter((f) => f !== fileName);
}
</script>
