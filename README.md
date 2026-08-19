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
        @click="toggleSnap"
      >
        🧲 Snap {{ snapEnabled ? 'ON' : 'OFF' }}
      </a-button>

      <!-- Clear -->
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
           Live measurement
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
        Snap:
        {{ snapPoint.objectName || 'nearest' }}

        <span>
          ({{ snapPoint.x.toFixed(2) }},
          {{ snapPoint.y.toFixed(2) }})
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
  Button as AButton
} from 'ant-design-vue'


/* ================================================================
 * Types
 * ================================================================ */

/**
 * 실제 Wafer Object 구조
 *
 * width / height / id / label 사용하지 않음.
 *
 * x, y는 Plotly scatter line에 사용하는 좌표입니다.
 *
 * 예:
 *
 * {
 *   name: 'WAFER_01',
 *   x: [0, 100, 200],
 *   y: [0, 100, 0]
 * }
 */
interface WaferObject {

  name: string

  x: number[]

  y: number[]
}


/**
 * 실제 Snap된 좌표
 */
interface SnapPoint {

  x: number

  y: number

  objectName?: string
}


/**
 * 측정 결과
 */
interface Measurement {

  dx: number

  dy: number

  distance: number

  startObject?: string

  endObject?: string
}


/**
 * 좌표
 */
interface Point {

  x: number

  y: number
}


/**
 * Props
 */
interface Props {

  unit?: string

  /**
   * Snap 허용 거리.
   *
   * Plotly 화면상의 pixel 기준.
   */
  snapThresholdPx?: number

  /**
   * 실제 Wafer 데이터.
   */
  objects?: WaferObject[]
}


/* ================================================================
 * Props
 * ================================================================ */

