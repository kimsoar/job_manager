<template>
  <div
    class="w-full h-full flex flex-col bg-white"
    @mouseenter="isHovering = true"
    @mouseleave="isHovering = false"
  >
    <div class="flex items-center px-3 py-2 border-b shrink-0 justify-between">
      <div class="flex item-center gap-2">
        <a-button
          size="small"
          :type="rulerMode ? 'primary' : 'default'"
          @click="toggleRuler"
        >
          📏 {{ rulerMode ? "Ruler ON" : "Ruler OFF" }}
        </a-button>

        <!-- <a-button
        size="small"
        :type="snapEnabled ? 'primary' : 'default'"
        :disabled="!rulerMode"
        @click="toggleSnap"
      >
        🧲 Snap {{ snapEnabled ? "ON" : "OFF" }}
      </a-button> -->

        <a-button
          size="small"
          :disabled="!hasMeasurement"
          @click="clearMeasurement"
        >
          Clear
        </a-button>
      </div>
      <div class="flex items-center gap-2">
        <a-button
          size="small"
          :type="showLegend ? 'primary' : 'default'"
          @click="toggleLegend"
        >
          🏷️ Legend {{ showLegend ? "ON" : "OFF" }}
        </a-button>

        <a-popover
          v-model:open="shortcutsPopoverOpen"
          trigger="click"
          placement="bottomRight"
          :overlay-style="{ width: '290px' }"
        >
          <!-- Popover는 항상 흰 배경(ant-design-vue 기본값)이라, 시스템 다크모드 영향을 받지 않도록
               색상은 라이트 팔레트로 고정합니다 (dark: variant 사용 안 함). -->
          <template #title>
            <div
              class="flex items-center gap-1.5 py-1.5 border-b border-slate-200"
            >
              <span class="text-base">⌨️</span>
              <span class="font-bold text-xs text-slate-900 leading-none">
                단축키 안내
              </span>
            </div>
          </template>

          <!-- Popover 내용 -->
          <template #content>
            <div class="py-1 space-y-1.5">
              <div
                v-for="item in SHORTCUT_LIST"
                :key="item.action"
                :class="[
                  'group flex items-center justify-between text-xs px-2 py-1.5 rounded-md transition-colors cursor-pointer active:scale-[0.98]',
                  item.action.includes('Ruler')
                    ? 'bg-amber-100 border border-amber-300 hover:bg-amber-200'
                    : 'hover:bg-slate-100',
                ]"
                @click="handleShortcutClick(item)"
              >
                <!-- 기능 설명 (좌측) -->
                <div class="flex items-center gap-1.5 shrink-0">
                  <!-- Ruler ON/OFF 일 때만 강조 뱃지/포인트 아이콘 표출 -->
                  <span
                    v-if="item.action.includes('Ruler')"
                    class="inline-block w-1.5 h-1.5 rounded-full bg-amber-600"
                  ></span>

                  <span
                    :class="[
                      'font-normal',
                      item.action.includes('Ruler')
                        ? 'font-bold text-amber-900'
                        : 'text-slate-800',
                    ]"
                  >
                    {{ item.action }}
                  </span>

                  <!-- Ruler 강조 태그 -->
                  <span
                    v-if="item.action.includes('Ruler')"
                    class="text-[9px] px-1 py-0.5 rounded bg-amber-600 text-white font-semibold leading-none"
                  >
                    KEY
                  </span>
                </div>

                <!-- 단축키 Badge (우측) -->
                <div class="flex items-center gap-1 shrink-0">
                  <!-- 배열 키 처리 (예: Shift + Drag 등) -->
                  <template v-if="Array.isArray(item.key)">
                    <template v-for="(k, idx) in item.key" :key="k">
                      <kbd
                        :class="[
                          'inline-flex items-center justify-center min-w-[20px] px-1.5 h-5 text-[10px] font-mono font-semibold rounded shadow-sm border transition-transform group-active:translate-y-px group-active:shadow-none',
                          item.action.includes('Ruler')
                            ? 'bg-amber-600 text-white border-amber-700 font-bold'
                            : 'bg-slate-200 text-slate-900 border-slate-300',
                        ]"
                      >
                        {{ k }}
                      </kbd>
                      <span
                        v-if="idx < item.key.length - 1"
                        class="text-[10px] text-slate-500 font-bold"
                        >+</span
                      >
                    </template>
                  </template>

                  <!-- 단일 문자열 키 처리 -->
                  <kbd
                    v-else
                    :class="[
                      'inline-flex items-center justify-center min-w-[20px] px-1.5 h-5 text-[10px] font-mono font-semibold rounded shadow-sm border transition-transform group-active:translate-y-px group-active:shadow-none',
                      item.action.includes('Ruler')
                        ? 'bg-amber-600 text-white border-amber-700 font-bold'
                        : 'bg-slate-200 text-slate-900 border-slate-300',
                    ]"
                  >
                    {{ item.key }}
                  </kbd>
                </div>
              </div>
            </div>
          </template>

          <!-- Trigger 버튼 -->
          <a-button
            size="small"
            class="inline-flex items-center justify-center px-2 text-xs"
          >
            <span>❓</span>
          </a-button>
        </a-popover>
      </div>
    </div>

    <div class="relative w-full aspect-square bg-black">
      <div ref="plotElement" class="w-full h-full" />
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  computed,
  nextTick,
  onBeforeUnmount,
  onMounted,
  ref,
  watch,
} from "vue";
import Plotly from "plotly.js-dist-min";
import type { Config, Layout, PlotData } from "plotly.js";
import { Button as AButton, Popover as APopover } from "ant-design-vue";
import {
  calculateMeasurement,
  findAxisLockedEdgeIntersection,
  findNearestEdgeInfo,
  getDistance,
  lockToAxis,
} from "../utils/geometry";
import type {
  Measurement,
  Point,
  CircuitObject,
  NearestEdgeInfo,
} from "../types/geometry";
import { usePlotlyAxes } from "../composables/usePlotlyAxes";

