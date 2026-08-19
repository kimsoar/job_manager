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

      <!-- Clear -->
      <a-button
        :disabled="!hasMeasurement"
        @click="clearMeasurement"
      >
        Clear
      </a-button>

      <!-- Snap type -->
      <a-select
        v-model:value="snapMode"
        :disabled="!rulerMode || !snapEnabled"
        style="width: 140px"
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
        </span>

        <span
          v-if="measurement.endObject"
          class="text-gray-500"
        >
          →
          {{ measurement.endObject }}
        </span>
      </div>

      <div
        v-if="rulerMode && !isDragging"
        class="ml-auto text-gray-400 text-sm"
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


    <!-- =========================================================
         Plot
    ========================================================== -->
    <div
      ref="plotContainer"
      class="relative flex-1 min-h-0"
    >

      <Plotly
        ref="plotly"
        :data="plotData"
        :layout="plotLayout"
        :config="plotConfig"
        class="w-full h-full"
      />


      <!-- =======================================================
           Current Snap indicator
      ======================================================== -->
      <div
        v-if="rulerMode && snapPoint"
        class="
          absolute
          pointer-events-none
          px-2
          py-1
          rounded
          bg-black
          text-white
          text-xs
        "
        :style="snapLabelStyle"
      >
        {{ snapPoint.type }}

        <span v-if="snapPoint.objectId">
          · {{ snapPoint.objectId }}
        </span>
      </div>


      <!-- =======================================================
           Current Measurement
      ======================================================== -->
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

import Plotly from 'vue-plotly'

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


/* ===============================================================
 * Types
 * =============================================================== */

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


/* ===============================================================
 * Props
 * =============================================================== */

interface Props {

  unit?: string

