<template>
  <div class="w-full h-full flex flex-col bg-white">

    <!-- Toolbar -->
    <div class="flex items-center gap-2 px-3 py-2 border-b shrink-0">

      <a-button
        :type="rulerMode ? 'primary' : 'default'"
        @click="toggleRuler"
      >
        📏 {{ rulerMode ? 'Ruler ON' : 'Ruler OFF' }}
      </a-button>

      <a-button
        :type="snapEnabled ? 'primary' : 'default'"
        :disabled="!rulerMode"
        @click="snapEnabled = !snapEnabled"
      >
        🧲 Snap {{ snapEnabled ? 'ON' : 'OFF' }}
      </a-button>

      <a-select
        v-model:value="snapMode"
        :disabled="!rulerMode || !snapEnabled"
        style="width: 130px"
      >
        <a-select-option value="nearest">
          Nearest
        </a-select-option>

        <a-select-option value="center">
          Center
        </a-select-option>

        <a-select-option value="corner">
          Corner
        </a-select-option>

        <a-select-option value="edge">
          Edge
        </a-select-option>
      </a-select>

      <a-button
        :disabled="!hasMeasurement"
        @click="clearMeasurement"
      >
        Clear
      </a-button>

      <!-- Measurement -->
      <div
        v-if="hasMeasurement"
        class="ml-4 flex items-center gap-5 text-sm"
      >
        <span>
          ΔX:
          <strong>
            {{ measurement.dx.toFixed(2) }}
          </strong>
          {{ unit }}
        </span>

        <span>
          ΔY:
          <strong>
            {{ measurement.dy.toFixed(2) }}
          </strong>
          {{ unit }}
        </span>

        <span>
          Distance:
          <strong>
            {{ measurement.distance.toFixed(2) }}
          </strong>
          {{ unit }}
        </span>

        <span
          v-if="measurement.startObject"
          class="text-gray-500"
        >
          {{ measurement.startObject }}

          →

          {{ measurement.endObject }}
        </span>
      </div>

      <span
        v-if="rulerMode && !isDragging"
        class="ml-auto text-gray-400 text-sm"
      >
        Drag to measure
      </span>

      <span
        v-if="isDragging"
        class="ml-auto text-blue-500 text-sm"
      >
        Measuring...
      </span>

    </div>

    <!-- Plotly -->
    <div
      ref="plotContainer"
      class="relative flex-1 min-h-0"
    >
      <div
        ref="plotElement"
        class="w-full h-full"
      />

      <!-- Current measurement -->
      <div
        v-if="rulerMode && isDragging"
        class="
          absolute
          top-3
          right-3
          pointer-events-none
          px-3
          py-2
          rounded
          border
          bg-white
          shadow
          text-sm
        "
      >
        <div>
          ΔX:
          <strong>
            {{ currentMeasurement.dx.toFixed(2) }}
          </strong>
          {{ unit }}
        </div>

        <div>
          ΔY:
          <strong>
            {{ currentMeasurement.dy.toFixed(2) }}
          </strong>
          {{ unit }}
        </div>

        <div>
          Distance:
          <strong>
            {{ currentMeasurement.distance.toFixed(2) }}
          </strong>
          {{ unit }}
        </div>

        <div
          v-if="currentMeasurement.startObject"
          class="text-gray-500"
        >
          {{ currentMeasurement.startObject }}
          →

          {{ currentMeasurement.endObject }}
        </div>
      </div>

      <!-- Snap information -->
      <div
        v-if="snapPoint"
        class="
          absolute
          bottom-3
          left-3
          px-2
          py-1
          bg-black
          text-white
          rounded
          text-xs
          pointer-events-none
        "
      >
        {{ snapPoint.type }}

        <span v-if="snapPoint.objectId">
          · {{ snapPoint.objectId }}
        </span>
      </div>

    </div>
  </div>
</template>


<script setup lang="ts">

import {
  computed,
  nextTick,
  onBeforeUnmount,
  onMounted,
  ref
} from 'vue'

import Plotly from 'plotly.js-dist-min'

import type {
  Config,
  Data,
  Layout,
  Shape,
  Annotations
} from 'plotly.js'

import {
  Button as AButton,
  Select as ASelect,
  SelectOption as ASelectOption
} from 'ant-design-vue'


/* ================================================================
 * Types
 * ================================================================ */

interface Point {
  x: number
  y: number
}


interface WaferObject {

  id: string

  x: number
  y: number

  width: number
  height: number
}


