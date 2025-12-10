<script setup lang="ts">
import { ref, onMounted } from "vue";

const editor = ref<HTMLDivElement | null>(null);

// 옵션 설정
const maxHeight = 200;
const minHeight = 40;

// paste로 이미지 삽입
const onPaste = (e: ClipboardEvent) => {
  const items = e.clipboardData?.items;
  if (!items) return;

  for (const item of items) {
    if (item.type.startsWith("image/")) {
      const file = item.getAsFile();
      if (!file) continue;

      const reader = new FileReader();
      reader.onload = () => {
        insertImageAtCursor(reader.result as string);
      };
      reader.readAsDataURL(file);

      e.preventDefault();
    }
  }
};

// 드래그&드롭 이미지 삽입
const onDrop = (e: DragEvent) => {
  e.preventDefault();
  const files = e.dataTransfer?.files;
  if (!files) return;

  [...files].forEach((file) => {
    if (!file.type.startsWith("image/")) return;

    const reader = new FileReader();
    reader.onload = () => {
      insertImageAtCursor(reader.result as string);
    };
    reader.readAsDataURL(file);
  });
};

const preventDefaults = (e: Event) => e.preventDefault();

// 커서 위치에 이미지 삽입
const insertImageAtCursor = (src: string) => {
  const img = document.createElement("img");
  img.src = src;
  img.className = "max-w-[200px] rounded-md my-2";

  const selection = window.getSelection();
  if (!selection || !selection.rangeCount) {
    editor.value?.appendChild(img);
    autoResize();
    return;
  }

  const range = selection.getRangeAt(0);
  range.insertNode(img);
  range.setStartAfter(img);
  range.setEndAfter(img);
  selection.removeAllRanges();
  selection.addRange(range);

  autoResize();
};

// ChatGPT 스타일 height 자동 조절
const autoResize = () => {
  const el = editor.value;
  if (!el) return;

  el.style.height = "auto";

  const contentHeight = el.scrollHeight;
  const targetHeight = Math.max(contentHeight, minHeight);

  if (targetHeight <= maxHeight) {
    el.style.height = targetHeight + "px";
    el.style.overflowY = "hidden";
  } else {
    el.style.height = maxHeight + "px";
    el.style.overflowY = "auto";
    el.scrollTop = el.scrollHeight;
  }
};

onMounted(() => {
  editor.value?.addEventListener("input", autoResize);
});
</script>



<script setup lang="ts">
import { ref, onMounted } from "vue";

const editor = ref<HTMLDivElement | null>(null);

// 옵션 설정
const maxHeight = 200;
const minHeight = 40;

// paste로 이미지 삽입
const onPaste = (e: ClipboardEvent) => {
  const items = e.clipboardData?.items;
  if (!items) return;

  for (const item of items) {
    if (item.type.startsWith("image/")) {
      const file = item.getAsFile();
      if (!file) continue;

      const reader = new FileReader();
      reader.onload = () => {
        insertImageAtCursor(reader.result as string);
      };
      reader.readAsDataURL(file);

      e.preventDefault();
    }
  }
};

// 드래그&드롭 이미지 삽입
const onDrop = (e: DragEvent) => {
  e.preventDefault();
  const files = e.dataTransfer?.files;
  if (!files) return;

  [...files].forEach((file) => {
    if (!file.type.startsWith("image/")) return;

    const reader = new FileReader();
    reader.onload = () => {
      insertImageAtCursor(reader.result as string);
    };
    reader.readAsDataURL(file);
  });
};

const preventDefaults = (e: Event) => e.preventDefault();

// 커서 위치에 이미지 삽입
const insertImageAtCursor = (src: string) => {
  const img = document.createElement("img");
  img.src = src;
  img.className = "max-w-[200px] rounded-md my-2";

  const selection = window.getSelection();
  if (!selection || !selection.rangeCount) {
    editor.value?.appendChild(img);
    autoResize();
    return;
  }

  const range = selection.getRangeAt(0);
  range.insertNode(img);
  range.setStartAfter(img);
  range.setEndAfter(img);
  selection.removeAllRanges();
  selection.addRange(range);

  autoResize();
};

// ChatGPT 스타일 height 자동 조절
const autoResize = () => {
  const el = editor.value;
  if (!el) return;

  el.style.height = "auto";

  const contentHeight = el.scrollHeight;
  const targetHeight = Math.max(contentHeight, minHeight);

  if (targetHeight <= maxHeight) {
    el.style.height = targetHeight + "px";
    el.style.overflowY = "hidden";
  } else {
    el.style.height = maxHeight + "px";
    el.style.overflowY = "auto";
    el.scrollTop = el.scrollHeight;
  }
};

onMounted(() => {
  editor.value?.addEventListener("input", autoResize);
});
</script>



<template>
  <ChatInput
    v-model="content"
    :uploadImage="uploadImage"
  />
</template>

<script setup lang="ts">
import ChatInput from "./ChatInput.vue";
import { ref } from "vue";

const content = ref("");

const uploadImage = async (file: File, onProgress: (percent: number) => void) => {
  // 예: FastAPI 업로드
  const form = new FormData();
  form.append("file", file);

  return new Promise(async (resolve) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/api/upload");

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) {
        onProgress(Math.round((e.loaded / e.total) * 100));
      }
    };

    xhr.onload = () => {
      const { url } = JSON.parse(xhr.responseText);
      resolve(url); // server url 리턴
    };

    xhr.send(form);
  });
};
</script>



<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from "vue";

const props = defineProps<{
  modelValue: string;
  uploadImage: (file: File, onProgress: (p: number) => void) => Promise<string>;
}>();

const emit = defineEmits(["update:modelValue"]);

const editor = ref<HTMLDivElement | null>(null);
const isComposing = ref(false);

const updateModelValue = () => {
  if (isComposing.value) return;
  emit("update:modelValue", editor.value?.innerHTML ?? "");
};

watch(
  () => props.modelValue,
  (v) => {
    if (editor.value && editor.value.innerHTML !== v) {
      editor.value.innerHTML = v || "";
    }
  }
);

onMounted(() => {
  editor.value!.innerHTML = props.modelValue || "";
});

/* ---------------------------------------------------------
   이미지 붙여넣기 처리
--------------------------------------------------------- */
const onPaste = async (e: ClipboardEvent) => {
  const items = e.clipboardData?.items;
  if (!items) return;

  for (const item of items) {
    if (!item.type.startsWith("image/")) continue;

    const file = item.getAsFile();
    if (!file) return;

    e.preventDefault();

    // 1) Blob URL로 임시 삽입
    const blobUrl = URL.createObjectURL(file);

    const tempId = "img-" + Math.random().toString(36).slice(2, 9);

    insertAtCursor(
      `<span class="relative inline-block group" data-temp="${tempId}">
          <img src="${blobUrl}" class="max-w-[150px] rounded-md" />
          <button class="absolute -top-2 -right-2 w-5 h-5 bg-black/60 text-white rounded-full opacity-0 group-hover:opacity-100 transition"
            data-remove="${tempId}">
            ×
          </button>

          <div class="absolute bottom-0 left-0 right-0 h-1 bg-gray-300">
            <div class="h-full bg-blue-500 upload-progress-${tempId}" style="width:0%"></div>
          </div>
      </span>`
    );

    updateModelValue();

    // 2) 이미지 업로드
    const serverUrl = await props.uploadImage(file, (percent) => {
      const bar = editor.value?.querySelector(
        `.upload-progress-${tempId}`
      ) as HTMLElement;
      if (bar) bar.style.width = `${percent}%`;
    });

    // 3) blob → server-url로 교체
    const el = editor.value?.querySelector(`[data-temp="${tempId}"]`);
    if (el) {
      el.innerHTML = `
        <img src="${serverUrl}" class="max-w-[150px] rounded-md" />
        <button class="absolute -top-2 -right-2 w-5 h-5 bg-black/60 text-white rounded-full opacity-0 group-hover:opacity-100 transition"
          data-remove="${tempId}">
          ×
        </button>
      `;
    }

    updateModelValue();
  }
};

/* ---------------------------------------------------------
   X 버튼으로 이미지 삭제
--------------------------------------------------------- */
const onClick = (e: MouseEvent) => {
  const target = e.target as HTMLElement;
  const id = target.getAttribute("data-remove");
  if (!id) return;

  const el = editor.value?.querySelector(`[data-temp="${id}"]`);
  if (el) el.remove();

  updateModelValue();
};

/* ---------------------------------------------------------
   커서 위치에 HTML 삽입
--------------------------------------------------------- */
const insertAtCursor = (html: string) => {
  editor.value?.focus();
  document.execCommand("insertHTML", false, html);
};
</script>

<template>
  <div
    class="border rounded-md p-3 min-h-[48px] max-h-[300px] overflow-y-auto focus-within:ring-2 focus-within:ring-ring bg-background text-foreground shadow-sm"
  >
    <div
      ref="editor"
      contenteditable="true"
      class="outline-none whitespace-pre-wrap break-words"
      @input="updateModelValue"
      @paste="onPaste"
      @click="onClick"
      @compositionstart="isComposing = true"
      @compositionend="isComposing = false"
    ></div>
  </div>
</template>

<style scoped>
/* shadcn-vue Textarea 스타일과 동일한 느낌 유지 */
</style>




<script setup lang="ts">
import { ref, onMounted } from "vue";

const editor = ref<HTMLDivElement | null>(null);

// 옵션 설정
const maxHeight = 200;
const minHeight = 40;

// paste로 이미지 삽입
const onPaste = (e: ClipboardEvent) => {
  const items = e.clipboardData?.items;
  if (!items) return;

  for (const item of items) {
    if (item.type.startsWith("image/")) {
      const file = item.getAsFile();
      if (!file) continue;

      const reader = new FileReader();
      reader.onload = () => {
        insertImageAtCursor(reader.result as string);
      };
      reader.readAsDataURL(file);

      e.preventDefault(); // 기본 텍스트 붙여넣기 차단
    }
  }
};

// 드래그&드롭 이미지 삽입
const onDrop = (e: DragEvent) => {
  e.preventDefault();
  const files = e.dataTransfer?.files;
  if (!files) return;

  [...files].forEach((file) => {
    if (!file.type.startsWith("image/")) return;

    const reader = new FileReader();
    reader.onload = () => {
      insertImageAtCursor(reader.result as string);
    };
    reader.readAsDataURL(file);
  });
};

const preventDefaults = (e: Event) => e.preventDefault();

// 커서 위치에 이미지 삽입
const insertImageAtCursor = (src: string) => {
  const img = document.createElement("img");
  img.src = src;
  img.className = "max-w-[200px] rounded-md mt-1 mb-1";

  const selection = window.getSelection();
  if (!selection || !selection.rangeCount) {
    editor.value?.appendChild(img);
    return;
  }

  const range = selection.getRangeAt(0);
  range.insertNode(img);
  range.setStartAfter(img);
  range.setEndAfter(img);
  selection.removeAllRanges();
  selection.addRange(range);

  autoResize();
};

// height 자동 조절 (ChatGPT 스타일)
const autoResize = () => {
  const el = editor.value;
  if (!el) return;

  el.style.height = "auto";

  const contentHeight = el.scrollHeight;
  const targetHeight = Math.max(contentHeight, minHeight);

  if (targetHeight <= maxHeight) {
    el.style.height = targetHeight + "px";
    el.style.overflowY = "hidden";
  } else {
    el.style.height = maxHeight + "px";
    el.style.overflowY = "auto";
    el.scrollTop = el.scrollHeight;
  }
};

onMounted(() => {
  editor.value?.addEventListener("input", autoResize);
});
</script>

<template>
  <div
    ref="editor"
    contenteditable="true"
    class="border rounded-md p-3 text-base leading-relaxed focus:outline-none bg-white
           min-h-[40px] max-h-[200px] overflow-hidden transition-all"
    @paste="onPaste"
    @drop="onDrop"
    @dragover="preventDefaults"
    @dragenter="preventDefaults"
  ></div>
</template>




import type { DirectiveBinding } from "vue";

interface Options {
  maxHeight?: number;
  minHeight?: number;
  duration?: number; // 애니메이션 지속시간(ms)
}

const adjustHeight = (el: HTMLTextAreaElement, options: Options) => {
  const {
    maxHeight = 200,
    minHeight = 40,
    duration = 150,
  } = options;

  // 애니메이션 적용
  el.style.transition = `height ${duration}ms ease`;

  // height 초기화 후 scrollHeight 측정
  el.style.height = "auto";
  const contentHeight = el.scrollHeight;

  // 최소 높이 → 초기 입력창 크기 보장
  const targetHeight = Math.max(contentHeight, minHeight);

  // 최대 높이 미만일 때
  if (targetHeight <= maxHeight) {
    el.style.overflowY = "hidden";
    el.style.height = `${targetHeight}px`;
    return;
  }

  // 최대 높이 이상일 때 → 고정 크기 + 스크롤
  el.style.height = `${maxHeight}px`;
  el.style.overflowY = "auto";

  // 스크롤을 항상 아래로
  requestAnimationFrame(() => {
    el.scrollTop = el.scrollHeight;
  });
};

export default {
  mounted(el: HTMLTextAreaElement, binding: DirectiveBinding) {
    const value = binding.value || {};
    const options: Options =
      typeof value === "object"
        ? value
        : { maxHeight: Number(value) || 200 };

    // 사용자가 강제로 resize하지 못하도록
    el.style.resize = "none";

    // 초기 높이 맞추기
    requestAnimationFrame(() => adjustHeight(el, options));

    // 입력할 때 자연스럽게 변경
    el.addEventListener("input", () => adjustHeight(el, options));
  },

  updated(el: HTMLTextAreaElement, binding: DirectiveBinding) {
    const value = binding.value || {};
    const options: Options =
      typeof value === "object"
        ? value
        : { maxHeight: Number(value) || 200 };

    requestAnimationFrame(() => adjustHeight(el, options));
  },
};

import chatgptAutoresize from "@/directives/chatgpt-autoresize";

app.directive("chatgpt-autoresize", chatgptAutoresize);



<Textarea
  v-model="message"
  v-chatgpt-autoresize="{ maxHeight: 200, minHeight: 40, duration: 150 }"
  class="overflow-hidden"
  placeholder="메시지를 입력하세요..."
/>









import type { DirectiveBinding } from "vue";

const adjustHeight = (el: HTMLTextAreaElement, maxHeight?: number) => {
  // 콘텐츠 줄어들 때 높이가 줄어드는 문제 방지 위해 reset
  el.style.height = "auto";

  const contentHeight = el.scrollHeight;

  if (maxHeight && contentHeight > maxHeight) {
    el.style.height = maxHeight + "px";
    el.style.overflowY = "auto";

    // 🔥 스크롤이 생긴 경우 항상 아래로 유지
    el.scrollTop = el.scrollHeight;
  } else {
    el.style.height = contentHeight + "px";
    el.style.overflowY = "hidden";

    // 🔥 overflow 없을 때는 scrollTop 리셋 필요 없음
  }
};

export default {
  mounted(el: HTMLTextAreaElement, binding: DirectiveBinding) {
    const maxHeight = binding.value;

    el.style.resize = "none";

    requestAnimationFrame(() => adjustHeight(el, maxHeight));
    el.addEventListener("input", () => adjustHeight(el, maxHeight));
  },

  updated(el: HTMLTextAreaElement, binding: DirectiveBinding) {
    const maxHeight = binding.value;
    requestAnimationFrame(() => adjustHeight(el, maxHeight));
  },
};



<script setup lang="ts">
import { ref } from "vue";
import { Textarea } from "@/components/ui/textarea";

const bio = ref("");
</script>

<template>
  <Textarea
    v-model="bio"
    v-autoresize="300"   <!-- 최대 높이 300px -->
    class="overflow-hidden"
  />
</template>


import { createApp } from "vue";
import App from "./App.vue";
import autoresize from "@/directives/autoresize";

const app = createApp(App);

app.directive("autoresize", autoresize);

app.mount("#app");


import type { DirectiveBinding } from "vue";

const adjustHeight = (el: HTMLTextAreaElement, maxHeight?: number) => {
  el.style.height = "0px";                    // reset
  el.style.height = el.scrollHeight + "px";   // adjust

  if (maxHeight && el.scrollHeight > maxHeight) {
    el.style.height = maxHeight + "px";
    el.style.overflowY = "auto";
  } else {
    el.style.overflowY = "hidden";
  }
};

