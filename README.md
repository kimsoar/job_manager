npm install plotly.js-dist-min vue-plotly
npm install -D @types/plotly.js


<template>
  <div class="w-full rounded-xl border border-slate-200 bg-white p-4">
    <!-- Header -->
    <div class="mb-4 flex items-center justify-between">
      <div>
        <h2 class="text-lg font-semibold text-slate-800">
          Wafer Map
        </h2>
        <p class="text-sm text-slate-500">
          Lot: LOT-001 / Wafer: 01
        </p>
      </div>
      <!-- Legend -->
      <div class="flex items-center gap-4 text-sm">
        <div class="flex items-center gap-1.5">
          <span class="h-3 w-3 rounded-full bg-green-500"></span>
          <span>양품</span>
        </div>
        <div class="flex items-center gap-1.5">
          <span class="h-3 w-3 rounded-full bg-red-500"></span>
          <span>불량</span>
        </div>
        <div class="flex items-center gap-1.5">
          <span class="h-3 w-3 rounded-full bg-slate-300"></span>
          <span>미측정</span>
        </div>
      </div>
    </div>
    <!-- Wafer -->
    <div class="flex justify-center">
      <VuePlotly
        :data="plotData"
        :layout="layout"
        :config="config"
        class="h-[600px] w-full"
      />
    </div>
    <!-- Summary -->
    <div class="mt-4 grid grid-cols-3 gap-3">
      <div class="rounded-lg bg-slate-50 p-3">
        <div class="text-xs text-slate-500">
          Total
        </div>
        <div class="mt-1 text-xl font-semibold text-slate-800">
          {{ totalCount }}
        </div>
      </div>
      <div class="rounded-lg bg-green-50 p-3">
        <div class="text-xs text-green-600">
          Good
        </div>
        <div class="mt-1 text-xl font-semibold text-green-700">
          {{ goodCount }}
        </div>
      </div>
      <div class="rounded-lg bg-red-50 p-3">
        <div class="text-xs text-red-600">
          Fail
        </div>
        <div class="mt-1 text-xl font-semibold text-red-700">
          {{ failCount }}
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import VuePlotly from 'vue-plotly'
interface Die {
  x: number
  y: number
  row: number
  col: number
  status: 'GOOD' | 'FAIL' | 'EMPTY'
  bin?: number
  value?: number
}
/**
 * 샘플 Wafer 데이터
 *
 * 실제 프로젝트에서는 API에서 받아온 데이터를
 * 이 형태로 mapping해서 사용하면 됩니다.
 */
const dies: Die[] = []
const WAFER_RADIUS = 150
const DIE_SIZE = 10
/**
 * 샘플 Wafer Die 생성
 */
for (let row = -15; row <= 15; row++) {
  for (let col = -15; col <= 15; col++) {
    const x = col * DIE_SIZE
    const y = row * DIE_SIZE
    const distance = Math.sqrt(x * x + y * y)
    // Wafer 원 밖이면 제외
    if (distance > WAFER_RADIUS - 5) {
      continue
    }
    let status: Die['status'] = 'GOOD'
    // 일부 Die를 불량으로 설정
    if (
      (row === 3 && col === 2) ||
      (row === 4 && col === 2) ||
      (row === -4 && col === -5) ||
      (row === -5 && col === -5)
    ) {
      status = 'FAIL'
    }
    dies.push({
      x,
      y,
      row,
      col,
      status,
      bin: status === 'GOOD' ? 1 : 2,
      value: Math.round(Math.random() * 100) / 10,
    })
  }
}
/**
 * 상태별 데이터 분리
 */
const goodDies = computed(() =>
  dies.filter((die) => die.status === 'GOOD')
)
const failDies = computed(() =>
  dies.filter((die) => die.status === 'FAIL')
)
const emptyDies = computed(() =>
  dies.filter((die) => die.status === 'EMPTY')
)
/**
 * Plotly 데이터
 */