type SnapType =
  | 'center'
  | 'corner'
  | 'edge'


interface SnapPoint {

  x: number
  y: number

  type: SnapType

  objectId?: string

  corner?: string
}


interface Measurement {

  dx: number
  dy: number
  distance: number

  startObject?: string
  endObject?: string
}


/* ================================================================
 * Props
 * ================================================================ */

interface Props {

  unit?: string

  snapThresholdPx?: number
}


const props = withDefaults(
  defineProps<Props>(),
  {
    unit: 'μm',
    snapThresholdPx: 15
  }
)


const unit = computed(
  () => props.unit
)


/* ================================================================
 * Refs
 * ================================================================ */

const plotContainer =
  ref<HTMLElement | null>(null)

const plotElement =
  ref<HTMLElement | null>(null)


const rulerMode =
  ref(false)


const snapEnabled =
  ref(true)


const snapMode =
  ref<SnapType | 'nearest'>(
    'nearest'
  )


const isDragging =
  ref(false)


const startPoint =
  ref<Point | null>(null)


const currentPoint =
  ref<Point | null>(null)


const snapPoint =
  ref<SnapPoint | null>(null)


const measurement =
  ref<Measurement>({
    dx: 0,
    dy: 0,
    distance: 0
  })


/* ================================================================
 * Wafer Objects
 *
 * 실제 프로젝트에서는 props/API 데이터 사용
 * ================================================================ */

const waferObjects =
  ref<WaferObject[]>([
    {
      id: 'DIE_01',
      x: -30000,
      y: 0,
      width: 15000,
      height: 15000
    },

    {
      id: 'DIE_02',
      x: -10000,
      y: 0,
      width: 15000,
      height: 15000
    },

    {
      id: 'DIE_03',
      x: 10000,
      y: 0,
      width: 15000,
      height: 15000
    },

    {
      id: 'DIE_04',
      x: -30000,
      y: -20000,
      width: 15000,
      height: 15000
    },

    {
      id: 'DIE_05',
      x: -10000,
      y: -20000,
      width: 15000,
      height: 15000
    }
  ])


/* ================================================================
 * Geometry
 * ================================================================ */

function getCenter(
  obj: WaferObject
): Point {

  return {
    x: obj.x + obj.width / 2,
    y: obj.y + obj.height / 2
  }
}


function getCorners(
  obj: WaferObject
): SnapPoint[] {

  return [

    {
      x: obj.x,
      y: obj.y,

      type: 'corner',

      objectId: obj.id,

      corner: 'bottom-left'
    },

    {
      x: obj.x + obj.width,
      y: obj.y,

      type: 'corner',

      objectId: obj.id,

      corner: 'bottom-right'
    },

    {
      x: obj.x + obj.width,
      y: obj.y + obj.height,

      type: 'corner',

      objectId: obj.id,

      corner: 'top-right'
    },

    {
      x: obj.x,
      y: obj.y + obj.height,

      type: 'corner',

      objectId: obj.id,

      corner: 'top-left'
    }
  ]
}


function distance(
  a: Point,
  b: Point
): number {

  const dx =
    b.x - a.x

  const dy =
    b.y - a.y

  return Math.sqrt(
    dx * dx +
    dy * dy
  )
}


/* ================================================================
 * Closest point on Edge
 * ================================================================ */

function closestPointOnEdge(
  point: Point,
  obj: WaferObject
): SnapPoint {

  const left =
    obj.x

  const right =
    obj.x + obj.width

  const bottom =
    obj.y

  const top =
    obj.y + obj.height


  const x =
    Math.max(
      left,
      Math.min(
        point.x,
        right
      )
    )


  const y =
    Math.max(
      bottom,
      Math.min(
        point.y,
        top
      )
    )


  const distances = [

    {
      value: Math.abs(point.x - left),

      point: {
        x: left,
        y
      }
    },

    {
      value: Math.abs(point.x - right),

      point: {
        x: right,
        y
      }
    },

    {
      value: Math.abs(point.y - bottom),

      point: {
        x,
        y: bottom
      }
    },

    {
      value: Math.abs(point.y - top),

      point: {
        x,
        y: top
      }
    }

  ]


  distances.sort(
    (a, b) =>
      a.value - b.value
  )


  return {

    ...distances[0].point,

    type: 'edge',

    objectId: obj.id
  }
}


/* ================================================================
 * Snap Candidate
 * ================================================================ */

