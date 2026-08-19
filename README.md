<template>
  <div class="w-full h-full flex flex-col bg-white">

    <!-- =========================================================
         Toolbar
    ========================================================== -->
    <div
      class="flex items-center gap-2 px-3 py-2 border-b shrink-0"
    >
      <!-- Ruler ON / OFF -->
      <a-button
        :type="rulerMode ? 'primary' : 'default'"
        @click="toggleRuler"
      >
        📏
        {{ rulerMode ? 'Ruler ON' : 'Ruler OFF' }}
      </a-button>


      <!-- Snap ON / OFF -->
      <a-button
        :type="snapEnabled ? 'primary' : 'default'"
        :disabled="!rulerMode"
        @click="toggleSnap"
      >
        🧲
        Snap {{ snapEnabled ? 'ON' : 'OFF' }}
      </a-button>


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


        <!-- Start / End Object -->
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


      <!-- =======================================================
           Instruction
      ======================================================== -->
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

      <!--
        ★ 중요

        이 element 자체가 Plotly graph입니다.

        querySelector('.js-plotly-plot') 사용하지 않습니다.
      -->
      <div
        ref="plotElement"
        class="w-full h-full"
      />


      <!-- =======================================================
           Live Measurement
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
           Snap Information
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

        {{ snapPoint.objectName || '-' }}

        <span>
          (
          {{ snapPoint.x.toFixed(2) }},
          {{ snapPoint.y.toFixed(2) }}
          )
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
  ref,
  watch
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
 * 실제 WaferObject
 *
 * width / height / id / label 없음
 *
 * x / y 배열 자체가 Plotly line을 구성합니다.
 *
 * 예:
 *
 * {
 *   name: 'RECT_01',
 *   x: [0, 100, 100, 0, 0],
 *   y: [0, 0, 100, 100, 0]
 * }
 *
 * 또는
 *
 * {
 *   name: 'LINE_01',
 *   x: [0, 100],
 *   y: [0, 100]
 * }
 */
export interface WaferObject {

  name: string

  x: number[]

  y: number[]
}


/**
 * 일반 좌표
 */
interface Point {

  x: number

  y: number
}


/**
 * Snap된 좌표
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
 * Props
 */
interface Props {

  /**
   * 표시 단위
   */
  unit?: string


  /**
   * Snap 허용 범위
   *
   * 화면상의 pixel 기준
   */
  snapThresholdPx?: number