export type { CircuitObject };

interface Props {
  unit?: string;
  /** Snap 허용 범위 (화면 pixel 기준) */
  snapThresholdPx?: number;
  objects?: Partial<PlotData>[];
  /** ⚠️ xaxis.scaleanchor/scaleratio를 layout으로 덮어쓰면 snap/marker 크기 계산이 틀어집니다. */
  layout?: Partial<Layout>;
}

const props = withDefaults(defineProps<Props>(), {
  unit: "μm",
  snapThresholdPx: 30,
  objects: () => [],
  layout: () => ({}),
});

const emit = defineEmits<{
  (event: "measure", value: Measurement): void;
}>();

const unit = computed(() => props.unit);
const circuitObjects = computed<Partial<PlotData>[]>(() => props.objects);

function toCircuitObject(trace: Partial<PlotData>): CircuitObject | null {
  if (!Array.isArray(trace.x) || !Array.isArray(trace.y)) {
    return null;
  }

  return {
    name: trace.name ?? "",
    x: trace.x as (number | null)[],
    y: trace.y as (number | null)[],
  };
}

const circuitGeometry = computed<CircuitObject[]>(() =>
  circuitObjects.value
    .map(toCircuitObject)
    .filter((object): object is CircuitObject => object !== null)
);

const plotElement = ref<HTMLElement | null>(null);

// keydown은 document 레벨이라, 여러 chart가 있으면 마우스가 위에 있는 chart만 반응시킵니다.
const isHovering = ref(false);

const rulerMode = ref(false);
const snapEnabled = ref(true);
const showLegend = ref(true);
const isMeasuring = ref(false);
const startPoint = ref<Point | null>(null);
const currentPoint = ref<Point | null>(null);
const measurement = ref<Measurement>({ dx: 0, dy: 0, distance: 0 });

// 측정 중 start는 안 바뀌므로 첫 클릭 시점의 nearestEdge를 캐싱해 매 프레임 재탐색을 피합니다.
const startEdgeInfo = ref<NearestEdgeInfo | null>(null);

/**
 * start/end가 최종적으로 object edge 위에 있는지(measurementColor가 씀). isPointOnEdge를
 * 다시 호출하지 않고, applySnap 시점에 이미 계산해둔 nearestEdge/snapped로부터
 * isFinallyOnEdge()로 파생시켜 저장해둡니다 (아래 isFinallyOnEdge 참고).
 */
const startOnEdge = ref(false);
const endOnEdge = ref(false);

interface CompletedRuler {
  start: Point;
  end: Point;
  startOnEdge: boolean;
  endOnEdge: boolean;
}

// 완료된 측정들을 전부 누적해서 동시에 여러 ruler를 표시합니다. 진행 중인(첫 클릭만 한) 측정은
// 여기 들어있지 않고 startPoint/currentPoint 등 단일 상태로만 존재하다가 finishMeasurement에서 여기로 옮겨집니다.
const measurements = ref<CompletedRuler[]>([]);

const hoveredEdge = ref<{
  objectName: string;
  a: Point;
  b: Point;
  snapPoint: Point;
} | null>(null);

let rulerRafId: number | null = null;

// updateRuler()가 스스로 발생시키는 plotly_relayout을 걸러내는 플래그 (무한 루프 방지, handlePlotlyRelayout 참고)
let isSyncingRuler = false;

function getGraph(): HTMLElement | null {
  return plotElement.value;
}

