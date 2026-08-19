<template>
  <div class="w-full h-full flex flex-col bg-white">

    <!-- =========================================================
         Toolbar
    ========================================================== -->
    <div
      class="flex items-center gap-2 px-3 py-2 border-b shrink-0"
    >

      <!-- Ruler -->
      <a-button
        :type="rulerMode ? 'primary' : 'default'"
        @click="toggleRuler"
      >
        📏 {{ rulerMode ? 'Ruler ON' : 'Ruler OFF' }}
      </a-button>


      <!-- Snap -->
      <a-button
        :type="snapEnabled ? 'primary' : 'default'"
        :disabled="!rulerMode"
        @click="snapEnabled = !snapEnabled"
      >
        🧲 Snap {{ snapEnabled ? 'ON' : 'OFF' }}
      </a-button>


      <!-- Snap mode -->
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


      <!-- Clear -->
      <a-button
        :disabled="!hasMeasurement"
        @click="clearMeasurement"
      >
        Clear
      </a-button>


      <!-- =======================================================
           Measurement
      ======================================================== -->
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
          v-if="
            measurement.startObject ||
            measurement.endObject
          "
          class="text-gray-500"
        >
          {{ measurement.startObject || '-' }}

          →

          {{ measurement.endObject || '-' }}
        </span>

      </div>


      <span
        v-if="
          rulerMode &&
          !isDragging
        "
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


    <!-- =========================================================
         Plotly
    ========================================================== -->
    <div
      ref="plotContainer"
      class="relative flex-1 min-h-0"
    >

      <div
        ref="plotElement"
        class="w-full h-full"
      />


      <!-- =======================================================
           Current measurement
      ======================================================== -->
      <div
        v-if="
          rulerMode &&
          isDragging
        "
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
          v-if="
            currentMeasurement.startObject ||
            currentMeasurement.endObject
          "
          class="text-gray-500"
        >
          {{ currentMeasurement.startObject || '-' }}

          →

          {{ currentMeasurement.endObject || '-' }}
        </div>

      </div>


      <!-- =======================================================
           Snap information
      ======================================================== -->
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

        <span
          v-if="snapPoint.objectId"
        >
          · {{ snapPoint.objectId }}
        </span>

        <span
          v-if="snapPoint.corner"
        >
          · {{ snapPoint.corner }}
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
  Layout
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

  /*
   * Left-bottom coordinate
   */
  x: number
  y: number

  width: number
  height: number

  label?: string
}


type SnapMode =
  | 'nearest'
  | 'center'
  | 'corner'
  | 'edge'


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

  /*
   * Snap tolerance.
   *
   * Pixel 기준.
   */
  snapThresholdPx?: number
}


const props =
  withDefaults(
    defineProps<Props>(),
    {
      unit: 'μm',

      snapThresholdPx: 15
    }
  )


const unit =
  computed(
    () => props.unit
  )


/* ================================================================
 * DOM
 * ================================================================ */

const plotContainer =
  ref<HTMLElement | null>(null)


const plotElement =
  ref<HTMLElement | null>(null)


/* ================================================================
 * State
 * ================================================================ */

const rulerMode =
  ref(false)


const snapEnabled =
  ref(true)


const snapMode =
  ref<SnapMode>('nearest')


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
 * 실제 프로젝트에서는 API 데이터 또는 props로 교체
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
 * Utility
 * ================================================================ */