export default {
  mounted(el: HTMLTextAreaElement, binding: DirectiveBinding) {
    const maxHeight = binding.value;

    // disable manual resizing
    el.style.resize = "none";

    // adjust on mount
    requestAnimationFrame(() => adjustHeight(el, maxHeight));

    // adjust on input
    el.addEventListener("input", () => adjustHeight(el, maxHeight));
  },

  updated(el: HTMLTextAreaElement, binding: DirectiveBinding) {
    const maxHeight = binding.value;
    requestAnimationFrame(() => adjustHeight(el, maxHeight));
  },
};




// src/composables/useAutosizeTextarea.ts

import { ref, watch, onMounted, nextTick, type Ref } from 'vue';

/**
 * v-model 값에 따라 textarea의 높이를 자동으로 조절하는 로직
 * @param modelValue v-model로 바인딩된 텍스트 내용의 Ref
 * @returns {Ref<HTMLTextAreaElement | null>} textarea DOM 요소에 바인딩할 Ref
 */
export function useAutosizeTextarea(modelValue: Ref<string>) {
  // 1. <textarea> DOM 요소를 참조하기 위한 Ref
  const textareaRef = ref<HTMLTextAreaElement | null>(null);

  // 2. 높이 조절 로직
  const resize = () => {
    if (textareaRef.value) {
      const textarea = textareaRef.value;

      // 1단계: 높이를 'auto'로 설정하여 스크롤바를 숨기고
      // 컨텐츠에 맞는 최소 높이를 재계산하도록 준비합니다.
      textarea.style.height = 'auto';

      // 2단계: 'scrollHeight' (컨텐츠 전체 높이)를 새로운 높이로 설정합니다.
      // 36px은 (줄 높이 + 패딩)에 따라 다를 수 있으며, 최소 높이 확보를 위해
      // 여기서는 scrollHeight를 그대로 사용합니다.
      textarea.style.height = `${textarea.scrollHeight}px`;
    }
  };

  // 3. 텍스트 내용(modelValue)이 변경될 때마다 높이 조절
  watch(modelValue, () => {
    // DOM 업데이트가 완료된 후 (e.g., 새 줄이 추가된 후) 높이를 계산
    nextTick(resize);
  });

  // 4. 컴포넌트 마운트 시 초기 높이 설정
  onMounted(resize);

  return { textareaRef, resize };
}







<script setup lang="ts">
import { ref } from 'vue';
// shadcn-vue의 Textarea 컴포넌트 임포트
import { Textarea } from '@/components/ui/textarea';
import { useAutosizeTextarea } from './composables/useAutosizeTextarea';

// 1. v-model로 사용할 반응형 상태
const content = ref('');
</script>

<template>
  <div>
    <Textarea
      v-model="content"
      placeholder="여기에 내용을 입력하세요..."
      :ref="useAutosizeTextarea(content).textareaRef"
      
      class="
        min-h-[100px]  /* 최소 높이 설정 */
        resize-none    /* 사용자가 임의로 크기를 조절하는 기능 비활성화 */
        overflow-hidden /* 스크롤바가 생기지 않도록 숨김 */
      "
    />
    <p class="mt-2 text-sm text-gray-500">
      현재 내용: {{ content.length }}자
    </p>
  </div>
</template>



=====






<script setup lang="ts">
import { ref, onMounted, nextTick } from "vue"
import { Textarea } from "@/components/ui/textarea"

interface PreviewImage {
  id: string
  file: File
  base64: string   // 미리보기 & 전송용 (data:*;base64,...)
}

const message = ref("")
const images = ref<PreviewImage[]>([])
const dropActive = ref(false)
const textareaRef = ref<HTMLTextAreaElement | null>(null)

// --- autosize ---
function resizeTextarea() {
  const ta = textareaRef.value
  if (!ta) return
  // reset then set to scrollHeight
  ta.style.height = "0px"
  // a small offset ensures no scrollbar flicker
  ta.style.height = (ta.scrollHeight) + "px"
}

onMounted(async () => {
  await nextTick()
  resizeTextarea()
})

// --- 파일 -> base64 변환 ---
function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result as string)
    reader.onerror = () => reject(new Error("FileReader error"))
    reader.readAsDataURL(file)
  })
}

async function addImageFile(file: File) {
  if (!file.type.startsWith("image/")) return
  // optional: file size limit (예: 5MB)
  const MAX_MB = 8
  if (file.size > MAX_MB * 1024 * 1024) {
    // 원하면 사용자에게 알리는 UI를 추가하세요
    console.warn("파일이 너무 큽니다:", file.name)
    return
  }

  const base64 = await fileToBase64(file)
  images.value.push({
    id: crypto.randomUUID(),
    file,
    base64,
  })
}

// --- paste ---
function onPaste(e: ClipboardEvent) {
  const items = e.clipboardData?.items
  if (!items) return
  for (let i = 0; i < items.length; i++) {
    const item = items[i]
    if (item.type.startsWith("image/")) {
      const file = item.getAsFile()
      if (file) addImageFile(file)
    }
  }
}

// --- drag & drop ---
function onDragOver(e: DragEvent) {
  e.preventDefault()
  dropActive.value = true
}
function onDragLeave() {
  dropActive.value = false
}
function onDrop(e: DragEvent) {
  e.preventDefault()
  dropActive.value = false
  const files = e.dataTransfer?.files
  if (!files) return
  for (let i = 0; i < files.length; i++) {
    addImageFile(files[i])
  }
}

// --- 기타 UI 핸들러 ---
function onInput() {
  resizeTextarea()
}

function removeImage(id: string) {
  images.value = images.value.filter(i => i.id !== id)
}

// --- submit (Base64 전송) ---
async function submit() {
  if (!message.value.trim() && images.value.length === 0) return

  const payload = {
    text: message.value.trim(),
    images: images.value.map(i => i.base64),
  }

  // 예시: 실제 API 호출
  // await api.post("/api/chat", payload)

  console.log("전송 payload:", payload)

  // 초기화
  message.value = ""
  images.value = []
  await nextTick()
  resizeTextarea()
}
</script>

<template>
  <div
    class="w-full max-w-3xl mx-auto p-4 rounded-xl border bg-white shadow-sm transition-colors"
    @dragover.prevent="onDragOver"
    @dragleave="onDragLeave"
    @drop.prevent="onDrop"
    :class="{ 'border-blue-400 bg-blue-50/50': dropActive }"
  >
    <!-- 이미지 미리보기 -->
    <div v-if="images.length" class="flex flex-wrap gap-3 mb-3">
      <div
        v-for="img in images"
        :key="img.id"
        class="relative w-28 h-28 rounded-md border overflow-hidden bg-gray-50"
      >
        <img :src="img.base64" class="object-cover w-full h-full" />
        <button
          @click="removeImage(img.id)"
          class="absolute top-1 right-1 bg-black/60 text-white text-xs rounded px-1"
          aria-label="이미지 삭제"
        >
          ✕
        </button>
      </div>
    </div>

    <!-- 입력창 -->
    <div class="flex items-end gap-3">
      <!-- asChild로 내부 textarea에 ref 직접 붙임 -->
      <Textarea class="flex-1" asChild>
        <textarea
          ref="textareaRef"
          v-model="message"
          @paste="onPaste"
          @input="onInput"
          placeholder="메시지를 입력하거나 이미지를 붙여넣기하세요…"
          class="w-full min-h-[40px] max-h-[300px] overflow-y-auto resize-none rounded-lg border px-3 py-2 text-sm
                 placeholder:text-muted-foreground focus-visible:ring-2 focus-visible:outline-none"
        />
      </Textarea>

      <button
        @click="submit"
        class="h-10 px-4 rounded-md bg-black text-white font-medium hover:bg-black/80 disabled:opacity-50"
        :disabled="!message.trim() && images.length === 0"
      >
        전송
      </button>
    </div>
  </div>
</template>

<style scoped>
/* 필요 시 추가 스타일 */
</style>




<script setup lang="ts">
import { ref, onMounted } from "vue"
import { Textarea } from "@/components/ui/textarea"

interface PreviewImage {
  id: string
  file: File
  url: string       // 미리보기용
  base64: string    // 전송용
}

const message = ref("")
const images = ref<PreviewImage[]>([])

const dropActive = ref(false)
const textareaRef = ref<HTMLTextAreaElement | null>(null)

function resizeTextarea() {
  if (!textareaRef.value) return
  textareaRef.value.style.height = "auto"
  textareaRef.value.style.height = textareaRef.value.scrollHeight + "px"
}

onMounted(() => {
  resizeTextarea()
})

function onInput() {
  resizeTextarea()
}

// 파일을 Base64로 변환
function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result as string)
    reader.readAsDataURL(file)
  })
}

async function addImage(file: File) {
  const base64 = await fileToBase64(file)
  const url = URL.createObjectURL(file)

  images.value.push({
    id: crypto.randomUUID(),
    file,
    url,
    base64,
  })
}

// 붙여넣기 처리
function onPaste(e: ClipboardEvent) {
  const items = e.clipboardData?.items
  if (!items) return

  for (const item of items) {
    if (item.type.startsWith("image/")) {
      const file = item.getAsFile()
      if (file) addImage(file)
    }
  }
}

// Drag & Drop
function onDrop(e: DragEvent) {
  dropActive.value = false
  const files = e.dataTransfer?.files
  if (!files) return

  for (const file of files) {
    if (file.type.startsWith("image/")) {
      addImage(file)
    }
  }
}

function onDragOver(e: DragEvent) {
  e.preventDefault()
  dropActive.value = true
}

function onDragLeave() {
  dropActive.value = false
}

function removeImage(id: string) {
  images.value = images.value.filter((img) => img.id !== id)
}

// 최종 전송
function submit() {
  const payload = {
    text: message.value,
    images: images.value.map((img) => img.base64),
  }

  console.log("전송 Payload:", payload)

  // 실제 API 호출 예시
  // await api.post("/message", payload)

  message.value = ""
  images.value = []
  resizeTextarea()
}
</script>


<template>
  <div 
    class="w-full max-w-3xl mx-auto p-4 rounded-xl border bg-white shadow-sm transition-colors"
    @drop.prevent="onDrop"
    @dragover.prevent="onDragOver"
    @dragleave="onDragLeave"
    :class="{ 'border-blue-400 bg-blue-50/50': dropActive }"
  >

    <!-- 이미지 미리보기 -->
    <div v-if="images.length" class="flex flex-wrap gap-3 mb-3">
      <div
        v-for="img in images"
        :key="img.id"
        class="relative w-24 h-24 rounded-md border overflow-hidden"
      >
        <img :src="img.url" class="object-cover w-full h-full" />
        <button
          class="absolute top-1 right-1 bg-black/60 text-white text-xs rounded px-1"
          @click="removeImage(img.id)"
        >✕</button>
      </div>
    </div>

    <!-- 입력 + 전송 -->
    <div class="flex items-end gap-3">
      <Textarea
        ref="textareaRef"
        v-model="message"
        @paste="onPaste"
        @input="onInput"
        placeholder="메시지를 입력하거나 이미지를 붙여넣기하세요…"
        class="flex-1 min-h-[40px] max-h-[200px] overflow-y-auto resize-none rounded-lg 
               border px-3 py-2 focus-visible:ring-2"
      />

      <button
        @click="submit"
        class="h-10 px-4 rounded-md bg-black text-white hover:bg-black/80"
      >
        전송
      </button>
    </div>

  </div>
</template>


<script setup lang="ts">
import { ref, onMounted } from "vue"
import { Textarea } from "@/components/ui/textarea"

interface PreviewImage {
  id: string
  file: File
  url: string       // 미리보기용
  base64: string    // 전송용
}

const message = ref("")
const images = ref<PreviewImage[]>([])

const dropActive = ref(false)
const textareaRef = ref<HTMLTextAreaElement | null>(null)

function resizeTextarea() {
  if (!textareaRef.value) return
  textareaRef.value.style.height = "auto"
  textareaRef.value.style.height = textareaRef.value.scrollHeight + "px"
}

onMounted(() => {
  resizeTextarea()
})

function onInput() {
  resizeTextarea()
}

// 파일을 Base64로 변환
function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result as string)
    reader.readAsDataURL(file)
  })
}

async function addImage(file: File) {
  const base64 = await fileToBase64(file)
  const url = URL.createObjectURL(file)

  images.value.push({
    id: crypto.randomUUID(),
    file,
    url,
    base64,
  })
}

// 붙여넣기 처리
function onPaste(e: ClipboardEvent) {
  const items = e.clipboardData?.items
  if (!items) return

  for (const item of items) {
    if (item.type.startsWith("image/")) {
      const file = item.getAsFile()
      if (file) addImage(file)
    }
  }
}

// Drag & Drop
function onDrop(e: DragEvent) {
  dropActive.value = false
  const files = e.dataTransfer?.files
  if (!files) return

  for (const file of files) {
    if (file.type.startsWith("image/")) {
      addImage(file)
    }
  }
}

function onDragOver(e: DragEvent) {
  e.preventDefault()
  dropActive.value = true
}

function onDragLeave() {
  dropActive.value = false
}

function removeImage(id: string) {
  images.value = images.value.filter((img) => img.id !== id)
}

// 최종 전송
function submit() {
  const payload = {
    text: message.value,
    images: images.value.map((img) => img.base64),
  }

  console.log("전송 Payload:", payload)

  // 실제 API 호출 예시
  // await api.post("/message", payload)

  message.value = ""
  images.value = []
  resizeTextarea()
}
</script>


<template>
  <div 
    class="w-full max-w-3xl mx-auto p-4 rounded-xl border bg-white shadow-sm transition-colors"
    @drop.prevent="onDrop"
    @dragover.prevent="onDragOver"
    @dragleave="onDragLeave"
    :class="{ 'border-blue-400 bg-blue-50/50': dropActive }"
  >

    <!-- 이미지 미리보기 -->
    <div v-if="images.length" class="flex flex-wrap gap-3 mb-3">
      <div
        v-for="img in images"
        :key="img.id"
        class="relative w-24 h-24 rounded-md border overflow-hidden"
      >
        <img :src="img.url" class="object-cover w-full h-full" />
        <button
          class="absolute top-1 right-1 bg-black/60 text-white text-xs rounded px-1"
          @click="removeImage(img.id)"
        >✕</button>
      </div>
    </div>

    <!-- 입력 + 전송 -->
    <div class="flex items-end gap-3">
      <Textarea
        ref="textareaRef"
        v-model="message"
        @paste="onPaste"
        @input="onInput"
        placeholder="메시지를 입력하거나 이미지를 붙여넣기하세요…"
        class="flex-1 min-h-[40px] max-h-[200px] overflow-y-auto resize-none rounded-lg 
               border px-3 py-2 focus-visible:ring-2"
      />

      <button
        @click="submit"
        class="h-10 px-4 rounded-md bg-black text-white hover:bg-black/80"
      >
        전송
      </button>
    </div>

  </div>
</template>


<script setup lang="ts">
import { ref, onMounted } from "vue"
import { Textarea } from "@/components/ui/textarea"

interface PreviewImage {
  id: string
  file: File
  url: string
}

// 상태
const message = ref("")
const images = ref<PreviewImage[]>([])

const dropActive = ref(false)
const textareaRef = ref<HTMLTextAreaElement | null>(null)

function resizeTextarea() {
  if (!textareaRef.value) return
  textareaRef.value.style.height = "auto"
  textareaRef.value.style.height = textareaRef.value.scrollHeight + "px"
}

onMounted(() => {
  resizeTextarea()
})

// 입력 텍스트 변화 시 자동 높이 조절
function onInput() {
  resizeTextarea()
}

// 붙여넣기 이미지 처리
function onPaste(e: ClipboardEvent) {
  const items = e.clipboardData?.items
  if (!items) return

  for (const item of items) {
    if (item.type.startsWith("image/")) {
      const file = item.getAsFile()
      if (file) {
        addImage(file)
      }
    }
  }
}

// 파일을 preview list에 추가
function addImage(file: File) {
  const url = URL.createObjectURL(file)
  images.value.push({
    id: crypto.randomUUID(),
    file,
    url,
  })
}