const { getPlotPoint, getSnapThreshold, getMarkerSize } = usePlotlyAxes(
  plotElement,
  () => props.snapThresholdPx
);

interface SnapResult {
  point: Point;
  /** point가 실제로 edge에 스냅됐는지(=정확히 그 edge 위인지). measurementColor가 재사용합니다. */
  snapped: boolean;
}

/**
 * Shift 축 고정(lockToAxis) 여부에 따라 constrainedPoint와 그에 맞는 nearestEdge를
 * 함께 계산합니다.
 *
 * ★ 축 고정 상태에서 findNearestEdgeInfo(전체에서 가장 가까운 edge)를 그대로 쓰면,
 * 그 edge가 고정된 축 위에 있지 않을 때 snap된 결과가 축을 벗어나 버립니다 (Shift로
 * 수평/수직 고정을 했는데도 선이 미세하게 꺾이는 버그). 그래서 축 고정 중에는
 * findAxisLockedEdgeIntersection으로 "고정된 축 위의 edge 교차점"만 후보로 삼아,
 * 스냅되더라도 축 고정이 항상 유지되도록 합니다.
 */
function resolveConstrainedPoint(
  start: Point,
  rawPoint: Point,
  shiftKey: boolean
): { constrainedPoint: Point; nearestEdge: NearestEdgeInfo | null } {
  if (!shiftKey) {
    return {
      constrainedPoint: rawPoint,
      nearestEdge: findNearestEdgeInfo(rawPoint, circuitGeometry.value),
    };
  }

  const constrainedPoint = lockToAxis(start, rawPoint);
  // lockToAxis가 y를 start.y로 고정했으면(dx>=dy) 'y', 아니면 x를 고정했으므로 'x'
  const lockedAxis: "x" | "y" = constrainedPoint.y === start.y ? "y" : "x";

  return {
    constrainedPoint,
    nearestEdge: findAxisLockedEdgeIntersection(
      constrainedPoint,
      lockedAxis,
      circuitGeometry.value
    ),
  };
}

// nearestEdge 생략 시 내부에서 계산. 기본 파라미터는 인자 생략 시 함수 본문보다 먼저 평가되므로
// snapEnabled 가드를 기본값 식 자체에 둬야 snap 꺼졌을 때 불필요한 탐색을 막을 수 있습니다.
function applySnap(
  point: Point,
  nearestEdge: NearestEdgeInfo | null = snapEnabled.value
    ? findNearestEdgeInfo(point, circuitGeometry.value)
    : null
): SnapResult {
  if (
    !snapEnabled.value ||
    !nearestEdge ||
    nearestEdge.distance > getSnapThreshold()
  ) {
    return { point, snapped: false };
  }

  return {
    point: { x: nearestEdge.point.x, y: nearestEdge.point.y },
    snapped: true,
  };
}

function updateHoveredEdge(
  point: Point,
  nearestEdge: NearestEdgeInfo | null = snapEnabled.value
    ? findNearestEdgeInfo(point, circuitGeometry.value)
    : null
) {
  if (!snapEnabled.value) {
    hoveredEdge.value = null;
    return;
  }

  if (nearestEdge && nearestEdge.distance <= getSnapThreshold()) {
    hoveredEdge.value = {
      objectName: nearestEdge.objectName,
      a: nearestEdge.a,
      b: nearestEdge.b,
      snapPoint: nearestEdge.point,
    };
  } else {
    hoveredEdge.value = null;
  }
}

const hasMeasurement = computed(
  () => measurements.value.length > 0 || isMeasuring.value
);

function buildBaseLayout(): Partial<Layout> {
  const defaults: Partial<Layout> = {
    margin: { l: 60, r: 30, t: 30, b: 60 },
    paper_bgcolor: "#000000",
    plot_bgcolor: "#000000",
    font: { color: "#e5e5e5" },
    xaxis: {
      title: { text: `X (${unit.value})` },
      showgrid: true,
      gridcolor: "#333333",
      zeroline: true,
      zerolinecolor: "#555555",
      linecolor: "#555555",
      tickfont: { color: "#e5e5e5" },
      scaleanchor: "y",
      scaleratio: 1,
    },
    yaxis: {
      title: { text: `Y (${unit.value})` },
      showgrid: true,
      gridcolor: "#333333",
      zeroline: true,
      zerolinecolor: "#555555",
      linecolor: "#555555",
      tickfont: { color: "#e5e5e5" },
    },
    dragmode: "pan",

    showlegend: showLegend.value,

    legend: {
      x: 0,
      y: 1,
      xanchor: "left",
      yanchor: "top",
      bgcolor: "rgba(255, 255, 255, 0.7)",
    },
  };

  // xaxis/yaxis는 한 단계 더 깊게 merge해서 scaleanchor 같은 기본값이 통째로 사라지지 않게 함
  return {
    ...defaults,
    ...props.layout,
    xaxis: { ...defaults.xaxis, ...props.layout.xaxis },
    yaxis: { ...defaults.yaxis, ...props.layout.yaxis },
  };
}