function findSnapCandidate(
  point: Point
): SnapPoint | null {

  if (!snapEnabled.value) {
    return null
  }


  let best:
    SnapPoint | null = null


  let bestDistance =
    Number.POSITIVE_INFINITY


  for (
    const obj of waferObjects.value
  ) {

    /*
     * Center
     */
    if (
      snapMode.value === 'center' ||
      snapMode.value === 'nearest'
    ) {

      const center =
        getCenter(obj)


      const d =
        distance(
          point,
          center
        )


      if (
        d < bestDistance
      ) {

        bestDistance = d

        best = {
          ...center,

          type: 'center',

          objectId: obj.id
        }
      }
    }


    /*
     * Corners
     */
    if (
      snapMode.value === 'corner' ||
      snapMode.value === 'nearest'
    ) {

      for (
        const corner
        of getCorners(obj)
      ) {

        const d =
          distance(
            point,
            corner
          )


        if (
          d < bestDistance
        ) {

          bestDistance = d

          best = corner
        }
      }
    }


    /*
     * Edge
     */
    if (
      snapMode.value === 'edge' ||
      snapMode.value === 'nearest'
    ) {

      const edge =
        closestPointOnEdge(
          point,
          obj
        )


      const d =
        distance(
          point,
          edge
        )


      if (
        d < bestDistance
      ) {

        bestDistance = d

        best = edge
      }
    }
  }


  return best
}


/* ================================================================
 * Plotly coordinate conversion
 * ================================================================ */

function getPlotPoint(
  event: MouseEvent
): Point | null {

  if (!plotElement.value) {
    return null
  }


  const graph =
    plotElement.value
      .querySelector(
        '.js-plotly-plot'
      ) as any


  if (!graph) {
    return null
  }


  const layout =
    graph._fullLayout


  if (!layout) {
    return null
  }


  const rect =
    graph.getBoundingClientRect()


  const px =
    event.clientX -
    rect.left


  const py =
    event.clientY -
    rect.top


  const xaxis =
    layout.xaxis

  const yaxis =
    layout.yaxis


  if (
    !xaxis ||
    !yaxis
  ) {
    return null
  }


  return {

    x: xaxis.p2l(
      px - xaxis._offset
    ),

    y: yaxis.p2l(
      py - yaxis._offset
    )
  }
}


/* ================================================================
 * Snap threshold
 * ================================================================ */

function getSnapThreshold(): number {

  if (!plotElement.value) {
    return 0
  }


  const graph =
    plotElement.value
      .querySelector(
        '.js-plotly-plot'
      ) as any


  if (!graph) {
    return 0
  }


  const xaxis =
    graph._fullLayout.xaxis


  if (!xaxis) {
    return 0
  }


  const p1 =
    xaxis.p2l(
      xaxis._offset
    )


  const p2 =
    xaxis.p2l(
      xaxis._offset +
      props.snapThresholdPx
    )


  return Math.abs(
    p2 - p1
  )
}


/* ================================================================
 * Apply Snap
 * ================================================================ */

function applySnap(
  point: Point
): Point {

  if (!snapEnabled.value) {

    snapPoint.value =
      null

    return point
  }


  const candidate =
    findSnapCandidate(point)


  if (!candidate) {

    snapPoint.value =
      null

    return point
  }


  const d =
    distance(
      point,
      candidate
    )


  const threshold =
    getSnapThreshold()


  if (
    d <= threshold
  ) {

    snapPoint.value =
      candidate


    return {

      x: candidate.x,

      y: candidate.y
    }
  }


  snapPoint.value =
    null


  return point
}


/* ================================================================
 * Object search
 * ================================================================ */

function findObjectAtPoint(
  point: Point
): WaferObject | undefined {

  return waferObjects.value.find(
    obj => {

      return (

        point.x >= obj.x &&

        point.x <=
          obj.x + obj.width &&

        point.y >= obj.y &&

        point.y <=
          obj.y + obj.height
      )
    }
  )
}


/* ================================================================
 * Measurement
 * ================================================================ */

function calculateMeasurement(
  start: Point,
  end: Point
): Measurement {

  const dx =
    Math.abs(
      end.x - start.x
    )


  const dy =
    Math.abs(
      end.y - start.y
    )


  const distance =
    Math.sqrt(
      dx * dx +
      dy * dy
    )


  const startObject =
    findObjectAtPoint(
      start
    )


  const endObject =
    findObjectAtPoint(
      end
    )


  return {

    dx,

    dy,

    distance,

    startObject:
      startObject?.id,

    endObject:
      endObject?.id
  }
}


