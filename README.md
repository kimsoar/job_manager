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