const plotConfig: Partial<Config> = {
  responsive: true,
  displaylogo: false,
  scrollZoom: true,
  modeBarButtonsToRemove: ["select2d", "lasso2d"],
};

async function initializePlot() {
  const graph = getGraph();
  if (!graph) return;

  await Plotly.newPlot(
    graph,
    circuitObjects.value,
    buildBaseLayout(),
    plotConfig
  );
}

const MARKER_RADIUS_PX = 3;

const RULER_COLOR_SNAPPED = "#EFFF00";
const RULER_COLOR_UNSNAPPED = "#FF6A00";

function hexToRgba(hex: string, alpha: number): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

const ON_EDGE_EPSILON = 1e-6; // 기존 isPointOnEdge 기본 epsilon과 동일 (동치성 유지를 위해 맞춤)

/**
 * nearestEdge/snapped로부터 "최종 좌표가 정확히 edge 위인지"를 재탐색 없이 판정합니다.
 * - snapped === true: point는 nearestEdge.point 그 자체이므로 무조건 edge 위 (distance 0)
 * - snapped === false: point는 nearestEdge를 구할 때 쓴 바로 그 좌표이므로, nearestEdge.distance를
 *   epsilon과 비교하는 것만으로 isPointOnEdge(point, ...)와 완전히 동일한 결과를 얻습니다
 *   (같은 point에 대한 탐색이라 재탐색해도 결과가 같기 때문입니다).
 */
function isFinallyOnEdge(
  nearestEdge: NearestEdgeInfo | null,
  snapped: boolean
): boolean {
  if (snapped) {
    return true;
  }

  return nearestEdge !== null && nearestEdge.distance <= ON_EDGE_EPSILON;
}

/**
 * start/end가 둘 다 object edge에 실제로 닿아있는지로 ruler 색을 정합니다.
 * (snap threshold 안이어도 Snap이 꺼져 있으면 정확히 edge 위가 아닐 수 있음)
 *
 * 매 프레임 isPointOnEdge로 재탐색하지 않고, applySnap 호출 시점에 이미 기록해둔
 * startOnEdge/endOnEdge를 그대로 씁니다 (findNearestEdgeInfo 프레임당 2회 절감).
 */
function measurementColor(edges: {
  startOnEdge: boolean;
  endOnEdge: boolean;
}): string {
  return edges.startOnEdge && edges.endOnEdge
    ? RULER_COLOR_SNAPPED
    : RULER_COLOR_UNSNAPPED;
}

const HOVER_EDGE_COLOR = "#39FF14";
const HOVER_MARKER_RADIUS_PX = 3;

function buildHoverEdgeShapes() {
  if (!hoveredEdge.value) {
    return [];
  }

  const { a, b, snapPoint } = hoveredEdge.value;
  const hoverMarkerRadius = getMarkerSize(HOVER_MARKER_RADIUS_PX);

  return [
    {
      type: "line" as const,
      x0: a.x,
      y0: a.y,
      x1: b.x,
      y1: b.y,
      line: {
        color: HOVER_EDGE_COLOR,
        width: 1,
        dash: "dot" as const,
      },
      opacity: 0.6,
    },
    {
      type: "circle" as const,
      x0: snapPoint.x - hoverMarkerRadius,
      x1: snapPoint.x + hoverMarkerRadius,
      y0: snapPoint.y - hoverMarkerRadius,
      y1: snapPoint.y + hoverMarkerRadius,
      fillcolor: HOVER_EDGE_COLOR,
      line: {
        color: "#000000",
        width: 1,
      },
      opacity: 0.9,
    },
  ];
}

function buildRulerShapes(entry: { start: Point; end: Point; color: string }) {
  const { start, end, color } = entry;
  const markerSize = getMarkerSize(MARKER_RADIUS_PX);

  const hollowMarker = (center: Point) => ({
    type: "circle" as const,
    x0: center.x - markerSize,
    x1: center.x + markerSize,
    y0: center.y - markerSize,
    y1: center.y + markerSize,
    fillcolor: hexToRgba(color, 0.15),
    line: {
      color: color,
      width: 1,
    },
  });

  return [
    {
      type: "line" as const,
      x0: start.x,
      y0: start.y,
      x1: end.x,
      y1: end.y,
      line: {
        color: color,
        width: 1,
        dash: "dot" as const,
      },
    },
    hollowMarker(start),
    hollowMarker(end),
  ];
}

