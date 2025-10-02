<style lang="scss" scoped>
::v-deep [aria-roledescription='error'] {
  display: none !important;
}
</style>



// src/plugins/MermaidPlugin.ts
import type MarkdownIt from "markdown-it";

export function MermaidPlugin(md: MarkdownIt) {
  const defaultFence =
    md.renderer.rules.fence ||
    ((tokens, idx, options, _env, self) => self.renderToken(tokens, idx, options));

  md.renderer.rules.fence = (tokens, idx, options, env, self) => {
    const token = tokens[idx];
    const lang = (token.info || "").trim();
    const raw = token.content || "";

    if (lang === "mermaid") {
      // 인코딩해서 안전하게 data-attr에 담음
      const encoded = encodeURIComponent(raw);
      return `<div class="mermaid-block" data-raw-enc="${encoded}"></div>`;
    }

    return defaultFence(tokens, idx, options, env, self);
  };
}






<template>
  <div ref="container">
    <vue-markdown-render
      :source="content"
      :plugins="[MermaidPlugin]"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import mermaid from "mermaid";
import { MermaidPlugin } from "@/plugins/MermaidPlugin";
import VueMarkdownRender from "vue-markdown-render";

interface Props {
  content: string;
}
const props = defineProps<Props>();
const container = ref<HTMLElement | null>(null);

function escapeHtml(s: string) {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

async function renderMermaid() {
  if (!container.value) return;

  mermaid.initialize({ startOnLoad: false, theme: "default" });

  const blocks = container.value.querySelectorAll<HTMLElement>(".mermaid-block");

  for (const block of Array.from(blocks)) {
    // dataset 대신 getAttribute 사용 (타입/네이밍 문제 회피)
    const enc = block.getAttribute("data-raw-enc") || "";
    const raw = enc ? decodeURIComponent(enc) : "";

    try {
      // mermaid.render는 버전 따라 반환형이 다를 수 있으니 안전하게 처리
      const result = await (mermaid as any).render(
        `mermaid-${Math.random().toString(36).slice(2)}`,
        raw
      );

      // result가 string인지 객체인지 체크
      let svg = "";
      if (typeof result === "string") svg = result;
      else if (result && typeof result === "object") svg = (result as any).svg ?? String(result);
      else svg = String(result);

      block.innerHTML = svg;
    } catch (err) {
      // 파싱 실패 시 경고 + 원본 코드 표시 (이때는 HTML 이스케이프해서 안전하게 삽입)
      block.innerHTML = `
        <div style="color: #b02a37; font-weight: 600; margin-bottom: 6px;">
          ⚠️ 이 mermaid 블록에는 문법 오류가 있습니다.
        </div>
        <pre style="background:#f8f9fa;padding:8px;border-radius:4px;overflow:auto;">
          <code>${escapeHtml(raw)}</code>
        </pre>
      `;
      // 필요하면 콘솔에 에러 출력
      // console.error("mermaid render error:", err);
    }
  }
}

onMounted(renderMermaid);
watch(() => props.content, renderMermaid);
</script>import type { Config } from "tailwindcss"






tailwindcss

const config: Config = {
  darkMode: "class", // 여전히 동일
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
  plugins: [],
}

export default config




ㅇ
global
@import "tailwindcss";

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;

    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;

    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;

    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 222.2 84% 4.9%;

    --radius: 0.5rem;
  }
}






d

d

import { clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: any[]) {
  return twMerge(clsx(inputs))
}



ㅇ
@import "tailwindcss";

/* ✅ theme 확장 */
@theme {
  --color-border: hsl(var(--border));
  --color-input: hsl(var(--input));
  --color-ring: hsl(var(--ring));
  --color-background: hsl(var(--background));
  --color-foreground: hsl(var(--foreground));

  --color-primary: hsl(var(--primary));
  --color-primary-foreground: hsl(var(--primary-foreground));

  --color-secondary: hsl(var(--secondary));
  --color-secondary-foreground: hsl(var(--secondary-foreground));

  --radius-lg: var(--radius);
  --radius-md: calc(var(--radius) - 2px);
  --radius-sm: calc(var(--radius) - 4px);
}

/* ✅ base layer: shadcn-vue 테마 변수 */
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;

    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;

    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;

    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 222.2 84% 4.9%;

    --radius: 0.5rem;
  }
}



<template>
  <div ref="chartRef" style="width: 100%; height: 400px;"></div>
</template>

<script lang="ts" setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import * as echarts from "echarts/core";
import { GridComponent, TooltipComponent, TitleComponent } from "echarts/components";
import { BarChart, CustomChart } from "echarts/charts";
import { CanvasRenderer } from "echarts/renderers";

// 필요한 모듈 등록
echarts.use([GridComponent, TooltipComponent, TitleComponent, BarChart, CustomChart, CanvasRenderer]);

const chartRef = ref<HTMLDivElement | null>(null);
let chart: echarts.ECharts | null = null;