/* ================================================================
 * Current measurement
 * ================================================================ */

const currentMeasurement =
  computed(() => {

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


const hasMeasurement =
  computed(() => {

    return (

      startPoint.value !== null &&

      currentPoint.value !== null
    )
  })


/* ================================================================
 * Plotly Data
 * ================================================================ */

const buildData =
  (): Data[] => {

    const data:
      Data[] = []


    /*
     * Objects
     */
    for (
      const obj of waferObjects.value
    ) {

      data.push({

        type: 'scatter',

        mode: 'lines',

        x: [

          obj.x,

          obj.x + obj.width,

          obj.x + obj.width,

          obj.x,

          obj.x

        ],

        y: [

          obj.y,

          obj.y,

          obj.y + obj.height,

          obj.y + obj.height,

          obj.y

        ],

        name: obj.id,

        hovertemplate:

          `${obj.id}<br>` +

          `X: %{x:.0f} ${unit.value}<br>` +

          `Y: %{y:.0f} ${unit.value}` +

          '<extra></extra>'
      })
    }


    /*
     * Snap marker
     */
    if (
      snapPoint.value
    ) {

      data.push({

        type: 'scatter',

        mode: 'markers',

        x: [
          snapPoint.value.x
        ],

        y: [
          snapPoint.value.y
        ],

        marker: {

          size: 14,

          symbol: 'cross'
        },

        hoverinfo: 'skip'
      })
    }


    return data
  }


/* ================================================================
 * Ruler Shapes
 * ================================================================ */

function buildRulerShapes():
  Shape[] {

  if (
    !startPoint.value ||
    !currentPoint.value
  ) {
    return []
  }


  const start =
    startPoint.value

  const end =
    currentPoint.value


  return [

    {

      type: 'line',

      x0: start.x,

      y0: start.y,

      x1: end.x,

      y1: end.y,

      line: {

        width: 3
      }
    },

    {

      type: 'circle',

      x0: start.x - 200,

      x1: start.x + 200,

      y0: start.y - 200,

      y1: start.y + 200,

      line: {

        width: 2
      }
    },

    {

      type: 'circle',

      x0: end.x - 200,

      x1: end.x + 200,

      y0: end.y - 200,

      y1: end.y + 200,

      line: {

        width: 2
      }
    }

  ]
}


/* ================================================================
 * Ruler Annotation
 * ================================================================ */

function buildAnnotations():
  Annotations[] {

  if (
    !startPoint.value ||
    !currentPoint.value
  ) {
    return []
  }


  const start =
    startPoint.value

  const end =
    currentPoint.value


  const result =
    calculateMeasurement(
      start,
      end
    )


  return [

    {

      x:
        (start.x + end.x) / 2,

      y:
        (start.y + end.y) / 2,

      text:

        `ΔX: ${result.dx.toFixed(2)} ${unit.value}` +

        `<br>` +

        `ΔY: ${result.dy.toFixed(2)} ${unit.value}` +

        `<br>` +

        `<b>${result.distance.toFixed(2)} ${unit.value}</b>`,

      showarrow: false,

      bgcolor: 'white',

      borderwidth: 1,

      borderpad: 5
    }

  ]
}


/* ================================================================
 * Layout
 * ================================================================ */

function buildLayout():
  Partial<Layout> {

  return {

    margin: {

      l: 60,

      r: 30,

      t: 30,

      b: 60
    },


    xaxis: {

      title: {

        text:
          `X (${unit.value})`
      },

      scaleanchor: 'y',

      scaleratio: 1,

      showgrid: true,

      zeroline: true
    },


    yaxis: {

      title: {

        text:
          `Y (${unit.value})`
      },

      showgrid: true,

      zeroline: true
    },


    hovermode: 'closest',


    /*
     * Ruler ON:
     * Plotly drag interaction disabled.
     */
    dragmode:
      rulerMode.value
        ? false
        : 'pan',


    shapes:
      buildRulerShapes(),


    annotations:
      buildAnnotations()
  }
}


/* ================================================================
 * Plotly Config
 * ================================================================ */

const plotConfig:
  Partial<Config> = {

  responsive: true,

  displaylogo: false,

  scrollZoom: true,

  modeBarButtonsToRemove: [

    'select2d',

    'lasso2d'
  ]
}


/* ================================================================
 * Render Plotly
 * ================================================================ */

async function renderPlot() {

  if (!plotElement.value) {
    return
  }


  await Plotly.react(

    plotElement.value,

    buildData(),

    buildLayout(),

    plotConfig
  )
}


/* ================================================================
 * Update Plot
 * ================================================================ */

async function updatePlot() {

  if (!plotElement.value) {
    return
  }


  await Plotly.react(

    plotElement.value,

    buildData(),

    buildLayout(),

    plotConfig
  )
}


/* ================================================================
 * Mouse Down
 * ================================================================ */

function handleMouseDown(
  event: MouseEvent
) {

  if (
    !rulerMode.value
  ) {
    return
  }


  if (
    event.button !== 0
  ) {
    return
  }


  const raw =
    getPlotPoint(event)


  if (!raw) {
    return
  }


  const point =
    applySnap(raw)


  startPoint.value =
    point


  currentPoint.value =
    point


  isDragging.value =
    true


  measurement.value =
    calculateMeasurement(
      point,
      point
    )


  event.preventDefault()
}


/* ================================================================
 * Mouse Move
 * ================================================================ */

function handleMouseMove(
  event: MouseEvent
) {

  if (

    !rulerMode.value ||

    !isDragging.value ||

    !startPoint.value
  ) {

    return
  }


  const raw =
    getPlotPoint(event)


  if (!raw) {
    return
  }


  const point =
    applySnap(raw)


  currentPoint.value =
    point


  measurement.value =
    calculateMeasurement(

      startPoint.value,

      point
    )


  updatePlot()
}


/* ================================================================
 * Mouse Up
 * ================================================================ */

function handleMouseUp(
  event: MouseEvent
) {

  if (
    !rulerMode.value ||
    !isDragging.value
  ) {
    return
  }


  const raw =
    getPlotPoint(event)


  if (raw) {

    const point =
      applySnap(raw)


    currentPoint.value =
      point


    if (
      startPoint.value
    ) {

      measurement.value =
        calculateMeasurement(

          startPoint.value,

          point
        )
    }
  }


  isDragging.value =
    false


  updatePlot()
}


/* ================================================================
 * Toggle Ruler
 * ================================================================ */

async function toggleRuler() {

  rulerMode.value =
    !rulerMode.value


  if (
    !rulerMode.value
  ) {

    isDragging.value =
      false

    startPoint.value =
      null

    currentPoint.value =
      null

    snapPoint.value =
      null
  }


  await updatePlot()
}


/* ================================================================
 * Clear
 * ================================================================ */

async function clearMeasurement() {

  isDragging.value =
    false

  startPoint.value =
    null

  currentPoint.value =
    null

  snapPoint.value =
    null


  measurement.value = {

    dx: 0,

    dy: 0,

    distance: 0
  }


  await updatePlot()
}


/* ================================================================
 * ESC
 * ================================================================ */

function handleKeyDown(
  event: KeyboardEvent
) {

  if (
    event.key !== 'Escape'
  ) {
    return
  }


  rulerMode.value =
    false

  isDragging.value =
    false

  startPoint.value =
    null

  currentPoint.value =
    null

  snapPoint.value =
    null


  updatePlot()
}


/* ================================================================
 * Lifecycle
 * ================================================================ */

onMounted(
  async () => {

    await nextTick()


    if (
      !plotElement.value
    ) {
      return
    }


    await renderPlot()


    /*
     * Plotly graph element
     */
    const graph =
      plotElement.value
        .querySelector(
          '.js-plotly-plot'
        )


    if (!graph) {
      return
    }


    graph.addEventListener(
      'mousedown',
      handleMouseDown
    )


    graph.addEventListener(
      'mousemove',
      handleMouseMove
    )


    graph.addEventListener(
      'mouseup',
      handleMouseUp
    )


    document.addEventListener(
      'keydown',
      handleKeyDown
    )
  }
)


/* ================================================================
 * Cleanup
 * ================================================================ */

onBeforeUnmount(
  () => {

    const graph =
      plotElement.value
        ?.querySelector(
          '.js-plotly-plot'
        )


    if (graph) {

      graph.removeEventListener(
        'mousedown',
        handleMouseDown
      )

      graph.removeEventListener(
        'mousemove',
        handleMouseMove
      )

      graph.removeEventListener(
        'mouseup',
        handleMouseUp
      )
    }


    document.removeEventListener(
      'keydown',
      handleKeyDown
    )


    if (
      plotElement.value
    ) {

      Plotly.purge(
        plotElement.value
      )
    }
  }
)

</script>