const LABEL_MARGIN_PX = 3;

// distance는 start/end 좌표만으로 정해지므로 그때그때 계산합니다 (완료된 항목은 정적이라 재계산 비용이 없음).
function buildRulerAnnotation(entry: {
  end: Point;
  distance: number;
  color: string;
}) {
  return {
    x: entry.end.x,
    y: entry.end.y,
    xanchor: "left" as const,
    yanchor: "top" as const,
    xshift: LABEL_MARGIN_PX,
    yshift: -LABEL_MARGIN_PX,
    text: `${entry.distance.toFixed(2)} ${unit.value}`,
    showarrow: false,
    font: { color: entry.color, size: 8, weight: 300 },
  };
}

/**
 * 완료된 측정(measurements)과 진행 중인 측정(startPoint~currentPoint, isMeasuring일 때만)을
 * 합쳐 렌더링용 entry 목록으로 만듭니다. 진행 중인 측정은 measurement.value.distance를
 * 재사용해 매 프레임 재계산하지 않습니다 (buildRulerAnnotation 참고).
 */
function buildRenderEntries() {
  const entries = measurements.value.map((m) => ({
    start: m.start,
    end: m.end,
    color: measurementColor(m),
    distance: getDistance(m.start, m.end),
  }));

  if (isMeasuring.value && startPoint.value && currentPoint.value) {
    entries.push({
      start: startPoint.value,
      end: currentPoint.value,
      color: measurementColor({
        startOnEdge: startOnEdge.value,
        endOnEdge: endOnEdge.value,
      }),
      distance: measurement.value.distance,
    });
  }

  return entries;
}

// 측정 중에는 Plotly.react()가 아니라 shapes/annotations만 relayout합니다.
async function updateRuler() {
  const graph = getGraph();
  if (!graph) return;

  const entries = buildRenderEntries();

  isSyncingRuler = true;

  try {
    await Plotly.relayout(graph, {
      shapes: [
        ...buildHoverEdgeShapes(),
        ...entries.flatMap((entry) => buildRulerShapes(entry)),
      ],
      annotations: entries.map((entry) => buildRulerAnnotation(entry)),
    });
  } finally {
    isSyncingRuler = false;
  }
}

async function updatePlot() {
  const graph = getGraph();
  if (!graph) return;

  await Plotly.react(
    graph,
    circuitObjects.value,
    buildBaseLayout(),
    plotConfig
  );

  if (hasMeasurement.value) {
    await updateRuler();
  }
}

// 첫 클릭: object edge 근처에서만 측정을 시작합니다 (빈 공간 오클릭 방지)
function startMeasurement(rawPoint: Point) {
  const nearestEdge = findNearestEdgeInfo(rawPoint, circuitGeometry.value);

  if (!nearestEdge || nearestEdge.distance > getSnapThreshold()) {
    return;
  }

  const { point, snapped } = applySnap(rawPoint, nearestEdge);

  startPoint.value = point;
  currentPoint.value = point;
  startEdgeInfo.value = nearestEdge;
  startOnEdge.value = isFinallyOnEdge(nearestEdge, snapped);
  endOnEdge.value = startOnEdge.value; // 시작 시점은 start === end
  isMeasuring.value = true;
  measurement.value = calculateMeasurement(
    point,
    point,
    circuitGeometry.value,
    getSnapThreshold(),
    { startEdge: nearestEdge, endEdge: nearestEdge }
  );

  void updateRuler();
}

// 두 번째 클릭: edge 근처가 아니어도 확정합니다 (start와 달리 end는 임의 지점 허용)
function finishMeasurement(rawPoint: Point, event: MouseEvent) {
  if (!startPoint.value) {
    return;
  }

  const { constrainedPoint, nearestEdge } = resolveConstrainedPoint(
    startPoint.value,
    rawPoint,
    event.shiftKey
  );
  const { point, snapped } = applySnap(constrainedPoint, nearestEdge);

  currentPoint.value = point;
  endOnEdge.value = isFinallyOnEdge(nearestEdge, snapped);
  measurement.value = calculateMeasurement(
    startPoint.value,
    point,
    circuitGeometry.value,
    getSnapThreshold(),
    { startEdge: startEdgeInfo.value, endEdge: nearestEdge }
  );

  emit("measure", measurement.value);

  // 완료된 측정을 누적 목록으로 옮기고, 다음 측정을 위해 진행 중 상태는 비웁니다
  // (measurements에 남아있으니 여러 개를 동시에 표시할 수 있습니다).
  measurements.value.push({
    start: startPoint.value,
    end: point,
    startOnEdge: startOnEdge.value,
    endOnEdge: endOnEdge.value,
  });

  isMeasuring.value = false;
  startPoint.value = null;
  currentPoint.value = null;
  startEdgeInfo.value = null;
  startOnEdge.value = false;
  endOnEdge.value = false;

  cancelScheduledRulerUpdate();
  void updateRuler();
}