const plotData = computed(() => [
  // GOOD
  {
    x: goodDies.value.map((die) => die.x),
    y: goodDies.value.map((die) => die.y),
    type: 'scattergl',
    mode: 'markers',
    name: '양품',
    marker: {
      symbol: 'square',
      size: DIE_SIZE - 1,
      color: '#22c55e',
      line: {
        width: 0.5,
        color: '#166534',
      },
    },
    text: goodDies.value.map(
      (die) =>
        `Row: ${die.row}<br>` +
        `Col: ${die.col}<br>` +
        `Status: GOOD<br>` +
        `Bin: ${die.bin}<br>` +
        `Value: ${die.value}`
    ),
    hovertemplate:
      '%{text}<extra></extra>',
  },
  // FAIL
  {
    x: failDies.value.map((die) => die.x),
    y: failDies.value.map((die) => die.y),
    type: 'scattergl',
    mode: 'markers',
    name: '불량',
    marker: {
      symbol: 'square',
      size: DIE_SIZE - 1,
      color: '#ef4444',
      line: {
        width: 0.5,
        color: '#991b1b',
      },
    },
    text: failDies.value.map(
      (die) =>
        `Row: ${die.row}<br>` +
        `Col: ${die.col}<br>` +
        `Status: FAIL<br>` +
        `Bin: ${die.bin}<br>` +
        `Value: ${die.value}`
    ),
    hovertemplate:
      '%{text}<extra></extra>',
  },
  // EMPTY
  {
    x: emptyDies.value.map((die) => die.x),
    y: emptyDies.value.map((die) => die.y),
    type: 'scattergl',
    mode: 'markers',
    name: '미측정',
    marker: {
      symbol: 'square',
      size: DIE_SIZE - 1,
      color: '#cbd5e1',
      line: {
        width: 0.5,
        color: '#94a3b8',
      },
    },
    hovertemplate:
      '미측정<extra></extra>',
  },
  // Wafer Edge
  {
    x: createCircleX(WAFER_RADIUS),
    y: createCircleY(WAFER_RADIUS),
    type: 'scatter',
    mode: 'lines',
    name: 'Wafer',
    line: {
      color: '#334155',
      width: 2,
    },
    hoverinfo: 'skip',
    showlegend: false,
  },
  // Center Cross X
  {
    x: [-5, 5],
    y: [0, 0],
    type: 'scatter',
    mode: 'lines',
    line: {
      color: '#64748b',
      width: 1,
      dash: 'dot',
    },
    hoverinfo: 'skip',
    showlegend: false,
  },
  // Center Cross Y
  {
    x: [0, 0],
    y: [-5, 5],
    type: 'scatter',
    mode: 'lines',
    line: {
      color: '#64748b',
      width: 1,
      dash: 'dot',
    },
    hoverinfo: 'skip',
    showlegend: false,
  },
])
/**
 * Plotly Layout
 */
const layout = computed(() => ({
  autosize: true,
  margin: {
    l: 30,
    r: 30,
    t: 20,
    b: 30,
  },
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
  xaxis: {
    visible: false,
    range: [
      -WAFER_RADIUS - 10,
      WAFER_RADIUS + 10,
    ],
    scaleanchor: 'y',
    scaleratio: 1,
  },
  yaxis: {
    visible: false,
    range: [
      -WAFER_RADIUS - 10,
      WAFER_RADIUS + 10,
    ],
  },
  showlegend: false,
  hovermode: 'closest',
  dragmode: 'pan',
}))
/**
 * Plotly Config
 */
const config = {
  responsive: true,
  displaylogo: false,
  modeBarButtonsToRemove: [
    'select2d',
    'lasso2d',
    'autoScale2d',
  ],
  scrollZoom: true,
}
/**
 * Circle 좌표 생성
 */
function createCircleX(radius: number) {
  const result: number[] = []
  for (let i = 0; i <= 360; i++) {
    const radian = (i * Math.PI) / 180
    result.push(radius * Math.cos(radian))
  }
  return result
}
function createCircleY(radius: number) {
  const result: number[] = []
  for (let i = 0; i <= 360; i++) {
    const radian = (i * Math.PI) / 180
    result.push(radius * Math.sin(radian))
  }
  return result
}
/**
 * Summary
 */
const totalCount = computed(() => dies.length)
const goodCount = computed(() =>
  dies.filter((die) => die.status === 'GOOD').length
)
const failCount = computed(() =>
  dies.filter((die) => die.status === 'FAIL').length
)
</script>