const props =
  withDefaults(
    defineProps<Props>(),
    {
      unit: 'μm',

      snapThresholdPx: 15,

      objects: () => []
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
 * Ruler State
 * ================================================================ */

const rulerMode =
  ref(false)


const snapEnabled =
  ref(true)


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
 * Objects
 *
 * 실제 프로젝트에서는 props.objects 사용
 * ================================================================ */

const waferObjects =
  computed<WaferObject[]>(
    () => props.objects
  )


/* ================================================================
 * Get Plotly Graph
 *
 * ★ 중요
 *
 * plotElement 자체가 Plotly graph입니다.
 *
 * querySelector('.js-plotly-plot') 사용하지 않습니다.
 * ================================================================ */

function getGraph():
  HTMLElement | null {

  return plotElement.value
}


/* ================================================================
 * Distance
 * ================================================================ */

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
 * Point → Line Segment
 *
 * 마우스 위치에서 선분까지의 가장 가까운 점
 *
 * A -------- B
 *       ↑
 *       P
 *
 * P를 선분 AB에 projection
 * ================================================================ */

function closestPointOnSegment(
  point: Point,
  a: Point,
  b: Point
): Point {

  const dx =
    b.x - a.x

  const dy =
    b.y - a.y


  /*
   * A와 B가 같은 점인 경우
   */
  const lengthSquared =
    dx * dx +
    dy * dy


  if (
    lengthSquared === 0
  ) {

    return {

      x: a.x,

      y: a.y
    }
  }


  /*
   * Projection parameter
   *
   * 0 → A
   * 1 → B
   */
  let t =
    (
      (point.x - a.x) * dx +
      (point.y - a.y) * dy
    ) /
    lengthSquared


  /*
   * 선분 밖으로 나가지 않도록 clamp
   */
  t =
    Math.max(
      0,

      Math.min(
        1,

        t
      )
    )


  return {

    x:
      a.x +
      t * dx,

    y:
      a.y +
      t * dy
  }
}


/* ================================================================
 * Find Nearest Point on All Objects
 *
 * ★ Ruler의 핵심 Snap
 *
 * 모든 객체의 모든 line segment를 검사하고
 * 마우스 위치와 가장 가까운 선상의 좌표를 반환
 * ================================================================ */

function findNearestPoint(
  point: Point
): SnapPoint | null {

  let nearest:
    SnapPoint | null = null


  let nearestDistance =
    Number.POSITIVE_INFINITY


  for (
    const object
    of waferObjects.value
  ) {

    const x =
      object.x

    const y =
      object.y


    /*
     * 잘못된 데이터 방어
     */
    if (
      x.length === 0 ||
      y.length === 0
    ) {

      continue
    }


    /*
     * x/y 길이가 다르면
     * 짧은 쪽까지만 사용
     */
    const length =
      Math.min(
        x.length,
        y.length
      )


    /*
     * ------------------------------------------------------------
     * 각 line segment 검사
     *
     * P0 → P1
     * P1 → P2
     * P2 → P3
     * ...
     * ------------------------------------------------------------
     */
    for (
      let i = 0;
      i < length - 1;
      i++
    ) {

      const a: Point = {

        x: x[i],

        y: y[i]
      }


      const b: Point = {

        x: x[i + 1],

        y: y[i + 1]
      }


      const closest =
        closestPointOnSegment(

          point,

          a,

          b
        )


      const d =
        distance(
          point,

          closest
        )


      if (
        d < nearestDistance
      ) {

        nearestDistance =
          d


        nearest = {

          x:
            closest.x,

          y:
            closest.y,

          objectName:
            object.name
        }
      }
    }
  }


  /*
   * Snap threshold
   */
  if (
    !nearest
  ) {

    return null
  }


  const threshold =
    getSnapThreshold()


  if (
    nearestDistance >
    threshold
  ) {

    return null
  }


  return nearest
}


/* ================================================================
 * Pixel → Data threshold
 * ================================================================ */

function getSnapThreshold():
  number {

  const graph =
    getGraph() as any


  if (!graph) {

    return 0
  }


  const fullLayout =
    graph._fullLayout


  if (!fullLayout) {

    return 0
  }


  const xaxis =
    fullLayout.xaxis


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


  const nearest =
    findNearestPoint(
      point
    )


  if (!nearest) {

    snapPoint.value =
      null

    return point
  }


  snapPoint.value =
    nearest


  return {

    x:
      nearest.x,

    y:
      nearest.y
  }
}


/* ================================================================
 * Mouse → Plotly coordinate
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
 * Find Object Near Point
 *
 * Snap된 점이 어느 객체에 속하는지 확인
 * ================================================================ */

function findObjectName(
  point: Point
): string | undefined {

  let nearest:
    string | undefined


  let nearestDistance =
    Number.POSITIVE_INFINITY


  for (
    const object
    of waferObjects.value
  ) {

    const x =
      object.x

    const y =
      object.y


    const length =
      Math.min(
        x.length,
        y.length
      )


    for (
      let i = 0;
      i < length - 1;
      i++
    ) {

      const closest =
        closestPointOnSegment(

          point,

          {
            x: x[i],

            y: y[i]
          },

          {
            x: x[i + 1],

            y: y[i + 1]
          }
        )


      const d =
        distance(
          point,

          closest
        )


      if (
        d < nearestDistance
      ) {

        nearestDistance =
          d

        nearest =
          object.name
      }
    }
  }


  return nearest
}


/* ================================================================
 * Calculate Measurement
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


  const result =
    Math.sqrt(
      dx * dx +
      dy * dy
    )


  return {

    dx,

    dy,

    distance:
      result,

    startObject:
      findObjectName(
        start
      ),

    endObject:
      findObjectName(
        end
      )
  }
}


/* ================================================================
 * Current Measurement
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


/* ================================================================
 * Has Measurement
 * ================================================================ */

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
 * 실제 WaferObject를 그대로 scatter lines로 표현
 * ================================================================ */

function buildData():
  Data[] {

  return waferObjects.value.map(
    (
      object
    ): Data => {

      return {

        type:
          'scatter',

        mode:
          'lines',

        x:
          object.x,

        y:
          object.y,

        name:
          object.name,

        hovertemplate:

          `${object.name}` +

          `<br>` +

          `X: %{x:.2f} ${unit.value}` +

          `<br>` +

          `Y: %{y:.2f} ${unit.value}` +

          '<extra></extra>'
      }
    }
  )
}


/* ================================================================
 * Base Layout
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

      showgrid:
        true,

      zeroline:
        true,

      scaleanchor:
        'y',

      scaleratio:
        1
    },


    yaxis: {

      title: {

        text:
          `Y (${unit.value})`
      },

      showgrid:
        true,

      zeroline:
        true
    },


    hovermode:
      'closest',

    /*
     * 일반 모드에서는 pan
     */
    dragmode:
      'pan'
  }
}


/* ================================================================
 * Plotly Config
 * ================================================================ */

const plotConfig:
  Partial<Config> = {

  responsive:
    true,

  displaylogo:
    false,

  scrollZoom:
    true,

  modeBarButtonsToRemove: [

    'select2d',

    'lasso2d'

  ]
}


/* ================================================================
 * Initialize Plot
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
 * Build Ruler Shapes
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


  const markerSize =
    getMarkerSize()


  return [

    /*
     * Ruler line
     */
    {

      type:
        'line' as const,

      x0:
        start.x,

      y0:
        start.y,

      x1:
        end.x,

      y1:
        end.y,

      line: {

        width:
          3
      }
    },


    /*
     * Start point
     */
    {

      type:
        'circle' as const,

      x0:
        start.x -
        markerSize,

      x1:
        start.x +
        markerSize,

      y0:
        start.y -
        markerSize,

      y1:
        start.y +
        markerSize,

      line: {

        width:
          2
      }
    },


    /*
     * End point
     */
    {

      type:
        'circle' as const,

      x0:
        end.x -
        markerSize,

      x1:
        end.x +
        markerSize,

      y0:
        end.y -
        markerSize,

      y1:
        end.y +
        markerSize,

      line: {

        width:
          2
      }
    }

  ]
}


