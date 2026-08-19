<template>
  <div class="w-full h-full flex flex-col">
    <!-- Toolbar -->
    <div class="flex items-center gap-2 p-2 border-b bg-white">
      <a-button
        :type="rulerMode ? 'primary' : 'default'"
        @click="toggleRuler"
      >
        📏 {{ rulerMode ? 'Ruler ON' : 'Ruler OFF' }}
      </a-button>

      <a-button
        :disabled="!hasMeasurement"
        @click="clearRuler"
      >
        Clear
      </a-button>

      <!-- Measurement result -->
      <div
        v-if="hasMeasurement"
        class="ml-4 flex items-center gap-4 text-sm"
      >
        <span>
          ΔX:
          <strong>{{ measurement.dx.toFixed(2) }}</strong>
          {{ unit }}
        </span>

        <span>
          ΔY:
          <strong>{{ measurement.dy.toFixed(2) }}</strong>
          {{ unit }}
        </span>

        <span>
          Distance:
          <strong>{{ measurement.distance.toFixed(2) }}</strong>
          {{ unit }}
        </span>
      </div>

      <div
        v-if="rulerMode && !isDragging"
        class="ml-auto text-gray-500 text-sm"
      >
        Click & Drag to measure
      </div>

      <div
        v-if="isDragging"
        class="ml-auto text-blue-500 text-sm"
      >
        Measuring...
      </div>
    </div>

    <!-- Plotly -->
    <div
      ref="plotContainer"
      class="flex-1 min-h-0 relative"
    >
      <Plotly
        ref="plotly"
        :data="plotData"
        :layout="plotLayout"
        :config="plotConfig"
        class="w-full h-full"
        @after-plot="onAfterPlot"
      />

      <!-- Ruler information overlay -->
      <div
        v-if="rulerMode && isDragging"
        class="
          absolute
          top-3
          right-3
          px-3
          py-2
          rounded
          bg-white
          border
          shadow
          text-sm
          pointer-events-none
        "
      >
        <div>
          ΔX:
          <strong>{{ currentMeasurement.dx.toFixed(2) }}</strong>
          {{ unit }}
        </div>

        <div>
          ΔY:
          <strong>{{ currentMeasurement.dy.toFixed(2) }}</strong>
          {{ unit }}
        </div>

        <div>
          Distance:
          <strong>
            {{ currentMeasurement.distance.toFixed(2) }}
          </strong>
          {{ unit }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import Plotly from 'vue-plotly'
import type {
  Data,
  Layout,
  Config
} from 'plotly.js'

import { Button as AButton } from 'ant-design-vue'

/* ------------------------------------------------------------------
 * Types
 * ---------------------------------------------------------------- */

interface Point {
  x: number
  y: number
}

interface Measurement {
  dx: number
  dy: number
  distance: number
}

/* ------------------------------------------------------------------
 * Props
 * ---------------------------------------------------------------- */

interface Props {
  unit?: string
}

const props = withDefaults(defineProps<Props>(), {
  unit: 'μm'
})

const unit = computed(() => props.unit)

/* ------------------------------------------------------------------
 * Refs
 * ---------------------------------------------------------------- */

const plotly = ref<any>(null)

const plotContainer = ref<HTMLElement | null>(null)

const rulerMode = ref(false)

const isDragging = ref(false)

const startPoint = ref<Point | null>(null)

const currentPoint = ref<Point | null>(null)

const measurement = ref<Measurement>({
  dx: 0,
  dy: 0,
  distance: 0
})

/* ------------------------------------------------------------------
 * Example Wafer data
 *
 * 실제 프로젝트에서는 이 부분을
 * props 또는 API 데이터로 변경하면 됩니다.
 * ---------------------------------------------------------------- */

const waferX: number[] = []
const waferY: number[] = []
const waferColor: number[] = []

for (let y = -10; y <= 10; y++) {
  for (let x = -10; x <= 10; x++) {
    const distance = Math.sqrt(x * x + y * y)

    if (distance <= 10) {
      waferX.push(x * 1000)
      waferY.push(y * 1000)
      waferColor.push(Math.random())
    }
  }
}

/* ------------------------------------------------------------------
 * Plotly Data
 * ---------------------------------------------------------------- */

const plotData = computed<Data[]>(() => {
  return [
    {
      type: 'scatter',
      mode: 'markers',

      x: waferX,
      y: waferY,

      marker: {
        size: 18,
        color: waferColor,
        colorscale: 'Viridis',
        showscale: true
      },

      hovertemplate:
        'X: %{x:.0f} ' +
        `${unit.value}<br>` +
        'Y: %{y:.0f} ' +
        `${unit.value}` +
        '<extra></extra>'
    }
  ]
})

/* ------------------------------------------------------------------
 * Plotly Layout
 * ---------------------------------------------------------------- */

const plotLayout = computed<Partial<Layout>>(() => {
  const layout: Partial<Layout> = {
    margin: {
      l: 60,
      r: 30,
      t: 30,
      b: 60
    },

    xaxis: {
      title: {
        text: `X (${unit.value})`
      },

      scaleanchor: 'y',
      scaleratio: 1,

      zeroline: true,

      showgrid: true
    },

    yaxis: {
      title: {
        text: `Y (${unit.value})`
      },

      zeroline: true,

      showgrid: true
    },

    hovermode: 'closest',

    dragmode: rulerMode.value ? false : 'pan',

    shapes: [],
    annotations: []
  }

  /*
   * Ruler
   */
  if (
    startPoint.value &&
    currentPoint.value
  ) {
    const start = startPoint.value
    const end = currentPoint.value

    const dx = end.x - start.x
    const dy = end.y - start.y

    const distance = Math.sqrt(
      dx * dx + dy * dy
    )

    /*
     * Measurement line
     */
    layout.shapes = [
      {
        type: 'line',

        x0: start.x,
        y0: start.y,

        x1: end.x,
        y1: end.y,

        line: {
          width: 3,
          color: '#1677ff'
        }
      },

      /*
       * Start point
       */
      {
        type: 'circle',

        x0: start.x - 30,
        x1: start.x + 30,

        y0: start.y - 30,
        y1: start.y + 30,

        line: {
          width: 2,
          color: '#1677ff'
        },

        fillcolor: '#1677ff'
      },

      /*
       * End point
       */
      {
        type: 'circle',

        x0: end.x - 30,
        x1: end.x + 30,

        y0: end.y - 30,
        y1: end.y + 30,

        line: {
          width: 2,
          color: '#1677ff'
        },

        fillcolor: '#1677ff'
      }
    ]

    /*
     * Measurement label
     */
    layout.annotations = [
      {
        x: (start.x + end.x) / 2,
        y: (start.y + end.y) / 2,

        text:
          `ΔX: ${Math.abs(dx).toFixed(2)} ${unit.value}` +
          `<br>` +
          `ΔY: ${Math.abs(dy).toFixed(2)} ${unit.value}` +
          `<br>` +
          `<b>${distance.toFixed(2)} ${unit.value}</b>`,

        showarrow: false,

        bgcolor: 'white',

        bordercolor: '#1677ff',

        borderwidth: 1,

        borderpad: 5,

        font: {
          size: 12
        }
      }
    ]
  }

  return layout
})

/* ------------------------------------------------------------------
 * Plotly Config
 * ---------------------------------------------------------------- */

const plotConfig = computed<Partial<Config>>(() => {
  return {
    responsive: true,

    displaylogo: false,

    modeBarButtonsToRemove: [
      'select2d',
      'lasso2d'
    ],

    scrollZoom: true
  }
})

/* ------------------------------------------------------------------
 * Measurement
 * ---------------------------------------------------------------- */

const calculateMeasurement = (
  start: Point,
  end: Point
): Measurement => {
  const dx = end.x - start.x

  const dy = end.y - start.y

  const distance = Math.sqrt(
    dx * dx + dy * dy
  )

  return {
    dx: Math.abs(dx),
    dy: Math.abs(dy),
    distance
  }
}

/* ------------------------------------------------------------------
 * Current measurement
 * ---------------------------------------------------------------- */

const currentMeasurement = computed<Measurement>(() => {
  if (
    !startPoint.value ||
    !currentPoint.value
  ) {
    return {
      dx: 0,
      dy: 0,
      distance: 0
    }
  }

  return calculateMeasurement(
    startPoint.value,
    currentPoint.value
  )
})

/* ------------------------------------------------------------------
 * Has measurement
 * ---------------------------------------------------------------- */

const hasMeasurement = computed(() => {
  return (
    startPoint.value !== null &&
    currentPoint.value !== null
  )
})

/* ------------------------------------------------------------------
 * Plotly graph div
 * ---------------------------------------------------------------- */

const getGraphDiv = (): HTMLElement | null => {
  if (!plotly.value) {
    return null
  }

  /*
   * vue-plotly exposes Plotly graph div
   */
  return (
    plotly.value.$el?.querySelector('.js-plotly-plot') ??
    plotly.value.$el ??
    null
  )
}

/* ------------------------------------------------------------------
 * Convert mouse pixel → Plotly coordinate
 * ---------------------------------------------------------------- */

const getPlotPoint = (
  event: MouseEvent
): Point | null => {
  const graph = getGraphDiv()

  if (!graph) {
    return null
  }

  const gd = graph as any

  const fullLayout = gd._fullLayout

  if (!fullLayout) {
    return null
  }

  const rect = graph.getBoundingClientRect()

  /*
   * Mouse position relative to graph
   */
  const px =
    event.clientX - rect.left

  const py =
    event.clientY - rect.top

  /*
   * Plot area coordinates
   */
  const xaxis = fullLayout.xaxis
  const yaxis = fullLayout.yaxis

  if (
    !xaxis ||
    !yaxis
  ) {
    return null
  }

  /*
   * Plotly pixel → data coordinate
   */
  const x =
    xaxis.p2l(
      px - xaxis._offset
    )

  const y =
    yaxis.p2l(
      py - yaxis._offset
    )

  return {
    x,
    y
  }
}

/* ------------------------------------------------------------------
 * Mouse Down
 * ---------------------------------------------------------------- */

const handleMouseDown = (
  event: MouseEvent
) => {
  if (!rulerMode.value) {
    return
  }

  /*
   * Only left mouse button
   */
  if (event.button !== 0) {
    return
  }

  const point = getPlotPoint(event)

  if (!point) {
    return
  }

  startPoint.value = point

  currentPoint.value = point

  isDragging.value = true

  event.preventDefault()
}

/* ------------------------------------------------------------------
 * Mouse Move
 * ---------------------------------------------------------------- */

const handleMouseMove = (
  event: MouseEvent
) => {
  if (
    !rulerMode.value ||
    !isDragging.value ||
    !startPoint.value
  ) {
    return
  }

  const point = getPlotPoint(event)

  if (!point) {
    return
  }

  currentPoint.value = point

  measurement.value =
    calculateMeasurement(
      startPoint.value,
      point
    )
}

/* ------------------------------------------------------------------
 * Mouse Up
 * ---------------------------------------------------------------- */

const handleMouseUp = (
  event: MouseEvent
) => {
  if (
    !rulerMode.value ||
    !isDragging.value
  ) {
    return
  }

  const point = getPlotPoint(event)

  if (point) {
    currentPoint.value = point

    if (startPoint.value) {
      measurement.value =
        calculateMeasurement(
          startPoint.value,
          point
        )
    }
  }

  isDragging.value = false
}

/* ------------------------------------------------------------------
 * Toggle Ruler
 * ---------------------------------------------------------------- */

const toggleRuler = async () => {
  rulerMode.value =
    !rulerMode.value

  if (!rulerMode.value) {
    isDragging.value = false
    startPoint.value = null
    currentPoint.value = null
  }

  await nextTick()
}

/* ------------------------------------------------------------------
 * Clear
 * ---------------------------------------------------------------- */

const clearRuler = () => {
  isDragging.value = false

  startPoint.value = null

  currentPoint.value = null

  measurement.value = {
    dx: 0,
    dy: 0,
    distance: 0
  }
}

/* ------------------------------------------------------------------
 * ESC
 * ---------------------------------------------------------------- */

const handleKeyDown = (
  event: KeyboardEvent
) => {
  if (event.key === 'Escape') {
    rulerMode.value = false

    isDragging.value = false

    startPoint.value = null

    currentPoint.value = null
  }
}

/* ------------------------------------------------------------------
 * Plotly rendered
 * ---------------------------------------------------------------- */

const onAfterPlot = () => {
  /*
   * Nothing required here currently.
   *
   * Plotly is rendered asynchronously,
   * so event listeners are attached
   * to document/window instead.
   */
}

/* ------------------------------------------------------------------
 * Lifecycle
 * ---------------------------------------------------------------- */

onMounted(() => {
  document.addEventListener(
    'mousedown',
    handleMouseDown
  )

  document.addEventListener(
    'mousemove',
    handleMouseMove
  )

  document.addEventListener(
    'mouseup',
    handleMouseUp
  )

  document.addEventListener(
    'keydown',
    handleKeyDown
  )
})

onBeforeUnmount(() => {
  document.removeEventListener(
    'mousedown',
    handleMouseDown
  )

  document.removeEventListener(
    'mousemove',
    handleMouseMove
  )

  document.removeEventListener(
    'mouseup',
    handleMouseUp
  )

  document.removeEventListener(
    'keydown',
    handleKeyDown
  )
})
</script>