  /*
   * Snap tolerance in screen pixels
   */
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


/* ===============================================================
 * Refs
 * =============================================================== */

const plotly = ref<any>(null)

const plotContainer =
  ref<HTMLElement | null>(null)


const rulerMode =
  ref(false)


const snapEnabled =
  ref(true)


const snapMode =
  ref<SnapType | 'nearest'>('nearest')


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


/* ===============================================================
 * Wafer Objects
 *
 * 실제 프로젝트에서는 API/Props에서 받아오면 됩니다.
 * =============================================================== */

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


/* ===============================================================
 * Object helpers
 * =============================================================== */

const getCenter =
  (obj: WaferObject): Point => {

    return {
      x: obj.x + obj.width / 2,
      y: obj.y + obj.height / 2
    }
  }


const getCorners =
  (obj: WaferObject): SnapPoint[] => {

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


/* ===============================================================
 * Distance
 * =============================================================== */

const pointDistance =
  (
    a: Point,
    b: Point
  ) => {

    const dx =
      b.x - a.x

    const dy =
      b.y - a.y

    return Math.sqrt(
      dx * dx +
      dy * dy
    )
  }


/* ===============================================================
 * Closest point on rectangle edge
 * =============================================================== */

const closestPointOnRectangle =
  (
    point: Point,
    obj: WaferObject
  ): SnapPoint => {

    const left =
      obj.x

    const right =
      obj.x + obj.width

    const bottom =
      obj.y

    const top =
      obj.y + obj.height


    /*
     * Clamp X/Y
     */
    const cx =
      Math.max(
        left,
        Math.min(
          point.x,
          right
        )
      )

    const cy =
      Math.max(
        bottom,
        Math.min(
          point.y,
          top
        )
      )


    /*
     * Distance to each edge
     */
    const dLeft =
      Math.abs(point.x - left)

    const dRight =
      Math.abs(point.x - right)

    const dBottom =
      Math.abs(point.y - bottom)

    const dTop =
      Math.abs(point.y - top)


    const min =
      Math.min(
        dLeft,
        dRight,
        dBottom,
        dTop
      )


    if (min === dLeft) {

      return {
        x: left,
        y: cy,

        type: 'edge',

        objectId: obj.id
      }
    }


    if (min === dRight) {

      return {
        x: right,
        y: cy,

        type: 'edge',

        objectId: obj.id
      }
    }


    if (min === dBottom) {

      return {
        x: cx,
        y: bottom,

        type: 'edge',

        objectId: obj.id
      }
    }


    return {
      x: cx,
      y: top,

      type: 'edge',

      objectId: obj.id
    }
  }


/* ===============================================================
 * Snap candidate
 * =============================================================== */

const getSnapCandidate =
  (
    point: Point
  ): SnapPoint | null => {

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

        const distance =
          pointDistance(
            point,
            center
          )


        if (
          distance <
          bestDistance
        ) {

          bestDistance =
            distance

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

        const corners =
          getCorners(obj)


        for (
          const corner of corners
        ) {

          const distance =
            pointDistance(
              point,
              corner
            )


          if (
            distance <
            bestDistance
          ) {

            bestDistance =
              distance

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
          closestPointOnRectangle(
            point,
            obj
          )


        const distance =
          pointDistance(
            point,
            edge
          )


        if (
          distance <
          bestDistance
        ) {

          bestDistance =
            distance

          best = edge
        }
      }
    }


    /*
     * Convert pixel threshold
     * outside this function.
     *
     * Here we only return the
     * mathematically nearest object.
     */
    return best
  }


/* ===============================================================
 * Plotly graph
 * =============================================================== */

const getGraphDiv =
  (): HTMLElement | null => {

    if (!plotContainer.value) {
      return null
    }


    return plotContainer.value
      .querySelector(
        '.js-plotly-plot'
      )
  }


/* ===============================================================
 * Pixel → Data coordinate
 * =============================================================== */

const getPlotPoint =
  (
    event: MouseEvent
  ): Point | null => {

    const graph =
      getGraphDiv()


    if (!graph) {
      return null
    }


    const gd =
      graph as any


    const fullLayout =
      gd._fullLayout


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


/* ===============================================================
 * Pixel threshold → data threshold
 * =============================================================== */

const getSnapThreshold =
  (): number => {

    const graph =
      getGraphDiv()


    if (!graph) {
      return 0
    }


    const gd =
      graph as any


    const layout =
      gd._fullLayout


    if (!layout) {
      return 0
    }


    const xaxis =
      layout.xaxis


    const thresholdPx =
      props.snapThresholdPx


    const p1 =
      xaxis.p2l(
        xaxis._offset
      )


    const p2 =
      xaxis.p2l(
        xaxis._offset +
        thresholdPx
      )


    return Math.abs(
      p2 - p1
    )
  }


/* ===============================================================
 * Snap with threshold
 * =============================================================== */

const snap =
  (
    point: Point
  ): Point => {

    if (!snapEnabled.value) {
      snapPoint.value = null

      return point
    }


    const candidate =
      getSnapCandidate(point)


    if (!candidate) {
      snapPoint.value = null

      return point
    }


    const distance =
      pointDistance(
        point,
        candidate
      )


    const threshold =
      getSnapThreshold()


    if (
      distance <= threshold
    ) {

      snapPoint.value =
        candidate

      return {
        x: candidate.x,
        y: candidate.y
      }
    }


    snapPoint.value = null


    return point
  }


/* ===============================================================
 * Measurement
 * =============================================================== */

const calculateMeasurement =
  (
    start: Point,
    end: Point
  ): Measurement => {

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


    return {
      dx,
      dy,
      distance
    }
  }


/* ===============================================================
 * Find object containing point
 * =============================================================== */

const findObjectAtPoint =
  (
    point: Point
  ): WaferObject | undefined => {

    return waferObjects.value.find(
      obj => {

        return (
          point.x >= obj.x &&
          point.x <= obj.x + obj.width &&
          point.y >= obj.y &&
          point.y <= obj.y + obj.height
        )
      }
    )
  }


/* ===============================================================
 * Current measurement
 * =============================================================== */

const currentMeasurement =
  computed<Measurement>(() => {

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


    const result =
      calculateMeasurement(
        startPoint.value,
        currentPoint.value
      )


    const startObject =
      findObjectAtPoint(
        startPoint.value
      )


    const endObject =
      findObjectAtPoint(
        currentPoint.value
      )


    return {

      ...result,

      startObject:
        startObject?.id,

      endObject:
        endObject?.id
    }
  })


/* ===============================================================
 * Has measurement
 * =============================================================== */

const hasMeasurement =
  computed(() => {

    return (
      startPoint.value !== null &&
      currentPoint.value !== null
    )
  })


/* ===============================================================
 * Plotly Data
 * =============================================================== */

const plotData =
  computed<Data[]>(() => {

    const data: Data[] = []


    /*
     * Object traces
     */
    for (
      const obj of waferObjects.value
    ) {

      const x0 =
        obj.x

      const x1 =
        obj.x + obj.width

      const y0 =
        obj.y

      const y1 =
        obj.y + obj.height


      data.push({
        type: 'scatter',

        mode: 'lines',

        x: [
          x0,
          x1,
          x1,
          x0,
          x0
        ],

        y: [
          y0,
          y0,
          y1,
          y1,
          y0
        ],

        name: obj.id,

        hovertemplate:
          `${obj.id}<br>` +
          `X: %{x:.0f} ${unit.value}<br>` +
          `Y: %{y:.0f} ${unit.value}` +
          '<extra></extra>',

        line: {
          width: 1
        }
      })
    }


    /*
     * Snap point
     */
    if (snapPoint.value) {

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
  })


/* ===============================================================
 * Plotly Layout
 * =============================================================== */

const plotLayout =
  computed<Partial<Layout>>(() => {

    const layout:
      Partial<Layout> = {

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


      /*
       * Ruler active:
       * Plotly pan/zoom drag disabled.
       */
      dragmode:
        rulerMode.value
          ? false
          : 'pan',


      shapes: [],

      annotations: []
    }


    /*
     * Ruler line
     */
    if (
      startPoint.value &&
      currentPoint.value
    ) {

      const start =
        startPoint.value

      const end =
        currentPoint.value


      const distance =
        pointDistance(
          start,
          end
        )


      layout.shapes = [

        /*
         * Main line
         */
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


        /*
         * Start marker
         */
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


        /*
         * End marker
         */
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


      layout.annotations = [

        {

          x:
            (start.x + end.x) / 2,

          y:
            (start.y + end.y) / 2,

          text:
            `ΔX: ${Math.abs(
              end.x - start.x
            ).toFixed(2)} ${unit.value}` +

            `<br>` +

            `ΔY: ${Math.abs(
              end.y - start.y
            ).toFixed(2)} ${unit.value}` +

            `<br>` +

            `<b>${distance.toFixed(
              2
            )} ${unit.value}</b>`,

          showarrow: false,

          bgcolor: 'white',

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


/* ===============================================================
 * Plotly Config
 * =============================================================== */

const plotConfig =
  computed<Partial<Config>>(
    () => {

      return {

        responsive: true,

        displaylogo: false,

        scrollZoom: true,

        modeBarButtonsToRemove: [
          'select2d',
          'lasso2d'
        ]
      }
    }
  )


/* ===============================================================
 * Mouse Down
 * =============================================================== */

const handleMouseDown =
  (
    event: MouseEvent
  ) => {

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
      getPlotPoint(event)


    if (!rawPoint) {
      return
    }


    const point =
      snap(rawPoint)


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


/* ===============================================================
 * Mouse Move
 * =============================================================== */

const handleMouseMove =
  (
    event: MouseEvent
  ) => {

    if (
      !rulerMode.value ||
      !isDragging.value ||
      !startPoint.value
    ) {
      return
    }


    const rawPoint =
      getPlotPoint(event)


    if (!rawPoint) {
      return
    }


    const point =
      snap(rawPoint)


    currentPoint.value =
      point


    measurement.value =
      calculateMeasurement(
        startPoint.value,
        point
      )
  }


/* ===============================================================
 * Mouse Up
 * =============================================================== */

const handleMouseUp =
  (
    event: MouseEvent
  ) => {

    if (
      !rulerMode.value ||
      !isDragging.value
    ) {
      return
    }


    const rawPoint =
      getPlotPoint(event)


    if (rawPoint) {

      const point =
        snap(rawPoint)


      currentPoint.value =
        point


      if (startPoint.value) {

        measurement.value =
          calculateMeasurement(
            startPoint.value,
            point
          )
      }
    }


    isDragging.value =
      false
  }


/* ===============================================================
 * Toggle Ruler
 * =============================================================== */

const toggleRuler =
  async () => {

    rulerMode.value =
      !rulerMode.value


    if (
      !rulerMode.value
    ) {

      isDragging.value =
        false

      snapPoint.value =
        null

      startPoint.value =
        null

      currentPoint.value =
        null
    }


    await nextTick()
  }


/* ===============================================================
 * Clear
 * =============================================================== */

const clearMeasurement =
  () => {

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
  }


/* ===============================================================
 * ESC
 * =============================================================== */

const handleKeyDown =
  (
    event: KeyboardEvent
  ) => {

    if (
      event.key === 'Escape'
    ) {

      rulerMode.value =
        false

      isDragging.value =
        false

      snapPoint.value =
        null

      startPoint.value =
        null

      currentPoint.value =
        null
    }
  }


/* ===============================================================
 * Snap label
 *
 * 실제 UI에서는 Plotly coordinate → screen coordinate
 * 변환을 추가해서 label 위치를 정확하게 잡을 수 있습니다.
 * =============================================================== */

const snapLabelStyle =
  computed(() => {

    return {
      left: '10px',
      bottom: '10px'
    }
  })


/* ===============================================================
 * Event binding
 * =============================================================== */

onMounted(
  async () => {

    await nextTick()


    const graph =
      getGraphDiv()


    if (graph) {

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
    }


    document.addEventListener(
      'keydown',
      handleKeyDown
    )
  }
)


/* ===============================================================
 * Cleanup
 * =============================================================== */

onBeforeUnmount(
  () => {

    const graph =
      getGraphDiv()


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
  }
)

</script>