  /**
   * 실제 Wafer line data
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

      unit:
        'μm',

      snapThresholdPx:
        15,

      objects:
        () => []
    }
  )


/* ================================================================
 * Emits
 * ================================================================ */

const emit =
  defineEmits<{

    (
      event: 'measure',

      value: Measurement
    ): void

  }>()


/* ================================================================
 * Computed
 * ================================================================ */

const unit =
  computed(
    () =>
      props.unit
  )


const waferObjects =
  computed<WaferObject[]>(
    () =>
      props.objects
  )


/* ================================================================
 * DOM refs
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

    dx:
      0,

    dy:
      0,

    distance:
      0
  })


/* ================================================================
 * Get Plotly Graph
 *
 * ★ 이전 문제 수정
 *
 * querySelector()를 사용하지 않습니다.
 *
 * plotElement 자체가 Plotly graph입니다.
 * ================================================================ */

function getGraph():
  HTMLElement | null {

  return plotElement.value
}


/* ================================================================
 * Euclidean Distance
 * ================================================================ */

function getDistance(
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
 * point에서 실제 선분 AB까지의
 * 가장 가까운 점을 계산합니다.
 *
 * 무한한 직선이 아니라
 * 실제 A-B 선분 내부로 제한합니다.
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


  const lengthSquared =
    dx * dx +
    dy * dy


  /*
   * 동일한 점
   */
  if (
    lengthSquared === 0
  ) {

    return {

      x:
        a.x,

      y:
        a.y
    }
  }


  /*
   * Projection
   */
  let t =
    (
      (point.x - a.x) * dx +
      (point.y - a.y) * dy
    ) /
    lengthSquared


  /*
   * 선분 밖으로 나가지 않도록 제한
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
 * Find Nearest Edge
 *
 * 모든 WaferObject의
 * 모든 line segment를 검사합니다.
 *
 * 예:
 *
 * x = [0, 100, 100, 0, 0]
 * y = [0, 0, 100, 100, 0]
 *
 * 다음 4개의 edge가 만들어집니다.
 *
 * P0 → P1
 * P1 → P2
 * P2 → P3
 * P3 → P4
 *
 * ★ 자동으로 P4 → P0를 연결하지 않습니다.
 * Plotly에 실제로 존재하는 line만 사용합니다.
 * ================================================================ */

function findNearestEdge(
  point: Point
): SnapPoint | null {

  let nearest:
    SnapPoint | null =
      null


  let nearestDistance =
    Number.POSITIVE_INFINITY


  /*
   * 모든 Object
   */
  for (
    const object
    of waferObjects.value
  ) {

    /*
     * x/y 길이가 다를 수 있으므로
     * 짧은 쪽에 맞춥니다.
     */
    const length =
      Math.min(
        object.x.length,
        object.y.length
      )


    /*
     * line segment
     */
    for (
      let i = 0;
      i < length - 1;
      i++
    ) {

      const a: Point = {

        x:
          object.x[i],

        y:
          object.y[i]
      }


      const b: Point = {

        x:
          object.x[i + 1],

        y:
          object.y[i + 1]
      }


      /*
       * 마우스에서
       * 실제 edge 위 가장 가까운 점
       */
      const closest =
        closestPointOnSegment(

          point,

          a,

          b
        )


      const d =
        getDistance(
          point,

          closest
        )


      /*
       * 가장 가까운 edge 저장
       */
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


  if (!nearest) {

    return null
  }


  /*
   * 화면 pixel 기준 Snap threshold
   */
  const threshold =
    getSnapThreshold()


  /*
   * threshold 밖이면 Snap하지 않음
   */
  const actualDistance =
    getDistance(

      point,

      nearest
    )


  if (
    actualDistance >
    threshold
  ) {

    return null
  }


  return nearest
}


/* ================================================================
 * Plotly Pixel → Data Coordinate
 *
 * ★ Plotly 내부 axis 변환을 사용합니다.
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


  const rect =
    graph.getBoundingClientRect()


  const px =
    event.clientX -
    rect.left


  const py =
    event.clientY -
    rect.top


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
 * Snap Threshold
 *
 * Pixel → 실제 좌표 변환
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

  /*
   * Snap OFF
   */
  if (
    !snapEnabled.value
  ) {

    snapPoint.value =
      null

    return point
  }


  /*
   * 가장 가까운 Edge
   */
  const nearest =
    findNearestEdge(
      point
    )


  /*
   * Snap 가능한 Edge 없음
   */
  if (!nearest) {

    snapPoint.value =
      null

    return point
  }


  /*
   * Snap marker
   */
  snapPoint.value =
    nearest


  /*
   * 실제 Ruler 좌표도
   * Edge 좌표로 변경
   */
  return {

    x:
      nearest.x,

    y:
      nearest.y
  }
}


/* ================================================================
 * Find Object At Point
 *
 * Snap된 점을 기준으로 가장 가까운
 * Object 이름을 반환합니다.
 * ================================================================ */

function findObjectAtPoint(
  point: Point
): string | undefined {

  let nearestName:
    string | undefined


  let nearestDistance =
    Number.POSITIVE_INFINITY


  for (
    const object
    of waferObjects.value
  ) {

    const length =
      Math.min(
        object.x.length,
        object.y.length
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
            x:
              object.x[i],

            y:
              object.y[i]
          },

          {
            x:
              object.x[i + 1],

            y:
              object.y[i + 1]
          }
        )


      const d =
        getDistance(
          point,
          closest
        )


      if (
        d < nearestDistance
      ) {

        nearestDistance =
          d

        nearestName =
          object.name
      }
    }
  }


  return nearestName
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


  const distance =
    Math.sqrt(
      dx * dx +
      dy * dy
    )


  return {

    dx,

    dy,

    distance,

    startObject:
      findObjectAtPoint(
        start
      ),

    endObject:
      findObjectAtPoint(
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

          dx:
            0,

          dy:
            0,

          distance:
            0
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
 * Plotly Data
 *
 * WaferObject를 그대로
 * scatter / lines로 표현
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

      l:
        60,

      r:
        30,

      t:
        30,

      b:
        60
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
     * 일반 모드
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

  const graph =
    getGraph()


  if (!graph) {

    return
  }


  await Plotly.newPlot(

    graph,

    buildData(),

    buildBaseLayout(),

    plotConfig
  )
}


/* ================================================================
 * Marker Size
 *
 * 화면에서 약 8px 정도로 보이도록
 * 현재 scale에 맞춰 데이터 좌표로 변환합니다.
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
 * Ruler Shapes
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
     * Ruler Line
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
     * Start marker
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
     * End marker
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
 * Ruler Annotation
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
        (
          start.x +
          end.x
        ) / 2,

      y:
        (
          start.y +
          end.y
        ) / 2,

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
 * Snap Marker
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
 * ★ 중요
 *
 * Ruler 이동 중에는 Plotly.react() 사용하지 않습니다.
 *
 * shapes / annotations만 relayout합니다.
 * ================================================================ */

async function updateRuler() {

  const graph =
    getGraph()


  if (!graph) {

    return
  }


  const rulerShapes =
    buildRulerShapes()


  const snapShapes =
    buildSnapShapes()


  const annotations =
    buildRulerAnnotations()


  await Plotly.relayout(

    graph,

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
 * Wafer data가 변경되었을 때 사용
 *
 * Plotly.react()
 * ================================================================ */

async function updatePlot() {

  const graph =
    getGraph()


  if (!graph) {

    return
  }


  await Plotly.react(

    graph,

    buildData(),

    buildBaseLayout(),

    plotConfig
  )


  /*
   * react 이후 Ruler 다시 표시
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

  /*
   * Ruler OFF
   */
  if (
    !rulerMode.value
  ) {

    return
  }


  /*
   * 왼쪽 버튼만
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
   * 가장 가까운 Edge에 Snap
   */
  const point =
    applySnap(
      rawPoint
    )


  /*
   * 시작점
   */
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


  /*
   * Ruler 표시
   */
  void updateRuler()
}


/* ================================================================
 * Mouse Move
 * ================================================================ */

function handleMouseMove(
  event: MouseEvent
) {

  /*
   * Ruler drag 중이 아니면 무시
   */
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
   * 현재 마우스 위치를
   * 가장 가까운 Edge로 Snap
   */
  const point =
    applySnap(
      rawPoint
    )


  currentPoint.value =
    point


  /*
   * 측정
   */
  measurement.value =
    calculateMeasurement(

      startPoint.value,

      point
    )


  /*
   * 외부에서도 결과를 받을 수 있도록 emit
   */
  emit(
    'measure',

    measurement.value
  )


  /*
   * ★ 중요
   *
   * Plotly.react()가 아니라
   * relayout()만 사용
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

    /*
     * 마지막 위치도 Snap
     */
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


      emit(
        'measure',

        measurement.value
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

    /*
     * Ruler OFF
     */
    startPoint.value =
      null


    currentPoint.value =
      null


    snapPoint.value =
      null


    await Plotly.relayout(

      getGraph()!,

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
     * Plotly 기본 drag 동작을 끕니다.
     */
    await Plotly.relayout(

      getGraph()!,

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


  const graph =
    getGraph()


  if (!graph) {

    return
  }


  await Plotly.relayout(

    graph,

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


  const graph =
    getGraph()


  if (!graph) {

    return
  }


  void Plotly.relayout(

    graph,

    {

      shapes: [],

      annotations: [],

      dragmode:
        'pan'
    }
  )
}


/* ================================================================
 * Watch Objects
 *
 * 부모에서 objects가 변경되면
 * Plotly.react()
 * ================================================================ */

watch(

  () =>
    props.objects,

  () => {

    void updatePlot()
  },

  {
    deep:
      true
  }
)


/* ================================================================
 * Mounted
 * ================================================================ */

onMounted(
  async () => {

    await nextTick()


    const graph =
      getGraph()


    if (!graph) {

      return
    }


    /*
     * 최초 Plotly 생성
     */
    await initializePlot()


    /*
     * ==========================================================
     * Mouse Event
     *
     * mousedown
     * → Plotly element
     *
     * mousemove
     * mouseup
     * → document
     * ==========================================================
     */

    graph.addEventListener(

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
 * Before Unmount
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


    if (graph) {

      Plotly.purge(
        graph
      )
    }
  }
)

</script>