function handleMouseDown(event: MouseEvent) {
  if (!rulerMode.value || event.button !== 0) {
    return;
  }

  // modebar 클릭도 graph 내부라 여기로 버블링됨: 가로채지 않고 Ruler를 꺼서 Zoom/Pan이 그대로 동작하게 함
  const target = event.target as HTMLElement | null;

  if (target?.closest(".modebar")) {
    void toggleRuler();

    return;
  }

  // legend 클릭도 버블링되지만 dragmode와 무관하므로 ruler 클릭만 막음 (ruler는 끄지 않음)
  if (target?.closest(".legend")) {
    return;
  }

  const rawPoint = getPlotPoint(event);

  if (!rawPoint) {
    return;
  }

  if (isMeasuring.value) {
    finishMeasurement(rawPoint, event);
  } else {
    startMeasurement(rawPoint);
  }

  event.preventDefault();
}

/**
 * mousemove가 한 프레임 안에 여러 번(트랙패드 스크롤 제스처와 겹칠 때 특히) 발생하면,
 * 예전엔 "그리기"만 rAF로 프레임당 1회로 묶이고 findNearestEdgeInfo 같은 무거운 탐색은
 * 매 mousemove마다 동기적으로 실행됐습니다. hover 중(isHovering=true) 스크롤 줌을 하면
 * 트랙패드가 mousemove를 같이 쏟아내면서, 이미 무거운 Plotly의 zoom 재렌더링과 겹쳐
 * 렉이 커지는 원인이었습니다. handleMouseMove는 이제 가벼운 좌표만 저장해두고,
 * 실제 탐색/스냅 계산은 여기서 그리기와 함께 rAF로 한 프레임당 최대 1회만 실행합니다.
 */
let pendingMouseMove: { rawPoint: Point; shiftKey: boolean } | null = null;

function processPendingMouseMove() {
  if (!pendingMouseMove) {
    return;
  }

  const { rawPoint, shiftKey } = pendingMouseMove;
  pendingMouseMove = null;

  if (!isMeasuring.value || !startPoint.value) {
    updateHoveredEdge(rawPoint);
    return;
  }

  // Shift 축 고정 시 스냅이 축을 벗어나지 않도록, 고정 축과 실제로 교차하는 edge만 탐색
  // (resolveConstrainedPoint 참고). updateHoveredEdge/applySnap/calculateMeasurement가
  // 이 nearestEdge를 그대로 재사용합니다.
  const { constrainedPoint, nearestEdge } = resolveConstrainedPoint(
    startPoint.value,
    rawPoint,
    shiftKey
  );

  updateHoveredEdge(constrainedPoint, nearestEdge);

  const { point, snapped } = applySnap(constrainedPoint, nearestEdge);

  currentPoint.value = point;
  endOnEdge.value = isFinallyOnEdge(nearestEdge, snapped);
  measurement.value = calculateMeasurement(
    startPoint.value,
    point,
    circuitGeometry.value,
    getSnapThreshold(),
    { startEdge: startEdgeInfo.value, endEdge: nearestEdge }
  );

  emit("measure", measurement.value);
}

function scheduleRulerUpdate() {
  if (rulerRafId !== null) {
    return;
  }

  rulerRafId = requestAnimationFrame(() => {
    rulerRafId = null;
    processPendingMouseMove();
    void updateRuler();
  });
}

/**
 * plotly_relayout(zoom/pan)이 유발하는 marker 재계산은 rAF가 아니라 짧은 debounce로 묶습니다.
 * scroll zoom처럼 plotly_relayout이 아주 짧은 간격으로 연달아 발생하면, 우리 updateRuler()의
 * Plotly.relayout() 호출이 미처 끝나기도 전에(isSyncingRuler는 그 호출 "동안"만 막아줌) Plotly
 * 자체의 다음 zoom relayout이 같은 gd에 겹쳐 들어오면서 두 relayout이 서로의 결과를 덮어써
 * ruler shapes/annotations가 순간적으로 사라지는 경쟁 상태가 있었습니다. rAF(프레임당 1회)는
 * 이 정도로 촘촘한 연속 이벤트를 막기엔 촘촘하므로, zoom이 짧게라도 멈춘 뒤 한 번만 다시
 * 그리도록 debounce합니다.
 */
let rulerResizeTimeoutId: ReturnType<typeof setTimeout> | null = null;
const RULER_RESIZE_DEBOUNCE_MS = 150;