/* ================================================================
 * Marker Size
 *
 * 데이터 좌표가 μm 단위이므로 고정된 200 같은 값을 쓰지 않고
 * 현재 화면의 pixel scale에 맞춰 계산합니다.
 * ================================================================ */

function getMarkerSize():
  number {

  const graph =
    getGraph() as any


  if (!graph) {

    return 1
  }


  const xaxis =
    graph._fullLayout?.xaxis


  if (!xaxis) {

    return 1
  }


  const p1 =
    xaxis.p2l(
      xaxis._offset
    )


  const p2 =
    xaxis.p2l(
      xaxis._offset + 8
    )


  return Math.abs(
    p2 - p1
  )
}


/* ================================================================
 * Build Annotation
 * ================================================================ */

function buildRulerAnnotations() {

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

      showarrow:
        false,

      bgcolor:
        'white',

      borderwidth:
        1,

      borderpad:
        5
    }

  ]
}


/* ================================================================
 * Build Snap Marker
 * ================================================================ */

function buildSnapShapes() {

  if (
    !snapPoint.value
  ) {

    return []
  }


  const point =
    snapPoint.value


  const size =
    getMarkerSize()


  return [

    {

      type:
        'circle' as const,

      x0:
        point.x -
        size,

      x1:
        point.x +
        size,

      y0:
        point.y -
        size,

      y1:
        point.y +
        size,

      line: {

        width:
          2
      }

    }

  ]
}


/* ================================================================
 * Update Ruler
 *
 * ★ mousemove에서는 Plotly.react()를 사용하지 않음
 *
 * ★ Plotly.relayout()만 사용
 * ================================================================ */

async function updateRuler() {

  if (
    !plotElement.value
  ) {

    return
  }


  const rulerShapes =
    buildRulerShapes()


  const snapShapes =
    buildSnapShapes()


  const annotations =
    buildRulerAnnotations()


  await Plotly.relayout(

    plotElement.value,

    {

      shapes: [

        ...rulerShapes,

        ...snapShapes

      ],

      annotations
    }
  )
}


/* ================================================================
 * Update Plot
 *
 * 데이터 자체가 변경되었을 때만 사용
 * ================================================================ */

async function updatePlot() {

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


  /*
   * Ruler가 존재한다면 다시 표시
   */
  if (
    startPoint.value &&
    currentPoint.value
  ) {

    await updateRuler()
  }
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


  /*
   * 왼쪽 마우스
   */
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


  /*
   * Nearest Snap
   */
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


  /*
   * Plotly pan 방지
   */
  event.preventDefault()


  void updateRuler()
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


  /*
   * Nearest Snap
   */
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
   * ★ react() 하지 않음
   *
   * ruler만 relayout
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


    await Plotly.relayout(

      plotElement.value!,

      {

        shapes: [],

        annotations: [],

        dragmode:
          'pan'
      }
    )

  } else {

    /*
     * Ruler ON
     *
     * Plotly pan을 끄고
     * 자체 ruler drag를 사용
     */
    await Plotly.relayout(

      plotElement.value!,

      {

        dragmode:
          false
      }
    )
  }
}


/* ================================================================
 * Toggle Snap
 * ================================================================ */

async function toggleSnap() {

  snapEnabled.value =
    !snapEnabled.value


  if (
    !snapEnabled.value
  ) {

    snapPoint.value =
      null
  }


  await updateRuler()
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

    dx:
      0,

    dy:
      0,

    distance:
      0
  }


  if (
    plotElement.value
  ) {

    await Plotly.relayout(

      plotElement.value,

      {

        shapes: [],

        annotations: []
      }
    )
  }
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


  if (
    plotElement.value
  ) {

    void Plotly.relayout(

      plotElement.value,

      {

        shapes: [],

        annotations: [],

        dragmode:
          'pan'
      }
    )
  }
}


/* ================================================================
 * Mounted
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
     * Plotly 생성
     */
    await initializePlot()


    /*
     * ★ 중요
     *
     * mousedown
     * → Plotly container
     *
     * mousemove / mouseup
     * → document
     */
    plotElement.value.addEventListener(
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
  }
)


/* ================================================================
 * Unmounted
 * ================================================================ */

onBeforeUnmount(
  () => {

    if (
      plotElement.value
    ) {

      plotElement.value.removeEventListener(
        'mousedown',
        handleMouseDown
      )
    }


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