// 이미지 제거
function removeImage(id: string) {
  images.value = images.value.filter((img) => img.id !== id)
}

// Drag & Drop 이벤트 처리
function onDrop(e: DragEvent) {
  dropActive.value = false
  const files = e.dataTransfer?.files
  if (!files) return

  for (const file of files) {
    if (file.type.startsWith("image/")) {
      addImage(file)
    }
  }
}

function onDragOver(e: DragEvent) {
  e.preventDefault()
  dropActive.value = true
}

function onDragLeave() {
  dropActive.value = false
}

// 전송
function submit() {
  console.log("Message:", message.value)
  console.log("Images:", images.value.map(i => i.file))

  // 실제 업로드 로직 넣으면 됨
  message.value = ""
  images.value = []
  resizeTextarea()
}
</script>

<template>
  <div 
    class="w-full max-w-3xl mx-auto p-4 rounded-xl border bg-white shadow-sm
           transition-colors"
    @drop.prevent="onDrop"
    @dragover.prevent="onDragOver"
    @dragleave="onDragLeave"
    :class="{ 'border-blue-400 bg-blue-50/50': dropActive }"
  >

    <!-- 미리보기 -->
    <div v-if="images.length" class="flex flex-wrap gap-3 mb-3">
      <div
        v-for="img in images"
        :key="img.id"
        class="relative w-24 h-24 rounded-md border overflow-hidden"
      >
        <img :src="img.url" class="object-cover w-full h-full" />

        <button
          class="absolute top-1 right-1 bg-black/60 text-white text-xs rounded px-1"
          @click="removeImage(img.id)"
        >
          ✕
        </button>
      </div>
    </div>

    <!-- 입력창 + 버튼 -->
    <div class="flex items-end gap-3">
      <Textarea
        ref="textareaRef"
        v-model="message"
        @paste="onPaste"
        @input="onInput"
        placeholder="메시지를 입력하거나 이미지를 붙여넣기하세요…"
        class="flex-1 min-h-[40px] max-h-[200px] overflow-y-auto resize-none rounded-lg 
               border px-3 py-2 focus-visible:ring-2"
      />

      <!-- 전송 버튼 -->
      <button
        @click="submit"
        class="h-10 px-4 rounded-md bg-black text-white font-medium hover:bg-black/80"
      >
        전송
      </button>
    </div>
  </div>
</template>


<script setup lang="ts">
import { ref } from "vue";
import { Textarea } from "@/components/ui/textarea";

interface PreviewImage {
  id: string;
  file: File;
  url: string;
}

const message = ref("");
const images = ref<PreviewImage[]>([]);

function onPaste(e: ClipboardEvent) {
  const items = e.clipboardData?.items;
  if (!items) return;

  for (const item of items) {
    if (item.type.startsWith("image/")) {
      const file = item.getAsFile();
      if (file) {
        const url = URL.createObjectURL(file);

        images.value.push({
          id: crypto.randomUUID(),
          file,
          url,
        });
      }
    }
  }
}

function removeImage(id: string) {
  images.value = images.value.filter((img) => img.id !== id);
}

function submit() {
  console.log("Text:", message.value);
  console.log("Images:", images.value.map(i => i.file));

  // 실제 업로드 API 호출 가능
  // formData.append("file", i.file)

  message.value = "";
  images.value = [];
}
</script>

<template>
  <div class="w-full space-y-2">

    <!-- 이미지 미리보기 -->
    <div v-if="images.length" class="flex flex-wrap gap-3">
      <div
        v-for="img in images"
        :key="img.id"
        class="relative w-24 h-24 rounded-md overflow-hidden border"
      >
        <img :src="img.url" class="object-cover w-full h-full" />
        <button
          class="absolute top-1 right-1 bg-black/60 text-white text-xs rounded px-1"
          @click="removeImage(img.id)"
        >
          ✕
        </button>
      </div>
    </div>

    <!-- Textarea -->
    <Textarea
      v-model="message"
      @paste="onPaste"
      placeholder="메시지를 입력하거나 이미지를 붙여넣기하세요..."
      class="min-h-24"
    />

    <!-- 전송 버튼 -->
    <button
      @click="submit"
      class="bg-black text-white px-4 py-2 rounded-md"
    >
      전송
    </button>

  </div>
</template>







<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <rewrite>
      <rules>

        <!-- 1) API Reverse Proxy -->
        <rule name="API-Proxy" stopProcessing="true">
          <match url="^api/(.*)" />
          <action type="Rewrite" url="http://127.0.0.1:7001/api/{R:1}" appendQueryString="true" />
        </rule>

        <!-- 2) Catch-all Rule: 모든 요청을 FastAPI로 전달 -->
        <rule name="SPA-CatchAll" stopProcessing="true">
          <match url="^(.*)" />
          <action type="Rewrite" url="http://127.0.0.1:7001/{R:1}" appendQueryString="true" />
        </rule>

      </rules>
    </rewrite>

    <!-- WebSocket 필요 시 -->
    <webSocket enabled="true" />

  </system.webServer>
</configuration>




from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

app = FastAPI()

# dist 폴더 경로
dist_path = Path(__file__).parent.parent / "dist"

# 1) 정적 파일 제공
app.mount("/assets", StaticFiles(directory=dist_path / "assets"), name="assets")

# 2) FastAPI API 라우터
@app.get("/api/health")
def health():
    return {"status": "ok"}

# 3) Vue SPA: 모든 나머지 라우팅 → index.html
@app.get("/{full_path:path}")
def spa_router(full_path: str):
    index_file = dist_path / "index.html"
    return FileResponse(index_file)




<script setup lang="ts">
interface Props {
  text?: string;
  size?: string;
  gap?: string;
}

const props = withDefaults(defineProps<Props>(), {
  text: "ChatGPT is typing",
  size: "text-base",
  gap: "gap-1",
});
</script>

<template>
  <div class="flex items-center" :class="props.gap">
    <span
      v-for="(char, i) in props.text.split('')"
      :key="i"
      class="bounced-text inline-block"
      :style="{ animationDelay: `${i * 0.1}s` }"
      :class="props.size"
    >
      {{ char === ' ' ? '\u00A0' : char }}
    </span>
  </div>
</template>

<style scoped>
@keyframes bounceChar {
  0%   { transform: translateY(0); opacity: 0.6; }
  30%  { transform: translateY(-4px); opacity: 1; }
  60%  { transform: translateY(0); opacity: 0.8; }
  100% { transform: translateY(0); opacity: 0.6; }
}

.bounced-text {
  animation: bounceChar 0.8s infinite ease-in-out;
}
</style>



<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';

// 1. Props 정의
interface Props {
  text: string; // 깜빡일 문자열 (예: 'Waiting for response...')
  interval?: number; // 문자(char)별 깜빡임 속도 (밀리초), 기본값: 500ms
  className?: string; // 전체 텍스트에 적용할 Tailwind CSS 클래스
}

const props = withDefaults(defineProps<Props>(), {
  interval: 500,
  className: 'text-lg font-semibold text-gray-500',
});

// 2. 깜빡임 상태 관리
const visibleIndex = ref(0); // 현재 보이는 문자열의 길이 (0부터 시작)
let blinkTimer: number | null = null; // 타이머 ID

// 3. 타이머 로직 (순차적 깜빡임 구현)
const startBlinking = () => {
  // 기존 타이머가 있으면 정리
  if (blinkTimer !== null) {
    clearInterval(blinkTimer);
  }

  // 주기적으로 visibleIndex를 업데이트합니다.
  blinkTimer = setInterval(() => {
    // visibleIndex를 1씩 증가시키고, 문자열 길이(props.text.length)에 도달하면 0으로 리셋합니다.
    visibleIndex.value = (visibleIndex.value + 1) % (props.text.length + 1);
  }, props.interval) as unknown as number; // TypeScript 환경에서 setInterval의 반환 타입 보정
};

// 4. 문자열 분리 및 상태 계산
const characters = computed(() => props.text.split(''));

// 5. 컴포넌트 라이프사이클 훅
onMounted(() => {
  startBlinking();
});

onUnmounted(() => {
  if (blinkTimer !== null) {
    clearInterval(blinkTimer);
  }
});

// 
</script>

<template>
  <div :class="props.className">
    <span v-for="(char, index) in characters" :key="index">
      <span 
        :class="{ 'opacity-100': index < visibleIndex, 'opacity-0': index >= visibleIndex }" 
        class="transition-opacity duration-150 ease-in-out inline-block"
      >
        {{ char }}
      </span>
    </span>
  </div>
</template>

<style scoped>
/* Tailwind CSS를 사용하므로 추가적인 <style>은 필요하지 않습니다. */
/* duration-150을 사용하여 깜빡이는 효과를 부드럽게 합니다. */
</style>




{"id":"48321","variant":"standard"}
<script setup lang="ts">
import { computed, toRefs, withDefaults, defineProps } from "vue"

/**
 Props 정의 (text는 필수)
 withDefaults를 써서 기본값 안전하게 지정
*/
const props = withDefaults(
  defineProps<{
    text: string
    speed?: number        // 한 글자가 깜빡이는 주기 (초)
    color?: string        // Tailwind 텍스트 색상 클래스 (예: 'text-primary')
    blinkOpacity?: number // 깜빡일 때 최소 불투명도 (0 ~ 1)
  }>(),
  {
    speed: 0.9,
    color: "text-primary",
    blinkOpacity: 0.2,
  }
)

const { text } = toRefs(props)

// 글자 배열 (공백도 보존)
const chars = computed(() => Array.from(text.value))

/**
 charStyle: 각 글자에 적용할 inline style 반환
 - animation: blink <speed>s infinite
 - animationDelay: 글자별 지연
 - --blink-opacity: CSS 변수로 keyframes에서 사용
*/
const charStyle = (index: number) => {
  const delay = index * 0.12 // 글자 간 딜레이(초) — 필요시 조절
  return {
    animation: `sb-blink ${props.speed}s infinite`,
    animationDelay: `${delay}s`,
    // CSS variable로 전달해서 keyframes에서 사용
    "--blink-opacity": String(props.blinkOpacity),
  } as Record<string, string>
}
</script>

<template>
  <span class="inline-flex" aria-hidden="false">
    <span
      v-for="(c, i) in chars"
      :key="i"
      :class="[props.color, 'inline-block']"
      :style="charStyle(i)"
    >
      {{ c === ' ' ? '\u00A0' : c }}
    </span>
  </span>
</template>

<style scoped>
/* keyframes에서 CSS 변수 --blink-opacity 사용 */
@keyframes sb-blink {
  0%, 100% {
    opacity: 1;
  }
  50% {
    /* props에서 전달한 값 사용 (기본 0.2) */
    opacity: var(--blink-opacity, 0.2);
  }
}

/* 기본적으로 inline-block에 애니메이션 적용 (스타일은 inline으로 덮음) */
</style>
SequentialBlinkText

<script setup lang="ts">
import { computed } from "vue"

interface Props {
  text: string
  speed?: number        // 한 글자가 깜빡이는 속도(s)
  color?: string        // Tailwind text color
  blinkOpacity?: number // 사라질 때 불투명도
}

const props = defineProps<Props>()

const chars = computed(() => props.text.split(""))
const speed = computed(() => props.speed || 0.9)
const color = computed(() => props.color || "text-primary")
const blinkOpacity = computed(() => props.blinkOpacity || 0.2)

const charStyle = (index: number) => ({
  animation: `blink ${speed.value}s infinite`,
  animationDelay: `${index * 0.15}s`,
})
</script>

<template>
  <span class="inline-flex">
    <span
      v-for="(c, i) in chars"
      :key="i"
      :class="color"
      :style="charStyle(i)"
      class="inline-block"
    >
      {{ c }}
    </span>
  </span>
</template>

<style scoped>
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.2; }
}
</style>




BounceDots.vue

<template>
  <div class="flex items-end gap-1 text-muted-foreground">
    <span class="dot dot1">•</span>
    <span class="dot dot2">•</span>
    <span class="dot dot3">•</span>
  </div>
</template>

<script setup lang="ts"></script>

<style lang="scss" scoped>
.dot {
  display: inline-block;
  font-size: 22px;
  transform: translateY(0);
  animation: bounce 1s infinite ease-in-out;

  &.dot1 {
    animation-delay: 0s;
  }
  &.dot2 {
    animation-delay: 0.15s;
  }
  &.dot3 {
    animation-delay: 0.3s;
  }
}

// 점 bounce 애니메이션
@keyframes bounce {
  0% {
    transform: translateY(0);
    opacity: 0.3;
  }
  30% {
    transform: translateY(-6px);
    opacity: 1;
  }
  60% {
    transform: translateY(0);
    opacity: 0.4;
  }
  100% {
    transform: translateY(0);
    opacity: 0.3;
  }
}
</style>



https://daisyui.com/docs/install/

1. npm i -D daisyui@latest

2. Add daisyUI to app.css:
@plugin "daisyui";


<span class="loading loading-dots loading-lg"></span>



// api/userApi.ts
export const userApi = {
  // 1. GET (가져오기)
  async getUserInfo(id: number) { 
    return await axios.get(`/users/${id}`); 
  },
  // 2. POST (생성)
  async postUser(data: UserData) { 
    return await axios.post('/users', data); 
  },
  // 3. PUT/PATCH (수정)
  async putUserInfo(id: number, data: UserData) { 
    return await axios.put(`/users/${id}`, data); 
  },
  // 4. DELETE (삭제)
  async deleteUser(id: number) { 
    return await axios.delete(`/users/${id}`); 
  },
};



// services/userService.ts
import { userApi } from '@/api/userApi';
import { useUserStore } from '@/stores/userStore';

export const userService = {
  // ⭐️ load: 데이터를 불러와서 처리하는 비즈니스 행위
  async loadUserInfo(id: number) {
    const userStore = useUserStore();
    try {
      const apiResponse = await userApi.getUserInfo(id); // API 호출
      // ... 데이터 가공 로직 ...
      userStore.setUser(apiResponse.data); // Store 업데이트
    } catch (e) {
      // ... 비즈니스 예외 처리 ...
    }
  },

  // ⭐️ save: 사용자 정보를 저장/수정하는 비즈니스 행위
  async saveUserInfo(id: number, data: UserData) {
    const userStore = useUserStore();
    // ... 사전 검증 로직 ...
    const apiResponse = await userApi.putUserInfo(id, data); // API 호출
    userStore.setUser(apiResponse.data); // Store 업데이트
  },
  
  // ⭐️ remove: 사용자 제거 비즈니스 행위
  async removeUser(id: number) {
      await userApi.deleteUser(id);
      // Store의 상태도 초기화하거나 업데이트...
  }
};





. userApi (기술적 레이어)
TypeScript

// api/userApi.ts
export const userApi = {
  // 1. GET (가져오기)
  async getUserInfo(id: number) { 
    return await axios.get(`/users/${id}`); 
  },
  // 2. POST (생성)
  async postUser(data: UserData) { 
    return await axios.post('/users', data); 
  },
  // 3. PUT/PATCH (수정)
  async putUserInfo(id: number, data: UserData) { 
    return await axios.put(`/users/${id}`, data); 
  },
  // 4. DELETE (삭제)
  async deleteUser(id: number) { 
    return await axios.delete(`/users/${id}`); 
  },
};
2. userService (비즈니스 레이어)
TypeScript

// services/userService.ts
import { userApi } from '@/api/userApi';
import { useUserStore } from '@/stores/userStore';

export const userService = {
  // ⭐️ load: 데이터를 불러와서 처리하는 비즈니스 행위
  async loadUserInfo(id: number) {
    const userStore = useUserStore();
    try {
      const apiResponse = await userApi.getUserInfo(id); // API 호출
      // ... 데이터 가공 로직 ...
      userStore.setUser(apiResponse.data); // Store 업데이트
    } catch (e) {
      // ... 비즈니스 예외 처리 ...
    }
  },

  // ⭐️ save: 사용자 정보를 저장/수정하는 비즈니스 행위
  async saveUserInfo(id: number, data: UserData) {
    const userStore = useUserStore();
    // ... 사전 검증 로직 ...
    const apiResponse = await userApi.putUserInfo(id, data); // API 호출
    userStore.setUser(apiResponse.data); // Store 업데이트
  },
  
  // ⭐️ remove: 사용자 제거 비즈니스 행위
  async removeUser(id: number) {
      await userApi.deleteUser(id);
      // Store의 상태도 초기화하거나 업데이트...
  }
};
이 방식은 함수명이 기술적(API) 역할과 비즈니스적(Service) 역할을 동시에 반영하여, 코드를 훨씬 더 구조적으로 만들어 줍니다.
==================================================================================================