function scheduleRulerResizeUpdate() {
  if (rulerResizeTimeoutId !== null) {
    clearTimeout(rulerResizeTimeoutId);
  }

  rulerResizeTimeoutId = setTimeout(() => {
    rulerResizeTimeoutId = null;
    void updateRuler();
  }, RULER_RESIZE_DEBOUNCE_MS);
}

function cancelScheduledRulerUpdate() {
  if (rulerRafId !== null) {
    cancelAnimationFrame(rulerRafId);
    rulerRafId = null;
  }

  pendingMouseMove = null;

  if (rulerResizeTimeoutId !== null) {
    clearTimeout(rulerResizeTimeoutId);
    rulerResizeTimeoutId = null;
  }
}

/**
 * 화면에 그려진 ruler/hover가 하나도 없으면 다시 그릴 것도 없으므로 스케줄조차 하지 않습니다.
 * 이 가드가 없으면 scroll zoom처럼 plotly_relayout이 짧은 시간에 여러 번 발생하는 상황에서
 * 매번 불필요한 Plotly.relayout()을 추가로 호출하게 되어, object가 많은 차트에서 Plotly
 * 자체 zoom 렌더링과 경합해 버벅임이 두드러집니다.
 */
function handlePlotlyRelayout() {
  if (isSyncingRuler) {
    return;
  }

  if (!hasMeasurement.value && !hoveredEdge.value) {
    return;
  }

  scheduleRulerResizeUpdate();
}

function handleMouseMove(event: MouseEvent) {
  if (!rulerMode.value) {
    return;
  }

  // mousemove는 document 레벨이라 chart 인스턴스가 여러 개면 전부 이 핸들러를 받습니다.
  // 이 인스턴스 위에 마우스가 없고 진행 중인 측정도 없으면 findNearestEdgeInfo 같은 무거운
  // 탐색을 할 이유가 없으므로 여기서 걸러냅니다 (handleKeyDown과 동일 패턴). 측정 중일 때는
  // 마우스가 이 chart 밖으로 나가도 계속 갱신되어야 하므로 isMeasuring을 OR로 남겨둡니다.
  if (!isHovering.value && !isMeasuring.value) {
    return;
  }

  // legend/modebar 위에서는 hover 하이라이트를 갱신하지 않음 (측정 중이면 계속 진행)
  const target = event.target as HTMLElement | null;

  if (
    (!isMeasuring.value || !startPoint.value) &&
    (target?.closest(".legend") || target?.closest(".modebar"))
  ) {
    return;
  }

  const rawPoint = getPlotPoint(event);

  if (!rawPoint) {
    return;
  }

  // 무거운 탐색(findNearestEdgeInfo)은 여기서 하지 않고 좌표만 저장해둡니다.
  // processPendingMouseMove(scheduleRulerUpdate 참고)가 그리기와 함께 rAF로
  // 프레임당 최대 1회만 실제 탐색/스냅 계산을 수행합니다.
  pendingMouseMove = { rawPoint, shiftKey: event.shiftKey };
  scheduleRulerUpdate();
}

// 첫 클릭만 찍힌 진행 중 측정만 취소합니다. measurements(완료된 항목들)는 건드리지 않습니다.
async function cancelInProgressMeasurement() {
  isMeasuring.value = false;
  startPoint.value = null;
  currentPoint.value = null;
  startEdgeInfo.value = null;
  startOnEdge.value = false;
  endOnEdge.value = false;

  await updateRuler();
}

/**
 * Ruler를 끄면서 dragmode를 finalDragmode로 전환합니다. 완료된 ruler들은 지우지 않고,
 * 첫 클릭만 찍힌 미완성 측정만 취소합니다 (전부 지우는 건 Clear 버튼만). Ruler 버튼/단축키/
 * Escape/Zoom·Pan 단축키가 모두 이 기준을 공유합니다.
 */
async function exitRulerMode(finalDragmode: "pan" | "zoom") {
  cancelScheduledRulerUpdate();

  rulerMode.value = false;
  hoveredEdge.value = null;

  const graph = getGraph();

  if (!graph) {
    return;
  }

  await Plotly.relayout(graph, { dragmode: finalDragmode });

  if (isMeasuring.value) {
    await cancelInProgressMeasurement();
  } else {
    await updateRuler();
  }
}

async function toggleRuler() {
  if (rulerMode.value) {
    await exitRulerMode("pan");
    return;
  }

  rulerMode.value = true;

  const graph = getGraph();

  if (!graph) {
    return;
  }

  await Plotly.relayout(graph, { dragmode: false });
}

async function toggleSnap() {
  snapEnabled.value = !snapEnabled.value;

  if (!snapEnabled.value) {
    hoveredEdge.value = null;
  }

  await updateRuler();
}