function pointDistance(
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
 * Object center
 * ================================================================ */

function getObjectCenter(
  object: WaferObject
): Point {

  return {

    x:
      object.x +
      object.width / 2,

    y:
      object.y +
      object.height / 2
  }
}


/* ================================================================
 * Object corners
 * ================================================================ */

function getObjectCorners(
  object: WaferObject
): SnapPoint[] {

  return [

    {
      x: object.x,

      y: object.y,

      type: 'corner',

      objectId: object.id,

      corner: 'bottom-left'
    },


    {
      x:
        object.x +
        object.width,

      y: object.y,

      type: 'corner',

      objectId: object.id,

      corner: 'bottom-right'
    },


    {
      x:
        object.x +
        object.width,

      y:
        object.y +
        object.height,

      type: 'corner',

      objectId: object.id,

      corner: 'top-right'
    },


    {
      x: object.x,

      y:
        object.y +
        object.height,

      type: 'corner',

      objectId: object.id,

      corner: 'top-left'
    }

  ]
}


/* ================================================================
 * Closest point on object edge
 * ================================================================ */

function getClosestPointOnEdge(
  point: Point,
  object: WaferObject
): SnapPoint {

  const left =
    object.x

  const right =
    object.x +
    object.width

  const bottom =
    object.y

  const top =
    object.y +
    object.height


  /*
   * Clamp point into rectangle.
   */
  const clampedX =
    Math.max(
      left,
      Math.min(
        point.x,
        right
      )
    )


  const clampedY =
    Math.max(
      bottom,
      Math.min(
        point.y,
        top
      )
    )


  const candidates = [

    {
      distance:
        Math.abs(
          point.x - left
        ),

      point: {
        x: left,

        y: clampedY
      }
    },


    {
      distance:
        Math.abs(
          point.x - right
        ),

      point: {
        x: right,

        y: clampedY
      }
    },


    {
      distance:
        Math.abs(
          point.y - bottom
        ),

      point: {
        x: clampedX,

        y: bottom
      }
    },


    {
      distance:
        Math.abs(
          point.y - top
        ),

      point: {
        x: clampedX,

        y: top
      }
    }

  ]


  candidates.sort(
    (a, b) =>
      a.distance -
      b.distance
  )


  return {

    x:
      candidates[0].point.x,

    y:
      candidates[0].point.y,

    type: 'edge',

    objectId:
      object.id
  }
}


/* ================================================================
 * Find nearest Snap
 * ================================================================ */

function findSnapCandidate(
  point: Point
): SnapPoint | null {

  if (
    !snapEnabled.value
  ) {
    return null
  }


  let best:
    SnapPoint | null = null


  let bestDistance =
    Number.POSITIVE_INFINITY


  for (
    const object
    of waferObjects.value
  ) {

    /* ------------------------------------------------------------
     * Center
     * ---------------------------------------------------------- */

    if (
      snapMode.value === 'center' ||
      snapMode.value === 'nearest'
    ) {

      const center =
        getObjectCenter(
          object
        )


      const d =
        pointDistance(
          point,
          center
        )


      if (
        d < bestDistance
      ) {

        bestDistance =
          d

        best = {

          x: center.x,

          y: center.y,

          type: 'center',

          objectId:
            object.id
        }
      }
    }


    /* ------------------------------------------------------------
     * Corner
     * ---------------------------------------------------------- */

    if (
      snapMode.value === 'corner' ||
      snapMode.value === 'nearest'
    ) {

      const corners =
        getObjectCorners(
          object
        )


      for (
        const corner
        of corners
      ) {

        const d =
          pointDistance(
            point,
            corner
          )


        if (
          d < bestDistance
        ) {

          bestDistance =
            d

          best =
            corner
        }
      }
    }


    /* ------------------------------------------------------------
     * Edge
     * ---------------------------------------------------------- */

    if (
      snapMode.value === 'edge' ||
      snapMode.value === 'nearest'
    ) {

      const edge =
        getClosestPointOnEdge(
          point,
          object
        )


      const d =
        pointDistance(
          point,
          edge
        )


      if (
        d < bestDistance
      ) {

        bestDistance =
          d

        best =
          edge
      }
    }
  }


  return best
}


/* ================================================================
 * Get Plotly Graph
 * ================================================================ */

function getGraph():
  HTMLElement | null {

  if (
    !plotElement.value
  ) {
    return null
  }


  return plotElement.value
    .querySelector(
      '.js-plotly-plot'
    )
}


/* ================================================================
 * Convert mouse pixel → Plotly coordinate
 * ================================================================ */

function getPlotPoint(
  event: MouseEvent
): Point | null {

  const graph =
    getGraph() as any


  if (!graph) {
    return null
  }


  const fullLayout =
    graph._fullLayout


  if (!fullLayout) {
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
    fullLayout.xaxis


  const yaxis =
    fullLayout.yaxis


  if (
    !xaxis ||
    !yaxis
  ) {
    return null
  }


  return {

    x:
      xaxis.p2l(
        px -
        xaxis._offset
      ),

    y:
      yaxis.p2l(
        py -
        yaxis._offset
      )
  }
}


/* ================================================================
 * Convert Snap threshold
 *
 * pixel → data coordinate
 * ================================================================ */

function getSnapThreshold():
  number {

  const graph =
    getGraph() as any


  if (!graph) {
    return 0
  }


  const xaxis =
    graph._fullLayout?.xaxis


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

  if (
    !snapEnabled.value
  ) {

    snapPoint.value =
      null

    return point
  }


  const candidate =
    findSnapCandidate(
      point
    )


  if (!candidate) {

    snapPoint.value =
      null

    return point
  }


  const d =
    pointDistance(
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
 * Find object at point
 * ================================================================ */

function findObjectAtPoint(
  point: Point
): WaferObject | undefined {

  return waferObjects.value.find(
    object => {

      return (

        point.x >= object.x &&

        point.x <=
          object.x +
          object.width &&

        point.y >= object.y &&

        point.y <=
          object.y +
          object.height
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
      end.x -
      start.x
    )


  const dy =
    Math.abs(
      end.y -
      start.y
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
 * Computed Measurement
 * ================================================================ */

const currentMeasurement =
  computed<Measurement>(
    () => {

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
    }
  )


const hasMeasurement =
  computed(
    () => {

      return (

        startPoint.value !== null &&

        currentPoint.value !== null
      )
    }
  )


/* ================================================================
 * Build Plotly Data
 *
 * 이 부분은 Ruler 이동 때 다시 실행하지 않습니다.
 * ================================================================ */

function buildData(): Data[] {

  const data:
    Data[] = []


  for (
    const object
    of waferObjects.value
  ) {

    data.push({

      type: 'scatter',

      mode: 'lines',

      x: [

        object.x,

        object.x +
          object.width,

        object.x +
          object.width,

        object.x,

        object.x

      ],

      y: [

        object.y,

        object.y,

        object.y +
          object.height,

        object.y +
          object.height,

        object.y

      ],

      name:
        object.id,

      hovertemplate:

        `${object.id}` +

        `<br>` +

        `X: %{x:.0f} ${unit.value}` +

        `<br>` +

        `Y: %{y:.0f} ${unit.value}` +

        '<extra></extra>'
    })
  }


  return data
}


/* ================================================================
 * Build Ruler Shapes
 *
 * 중요:
 * Shape 타입을 직접 지정하지 않습니다.
 * ================================================================ */

function buildRulerShapes() {

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
      type: 'line' as const,

      x0: start.x,

      y0: start.y,

      x1: end.x,

      y1: end.y,

      line: {

        width: 3
      }
    },


    {
      type: 'circle' as const,

      x0:
        start.x - 200,

      x1:
        start.x + 200,

      y0:
        start.y - 200,

      y1:
        start.y + 200,

      line: {

        width: 2
      }
    },


    {
      type: 'circle' as const,

      x0:
        end.x - 200,

      x1:
        end.x + 200,

      y0:
        end.y - 200,

      y1:
        end.y + 200,

      line: {

        width: 2
      }
    }

  ]
}


/* ================================================================
 * Build Annotation
 * ================================================================ */

function buildAnnotations() {

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
        (start.x +
          end.x) / 2,

      y:
        (start.y +
          end.y) / 2,

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
 * Base Layout
 *
 * Ruler 상태와 관계없는 Layout
 * ================================================================ */

function buildBaseLayout():
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

      showgrid: true,

      zeroline: true,

      scaleanchor: 'y',

      scaleratio: 1
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

    dragmode:
      'pan'
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
 * Initial Plot
 * ================================================================ */

async function initializePlot() {

  if (
    !plotElement.value
  ) {
    return
  }


  await Plotly.newPlot(

    plotElement.value,

    buildData(),

    buildBaseLayout(),

    plotConfig
  )
}


/* ================================================================
 * Update Ruler
 *
 * ★ 핵심
 *
 * 전체 Plotly.react()를 호출하지 않습니다.
 *
 * Ruler:
 *   → Plotly.relayout()
 *
 * Object 변경:
 *   → Plotly.react()
 * ================================================================ */

async function updateRuler() {

  if (
    !plotElement.value
  ) {
    return
  }


  const shapes =
    buildRulerShapes()


  const annotations =
    buildAnnotations()


  await Plotly.relayout(

    plotElement.value,

    {

      shapes,

      annotations
    }
  )
}


/* ================================================================
 * Update Object Data
 *
 * 외부에서 waferObjects가 변경되었을 때 사용하는 함수.
 * ================================================================ */

async function updateObjects() {

  if (
    !plotElement.value
  ) {
    return
  }


  await Plotly.react(

    plotElement.value,

    buildData(),

    buildBaseLayout(),

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


  const rawPoint =
    getPlotPoint(
      event
    )


  if (!rawPoint) {
    return
  }


  const point =
    applySnap(
      rawPoint
    )


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


  const rawPoint =
    getPlotPoint(
      event
    )


  if (!rawPoint) {
    return
  }


  const point =
    applySnap(
      rawPoint
    )


  currentPoint.value =
    point


  measurement.value =
    calculateMeasurement(

      startPoint.value,

      point
    )


  /*
   * ★ Ruler만 업데이트
   */
  void updateRuler()
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


  const rawPoint =
    getPlotPoint(
      event
    )


  if (rawPoint) {

    const point =
      applySnap(
        rawPoint
      )


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


  void updateRuler()
}


/* ================================================================
 * Toggle Ruler
 * ================================================================ */

async function toggleRuler() {

  rulerMode.value =
    !rulerMode.value


  isDragging.value =
    false


  if (
    !rulerMode.value
  ) {

    startPoint.value =
      null

    currentPoint.value =
      null

    snapPoint.value =
      null


    /*
     * Ruler 제거
     */
    await Plotly.relayout(

      plotElement.value!,

      {

        shapes: [],

        annotations: [],

        dragmode: 'pan'
      }
    )

  } else {

    /*
     * Ruler ON
     *
     * Plotly의 dragmode를 false로 변경.
     */
    await Plotly.relayout(

      plotElement.value!,

      {

        dragmode: false
      }
    )
  }
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


  await Plotly.relayout(

    plotElement.value!,

    {

      shapes: [],

      annotations: []
    }
  )
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


  void Plotly.relayout(

    plotElement.value!,

    {

      shapes: [],

      annotations: [],

      dragmode: 'pan'
    }
  )
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


    /*
     * Plotly 최초 생성
     */
    await initializePlot()


    const graph =
      getGraph()


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
      getGraph()


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