onMounted(() => {
  if (chartRef.value) {
    chart = echarts.init(chartRef.value);

    // Gantt용 데이터
    const tasks = [
      { name: "기획", start: "2025-10-01", end: "2025-10-05" },
      { name: "디자인", start: "2025-10-06", end: "2025-10-12" },
      { name: "개발", start: "2025-10-10", end: "2025-10-25" },
      { name: "테스트", start: "2025-10-20", end: "2025-10-30" },
    ];

    // 날짜를 number로 변환
    const parseDate = (d: string) => new Date(d).getTime();

    const option: echarts.EChartsOption = {
      title: { text: "프로젝트 Gantt 차트" },
      tooltip: {
        formatter: (p: any) => {
          return `${p.name}<br/>${new Date(p.value[0]).toLocaleDateString()} ~ ${new Date(p.value[1]).toLocaleDateString()}`;
        },
      },
      grid: { left: 120, right: 40, top: 40, bottom: 40 },
      xAxis: {
        type: "time",
        min: parseDate("2025-09-28"),
        max: parseDate("2025-11-05"),
        axisLabel: { formatter: (val: number) => new Date(val).toLocaleDateString() },
      },
      yAxis: {
        type: "category",
        data: tasks.map(t => t.name),
      },
      series: [
        {
          type: "custom",
          renderItem: (params, api) => {
            const categoryIndex = api.value(2); // y축 index
            const start = api.coord([api.value(0), categoryIndex]);
            const end = api.coord([api.value(1), categoryIndex]);
            const height = api.size([0, 1])[1] * 0.6;

            return {
              type: "rect",
              shape: {
                x: start[0],
                y: start[1] - height / 2,
                width: end[0] - start[0],
                height: height,
              },
              style: api.style(),
            };
          },
          encode: { x: [0, 1], y: 2 },
          data: tasks.map((t, i) => [parseDate(t.start), parseDate(t.end), i, t.name]),
          itemStyle: { color: "#4CAF50" },
        },
      ],
    };

    chart.setOption(option);
  }
});

onBeforeUnmount(() => {
  chart?.dispose();
});
</script>





<template>
  <div ref="chartRef" style="width: 100%; height: 500px;"></div>
</template>

<script lang="ts" setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import * as echarts from "echarts/core";
import { GridComponent, TooltipComponent, TitleComponent, LegendComponent } from "echarts/components";
import { CustomChart } from "echarts/charts";
import { CanvasRenderer } from "echarts/renderers";

echarts.use([GridComponent, TooltipComponent, TitleComponent, LegendComponent, CustomChart, CanvasRenderer]);

const chartRef = ref<HTMLDivElement | null>(null);
let chart: echarts.ECharts | null = null;

// 샘플 데이터
const statusData = [
  { equipment: "설비1", start: "2025-10-01 08:00", end: "2025-10-01 12:00", state: "run" },
  { equipment: "설비1", start: "2025-10-01 12:00", end: "2025-10-01 13:00", state: "idle" },
  { equipment: "설비1", start: "2025-10-01 13:00", end: "2025-10-01 15:00", state: "bm" },

  { equipment: "설비2", start: "2025-10-01 09:00", end: "2025-10-01 14:00", state: "run" },
  { equipment: "설비2", start: "2025-10-01 14:00", end: "2025-10-01 16:00", state: "idle" },
];

// 상태별 색상
const stateColors: Record<string, string> = {
  run: "#4CAF50",
  idle: "#FFC107",
  bm: "#F44336"
};

const parseDate = (d: string) => new Date(d).getTime();

// y축 설비 목록
const equipments = Array.from(new Set(statusData.map(s => s.equipment)));

onMounted(() => {
  if (chartRef.value) {
    chart = echarts.init(chartRef.value);

    const option: echarts.EChartsOption = {
      title: { text: "설비 상태 Gantt 차트" },
      tooltip: {
        formatter: (p: any) => {
          const s = p.data.raw;
          return `
            <b>${s.equipment}</b><br/>
            상태: ${s.state}<br/>
            ${new Date(s.start).toLocaleTimeString()} ~ ${new Date(s.end).toLocaleTimeString()}
          `;
        },
      },
      legend: {
        top: 30,
        data: Object.keys(stateColors),
        selectedMode: "multiple"
      },
      grid: { left: 120, right: 40, top: 80, bottom: 40 },
      xAxis: {
        type: "time",
        axisLabel: { formatter: (val: number) => new Date(val).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }
      },
      yAxis: {
        type: "category",
        data: equipments,
      },
      series: Object.keys(stateColors).map(state => ({
        name: state,
        type: "custom",
        renderItem: (params, api) => {
          const categoryIndex = api.value(2);
          const start = api.coord([api.value(0), categoryIndex]);
          const end = api.coord([api.value(1), categoryIndex]);
          const height = api.size([0, 1])[1] * 0.6;

          return {
            type: "rect",
            shape: {
              x: start[0],
              y: start[1] - height / 2,
              width: end[0] - start[0],
              height: height,
            },
            style: { fill: stateColors[state] }
          };
        },
        encode: { x: [0, 1], y: 2 },
        data: statusData
          .filter(s => s.state === state)
          .map(s => ({
            value: [parseDate(s.start), parseDate(s.end), equipments.indexOf(s.equipment)],
            raw: s
          })),
      }))
    };

    chart.setOption(option);
  }
});

onBeforeUnmount(() => {
  chart?.dispose();
});
</script>



const equipments = ["설비1", "설비2", "설비3"];

// 설비별 색상 매핑
const equipmentColors: Record<string, string> = {
  "설비1": "#4CAF50",
  "설비2": "#FFC107",
  "설비3": "#2196F3",
};

const option: echarts.EChartsOption = {
  yAxis: {
    type: "category",
    data: equipments,
    axisLabel: {
      formatter: (value: string) => `{${value}|${value}}`,  // rich 스타일 키와 동일하게
      rich: equipments.reduce((acc, eq) => {
        acc[eq] = { color: equipmentColors[eq], fontWeight: "bold" };
        return acc;
      }, {} as Record<string, any>)
    }
  },
  xAxis: {
    type: "time"
  },
  series: [] // Gantt 시리즈 들어가는 부분
};