async function toggleLegend() {
  showLegend.value = !showLegend.value;

  const graph = getGraph();

  if (!graph) {
    return;
  }

  await Plotly.relayout(graph, { showlegend: showLegend.value });
}

async function clearMeasurement() {
  cancelScheduledRulerUpdate();

  isMeasuring.value = false;
  startPoint.value = null;
  currentPoint.value = null;
  startEdgeInfo.value = null;
  startOnEdge.value = false;
  endOnEdge.value = false;
  measurements.value = [];
  measurement.value = { dx: 0, dy: 0, distance: 0 };

  // 부모가 measure 이벤트를 구독 중일 수 있어 리셋값도 emit
  emit("measure", measurement.value);

  const graph = getGraph();

  if (!graph) {
    return;
  }

  await Plotly.relayout(graph, { shapes: [], annotations: [] });
}

// i/o/a/x/d: dragmode와 무관한 1회성 액션이라 Ruler 상태는 건드리지 않고 modebar 버튼을 그대로 클릭합니다.
const MODEBAR_ACTION_KEYS: Record<string, string> = {
  i: "Zoom in",
  o: "Zoom out",
  a: "Autoscale",
  x: "Reset axes",
  d: "Download plot as a PNG",
};

function clickModebarButton(dataTitle: string) {
  const graph = getGraph();

  graph
    ?.querySelector<HTMLElement>(`.modebar-btn[data-title="${dataTitle}"]`)
    ?.click();
}

const shortcutsPopoverOpen = ref(false);

function handleShortcutClick(item: { run: () => void }) {
  item.run();
  shortcutsPopoverOpen.value = false;
}

// ❓ 팝오버에 표시할 단축키 목록. 행을 클릭하면 실제로 그 키를 누른 것과 동일한 동작이
// 실행되도록 run을 같이 둡니다 (handleKeyDown의 분기와 동일한 함수를 그대로 재사용).
// modebar 액션 5개는 MODEBAR_ACTION_KEYS를 그대로 재사용해 이름이 어긋나지 않게 합니다.
const SHORTCUT_LIST: { key: string; action: string; run: () => void }[] = [
  { key: "R", action: "Ruler ON/OFF", run: () => void toggleRuler() },
  { key: "Z", action: "Zoom", run: () => void exitRulerMode("zoom") },
  { key: "P", action: "Pan", run: () => void exitRulerMode("pan") },
  ...Object.entries(MODEBAR_ACTION_KEYS).map(([key, action]) => ({
    key: key.toUpperCase(),
    action,
    run: () => clickModebarButton(action),
  })),
  { key: "Esc", action: "Ruler OFF", run: () => void exitRulerMode("zoom") },
];

function handleKeyDown(event: KeyboardEvent) {
  if (!isHovering.value && !isMeasuring.value) {
    return;
  }

  // Escape는 Ruler만 끄고 Pan이 아닌 Zoom으로 전환합니다.
  if (event.key === "Escape") {
    void exitRulerMode("zoom");
    return;
  }

  // 키를 누르고 있으면 반복 keydown이 발생하므로 최초 누름에서만 반응
  if (event.repeat) {
    return;
  }

  const key = event.key.toLowerCase();

  if (key === "r") {
    void toggleRuler();
    return;
  }

  // Zoom/Pan은 dragmode를 false 아닌 값으로 바꾸므로 Ruler와 같이 켜둘 수 없어 항상 Ruler를 끕니다.
  if (key === "z") {
    void exitRulerMode("zoom");
    return;
  }

  if (key === "p") {
    void exitRulerMode("pan");
    return;
  }

  const modebarTitle = MODEBAR_ACTION_KEYS[key];

  if (modebarTitle) {
    clickModebarButton(modebarTitle);
  }
}

watch(
  () => props.objects,
  () => void updatePlot(),
  { deep: true }
);

onMounted(async () => {
  await nextTick();

  const graph = getGraph();

  if (!graph) {
    return;
  }

  await initializePlot();

  // mousemove는 그래프 밖으로 나가도 놓치지 않도록 document에서 받음
  graph.addEventListener("mousedown", handleMouseDown);
  document.addEventListener("mousemove", handleMouseMove);
  document.addEventListener("keydown", handleKeyDown);

  (graph as any).on("plotly_relayout", handlePlotlyRelayout);
});

onBeforeUnmount(() => {
  cancelScheduledRulerUpdate();

  const graph = getGraph();

  if (graph) {
    graph.removeEventListener("mousedown", handleMouseDown);
    (graph as any).removeListener("plotly_relayout", handlePlotlyRelayout);
  }

  document.removeEventListener("mousemove", handleMouseMove);
  document.removeEventListener("keydown", handleKeyDown);

  if (graph) {
    Plotly.purge(graph);
  }
});
</script>
