// Before
if (jText && !jText.includes("공통") && jText.includes(":g1=")) {
  lastValidJudgment = jText;
  break;
}

// After: 새 포맷(key=타입) 패턴 존재 여부로 판단
if (jText && !jText.includes("공통") && hasJudgmentPattern(jText)) {
  lastValidJudgment = jText;
  break;
}


const JUDGMENT_REGEX =
  /(ppid|eqp_id|chamber_id)=(완전 불일치|부분 불일치)\s*\(교집합:\s*\{[^}]*\}\)/g;

// ★ 추가: 전역 플래그 없는 검사 전용 정규식 (lastIndex 상태 없이 안전하게 존재 여부만 확인)
const JUDGMENT_DETECT_REGEX = /(ppid|eqp_id|chamber_id)=(완전 불일치|부분 불일치)/;

function hasJudgmentPattern(text: string): boolean {
  return JUDGMENT_DETECT_REGEX.test(text);
}