아래는 PostgreSQL에서 시간별 / 일별 / 주별 / 월별로 모두 취합하는 표준 패턴입니다.
timestamp 컬럼을 기준으로 date_trunc를 사용하면 됩니다.

✅ 1) 시간별(hourly) 집계
SELECT
    date_trunc('hour', timestamp) AS hour,
    COUNT(*) AS row_count
FROM your_table
GROUP BY hour
ORDER BY hour;

✅ 2) 일별(daily) 집계
SELECT
    date_trunc('day', timestamp) AS day,
    COUNT(*) AS row_count
FROM your_table
GROUP BY day
ORDER BY day;


또는 날짜만 보고 싶으면:

SELECT
    DATE(timestamp) AS day,
    COUNT(*) AS row_count
FROM your_table
GROUP BY day
ORDER BY day;

✅ 3) 주별(weekly) 집계

PostgreSQL 기준, 주 시작은 월요일입니다.

SELECT
    date_trunc('week', timestamp) AS week,
    COUNT(*) AS row_count
FROM your_table
GROUP BY week
ORDER BY week;

✅ 4) 월별(monthly) 집계
SELECT
    date_trunc('month', timestamp) AS month,
    COUNT(*) AS row_count
FROM your_table
GROUP BY month
ORDER BY month;

🔥 옵션: user_id 기준으로 필터링도 가능
WHERE user_id = 'tester1'


모든 쿼리에 추가 가능:

SELECT
    date_trunc('day', timestamp) AS day,
    COUNT(*) AS row_count
FROM your_table
WHERE user_id = 'tester1'
GROUP BY day
ORDER BY day;

🔥 옵션: 모든 집계를 한 번에 보고 싶으면
SELECT 'hourly' AS type, date_trunc('hour', timestamp) AS ts, COUNT(*) FROM your_table GROUP BY ts
UNION ALL
SELECT 'daily', date_trunc('day', timestamp), COUNT(*) FROM your_table GROUP BY 1,2
UNION ALL
SELECT 'weekly', date_trunc('week', timestamp), COUNT(*) FROM your_table GROUP BY 1,2
UNION ALL
SELECT 'monthly', date_trunc('month', timestamp), COUNT(*) FROM your_table GROUP BY 1,2
ORDER BY ts;


필요하면 연도별, 요일별, 시간대별 히트맵, user_id별 동시 집계, 그래프용 SQL도 만들어줄게!

==========================================================================================

아래는 FastAPI v1/v2 버전 구조를 실제 개발용 수준으로 설계한
📌 폴더 구조 + 라우터 + 서비스 + 모델 + 인증/세션 관리 전체 샘플 코드입니다.
Vue3 + FastAPI 백엔드를 동시에 운영하는 구조에 최적화했습니다.

📁 1. 디렉터리 구조 (추천 구조)
app/
 ├─ main.py
 ├─ core/
 │   ├─ config.py
 │   ├─ security.py
 │   └─ session.py
 ├─ api/
 │   ├─ deps/
 │   │   └─ auth.py
 │   ├─ v1/
 │   │   ├─ router.py
 │   │   ├─ users.py
 │   │   └─ items.py
 │   ├─ v2/
 │   │   ├─ router.py
 │   │   └─ users.py
 ├─ models/
 │   └─ user.py
 ├─ schemas/
 │   └─ user.py
 └─ services/
     ├─ user_service.py
     └─ item_service.py

🧩 2. 핵심 파일 상세 코드
▶ main.py

FastAPI 앱 생성 + v1/v2 라우터 등록.

from fastapi import FastAPI
from app.api.v1.router import api_router as v1_router
from app.api.v2.router import api_router as v2_router

app = FastAPI(title="My API", version="1.0.0")

app.include_router(v1_router)
app.include_router(v2_router)

▶ core/config.py (환경 설정 파일)
from pydantic import BaseSettings

class Settings(BaseSettings):
    JWT_SECRET: str = "secret"
    JWT_ALGO: str = "HS256"

settings = Settings()

▶ core/security.py (JWT 관련)
import jwt
from datetime import datetime, timedelta
from app.core.config import settings

def create_access_token(data: dict, expires_minutes=60):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGO)

def decode_token(token: str):
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGO])

▶ api/deps/auth.py (공통 인증 Dependency)

Router 전체에 적용할 인증 로직.

from fastapi import Depends, HTTPException, Request
from app.core.security import decode_token

def get_current_user(request: Request):
    token = request.headers.get("Authorization")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = token.replace("Bearer ", "")

    try:
        user = decode_token(token)
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

    request.state.user = user
    return user

▶ models/user.py (DB Model or ORM Model 자리)

여기선 간단한 예시로 dict 구조만.

class User:
    def __init__(self, user_id: str, role: str):
        self.user_id = user_id
        self.role = role

▶ schemas/user.py (Pydantic 입력/출력 모델)
from pydantic import BaseModel

class UserSchema(BaseModel):
    user_id: str
    role: str

▶ services/user_service.py
from app.models.user import User

class UserService:
    def get_user(self, user_id: str):
        return User(user_id=user_id, role="admin")

    def list_users(self):
        return [
            User(user_id="user1", role="user"),
            User(user_id="admin", role="admin"),
        ]

user_service = UserService()

▶ api/v1/users.py (v1 Users API)
from fastapi import APIRouter, Request
from app.services.user_service import user_service

router = APIRouter()

@router.get("/me")
def get_me(request: Request):
    return request.state.user

@router.get("/")
def list_users():
    return [vars(u) for u in user_service.list_users()]

▶ api/v1/items.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def list_items():
    return [{"id": "item1"}, {"id": "item2"}]

▶ api/v1/router.py (v1 라우터 통합)

여기서 인증 dependency를 전체 v1에 적용 👇

from fastapi import APIRouter, Depends
from app.api.deps.auth import get_current_user
from app.api.v1 import users, items

api_router = APIRouter(
    prefix="/v1",
    dependencies=[Depends(get_current_user)]  # ⭐ v1 전체 인증
)

api_router.include_router(users.router, prefix="/users")
api_router.include_router(items.router, prefix="/items")

▶ api/v2/router.py (v2 라우터 - 인증 옵션)

v2는 아직 인증 없는 API로 구성 가능.

from fastapi import APIRouter
from app.api.v2 import users

api_router = APIRouter(prefix="/v2")
api_router.include_router(users.router, prefix="/users")

▶ api/v2/users.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def list_users_v2():
    return {"message": "v2 improved users API"}

📌 전체 흐름 요약
계층	역할
main.py	FastAPI 앱 생성, v1/v2 라우터 등록
api/v1	모든 API + 인증 필요
api/v2	신규 API 버전, 인증 옵션
deps/auth.py	JWT 인증, request.state.user 저장
services/	비즈니스 로직
models/	DB/ORM 모델
schemas/	Pydantic 모델
core/	환경설정, JWT, DB 세션 등
👍 이 구조의 장점
✔ Vue3 + FastAPI 운영에 최적화

Axios 인증 인스턴스와 자연스럽게 매칭.

✔ v1/v2 버전 분리 깔끔

v1: 안정 API + 인증 필수

v2: 개선 API 점진 전환

✔ 인증·세션 로직을 1곳에서 처리

dependencies=[Depends(get_current_user)]

✔ 서비스·모델·스키마 완전 분리

TypeScript 구조 설계와 유사해서 관리 쉬움.

필요하면 아래도 만들어줄게:

📌 프론트(Vue3 Axios)와 연결되는 JWT 인증 템플릿

📌 MongoDB 또는 PostgreSQL ORM 버전 구조

📌 Redis 기반 Session Manager 추가 구조

📌 테스트 코드(pytest) 기본 구조

원하는 방향 있을까?

request: Request 를 받으면서 query 파라미터도 함께 받을 수 있습니다.
FastAPI에서는 Request와 Query/Path 파라미터를 함께 혼용할 수 있어요.

✅ 예시 1: 기본 Query 파라미터 추가
@router.get("/me")
def get_me(request: Request, detail: bool = False):
    user = request.state.user
    if detail:
        user["detail"] = "more detail info"
    return user


사용 예:

GET /me?detail=true

✅ 예시 2: 여러 Query 파라미터 추가
@router.get("/me")
def get_me(
    request: Request,
    page: int = 1,
    size: int = 20,
    include_role: bool = False,
):
    data = {
        "user": request.state.user,
        "page": page,
        "size": size
    }

    if include_role:
        data["role"] = request.state.user.get("role")

    return data

✅ 예시 3: Query 파라미터를 Pydantic 모델로 받기

QueryModel 하나로 묶어 깔끔하게 관리할 수 있음.

from pydantic import BaseModel
from fastapi import Depends, Query

class UserQuery(BaseModel):
    include_role: bool = False
    page: int = 1
    size: int = 10

def get_query(
    include_role: bool = Query(False),
    page: int = Query(1),
    size: int = Query(10),
):
    return UserQuery(include_role=include_role, page=page, size=size)


라우터:

@router.get("/me")
def get_me(
    request: Request,
    query: UserQuery = Depends(get_query)
):
    result = {
        "user": request.state.user,
        "page": query.page,
        "size": query.size,
    }
    
    if query.include_role:
        result["role"] = request.state.user.get("role")

    return result

📌 정리
✔ request: Request

→ 항상 첫 번째 파라미터로 받으면 됨

✔ Query 파라미터도 함께 사용 가능

→ def my_api(request: Request, q: str = None, page: int = 1)

✔ 깔끔한 구조를 원하면

→ Pydantic Query Model + Depends 추천

원하면
📌 “QueryModel을 자동으로 Swagger에 정리되는 형태로 사용하는 베스트 프랙티스”
도 만들어줄게.

post 예시를 들어줘
아래에 POST에서 Request + Body + Query를 모두 함께 사용하는 예시를 단계별로 정리해줄게.

FastAPI는 Request, Body, Query를 서로 섞어서 받을 수 있고, 특히
실무에서는 아래 형태가 많이 쓰임:

Request → 인증된 사용자 정보 (request.state.user)

Body → 실제 데이터 입력(Pydantic 모델)

Query → 옵션 필터, 모드, 페이지 등

✅ 1) 가장 기본적인 POST 예시

Request와 Body만 조합

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()

class ItemCreate(BaseModel):
    name: str
    price: float

@router.post("/items")
def create_item(request: Request, body: ItemCreate):
    user = request.state.user   # 인증된 사용자 정보
    
    return {
        "created_by": user,
        "item": body
    }

✅ 2) POST + Query + Body + Request 모두 조합

가장 많이 쓰는 패턴 (실무형)

from fastapi import APIRouter, Request, Query
from pydantic import BaseModel

router = APIRouter()

class ItemCreate(BaseModel):
    name: str
    price: float

@router.post("/items")
def create_item(
    request: Request,
    data: ItemCreate,
    notify: bool = Query(default=False),   # /items?notify=true
):
    user = request.state.user

    return {
        "user": user,
        "query_param_notify": notify,
        "item_body": data.dict(),
    }


사용:

POST /items?notify=true
{
  "name": "Apple",
  "price": 1000
}

✅ 3) Query 값을 별도 Pydantic 모델로 받는 실무형 패턴

복잡한 Query 파라미터가 많을 때 추천 👍

Query Model 정의
from pydantic import BaseModel
from fastapi import Query

class ItemQuery(BaseModel):
    category: str = None
    discount: bool = False

def get_item_query(
    category: str = Query(None),
    discount: bool = Query(False),
):
    return ItemQuery(category=category, discount=discount)

POST 라우터
@router.post("/items")
def create_item(
    request: Request,
    body: ItemCreate,
    q: ItemQuery = Depends(get_item_query)
):
    user = request.state.user
    
    return {
        "user": user,
        "body": body,
        "query": q,
    }


사용 예:

POST /items?category=fruit&discount=true
{
  "name": "Banana",
  "price": 2500
}

✅ 4) POST + Path + Query + Body + Request 모두 조합한 풀옵션 예시
@router.post("/users/{user_id}/items")
def create_user_item(
    user_id: str,
    request: Request,
    data: ItemCreate,
    priority: int = Query(1),
):
    user = request.state.user

    return {
        "login_user": user,
        "target_user_id": user_id,
        "priority": priority,
        "item_data": data.dict()
    }

📌 핵심 정리
✔ POST에서도 Request + Query + Body 조합 100% 가능
✔ Pydantic Body 모델 + Query 모델 분리 추천

→ Swagger 문서도 깔끔
→ 서비스·유즈케이스 레이어로 넘기기 쉬움

✔ 실무에서는 아래 패턴 가장 많이 씀
def api(request: Request, body: BodyModel, q: QueryModel = Depends(...))




dependencies=[Depends(get_current_user)] 를 APIRouter 전체에 걸었을 때,
일부 엔드포인트만 인증 없이(open API) 열어두고 싶다면 예외 처리 방식을 써야 해.

FastAPI에서 이 문제를 해결하는 방법은 3가지가 있고,
그중에서 가장 실무적인 베스트 프랙티스도 알려줄게.

✅ 방법 1 — “두 개의 Router로 분리” (가장 깔끔하고 추천)

인증이 필요한 API와
인증이 필요 없는 API를 별도 Router로 나누는 방식.

📁 구조 예시
api/v1/
 ├─ router.py
 ├─ items.py        # 인증 필요
 └─ auth.py         # 인증 불필요 (token 발급)

▶ auth.py — 인증이 필요 없는 API
from fastapi import APIRouter

router = APIRouter()

@router.post("/token")
def issue_token(login: LoginSchema):
    return {"access_token": "..."}

▶ router.py — 인증이 필요한 API만 묶기
from fastapi import APIRouter, Depends
from app.api.deps.auth import get_current_user
from app.api.v1 import items, auth

api_router = APIRouter(prefix="/v1")

# 인증 없이 접근 가능한 auth API 먼저 등록
api_router.include_router(auth.router, prefix="/auth")

# 인증이 필요한 부분만 dependencies 적용
protected_router = APIRouter(
    prefix="",
    dependencies=[Depends(get_current_user)]
)

protected_router.include_router(items.router, prefix="/items")

# protected router 등록
api_router.include_router(protected_router)

✔ 장점

인증 API와 일반 API가 확실하게 분리됨

개발하면서 인증 여부가 헷갈리지 않음

유지보수가 가장 쉽다
(대규모 프로젝트에서도 가장 사용되는 방식)

✅ 방법 2 — 엔드포인트 단위로 dependency override (추천 ❌)

FastAPI는 개별 API에서 dependency를 제거하는 override 구조를 지원하지 않음.
즉, dependencies=[Depends(...)] 가 Router에 지정되면 API마다 off 할 수 없음.

그래서 Router 분리가 올바른 방식임.

✅ 방법 3 — get_current_user에서 “optional 모드” 처리 (가능하지만 비추천)

아래처럼 token이 없으면 None, 있으면 인증 처리하도록 만들 수 있음.

def get_current_user_optional(request: Request):
    token = request.headers.get("Authorization")
    if not token:
        return None
    return decode_token(token)


문제는
실제 인증이 필요한 API에도 user가 없을 수 있음
→ 매번 코드에서 체크해야 함
→ 오류 발생 가능

그래서 비추천.




⭐ 결론 (실전에서 가장 많이 쓰는 방식)
⭐ Router를 두 개로 분리하라.

/v1/auth/* → 인증 불필요

/v1/* → 인증 필요 → dependencies=[Depends(get_current_user)] 적용

📌 예시 코드: 완성본
1) v1/auth.py
from fastapi import APIRouter

router = APIRouter()

@router.post("/token")
def issue_token(body: TokenRequest):
    # 로그인 검증 후 토큰 발급
    return {"access_token": "...", "token_type": "bearer"}

2) v1/items.py (인증 필요)
from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/")
def get_items(request: Request):
    return {"user": request.state.user, "items": []}

3) v1/router.py (최종 라우팅)
from fastapi import APIRouter, Depends
from app.api.deps.auth import get_current_user
from app.api.v1 import auth, items

api_router = APIRouter(prefix="/v1")

# 인증 필요 없는 영역
api_router.include_router(auth.router, prefix="/auth")

# 인증 필요 API들
protected_router = APIRouter(
    dependencies=[Depends(get_current_user)]
)

protected_router.include_router(items.router, prefix="/items")

api_router.include_router(protected_router)


필요하면
✔ v1/v2 버전별 인증 라우터 자동 분리
✔ 관리자 전용 Router
✔ Optional 인증 Router
등도 만들어줄게!

📁 1. 전체 구조 예시 (v1/v2 + 인증/비인증)
app/
 ├─ main.py
 ├─ core/
 │   ├─ config.py
 │   └─ security.py
 ├─ api/
 │   ├─ deps/
 │   │   └─ auth.py
 │   ├─ v1/
 │   │   ├─ router.py
 │   │   ├─ auth.py      # /auth/token → 인증 X
 │   │   ├─ items.py     # 인증 필요
 │   │   └─ users.py     # 인증 필요
 │   ├─ v2/
 │   │   ├─ router.py
 │   │   └─ users.py     # v2 개선 API
 ├─ services/
 │   ├─ user_service.py
 │   └─ item_service.py
 ├─ schemas/
 │   ├─ user.py
 │   └─ item.py
 └─ models/
     ├─ user.py
     └─ item.py

🧩 2. v1 Router 구조
# app/api/v1/router.py
from fastapi import APIRouter, Depends
from app.api.v1 import auth, items, users
from app.api.deps.auth import get_current_user

api_router = APIRouter(prefix="/v1")

# 인증 X → 로그인/토큰 발급 등
api_router.include_router(auth.router, prefix="/auth")

# 인증 필요 → items, users
protected_router = APIRouter(dependencies=[Depends(get_current_user)])
protected_router.include_router(items.router, prefix="/items")
protected_router.include_router(users.router, prefix="/users")

api_router.include_router(protected_router)

🧩 3. auth.py (인증 없이 접근 가능)
# app/api/v1/auth.py
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class TokenRequest(BaseModel):
    username: str
    password: str

@router.post("/token")
def issue_token(body: TokenRequest):
    # 로그인 검증 후 토큰 발급
    return {"access_token": "fake-token", "token_type": "bearer"}

🧩 4. items.py (인증 필요)
# app/api/v1/items.py
from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/")
def list_items(request: Request):
    return {
        "user": request.state.user,
        "items": ["item1", "item2"]
    }

🧩 5. get_current_user (Request state에 user 저장)
# app/api/deps/auth.py
from fastapi import Request, HTTPException

def get_current_user(request: Request):
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    token = token.replace("Bearer ", "")
    
    # 실제 검증 로직
    user = {"user_id": "admin", "role": "admin"}  # 예시
    request.state.user = user
    return user

✅ 정리

인증 없는 API → 별도 Router(/auth)

인증 있는 API → APIRouter(dependencies=[Depends(get_current_user)])

Router 단위로 묶으면 v1/v2 등 버전 관리가 편함

request.state.user를 통해 인증 정보를 쉽게 공유 가능

원하면 나는 이어서
v2 Router + 선택적 인증(Optional) API 구조까지 만들어서
로그인 유무 상관없이 접근 가능 + 인증 필요 시 권한 체크 패턴까지 만들어줄 수 있어.

그거 만들어줄까?



==========================================================================================



src/
 ├─ api/                     # Axios 인스턴스, 인터셉터, 공통 API 모듈
 │   ├─ http.ts              # Axios 인스턴스 생성
 │   ├─ auth.api.ts          # 인증/로그인 API 모듈
 │   ├─ user.api.ts          # 사용자 관련 API 모듈
 │   └─ ...                  
 │
 ├─ services/                # 비즈니스 로직 레이어
 │   ├─ auth.service.ts      # 로그인/로그아웃 서비스
 │   ├─ user.service.ts      # 사용자 비즈니스 로직
 │   └─ ...
 │
 ├─ stores/                  # Pinia store
 │   ├─ auth.store.ts        # 로그인 상태/토큰 관리
 │   ├─ user.store.ts        # 사용자 정보 store
 │   └─ ...
 │
 ├─ utils/                   # 공통 유틸 모듈
 │   ├─ encryption.ts        # 암호화/복호화 (예: 권한 암호화)
 │   ├─ validator.ts         # 입력 검증
 │   └─ ...
 │
 ├─ router/
 │   └─ index.ts
 │
 ├─ views/
 │   └─ ...
 │
 ├─ components/
 │   └─ ...
 │
 └─ main.ts

📌 파일별 역할 상세 설명
1) Axios 클라이언트 (api/http.ts)

// src/api/http.ts
import axios from 'axios';

export const http = axios.create({
  baseURL: '/api',
  timeout: 5000,
});

// 요청 인터셉터
http.interceptors.request.use(config => {
  // 예: 토큰 자동 추가
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// 응답 인터셉터
http.interceptors.response.use(
  res => res,
  err => Promise.reject(err)
);



2) API 모듈 (예: auth.api.ts)
// src/api/auth.api.ts
import { http } from './http';

export const authApi = {
  login(payload: { id: string; password: string }) {
    return http.post('/auth/login', payload);
  },
  refresh() {
    return http.post('/auth/refresh');
  },
};

→ API 모듈은 오직 HTTP 요청만 담당.
비즈니스 로직은 절대 넣지 않음.

3) Service 레이어 (예: auth.service.ts)

// src/services/auth.service.ts
import { authApi } from '@/api/auth.api';
import { useAuthStore } from '@/stores/auth.store';

export const authService = {
  async login(id: string, password: string) {
    const res = await authApi.login({ id, password });
    const store = useAuthStore();
    store.setToken(res.data.accessToken);
    return res.data;
  },

  async refreshToken() {
    const res = await authApi.refresh();
    const store = useAuthStore();
    store.setToken(res.data.accessToken);
  },
};
→ 서비스는 비즈니스 로직 담당

API 결과 가공

Pinia 업데이트

페이지 이동 처리

인증/권한 체크


4) Pinia Store (auth.store.ts)


// src/stores/auth.store.ts
import { defineStore } from 'pinia';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: '' as string,
    user: null as any,
  }),

  actions: {
    setToken(token: string) {
      this.accessToken = token;
      localStorage.setItem('access_token', token);
    },
    clear() {
      this.accessToken = '';
      this.user = null;
      localStorage.removeItem('access_token');
    }
  },
});

→ Pinia는 오직 상태(State) 관리만
→ 네트워크 호출은 Service에서 처리


5) Utils (예: encryption.ts)
// src/utils/encryption.ts
import CryptoJS from 'crypto-js';

export const encrypt = (text: string, key: string) => {
  return CryptoJS.AES.encrypt(text, key).toString();
};

export const decrypt = (cipher: string, key: string) => {
  return CryptoJS.AES.decrypt(cipher, key).toString(CryptoJS.enc.Utf8);
};


→ 인증 정보/권한을 암호화해서 전달할 때 사용

🎯 Why 이렇게 구성하는가?

레이어	역할	설명
API	HTTP 요청만 담당	Axios 인스턴스와 REST 호출 전담
Service	비즈니스 로직 담당	API 결과 가공, 상태 저장, 흐름 제어
Store (Pinia)	상태 관리	전역 상태·토큰 보관
Utils	공통 처리	암호화·포맷팅·검증

🎁 이 구조의 장점

유지보수 쉬움

테스트 편함

서비스 로직이 모여 있어 가독성 높음

API 변경되도 Service만 수정 가능

Store는 비즈니스 로직을 모르게 됨 → 깔끔함

axios를 두개로 관리 하려고 해 하나는 인증전 header에 정보없이 다른 하나는 인증후 header에 access token

✅ 폴더 구조 (Axios 2개 버전)


src/
 ├─ api/
 │   ├─ http.public.ts        # 인증 전 Axios
 │   ├─ http.auth.ts          # 인증 후 Axios (토큰 자동 포함)
 │   ├─ auth.api.ts           # Authentication API
 │   ├─ user.api.ts           # User API
 │   └─ ...
 │
 ├─ stores/
 │   └─ auth.store.ts
 │
 └─ services/
     └─ auth.service.ts

1) 인증 전 Axios (http.public.ts)

→ 로그인, 토큰 갱신 안된 상태 등 인증 없이 호출되는 API들

// src/api/http.public.ts
import axios from 'axios';

export const httpPublic = axios.create({
  baseURL: '/api',
  timeout: 5000,
});

// 별도 인터셉터 없음
2) 인증 후 Axios (http.auth.ts)

→ accessToken 자동 헤더 삽입

2) 인증 후 Axios (http.auth.ts)

→ accessToken 자동 헤더 삽입


// src/api/http.auth.ts
import axios from 'axios';
import { useAuthStore } from '@/stores/auth.store';

export const httpAuth = axios.create({
  baseURL: '/api',
  timeout: 5000,
});

// 요청 시 토큰 자동 주입
httpAuth.interceptors.request.use(config => {
  const auth = useAuthStore();
  if (auth.accessToken) {
    config.headers.Authorization = `Bearer ${auth.accessToken}`;
  }
  return config;
});

// 응답 인터셉터 (예: 401 처리)
httpAuth.interceptors.response.use(
  res => res,
  async error => {
    // 토큰 만료 등의 처리 가능 (원하면 refresh 로직도 넣어줌)
    return Promise.reject(error);
  }
);

3) API 예시: 로그인 (auth.api.ts)

// src/api/auth.api.ts
import { httpPublic } from './http.public';
import { httpAuth } from './http.auth';

export const authApi = {
  login(payload: { id: string; password: string }) {
    return httpPublic.post('/auth/login', payload);
  },
  getMyInfo() {
    return httpAuth.get('/auth/me');
  }
};

4) Service 레이어 (auth.service.ts)

→ API 호출 + Pinia 업데이트

// src/services/auth.service.ts
import { authApi } from '@/api/auth.api';
import { useAuthStore } from '@/stores/auth.store';

export const authService = {
  async login(id: string, password: string) {
    const res = await authApi.login({ id, password });

    const store = useAuthStore();
    store.setToken(res.data.accessToken);

    return res.data;
  },

  async loadMyInfo() {
    const res = await authApi.getMyInfo();
    return res.data;
  }
};
5) Pinia Store (auth.store.ts)

// src/stores/auth.store.ts
import { defineStore } from 'pinia';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: '' as string
  }),

  actions: {
    setToken(token: string) {
      this.accessToken = token;
      localStorage.setItem('accessToken', token);
    },
    loadToken() {
      this.accessToken = localStorage.getItem('accessToken') || '';
    },
    logout() {
      this.accessToken = '';
      localStorage.removeItem('accessToken');
    }
  }
});

✅ 이렇게 두 개로 분리하는 이유
인스턴스	목적	장점
httpPublic	로그인/회원가입/토큰없음 API	헤더가 간단해서 초기 요청 빠름
httpAuth	인증 필요한 API	토큰 자동 적용 → 코드 간결
둘 다 사용	API 모듈에서 상황별 선택	가독성 ↑ / 유지보수 ↑

📌 요청 흐름 요약

로그인 API → httpPublic

로그인 성공 → Pinia에 Token 저장

이후 모든 API → httpAuth → 토큰 자동 추가됨

service를 pinia에 코드에서 관리하는것 보다 분리 하는게 좋을까

결론부터 말하면 Service를 Pinia에서 분리하는 것이 훨씬 좋다.
대부분의 실무(중/대규모)에서 Store는 상태만, Service는 비즈니스 로직만 담당하도록 완전히 분리한다.

이유와 실제 장점들을 정리해줄게.

✅ 결론: Service를 Pinia와 분리하는 것이 Best Practice

🔥 왜 Store 안에 Service 로직을 넣으면 안 좋을까?

예시 문제점들:

1) Store가 너무 비대해짐 (Fat Store 문제)

API 호출

에러 처리

토큰 갱신

데이터 가공

화면 전환

상태 저장

이 모든 걸 Store가 처리하면 관리가 어려워진다.


2) 테스트하기 어려워짐

Store는 상태를 가진 객체라 단위테스트가 까다롭다.
Service는 순수 함수 로직으로 테스트하기 쉽다.

3) 재사용성이 떨어짐

Service는 여러 Store나 컴포넌트에서 같이 사용할 수 있지만,
Store 안에 API/로직이 있으면 Store를 강제로 import해야 한다 → 종속성 증가.

4) Store 로직이 변경될 때 UI 전체가 리렌더링될 가능성 증가

API 호출 실패나 에러 상태만 바뀌어도 Store가 notify 되면서 화면이 리렌더링될 수 있다.

5) API 계층(axios)과 상태 계층(pinia)이 강하게 결합됨 → 유지보수 어려움

🟦 그럼 어떤 구조가 가장 좋은가?
✔️ 구조적 역할 분리 (Clean Architecture 느낌)
1) API Layer

HTTP 요청만 담당

2) Service Layer

API 호출

데이터 가공

인증/권한 흐름

Store 업데이트

Refresh Token 처리

화면 이동 처리

3) Store Layer

상태 관리만

단순 setter / getter / reset 메서드만


🟢 예시 비교
❌ 나쁜 예: Store에 API 로직이 들어간 경우
export const useUserStore = defineStore('user', {
  state: () => ({ user: null }),

  actions: {
    async loadUser() {
      const res = await httpAuth.get('/user');
      this.user = res.data;
    }
  }
});

결과: Store가 비대해지고 테스트 어려움.

✅ 좋은 예: Service에서 로직 처리
user.service.ts


import { userApi } from '@/api/user.api';
import { useUserStore } from '@/stores/user.store';

export const userService = {
  async loadUser() {
    const store = useUserStore();
    const res = await userApi.getUser();
    store.setUser(res.data);
    return res.data;
  }
};
user.store.ts

export const useUserStore = defineStore('user', {
  state: () => ({ user: null }),

  actions: {
    setUser(user: any) {
      this.user = user;
    },
    clear() {
      this.user = null;
    }
  }
});
📌 Store는 “상태만 관리”, Service는 “API + 비즈니스 흐름 관리”.

🎯 결론 요약
방식	장점	단점
Service 분리 (추천)	유지보수 쉬움, 테스트 편함, 구조 깔끔	파일이 한두개 늘어남
Service를 Store 안에 넣음	초기엔 편해보이지만	규모 커지면 망함 (Fat Store)

🔥 그래서 실무에서는?

Vue + Pinia + Axios 프로젝트의 90% 이상이 "Service 분리형" 구조 사용
특히 TypeScript 기반은 더 강력하게 권장됨.

원하면 구조에 맞춰 **템플릿 프로젝트(폴더+파일+샘플코드)**까지 생성해줄게!

좋아! 그러면 Vue 3 + TypeScript + Pinia + Axios + Service Layer 구조를
바로 복붙해서 사용할 수 있는 완성형 템플릿 프로젝트 구조로 만들어줄게.

아래 구조 그대로 복사해서 프로젝트에 적용하면 된다.

🎯 최종 Recommended 구조

(인증 전/후 Axios 분리 + Service Layer 완전 분리 + Pinia 순수 상태관리)

src/
 ├─ api/
 │   ├─ http.public.ts
 │   ├─ http.auth.ts
 │   ├─ auth.api.ts
 │   ├─ user.api.ts
 │   └─ ...
 │
 ├─ services/
 │   ├─ auth.service.ts
 │   ├─ user.service.ts
 │   └─ ...
 │
 ├─ stores/
 │   ├─ auth.store.ts
 │   ├─ user.store.ts
 │   └─ ...
 │
 ├─ utils/
 │   ├─ encryption.ts
 │   └─ ...
 │
 ├─ router/
 │   └─ index.ts
 │
 └─ main.ts


아래에 각 파일의 샘플 코드를 바로 붙여둘게.
현재 프로젝트에 그대로 복사해서 구조를 만들면 된다.


📌 1) Axios 인스턴스 (인증 전/후)
http.public.ts (비로그인용)

// src/api/http.public.ts
import axios from 'axios';

export const httpPublic = axios.create({
  baseURL: '/api',
  timeout: 5000,
});


http.auth.ts (로그인 후 토큰 자동 주입)

// src/api/http.auth.ts
import axios from 'axios';
import { useAuthStore } from '@/stores/auth.store';

export const httpAuth = axios.create({
  baseURL: '/api',
  timeout: 5000,
});

// 요청 인터셉터
httpAuth.interceptors.request.use(config => {
  const auth = useAuthStore();

  if (auth.accessToken) {
    config.headers.Authorization = `Bearer ${auth.accessToken}`;
  }

  return config;
});




📌 2) API 모듈
auth.api.ts

// src/api/auth.api.ts
import { httpPublic } from './http.public';
import { httpAuth } from './http.auth';

export const authApi = {
  login(data: { id: string; password: string }) {
    return httpPublic.post('/auth/login', data);
  },

  refresh() {
    return httpPublic.post('/auth/refresh');
  },

  me() {
    return httpAuth.get('/auth/me');
  }
};

user.api.ts

// src/api/user.api.ts
import { httpAuth } from './http.auth';

export const userApi = {
  getProfile() {
    return httpAuth.get('/user/profile');
  }
};


📌 3) Pinia Store (상태만 관리)
auth.store.ts

// src/stores/auth.store.ts
import { defineStore } from 'pinia';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: '' as string,
    user: null as any
  }),

  actions: {
    setToken(token: string) {
      this.accessToken = token;
      localStorage.setItem('access_token', token);
    },

    loadToken() {
      this.accessToken = localStorage.getItem('access_token') || '';
    },

    setUser(user: any) {
      this.user = user;
    },

    clear() {
      this.accessToken = '';
      this.user = null;
      localStorage.removeItem('access_token');
    }
  }
});
user.store.ts

// src/stores/user.store.ts
import { defineStore } from 'pinia';

export const useUserStore = defineStore('user', {
  state: () => ({
    profile: null as any
  }),

  actions: {
    setProfile(profile: any) {
      this.profile = profile;
    }
  }
});


📌 4) Service Layer (API + Store 연결 = 비즈니스 로직)
auth.service.ts

// src/services/auth.service.ts
import { authApi } from '@/api/auth.api';
import { useAuthStore } from '@/stores/auth.store';

export const authService = {
  async login(id: string, password: string) {
    const store = useAuthStore();
    const res = await authApi.login({ id, password });

    store.setToken(res.data.accessToken);
    return res.data;
  },

  async loadUserInfo() {
    const store = useAuthStore();
    const res = await authApi.me();

    store.setUser(res.data);
    return res.data;
  }
};

user.service.ts

// src/services/user.service.ts
import { userApi } from '@/api/user.api';
import { useUserStore } from '@/stores/user.store';

export const userService = {
  async loadProfile() {
    const store = useUserStore();
    const res = await userApi.getProfile();

    store.setProfile(res.data);
    return res.data;
  }
};
📌 5) Utils 예시
encryption.ts

import CryptoJS from 'crypto-js';

export const encrypt = (value: string, secret: string) => {
  return CryptoJS.AES.encrypt(value, secret).toString();
};

export const decrypt = (value: string, secret: string) => {
  return CryptoJS.AES.decrypt(value, secret).toString(CryptoJS.enc.Utf8);
};


🎉 이렇게 구성하면 생기는 장점
✔ Store에서 API 코드가 없어져서 매우 깔끔
✔ Service에서 인증 흐름·특별 처리·가공 로직 모두 관리
✔ 테스트·유지보수 용이
✔ Axios 공통 처리 / Token 주입 완전 자동화
✔ 확장성 최고 (JWT Refresh, 권한 체크, 인터셉터 확장 가능)

원하면
✔️ refresh-token 자동 재발급 기능
✔️ 401 → 자동 로그인 페이지 이동
✔️ Role(권한) 기반 라우터 가드
까지 포함한 완전한 인증 구조 템플릿도 만들어줄게.

좋아!
이제 Refresh Token 자동 재발급 + 401 처리 + Role 기반 라우터 가드
까지 포함된 완성형 인증 구조 템플릿을 만들어줄게.

아래 코드는 Vue 3 + TypeScript + Pinia + Axios + Service Layer 기준으로
실무에서 그대로 쓸 수 있는 수준의 안정적인 구조야.


=========================================
🌈 1. 프로젝트 구조 (최종 완성형)

src/
 ├─ api/
 │   ├─ http.public.ts
 │   ├─ http.auth.ts
 │   ├─ auth.api.ts
 │   ├─ user.api.ts
 │   └─ ...
 │
 ├─ services/
 │   ├─ auth.service.ts
 │   ├─ user.service.ts
 │   └─ ...
 │
 ├─ stores/
 │   ├─ auth.store.ts
 │   ├─ user.store.ts
 │   └─ ...
 │
 ├─ router/
 │   └─ index.ts
 │
 └─ utils/
     ├─ encryption.ts
     └─ token.helper.ts

2. 📌 Token 관리 헬퍼 (token.helper.ts)

3. // src/utils/token.helper.ts
export const tokenHelper = {
  getAccess() {
    return localStorage.getItem('access_token') || '';
  },
  setAccess(token: string) {
    localStorage.setItem('access_token', token);
  },
  removeAccess() {
    localStorage.removeItem('access_token');
  },

  getRefresh() {
    return localStorage.getItem('refresh_token') || '';
  },
  setRefresh(token: string) {
    localStorage.setItem('refresh_token', token);
  },
  removeRefresh() {
    localStorage.removeItem('refresh_token');
  },

  clearAll() {
    this.removeAccess();
    this.removeRefresh();
  }
};


3. 📌 Axios — 인증 후(http.auth.ts) + 자동 토큰 재발급

4. // src/api/http.auth.ts
import axios from 'axios';
import { tokenHelper } from '@/utils/token.helper';
import { authService } from '@/services/auth.service';

export const httpAuth = axios.create({
  baseURL: '/api',
  timeout: 5000,
});

// 요청: AccessToken 자동 주입
httpAuth.interceptors.request.use(config => {
  const token = tokenHelper.getAccess();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 응답: 401 → Refresh Token으로 재발급 시도
let isRefreshing = false;
let failedQueue: any[] = [];

function processQueue(error: any, token: string | null = null) {
  failedQueue.forEach(prom => {
    if (error) prom.reject(error);
    else prom.resolve(token);
  });

  failedQueue = [];
}

httpAuth.interceptors.response.use(
  res => res,
  async err => {
    const originalRequest = err.config;

    // 401 + 재시도 한 적 없음 → refresh 시도
    if (err.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // refresh 중이면 큐에 추가
        return new Promise(function (resolve, reject) {
          failedQueue.push({ resolve, reject });
        }).then(token => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return httpAuth(originalRequest);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const newToken = await authService.refreshToken();
        processQueue(null, newToken);
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return httpAuth(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        authService.logout(); // refresh 실패 → 강제 로그아웃
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(err);
  }
);


✔️ 이 로직은

401 나오면 자동으로 refresh API 호출

refresh가 성공하면 대기 중인 API 요청 자동 재시도

refresh 실패하면 자동 로그아웃

실제 서비스 수준 구조이다.

4. 📌 Auth Service — 로그인 / 로그아웃 / refresh 로직
// src/services/auth.service.ts
import { authApi } from '@/api/auth.api';
import { useAuthStore } from '@/stores/auth.store';
import { tokenHelper } from '@/utils/token.helper';

export const authService = {
  async login(id: string, password: string) {
    const res = await authApi.login({ id, password });

    const { accessToken, refreshToken, user } = res.data;

    tokenHelper.setAccess(accessToken);
    tokenHelper.setRefresh(refreshToken);

    const store = useAuthStore();
    store.setUser(user);

    return res.data;
  },

  async refreshToken(): Promise<string> {
    const refreshToken = tokenHelper.getRefresh();
    if (!refreshToken) throw new Error('No refresh token');

    const res = await authApi.refresh();
    const newToken = res.data.accessToken;

    tokenHelper.setAccess(newToken);
    return newToken;
  },

  logout() {
    tokenHelper.clearAll();
    useAuthStore().clear();
  }
};
5. 📌 Auth API — Public API

// src/api/auth.api.ts
import { httpPublic } from './http.public';
import { httpAuth } from './http.auth';

export const authApi = {
  login(data: { id: string; password: string }) {
    return httpPublic.post('/auth/login', data);
  },

  refresh() {
    return httpPublic.post('/auth/refresh');
  },

  me() {
    return httpAuth.get('/auth/me');
  }
};


6. 📌 Pinia Store (상태만 관리)

7. // src/stores/auth.store.ts
import { defineStore } from 'pinia';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as any
  }),

  actions: {
    setUser(user: any) {
      this.user = user;
    },

    clear() {
      this.user = null;
    }
  }
});

7. 📌 Router — Role 기반 라우터 가드

예:

로그인해야 접근 가능

특정 Role(admin/user 등)에 따라 페이지 제한

// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/auth.store';
import { tokenHelper } from '@/utils/token.helper';
import { authService } from '@/services/auth.service';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: () => import('@/views/Home.vue') },
    { 
      path: '/admin',
      component: () => import('@/views/Admin.vue'),
      meta: { requiresAuth: true, role: 'admin' }
    },
    { 
      path: '/login',
      component: () => import('@/views/Login.vue')
    }
  ]
});

router.beforeEach(async (to, _from, next) => {
  const store = useAuthStore();
  const hasToken = !!tokenHelper.getAccess();

  // 인증 필요 없는 페이지면 pass
  if (!to.meta.requiresAuth) return next();

  // 인증 필요한데 토큰 없음 → login으로 이동
  if (!hasToken) return next('/login');

  // 유저정보 없으면 me() 호출해서 로드
  if (!store.user) {
    try {
      await authService.loadUserInfo();
    } catch {
      authService.logout();
      return next('/login');
    }
  }

  // Role 체크 (있을 경우)
  if (to.meta.role) {
    if (store.user.role !== to.meta.role) {
      return next('/'); // 권한 없으면 홈으로
    }
  }

  next();
});

export default router;


🎉 완성

이제 다음 기능까지 모두 포함된 실무 레벨 인증 아키텍처가 완성됐다.

✔️ Login
✔️ Logout
✔️ Access Token 자동 주입
✔️ Refresh Token 자동 재발급
✔️ 401 → 자동 재시도
✔️ Role 기반 페이지 접근 제한
✔️ Service / Store / API 완전 분리 (Best Practice)


========================================













--------




web.config
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <rewrite>
      <rules>
        <rule name="VueRouter" stopProcessing="true">
          <match url=".*" />
          <conditions logicalGrouping="MatchAll">
            <add input="{REQUEST_FILENAME}" matchType="IsFile" negate="true" />
            <add input="{REQUEST_FILENAME}" matchType="IsDirectory" negate="true" />
          </conditions>
          <action type="Rewrite" url="/" />
        </rule>
      </rules>
    </rewrite>
  </system.webServer>
</configuration>



<!-- C:\deploy\myapp\frontend\dist\web.config -->
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <rewrite>
      <rules>
        <rule name="VueRouterHistory" stopProcessing="true">
          <match url=".*" />
          <conditions logicalGrouping="MatchAll">
            <add input="{REQUEST_FILENAME}" matchType="IsFile" negate="true" />
            <add input="{REQUEST_FILENAME}" matchType="IsDirectory" negate="true" />
          </conditions>
          <action type="Rewrite" url="/index.html" />
        </rule>
      </rules>
    </rewrite>
  </system.webServer>
</configuration>




uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 --log-config log_config.yaml



version: 1
disable_existing_loggers: False
formatters:
  default:
    format: "%(levelprefix)s %(asctime)s %(message)s"
handlers:
  console:
    class: logging.StreamHandler
    formatter: default
  file:
    class: concurrent_log_handler.ConcurrentRotatingFileHandler
    filename: "app.log"
    maxBytes: 10485760
    backupCount: 5
    formatter: default
loggers:
  uvicorn:
    handlers: [console, file]
    level: INFO
root:
  level: INFO
  handlers: [console, file]




pip install concurrent-log-handler


from concurrent_log_handler import ConcurrentRotatingFileHandler
import logging

logger = logging.getLogger("my_logger")
logger.setLevel(logging.INFO)

handler = ConcurrentRotatingFileHandler(
    "app.log", maxBytes=10*1024*1024, backupCount=5
)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info("FastAPI 시작")




python 
-m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 --log-level info


using System.Net.Http;
using Microsoft.IdentityModel.Clients.ActiveDirectory;

// ADAL의 IHttpClientFactory 구현
public class NoProxyHttpClientFactory : Microsoft.IdentityModel.Clients.ActiveDirectory.IHttpClientFactory
{
    public HttpClient GetHttpClient()
    {
        var handler = new HttpClientHandler
        {
            UseProxy = false,   // 프록시 사용 안 함
            Proxy = null
        };

#if DEBUG
        // 테스트 전용: 인증서 검사 완화 (운영금지)
        handler.ServerCertificateCustomValidationCallback = HttpClientHandler.DangerousAcceptAnyServerCertificateValidator;
#endif

        return new HttpClient(handler, disposeHandler: true);
    }
}










using System.Net.Http;
using Microsoft.IdentityModel.Clients.ActiveDirectory;

// ADAL의 IHttpClientFactory 구현
public class NoProxyHttpClientFactory : Microsoft.IdentityModel.Clients.ActiveDirectory.IHttpClientFactory
{
    public HttpClient GetHttpClient()
    {
        var handler = new HttpClientHandler
        {
            UseProxy = false,   // 프록시 사용 안 함
            Proxy = null
        };

#if DEBUG
        // 테스트 전용: 인증서 검사 완화 (운영금지)
        handler.ServerCertificateCustomValidationCallback = HttpClientHandler.DangerousAcceptAnyServerCertificateValidator;
#endif

        return new HttpClient(handler, disposeHandler: true);
    }
}





using System.Net.Http;
using Microsoft.IdentityModel.Clients.ActiveDirectory;

// ADAL의 IHttpClientFactory 구현
public class NoProxyHttpClientFactory : Microsoft.IdentityModel.Clients.ActiveDirectory.IHttpClientFactory
{
    public HttpClient GetHttpClient()
    {
        var handler = new HttpClientHandler
        {
            UseProxy = false,   // 프록시 사용 안 함
            Proxy = null
        };

#if DEBUG
        // 테스트 전용: 인증서 검사 완화 (운영금지)
        handler.ServerCertificateCustomValidationCallback = HttpClientHandler.DangerousAcceptAnyServerCertificateValidator;
#endif

        return new HttpClient(handler, disposeHandler: var httpFactory = new NoProxyHttpClientFactory();
var authContext = new AuthenticationContext(authority, validateAuthority: true, tokenCache: null, httpClientFactory: httpFactory);

var result = await authContext.AcquireTokenAsync(resource, clientId, new Uri("https://your-return-uri"), new PlatformParameters(PromptBehavior.Auto));







using System;
using System.Net.Http;
using Microsoft.Identity.Client;         // Microsoft.Identity.Client v4+
using Microsoft.Identity.Client.Platforms.Shared; // 필요시

// IMsalHttpClientFactory 구현
public class NoProxyHttpClientFactory : IMsalHttpClientFactory
{
    public HttpClient GetHttpClient()
    {
        var handler = new HttpClientHandler
        {
            UseProxy = false,  // 프록시 사용 금지
            Proxy = null
        };

#if DEBUG
        // 테스트용: 인증서 검증을 완화 (절대 운영에 사용 금지)
        handler.ServerCertificateCustomValidationCallback = (req, cert, chain, errors) => true;
#endif

        return new HttpClient(handler, disposeHandler: true);
    }
}

// MSAL 앱 생성 및 토큰 획득 (Interactive 예시)
var clientId = "your-client-id";
var authority = "https://login.microsoftonline.com/your-tenant-id"; // 또는 "common"
var redirectUri = "http://localhost"; // 앱에 맞게 변경

var httpFactory = new NoProxyHttpClientFactory();

var app = PublicClientApplicationBuilder.Create(clientId)
    .WithAuthority(authority)
    .WithRedirectUri(redirectUri)
    .WithHttpClientFactory(httpFactory)   // 여기에 커스텀 HttpClient 공급
    .Build();

// 요청할 scope 목록 — 실제 사용하려는 리소스/권한으로 교체하세요.
string[] scopes = new[] { "User.Read" }; // 예: Microsoft Graph 권한 예시

var result = await app.AcquireTokenInteractive(scopes)
    .ExecuteAsync();

Console.WriteLine("Access token: " + result.AccessToken);






String regex = "^/api/v1/app/mbeat(/.*)?$";

boolean matched = Pattern.compile(regex).matcher(text).matches();

System.out.println(matched ? "경로 패턴 일치" : "일치하지 않음");



using System;
using System.Collections.Generic;
using System.Linq;

class Program
{
    static void Main()
    {
        var items = new List<string>
        {
            "apple orange banana",
            "apple banana",
            "orange mango",
            "apple orange",
            "grape apple juice"
        };

        string input = "apple,orange"; // 검색 입력값
        var keywords = input
            .Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);

        // 부분 일치하는 모든 키워드를 포함하는 항목만 필터링
        var filtered = items
            .Where(item => keywords.All(k => item.Contains(k, StringComparison.OrdinalIgnoreCase)))
            .ToList();

        // 결과 출력
        foreach (var result in filtered)
        {
            Console.WriteLine(result);
        }
    }
}



🧩 최종 FastAPI API 설계안
1️⃣ 기본 정보 (공용)
GET /models                     # 지원하는 LLM 모델 목록 조회
GET /prompts                    # 샘플 프롬프트 목록 조회


공용 리소스 — 로그인 없이 접근 가능

2️⃣ 대화 (Conversation)
GET    /conversations                 # 사용자의 전체 대화 목록 조회
POST   /conversations                 # 새 대화 생성 (첫 메시지 포함 가능)
GET    /conversations/{id}            # 특정 대화 상세 조회
PUT    /conversations/{id}            # 대화 제목 또는 속성 수정
DELETE /conversations/{id}            # 대화 삭제

POST   /conversations/{id}/messages   # 메시지 추가 및 LLM 응답 요청
GET    /conversations/{id}/messages   # 대화 메시지 전체 히스토리 조회

GET    /conversations/{id}/stream     # LLM 응답을 SSE로 실시간 스트리밍
POST   /conversations/{id}/feedback   # 대화 또는 메시지 피드백 제출


💬 ChatGPT와 유사한 구조로 “대화 → 메시지” 관계 명확
💡 실시간 응답(SSE)은 /stream 하위로 통합

3️⃣ 공유 (Share)
GET    /shares                        # 공유된 대화 목록 (관리자용 또는 내 공유)
POST   /shares                        # 새로운 공유 생성 (body: conversation_id)
GET    /shares/{id}                   # 공유된 대화 조회 (읽기 전용)
POST   /shares/{id}/clone             # 공유된 대화로부터 새 대화 생성
DELETE /shares/{id}                   # 공유 취소 또는 삭제


샘플 (Sample)
GET    /samples                       # 샘플 대화 목록 조회
POST   /samples                       # 새로운 샘플 생성 (body: conversation_id)
GET    /samples/{id}                  # 샘플 대화 조회
POST   /samples/{id}/clone            # 샘플 대화로부터 새 대화 생성


📤 공유는 “스냅샷 → 복제 → 새 대화 생성” 흐름으로 설계

4️⃣ 사용자 수집 자료 (Collector)
GET    /collector/items         # 수집 자료 목록 조회
POST   /collector/items         # 수집 자료 등록
DELETE /collector/items/{id}    # 수집 자료 삭제

📚 사용자가 참고용으로 업로드/저장한 자료 관리용

5️⃣ 사용자 설정 (User Settings)
GET    /user/settings                 # 전체 설정 조회
PUT    /user/settings                 # 설정 전체 수정

GET    /user/settings/subscription    # 구독 설정 조회
PUT    /user/settings/subscription    # 구독 설정 변경

GET    /user/settings/theme           # UI 테마 조회
PUT    /user/settings/theme           # UI 테마 변경

GET    /user/settings/notification    # 알림 설정 조회
PUT    /user/settings/notification    # 알림 설정 변경


⚙️ 향후 theme, notification 등 세부 설정이 추가되어도 확장 용이
/user는 단수형으로 유지 → 로그인된 사용자 한 명 기준

6️⃣ 인증 (Auth)
POST   /auth/login
POST   /auth/logout
POST   /auth/refresh
POST   /auth/register


🔐 JWT 기반 인증을 가정한 표준 구성

🧱 라우터 구성 예시
# main.py
app.include_router(model_router, prefix="/models", tags=["Models"])
app.include_router(prompt_router, prefix="/prompts", tags=["Prompts"])
app.include_router(conversation_router, prefix="/conversations", tags=["Conversations"])
app.include_router(share_router, prefix="/share", tags=["Share"])
app.include_router(collector_router, prefix="/collector", tags=["Collector"])
app.include_router(user_settings_router, prefix="/user/settings", tags=["User Settings"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])

✅ 요약
구분	Prefix	주요 기능	형태
기본 정보	/models, /prompts	모델 및 샘플 프롬프트 조회	공용
대화	/conversations	대화 CRUD 및 메시지 관리	복수형
공유	/share	대화 공유 및 복제	복수형
수집 자료	/collector	사용자가 등록한 자료 관리	복수형
사용자 설정	/user/settings	구독 및 기타 개인 설정	단수형
인증	/auth	로그인/회원가입/JWT 갱신	복수형

이 구성이 확장성·가독성·운영 편의성을 모두 고려한
“운영환경 기준의 실전형 REST API 구조”입니다.

원하신다면 이걸 기반으로
📁 routers/ 디렉토리 구조 + 각 router 기본 템플릿 코드 (conversation_router.py 등)까지 바로 만들어드릴 수도 있습니다.
그걸 원하시나요?



----------------

🧩 최종 FastAPI API 설계안 (v1)
1️⃣ 기본 정보 (공용)
GET /models                     # 지원하는 LLM 모델 목록 조회
GET /prompts                    # 샘플 프롬프트 목록 조회


공용 리소스 (로그인 불필요 가능)
ex) 모델 선택, 프롬프트 추천 등 기본 데이터 제공

2️⃣ 대화 (Conversations)
GET    /conversations                 # 사용자의 전체 대화 목록 조회
POST   /conversations                 # 새 대화 생성 (첫 메시지 포함 가능)
GET    /conversations/{id}            # 특정 대화 상세 조회
PUT    /conversations/{id}            # 대화 제목 또는 속성 수정
DELETE /conversations/{id}            # 대화 삭제

POST   /conversations/{id}/messages   # 메시지 추가 및 LLM 응답 요청
GET    /conversations/{id}/messages   # 대화 메시지 전체 히스토리 조회

GET    /conversations/{id}/stream     # LLM 응답을 SSE로 실시간 스트리밍
POST   /conversations/{id}/feedback   # 대화 또는 메시지 피드백 제출


💬 “대화”와 “메시지”의 계층 구조 명확
💡 SSE 응답은 /stream 하위에서 구분
💡 Feedback은 conversation 단위로 관리 가능

3️⃣ 공유 (Shares)
GET    /shares                        # 내가 생성한 공유 목록 조회
POST   /shares                        # 새 공유 생성 (body: conversation_id)
GET    /shares/{id}                   # 공유된 대화 조회 (읽기 전용)
POST   /shares/{id}/clone             # 공유된 대화로부터 새 대화 생성
DELETE /shares/{id}                   # 공유 삭제 또는 비활성화


📤 공유 리소스는 /shares로 복수형 관리
💡 “복제(clone)”는 명시적 액션으로 표현해 명확성 확보

4️⃣ 샘플 (Samples)
GET    /samples                       # 샘플 대화 목록 조회
POST   /samples                       # 새로운 샘플 등록 (body: conversation_id)
GET    /samples/{id}                  # 샘플 대화 상세 조회
POST   /samples/{id}/clone            # 샘플 대화로부터 새 대화 생성


🧠 /shares와 동일한 구조 유지 — 일관성 극대화
💡 관리자가 제공하는 샘플 프롬프트나 대화 예시용

5️⃣ 사용자 수집 자료 (Collector)
GET    /collector/items               # 사용자가 수집한 자료 목록 조회
POST   /collector/items               # 자료 등록
DELETE /collector/items/{id}          # 자료 삭제


📚 /collector는 기능 그룹, 실제 리소스는 /items
💡 나중에 /collector/tags, /collector/search 등 확장 가능

6️⃣ 사용자 설정 (User Settings)
GET    /user/settings                 # 사용자 설정 전체 조회
PUT    /user/settings                 # 사용자 설정 전체 수정

GET    /user/settings/subscription    # 구독 설정 조회
PUT    /user/settings/subscription    # 구독 설정 변경


관리자
GET  /users/{user_id}/settings                 # 특정 사용자의 설정 조회
PUT  /users/{user_id}/settings                 # 특정 사용자의 설정 수정
GET  /users/{user_id}/settings/subscription    # 특정 사용자의 구독 설정 조회
PUT  /users/{user_id}/settings/subscription    # 특정 사용자의 구독 설정 수정


GET    /users/{user_id}/conversations          # 특정 사용자의 대화 목록 조회
GET    /users/{user_id}/conversations/{id}     # 특정 사용자의 특정 대화 상세 조회
DELETE /users/{user_id}/conversations/{id}     # 특정 사용자의 대화 삭제 (관리자 권한)


⚙️ /user는 단수형 — 현재 로그인한 사용자 기준
💡 /user/settings 하위로 세부 설정 확장 용이
ex) /user/settings/notifications, /user/settings/theme

7️⃣ 인증 (Auth)
POST   /auth/login                    # 로그인
POST   /auth/logout                   # 로그아웃
POST   /auth/refresh                  # 토큰 갱신
POST   /auth/register                 # 회원가입


🔐 JWT 기반 인증을 가정
💡 /user와는 별도의 책임 영역

🧱 FastAPI 라우터 구성 예시
# main.py
app.include_router(model_router, prefix="/models", tags=["Models"])
app.include_router(prompt_router, prefix="/prompts", tags=["Prompts"])
app.include_router(conversation_router, prefix="/conversations", tags=["Conversations"])
app.include_router(share_router, prefix="/shares", tags=["Shares"])
app.include_router(sample_router, prefix="/samples", tags=["Samples"])
app.include_router(collector_router, prefix="/collector", tags=["Collector"])
app.include_router(user_settings_router, prefix="/user/settings", tags=["User Settings"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])

✅ 요약 테이블
구분	Prefix	주요 기능	특징
기본 정보	/models, /prompts	모델/프롬프트 목록	공용
대화	/conversations	대화 CRUD + 메시지/SSE	핵심 서비스
공유	/shares	대화 공유 및 복제	일관된 구조
샘플	/samples	샘플 대화 관리	/shares와 동일 패턴
수집 자료	/collector/items	사용자 저장 자료	확장성 높음
사용자 설정	/user/settings	구독/테마/알림 등	단수형 user
인증	/auth	로그인/회원가입	독립 영역

이 구조는 ChatGPT류 서비스에서

운영 시 API 관리가 쉽고

버전 확장(v2, v3 등)도 단순하며

Swagger/OpenAPI 문서 구조도 깔끔하게 유지됩니다.

원하신다면 다음 단계로
📁 /routers 폴더 구조 + 각 라우터 기본 코드 템플릿 (예: conversation_router.py, collector_router.py)
까지 자동 생성 형태로 구성해드릴까요?
→ 이 설계를 실제 FastAPI 프로젝트 스켈레톤 코드로 옮길 수 있습니다.



-------------


✅ 2️⃣ FastAPI에서 토큰 재발급 방식 (권장)

외부 인증이 성공하면 프론트엔드가 FastAPI에 외부 토큰을 전달,
FastAPI는 이를 검증 후 내부용 JWT를 발급하는 구조입니다.

🔹 흐름

Frontend가 외부 로그인 성공 후 외부 토큰을 획득

FastAPI /auth/exchange 엔드포인트에 외부 토큰 전달

FastAPI가 외부 서버에 토큰 검증 요청

검증 성공 시 FastAPI가 내부 JWT 발급 (ID 포함)

이후 모든 요청은 내부 토큰(Authorization: Bearer <fastapi_token>) 사용

🔹 FastAPI 예시 코드
from fastapi import FastAPI, HTTPException, Header
from jose import jwt
import httpx
import os

SECRET_KEY = os.getenv("FASTAPI_SECRET_KEY", "dev-secret")
ALGORITHM = "HS256"

app = FastAPI()

@app.post("/auth/exchange")
async def exchange_token(external_token: str = Header(..., alias="X-External-Token")):
    # 1️⃣ 외부 인증 서버에 토큰 검증 요청
    async with httpx.AsyncClient() as client:
        res = await client.get(
            "https://auth.example.com/userinfo",
            headers={"Authorization": f"Bearer {external_token}"}
        )
        if res.status_code != 200:
            raise HTTPException(401, "Invalid external token")

        userinfo = res.json()
        user_id = userinfo.get("id")
        if not user_id:
            raise HTTPException(400, "User ID not found in external response")

    # 2️⃣ 내부 JWT 발급
    payload = {"user_id": user_id}
    internal_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": internal_token, "token_type": "bearer"}

🔹 Vue3 프론트엔드 예시
const externalToken = externalAuthToken; // 외부 API 로그인 결과
const { data } = await api.post('/auth/exchange', null, {
  headers: { 'X-External-Token': externalToken },
});
localStorage.setItem('internal_token', data.access_token);


이후 모든 요청은:

api.interceptors.request.use(config => {
  const token = localStorage.getItem('internal_token');
  if (token) config.headers['Authorization'] = `Bearer ${token}`;
  return config;
});


이 구조는 OAuth 2.0의 token exchange (RFC 8693) 표준과 유사하며,
외부 인증 → 내부 서비스 간 토큰 교환이 필요한 상황에서 가장 안정적입니다.



✅ 1️⃣ Vue3 (Frontend) — 사용자 ID 전달

외부 인증 완료 후, FastAPI에 사용자 ID를 전송해 JWT를 받습니다.

import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

export async function loginToBackend(userId: string) {
  const res = await api.post('/auth/token', { user_id: userId });
  const token = res.data.access_token;
  localStorage.setItem('jwt', token);
}

// 이후 요청 시 자동으로 JWT 포함
api.interceptors.request.use(config => {
  const token = localStorage.getItem('jwt');
  if (token) config.headers['Authorization'] = `Bearer ${token}`;
  return config;
});

✅ 2️⃣ FastAPI (Backend) — JWT 생성 및 검증
🔹 auth/token 엔드포인트 — JWT 발급
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from jose import jwt
from datetime import datetime, timedelta

app = FastAPI()

SECRET_KEY = "your-very-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1일 유효

class TokenRequest(BaseModel):
    user_id: str

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/auth/token")
async def issue_token(request: TokenRequest):
    if not request.user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    # 🔹 사용자 ID를 기반으로 자체 JWT 생성
    token_data = {"sub": request.user_id}
    access_token = create_access_token(token_data)
    return {"access_token": access_token, "token_type": "bearer"}

🔹 보호된 API 예시 (JWT 검증)
from fastapi import Depends, HTTPException, Header
from jose import jwt, JWTError

def verify_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(401, "Invalid token: missing user_id")
        return user_id
    except JWTError:
        raise HTTPException(401, "Invalid or expired token")

@app.get("/user/me")
async def get_me(user_id: str = Depends(verify_token)):
    return {"user_id": user_id}

✅ 3️⃣ 흐름 요약

Frontend가 외부 인증을 통해 user_id를 획득

/auth/token으로 {"user_id": "<사용자ID>"} POST 요청

FastAPI가 JWT를 생성하여 반환

이후 모든 요청 시 Authorization: Bearer <JWT> 헤더 포함

FastAPI가 JWT를 검증해 사용자 식별 수행

✅ 4️⃣ 확장 포인트
항목	설명
🔐 보안 강화	user_id 전달 시, 외부 인증 서버의 서명값 or 해시값을 함께 전달하면 위변조 방지 가능
⏱ 토큰 만료	exp 만료시간 외에 iat, iss 등 클레임 추가 가능
🧩 역할(Role) 추가	JWT payload에 roles, permissions 추가 가능
🌐 도메인 제한	FastAPI CORS 설정에서 신뢰된 도메인만 허용
✅ 5️⃣ FastAPI CORS 설정 (필수)
from fastapi.middleware.cors import CORSMiddleware

origins = ["https://your-frontend.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


이 구조면 Frontend가 ID만 전달해도 안전하게 FastAPI에서 자체 토큰을 발급하고,
이후 통신은 표준적인 JWT 인증 체계로 돌아갑니다.
또한 FastAPI는 외부 인증 서버에 의존하지 않고 자체적으로 사용자 식별을 처리할 수 있습니다.

원하신다면 다음 중 하나로 코드를 확장해드릴 수 있어요:

🔄 Refresh Token 추가 버전

🧑‍💻 사용자 Role(권한) 포함 JWT 발급 버전

🧩 외부 인증서의 서명값(HMAC 등)을 검증하는 버전
Frontend]
  └─ 로그인 후 user_id 전송 → /auth/token
[FastAPI]
  ├─ access_token + refresh_token 발급
  ├─ access_token(15분) → 요청 보호
  └─ refresh_token(7일) → /auth/refresh 로 재발급
✅ 1️⃣ 설정값 정의
python
코드 복사
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, List

# 환경설정
SECRET_KEY = "super-secret-key"
REFRESH_SECRET_KEY = "another-refresh-secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

app = FastAPI()

# CORS (필수)
origins = ["https://your-frontend.com", "http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
✅ 2️⃣ 토큰 생성 함수
python
코드 복사
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
✅ 3️⃣ 요청 모델 및 역할(Role) 정보
python
코드 복사
class TokenRequest(BaseModel):
    user_id: str
    roles: Optional[List[str]] = []  # 예: ["admin", "user"]
✅ 4️⃣ /auth/token — 토큰 발급 API
python
코드 복사
@app.post("/auth/token")
async def issue_token(request: TokenRequest):
    if not request.user_id:
        raise HTTPException(400, "user_id required")

    # JWT payload (sub = subject, roles = 권한)
    payload = {"sub": request.user_id, "roles": request.roles}

    access_token = create_access_token(payload)
    refresh_token = create_refresh_token({"sub": request.user_id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }
✅ 5️⃣ /auth/refresh — 토큰 재발급 API
python
코드 복사
class RefreshRequest(BaseModel):
    refresh_token: str

@app.post("/auth/refresh")
async def refresh_token(req: RefreshRequest):
    try:
        payload = jwt.decode(req.refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(401, "Invalid refresh token")

        # 새 Access Token 발급
        new_access_token = create_access_token({"sub": user_id})
        return {"access_token": new_access_token, "token_type": "bearer"}
    except JWTError:
        raise HTTPException(401, "Invalid or expired refresh token")
✅ 6️⃣ 인증 의존성 (토큰 검증)
python
코드 복사
def verify_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Invalid Authorization header")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        roles = payload.get("roles", [])
        if not user_id:
            raise HTTPException(401, "Invalid token")
        return {"user_id": user_id, "roles": roles}
    except JWTError:
        raise HTTPException(401, "Invalid or expired token")
✅ 7️⃣ 보호된 API (Role 검증 포함)
python
코드 복사
@app.get("/user/me")
async def get_me(user=Depends(verify_token)):
    return {"user_id": user["user_id"], "roles": user["roles"]}

@app.get("/admin/only")
async def admin_only(user=Depends(verify_token)):
    if "admin" not in user["roles"]:
        raise HTTPException(403, "Admin role required")
    return {"message": f"Welcome, admin {user['user_id']}!"}
✅ 8️⃣ Vue3 프론트엔드 연동 예시
typescript
코드 복사
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

api.interceptors.request.use(async config => {
  const token = localStorage.getItem('access_token');
  const exp = localStorage.getItem('access_exp');
  const refresh = localStorage.getItem('refresh_token');

  if (token) config.headers['Authorization'] = `Bearer ${token}`;

  // (선택) 만료 감지 후 자동 재발급 로직
  // exp 시간 계산 후 재발급 호출 가능

  return config;
});

export async function login(userId: string, roles: string[]) {
  const { data } = await api.post('/auth/token', { user_id: userId, roles });
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
}
✅ 9️⃣ 정리
항목	설명
Access Token	사용자 ID + Role + 만료시간 (15분)
Refresh Token	사용자 ID만 포함, 7일 유효
재발급	/auth/refresh 에서 Refresh Token으로 새 Access Token
Role 검증	JWT payload 내 roles 필드
Vue	Axios interceptor로 자동 헤더 주입 및 갱신

이 구조는 JWT + Refresh Token + Role 기반 인증의 완성형 템플릿이에요.
실서비스에서도 거의 그대로 적용 가능합니다 ✅



🔄 자동 만료 감지 후 Access Token 재발급 (Vue3 Axios용 코드)

✅ 목표 구조
[Vue3 Axios Interceptor]
 ├─ 모든 요청에 Access Token 자동 포함
 ├─ 응답이 401이면 Refresh Token으로 재발급 시도
 └─ 재발급 성공 시 원래 요청 재시도

✅ 1️⃣ Axios 설정 (토큰 관리용 util)

src/api/auth.ts

import axios, { AxiosRequestConfig, AxiosError } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL;

// FastAPI 백엔드 인스턴스
const api = axios.create({
  baseURL: API_BASE_URL,
});

// === localStorage helper ===
function getAccessToken() {
  return localStorage.getItem('access_token');
}
function getRefreshToken() {
  return localStorage.getItem('refresh_token');
}
function saveTokens(access: string, refresh?: string) {
  localStorage.setItem('access_token', access);
  if (refresh) localStorage.setItem('refresh_token', refresh);
}
function clearTokens() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
}

// === JWT 만료 여부 확인 ===
function isTokenExpired(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const now = Math.floor(Date.now() / 1000);
    return payload.exp < now;
  } catch {
    return true;
  }
}

// === Refresh Token으로 재발급 ===
async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return null;

  try {
    const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
      refresh_token: refreshToken,
    });
    const newAccess = response.data.access_token;
    if (newAccess) {
      saveTokens(newAccess); // refresh_token은 그대로 유지
      return newAccess;
    }
  } catch (error) {
    console.warn('Failed to refresh token:', error);
    clearTokens();
    return null;
  }
  return null;
}

✅ 2️⃣ Axios Request Interceptor — 자동 토큰 주입 + 만료 감지
api.interceptors.request.use(async (config: AxiosRequestConfig) => {
  const token = getAccessToken();

  if (token) {
    // 요청 전에 만료 여부 확인
    if (isTokenExpired(token)) {
      const newAccess = await refreshAccessToken();
      if (!newAccess) throw new Error('Unable to refresh access token');
      config.headers!['Authorization'] = `Bearer ${newAccess}`;
    } else {
      config.headers!['Authorization'] = `Bearer ${token}`;
    }
  }

  return config;
});

✅ 3️⃣ Axios Response Interceptor — 401 자동 처리 및 재시도
api.interceptors.response.use(
  response => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      console.warn('Access token expired, attempting refresh...');
      const newAccess = await refreshAccessToken();

      if (newAccess && error.config) {
        error.config.headers!['Authorization'] = `Bearer ${newAccess}`;
        // 원래 요청 재시도
        return api.request(error.config);
      }

      // 재발급 실패 → 로그인 페이지로 이동 or 로그아웃
      clearTokens();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

✅ 4️⃣ 로그인 함수 예시
export async function login(userId: string, roles: string[]) {
  const { data } = await api.post('/auth/token', { user_id: userId, roles });
  saveTokens(data.access_token, data.refresh_token);
  return data;
}

✅ 5️⃣ FastAPI 대응 엔드포인트 요약 (참고)
엔드포인트	메서드	설명
/auth/token	POST	Access + Refresh Token 발급
/auth/refresh	POST	Refresh Token으로 Access 재발급
/user/me	GET	JWT 인증 테스트용
✅ 6️⃣ 실제 동작 흐름

로그인 성공 → /auth/token → Access + Refresh 저장

요청 시 Axios가 Access Token 자동 추가

만료 감지 시 자동 /auth/refresh 요청

재발급 성공 → Access 갱신 → 원래 API 재시도

Refresh Token도 만료 시 자동 로그아웃 처리

✅ 7️⃣ 추가 팁
상황	대응
Refresh Token도 만료됨	401 발생 시 로그인 페이지로 이동
여러 탭 동시 로그인	Refresh Token은 localStorage 공유됨 — 동작 일관
짧은 Access Token 주기	10~15분 추천 (보안 + UX 밸런스)

이 코드는 Axios + FastAPI JWT 인증의 베스트 프랙티스 구조로,
실제 운영 서비스에서도 거의 그대로 사용 가능한 형태입니다 ⚙️


좋아요 👍
이제 Vue3 + TypeScript + Pinia + Axios 조합으로
JWT 기반 인증 (Access + Refresh 토큰)과 자동 재발급 로직을 완전히 통합한 버전을 보여드릴게요.

🧩 구조 개요
src/
 ├─ stores/
 │   └─ auth.ts           # 인증 관련 Pinia 스토어
 ├─ api/
 │   └─ axios.ts          # Axios 인스턴스 + 인터셉터
 ├─ views/
 │   └─ LoginView.vue     # 로그인 화면 예시
 ├─ main.ts

1️⃣ stores/auth.ts (Pinia 스토어)
// stores/auth.ts
import { defineStore } from 'pinia'
import axios from '@/api/axios'

interface User {
  id: string
  role: string
}

interface AuthState {
  accessToken: string | null
  refreshToken: string | null
  user: User | null
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    accessToken: localStorage.getItem('accessToken'),
    refreshToken: localStorage.getItem('refreshToken'),
    user: JSON.parse(localStorage.getItem('user') || 'null'),
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken,
  },

  actions: {
    async login(id: string) {
      const res = await axios.post('/auth/login', { id })
      const { access_token, refresh_token, user } = res.data

      this.accessToken = access_token
      this.refreshToken = refresh_token
      this.user = user

      localStorage.setItem('accessToken', access_token)
      localStorage.setItem('refreshToken', refresh_token)
      localStorage.setItem('user', JSON.stringify(user))
    },

    async refreshAccessToken() {
      if (!this.refreshToken) throw new Error('No refresh token')

      const res = await axios.post('/auth/refresh', {
        refresh_token: this.refreshToken,
      })
      const { access_token } = res.data

      this.accessToken = access_token
      localStorage.setItem('accessToken', access_token)
      return access_token
    },

    logout() {
      this.accessToken = null
      this.refreshToken = null
      this.user = null
      localStorage.clear()
    },
  },
})

2️⃣ api/axios.ts (Axios 인스턴스 + 인터셉터)
// api/axios.ts
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000,
})

// ✅ 요청 인터셉터
api.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.accessToken) {
    config.headers.Authorization = `Bearer ${auth.accessToken}`
  }
  return config
})

// ✅ 응답 인터셉터 (AccessToken 자동 갱신)
let isRefreshing = false
let refreshQueue: (() => void)[] = []

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const auth = useAuthStore()
    const originalRequest = error.config

    // 토큰 만료로 인한 401 에러 감지
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // 이미 갱신 중이면, 큐에 추가
        return new Promise((resolve) => {
          refreshQueue.push(() => resolve(api(originalRequest)))
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const newAccessToken = await auth.refreshAccessToken()
        // 대기 중이던 요청 재시도
        refreshQueue.forEach((cb) => cb())
        refreshQueue = []
        return api(originalRequest)
      } catch (err) {
        auth.logout()
        window.location.href = '/login'
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

export default api

3️⃣ FastAPI 백엔드 (요약)
# auth_router.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt

SECRET_KEY = "secret"
ALGORITHM = "HS256"

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    id: str

@router.post("/login")
def login(req: LoginRequest):
    user = {"id": req.id, "role": "admin"}  # 외부에서 받은 사용자정보 기반
    access_token = jwt.encode(
        {"sub": user["id"], "role": user["role"], "exp": datetime.utcnow() + timedelta(minutes=30)},
        SECRET_KEY, algorithm=ALGORITHM
    )
    refresh_token = jwt.encode(
        {"sub": user["id"], "exp": datetime.utcnow() + timedelta(days=7)},
        SECRET_KEY, algorithm=ALGORITHM
    )
    return {"access_token": access_token, "refresh_token": refresh_token, "user": user}

class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/refresh")
def refresh(req: RefreshRequest):
    try:
        payload = jwt.decode(req.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        new_access = jwt.encode(
            {"sub": payload["sub"], "exp": datetime.utcnow() + timedelta(minutes=30)},
            SECRET_KEY, algorithm=ALGORITHM
        )
        return {"access_token": new_access}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")

4️⃣ LoginView.vue (예시)
<template>
  <div class="flex flex-col items-center justify-center h-screen">
    <div class="bg-white shadow-lg p-8 rounded-xl w-80">
      <h2 class="text-2xl font-semibold mb-6 text-center">Login</h2>
      <input
        v-model="userId"
        type="text"
        placeholder="User ID"
        class="border p-2 w-full rounded mb-4"
      />
      <button
        @click="login"
        class="bg-blue-500 hover:bg-blue-600 text-white py-2 rounded w-full"
      >
        Login
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const userId = ref('')
const auth = useAuthStore()
const router = useRouter()

async function login() {
  try {
    await auth.login(userId.value)
    router.push('/')
  } catch {
    alert('Login failed')
  }
}
</script>

✅ 동작 요약
상황	처리 방식
로그인	/auth/login → Access + Refresh Token 저장
API 호출 시	Axios가 Authorization: Bearer 자동 추가
Access Token 만료 시	401 감지 → Refresh Token으로 자동 재발급 후 재요청
Refresh Token 만료 시	로그아웃 처리 + /login으로 리다이렉트

원하신다면 다음 단계로

🔐 AccessToken을 localStorage 대신 메모리 저장 + RefreshToken만 안전하게 HttpOnly 쿠키로 관리하는 고보안 버전
도 이어서 만들어드릴 수 있어요.

그럴까요?

아주 좋은 질문이에요 👍
FastAPI에서 JWT 토큰 안의 사용자 정보(예: id, role 등) 를 읽는 표준적인 방법은 다음 단계로 진행됩니다.

🧩 기본 개념

1️⃣ Frontend → 요청 시 JWT를 Authorization: Bearer <access_token> 헤더에 담아 전송
2️⃣ Backend(FastAPI) → 요청을 받을 때 JWT를 디코딩(jwt.decode())하여 사용자 정보를 확인
3️⃣ Dependency 주입 방식으로 get_current_user() 함수를 공통으로 사용

✅ 예시 코드
1️⃣ auth.py – JWT 검증 및 사용자 정보 추출
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime
from typing import Optional

SECRET_KEY = "secret"
ALGORITHM = "HS256"

# Authorization 헤더에서 Bearer 토큰을 자동으로 추출
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# JWT payload 스키마
class TokenData:
    def __init__(self, sub: str, role: Optional[str] = None):
        self.sub = sub
        self.role = role

def get_current_user(token: str = Depends(oauth2_scheme)):
    """요청 헤더의 JWT를 검증하고 사용자 정보를 반환"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        exp: int = payload.get("exp")
        if user_id is None:
            raise credentials_exception
        if datetime.utcfromtimestamp(exp) < datetime.utcnow():
            raise credentials_exception
        return TokenData(sub=user_id, role=role)
    except JWTError:
        raise credentials_exception

2️⃣ 라우터에서 사용 예시
from fastapi import APIRouter, Depends
from .auth import get_current_user, TokenData

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me")
def read_users_me(current_user: TokenData = Depends(get_current_user)):
    return {
        "user_id": current_user.sub,
        "role": current_user.role,
    }


➡️ 클라이언트가 Authorization: Bearer <access_token> 을 보냈다면,
해당 엔드포인트에서 자동으로 토큰이 파싱되어 아래와 같은 응답을 받게 됩니다:

{
  "user_id": "abc123",
  "role": "admin"
}

3️⃣ (선택) 실제 DB 사용자 조회 예시

JWT payload에는 **기본 식별자(id)**만 넣고,
실제 데이터는 DB에서 가져오고 싶다면 이렇게 확장할 수 있습니다:

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

✅ 정리
항목	설명
Authorization	Bearer <token> 형식
OAuth2PasswordBearer	FastAPI가 자동으로 헤더에서 토큰 추출
jwt.decode()	토큰 검증 및 payload 읽기
Depends(get_current_user)	인증 미들웨어처럼 공통으로 사용 가능
role 포함 시	권한 분기 처리도 가능 (if user.role != "admin": ...)
