import streamlit as st
from google import genai
from google.genai import types
import os
from datetime import datetime
import pdfplumber
import io
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="AI 공간디자인 프로세스",
    page_icon="🏛️",
    layout="wide"
)

# ── 단계별 그래픽 ──────────────────────────────────────────

def show_stage_graphic(stage: int):
    if stage == 2:
        # 3가지 디자인 방향성 — 기하 도형으로 표현
        st.markdown("""
        <div style="display:flex;gap:24px;justify-content:center;align-items:flex-end;
                    margin:24px 0 8px;">
            <div style="text-align:center;">
                <div style="width:72px;height:72px;
                            background:linear-gradient(135deg,#1C2B3A,#4A6FA5);
                            border-radius:6px;margin:0 auto 8px;"></div>
                <span style="font-size:11px;color:#888;">기하 / 모던</span>
            </div>
            <div style="text-align:center;">
                <div style="width:72px;height:72px;
                            background:linear-gradient(135deg,#6B4F3A,#C4A882);
                            border-radius:50%;margin:0 auto 8px;"></div>
                <span style="font-size:11px;color:#888;">유기 / 자연</span>
            </div>
            <div style="text-align:center;">
                <div style="width:0;height:0;
                            border-left:36px solid transparent;
                            border-right:36px solid transparent;
                            border-bottom:72px solid #2D5A3D;
                            margin:0 auto 8px;
                            filter:drop-shadow(0 2px 4px rgba(45,90,61,0.3));"></div>
                <span style="font-size:11px;color:#888;">역동 / 대담</span>
            </div>
        </div>
        <p style="text-align:center;color:#aaa;font-size:12px;margin-bottom:20px;">
            아래 3가지 컨셉 중 하나를 선택하세요
        </p>
        """, unsafe_allow_html=True)

    elif stage == 3:
        # 무드보드 3방향 — 컬러 스트라이프로 표현
        st.markdown("""
        <div style="display:flex;flex-direction:column;gap:6px;margin:24px 0 8px;">
            <div style="display:flex;gap:4px;height:20px;border-radius:4px;overflow:hidden;">
                <div style="flex:3;background:#E8DCC8;"></div>
                <div style="flex:2;background:#C4A882;"></div>
                <div style="flex:1;background:#8B7355;"></div>
                <div style="flex:1;background:#5C4A2A;"></div>
                <div style="flex:2;background:#F5F0E8;"></div>
            </div>
            <div style="display:flex;gap:4px;height:20px;border-radius:4px;overflow:hidden;">
                <div style="flex:2;background:#1C2B3A;"></div>
                <div style="flex:2;background:#4A6FA5;"></div>
                <div style="flex:1;background:#7A9CC4;"></div>
                <div style="flex:2;background:#D0DCE8;"></div>
                <div style="flex:1;background:#F0F4F8;"></div>
            </div>
            <div style="display:flex;gap:4px;height:20px;border-radius:4px;overflow:hidden;">
                <div style="flex:2;background:#2D5A3D;"></div>
                <div style="flex:1;background:#5A8A6A;"></div>
                <div style="flex:2;background:#A8C8A0;"></div>
                <div style="flex:1;background:#D4E8D0;"></div>
                <div style="flex:2;background:#F5F8F4;"></div>
            </div>
        </div>
        <div style="display:flex;justify-content:space-around;margin-bottom:20px;">
            <span style="font-size:11px;color:#888;">Option A · 웜 내추럴</span>
            <span style="font-size:11px;color:#888;">Option B · 쿨 모던</span>
            <span style="font-size:11px;color:#888;">Option C · 바이오필릭</span>
        </div>
        """, unsafe_allow_html=True)

    elif stage == 4:
        # 페르소나 + 조닝 — 사람 아이콘 + 플로어플랜 그리드
        st.markdown("""
        <div style="display:flex;gap:24px;justify-content:center;
                    align-items:center;margin:24px 0 16px;">
            <div style="display:flex;gap:12px;">
                <div style="text-align:center;">
                    <svg width="40" height="52" viewBox="0 0 40 52"
                         fill="none" xmlns="http://www.w3.org/2000/svg">
                        <circle cx="20" cy="12" r="10" fill="#4A6FA5"/>
                        <path d="M4 48 Q4 28 20 28 Q36 28 36 48"
                              fill="#4A6FA5" opacity="0.7"/>
                    </svg>
                    <div style="font-size:10px;color:#888;margin-top:4px;">페르소나 1</div>
                </div>
                <div style="text-align:center;">
                    <svg width="40" height="52" viewBox="0 0 40 52"
                         fill="none" xmlns="http://www.w3.org/2000/svg">
                        <circle cx="20" cy="12" r="10" fill="#8B7355"/>
                        <path d="M4 48 Q4 28 20 28 Q36 28 36 48"
                              fill="#8B7355" opacity="0.7"/>
                    </svg>
                    <div style="font-size:10px;color:#888;margin-top:4px;">페르소나 2</div>
                </div>
                <div style="text-align:center;">
                    <svg width="40" height="52" viewBox="0 0 40 52"
                         fill="none" xmlns="http://www.w3.org/2000/svg">
                        <circle cx="20" cy="12" r="10" fill="#2D5A3D"/>
                        <path d="M4 48 Q4 28 20 28 Q36 28 36 48"
                              fill="#2D5A3D" opacity="0.7"/>
                    </svg>
                    <div style="font-size:10px;color:#888;margin-top:4px;">페르소나 3</div>
                </div>
            </div>
            <div style="font-size:24px;color:#ccc;">→</div>
            <div style="display:grid;grid-template-columns:1.5fr 1fr;
                        grid-template-rows:1fr 1fr;gap:4px;width:100px;height:80px;">
                <div style="background:#4A6FA5;border-radius:3px;grid-row:1/3;
                            display:flex;align-items:center;justify-content:center;
                            color:white;font-size:9px;font-weight:600;">MAIN</div>
                <div style="background:#8B7355;border-radius:3px;
                            display:flex;align-items:center;justify-content:center;
                            color:white;font-size:9px;">A</div>
                <div style="background:#2D5A3D;border-radius:3px;
                            display:flex;align-items:center;justify-content:center;
                            color:white;font-size:9px;">B</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── API 키 ─────────────────────────────────────────────────

def get_api_key() -> str:
    try:
        if "GOOGLE_API_KEY" in st.secrets:
            return st.secrets["GOOGLE_API_KEY"]
    except Exception:
        pass
    return os.getenv("GOOGLE_API_KEY", "")

# ── 세션 초기화 ────────────────────────────────────────────

def init_state():
    defaults = {
        "stage": 0,
        "file_parts": None,
        "rfp_draft": "", "rfp": "",
        "concept_draft": "", "concept": "",
        "keywords_draft": "", "keywords": "",
        "persona_draft": "", "persona": "",
        "midjourney_draft": "", "midjourney": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def go_back_to(stage: int):
    """stage 이후 모든 확정·초안 초기화 후 해당 단계로 복귀"""
    clear_map = {
        2: ["concept", "keywords_draft", "keywords",
            "persona_draft", "persona", "midjourney_draft", "midjourney"],
        3: ["keywords", "persona_draft", "persona",
            "midjourney_draft", "midjourney"],
        4: ["persona", "midjourney_draft", "midjourney"],
        5: ["midjourney"],
    }
    for key in clear_map.get(stage, []):
        st.session_state[key] = ""
    st.session_state.stage = stage

# ── 파일 처리 ──────────────────────────────────────────────

def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

def get_media_type(filename: str) -> str:
    ext = filename.lower().rsplit(".", 1)[-1]
    return {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
            "gif": "image/gif", "webp": "image/webp"}.get(ext, "image/jpeg")

def build_file_parts(uploaded_files) -> list:
    text_blocks = []
    image_parts = []
    for file in uploaded_files:
        file.seek(0)
        raw = file.read()
        name = file.name
        if name.lower().endswith(".txt"):
            text_blocks.append(f"[텍스트 파일: {name}]\n{raw.decode('utf-8', errors='ignore')}")
        elif name.lower().endswith(".pdf"):
            extracted = extract_text_from_pdf(raw)
            text_blocks.append(f"[PDF: {name}]\n{extracted}" if extracted
                               else f"[PDF: {name}]\n(텍스트 추출 불가)")
        elif name.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp")):
            text_blocks.append(f"[이미지: {name}] — 이미지 내 텍스트와 시각 내용을 분석해주세요.")
            image_parts.append(types.Part(inline_data=types.Blob(
                data=raw, mime_type=get_media_type(name))))
    parts = []
    if text_blocks:
        parts.append(types.Part(text="\n\n".join(text_blocks)))
    parts.extend(image_parts)
    return parts

# ── Gemini 호출 ────────────────────────────────────────────

def call_gemini(api_key: str, system_prompt: str, parts: list,
                model_name: str, placeholder) -> str:
    client = genai.Client(api_key=api_key)
    result = ""
    try:
        for chunk in client.models.generate_content_stream(
            model=model_name,
            contents=parts,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                max_output_tokens=4096,
            ),
        ):
            try:
                if chunk.text:
                    result += chunk.text
                    placeholder.markdown(result + "▌")
            except Exception:
                pass
    except Exception as e:
        st.error(f"❌ API 오류: {str(e)}")
        st.stop()
    placeholder.markdown(result)
    return result

# ── 섹션 추출 헬퍼 ─────────────────────────────────────────

def extract_concept_section(text: str, num: str) -> str:
    """컨셉 N번 섹션만 추출"""
    marker = f"### 컨셉 {num}:"
    start = text.find(marker)
    if start == -1:
        return text
    end = len(text)
    for other in ["1", "2", "3"]:
        if other == num:
            continue
        pos = text.find(f"### 컨셉 {other}:", start + 1)
        if pos != -1:
            end = min(end, pos)
    return text[start:end].strip()

def extract_keyword_option(text: str, option: str) -> str:
    """키워드 Option A/B/C 섹션만 추출"""
    marker = f"### Option {option}"
    start = text.find(marker)
    if start == -1:
        return text
    end = len(text)
    for other in ["A", "B", "C"]:
        if other == option:
            continue
        pos = text.find(f"### Option {other}", start + 1)
        if pos != -1:
            end = min(end, pos)
    return text[start:end].strip()

# ── 시스템 프롬프트 ────────────────────────────────────────

SYSTEMS = {
    "rfp":        "당신은 15년 경력의 공간디자인 전문가입니다. 클라이언트 RFP를 분석해 핵심 요소를 구조화합니다. 한국어로 답변하세요.",
    "concept":    "당신은 크리에이티브 디렉터로서 공간디자인 컨셉을 개발하는 전문가입니다. 한국어로 답변하세요.",
    "keywords":   "당신은 공간디자인 전문가이자 비주얼 디렉터입니다. 디자인 컨셉을 키워드와 시각 레퍼런스로 표현합니다. 한국어로 답변하세요.",
    "persona":    "당신은 UX 리서처와 공간 플래너를 겸하는 전문가입니다. 사용자 경험 중심으로 공간을 설계합니다. 한국어로 답변하세요.",
    "midjourney": "당신은 AI 이미지 생성 전문가이자 공간 렌더링 전문가입니다. Midjourney 프롬프트를 최적화합니다. 한국어 설명과 영어 프롬프트를 함께 제공하세요.",
}

RFP_INSTRUCTION = """다음 RFP 문서를 분석하여 아래 6가지 항목을 구조화해주세요.
명시되지 않은 항목은 문서 전체 맥락을 통해 합리적으로 추론하여 작성하고, 추론한 내용은 (추론) 표시를 붙여주세요.

## 📋 RFP 분석 결과

### 1. 프로젝트 개요
- 프로젝트명:
- 공간 유형:
- 위치 / 규모:
- 프로젝트 목적:
- 클라이언트:

### 2. 필요공간 및 프로그램
- 필수 공간 목록 (각 공간의 기능 및 면적 비중 포함):
- 공간 간 관계 및 동선:
- 특수 요구사항:

### 3. 예산 범위
- 명시된 예산:
- 예산 우선순위 (추론 포함):
- 제약 조건:

### 4. 일정 및 기한
- 프로젝트 시작일:
- 주요 마일스톤:
- 최종 완료 기한:
- 일정 리스크:

### 5. 디자인 방향 키워드
- 명시된 스타일 / 무드:
- 레퍼런스 (언급된 경우):
- 금지 또는 지양 요소:
- 핵심 디자인 키워드 5개: `키워드1` `키워드2` `키워드3` `키워드4` `키워드5`

### 6. 추론된 클라이언트의 숨은 니즈
> RFP에 명시되지 않았지만 문서 전체 맥락, 업종 특성, 클라이언트 유형 등을 종합해 추론한 진짜 니즈를 작성해주세요.
- 비즈니스 관점의 숨은 목표:
- 사용자 경험 관점의 기대:
- 브랜드/이미지 관점의 기대:
- 디자이너가 선제적으로 제안해야 할 사항:

[첨부 RFP 문서]"""

CONCEPT_INSTRUCTION = """위 RFP 분석을 바탕으로 서로 뚜렷하게 차별화된 3가지 디자인 컨셉을 제시해주세요.

## 🎨 디자인 컨셉

### 컨셉 1: [컨셉명]
**핵심 철학:**
**디자인 스토리:**
**주요 감성:**
**공간 경험:**
**차별점:**

### 컨셉 2: [컨셉명]
(동일 구조)

### 컨셉 3: [컨셉명]
(동일 구조)

[RFP 분석 결과]"""

KEYWORDS_INSTRUCTION = """위 선택된 컨셉을 바탕으로 서로 다른 분위기의 3가지 키워드 & 무드보드 방향을 제시해주세요.

## 🖼️ 키워드 & 무드보드

### Option A: [방향명]
**디자인 키워드 (10개):**
1.
2.
3.
4.
5.
6.
7.
8.
9.
10.

**컬러 팔레트:**
- 메인:
- 서브:
- 액센트:

**소재 & 텍스처:**

**무드보드 이미지 방향 (5장):**
1.
2.
3.
4.
5.

### Option B: [방향명]
(동일 구조)

### Option C: [방향명]
(동일 구조)

[선택된 컨셉]"""

PERSONA_INSTRUCTION = """위 프로젝트의 컨셉과 키워드를 바탕으로 페르소나와 조닝 계획을 작성해주세요.

## 👥 페르소나 & 경험 시나리오

### 페르소나 1
**이름 / 나이 / 직업:**
**라이프스타일:**
**공간 사용 목적:**
**경험 시나리오 (입장 → 이동 → 체류 → 퇴장):**
>

### 페르소나 2
(동일 구조)

### 페르소나 3 (선택)
(동일 구조)

---

## 🗺️ 조닝 계획

### 공간 구성 원칙

### 조닝 다이어그램
```
┌─────────────────────────────────┐
│           전체 공간              │
│  ┌──────┐  ┌──────┐  ┌──────┐  │
│  │Zone A│  │Zone B│  │Zone C│  │
│  └──────┘  └──────┘  └──────┘  │
└─────────────────────────────────┘
```

### 각 Zone 상세
**Zone A - [존명]:** 면적 비율 / 주요 기능 / 타겟 페르소나 / 디자인 특성
(Zone B, C 동일)

[RFP 분석 + 선택된 컨셉 + 선택된 키워드]"""

MIDJOURNEY_INSTRUCTION = """위 조닝 계획의 각 Zone에 맞는 Midjourney 프롬프트를 생성해주세요.

## 🎬 조닝별 Midjourney 프롬프트

### Zone [X] - [존명]

**렌더링 방향:**
- 촬영 앵글:
- 조명 설정:
- 강조 요소:

**Midjourney 프롬프트:**
```
/imagine [상세 영어 프롬프트], interior design, [style keywords], [lighting], [camera angle], [material details], photorealistic, 8k, architectural visualization --ar 16:9 --v 6.1 --stylize 200
```

**네거티브 프롬프트:**
```
--no people, clutter, dark shadows, low quality
```

> 💡 프롬프트를 그대로 복사해서 Discord Midjourney 봇에 붙여넣기 하세요.

[선택된 컨셉 + 키워드 + 조닝 계획]"""

# ── 보고서 ─────────────────────────────────────────────────

def build_report(project_name: str) -> tuple[str, str]:
    now = datetime.now()
    report = f"""# AI 공간디자인 프로세스 보고서
**프로젝트:** {project_name}
**생성일시:** {now.strftime("%Y년 %m월 %d일 %H:%M")}

---

{st.session_state.rfp}

---

{st.session_state.concept}

---

{st.session_state.keywords}

---

{st.session_state.persona}

---

{st.session_state.midjourney}

---
*본 보고서는 AI 공간디자인 프로세스 시스템으로 자동 생성되었습니다.*
"""
    return report, now.strftime("%Y%m%d_%H%M")

# ── 확정된 단계 표시 ───────────────────────────────────────

def show_confirmed(stage_num: int, title: str, content: str, back_label: str):
    col1, col2 = st.columns([5, 1])
    with col1:
        st.success(f"✅ {stage_num}단계: {title} — 확정 완료")
    with col2:
        if st.button("↩ 다시 선택", key=f"back_{stage_num}", use_container_width=True):
            go_back_to(stage_num)
            st.rerun()
    with st.expander(f"{back_label} 보기"):
        st.markdown(content)

# ── 메인 ──────────────────────────────────────────────────

def main():
    init_state()

    st.title("🏛️ AI 공간디자인 프로세스")
    st.caption("단계별로 결과를 확인·선택하고 확정한 뒤 다음 단계로 진행합니다.")

    # 사이드바
    with st.sidebar:
        st.header("📁 프로젝트 정보")
        project_name = st.text_input("프로젝트명", placeholder="예: 강남 카페 리뉴얼 2025")
        model = st.selectbox(
            "AI 모델",
            ["gemini-2.5-flash", "gemini-2.5-pro"],
            help="2.5-flash: 빠름 (권장) | 2.5-pro: 최고 품질"
        )
        st.divider()
        st.markdown("**지원 파일 형식**")
        st.markdown("- 텍스트 `.txt`\n- PDF `.pdf`\n- 이미지 `.jpg` `.png` `.webp`")
        st.divider()
        preset_key = get_api_key()
        if preset_key:
            api_key = preset_key
            st.success("✅ API 연결됨")
        else:
            api_key = st.text_input("Google API Key", type="password",
                                    help="aistudio.google.com 에서 무료 발급")
        if st.session_state.stage > 0:
            st.divider()
            if st.button("🔄 처음부터 다시", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

    # ══ 0단계: 파일 업로드 ════════════════════════════════
    if st.session_state.stage == 0:
        st.header("📤 RFP 문서 업로드")
        uploaded_files = st.file_uploader(
            "파일 드래그 또는 클릭하여 업로드 (여러 파일 동시 가능)",
            accept_multiple_files=True,
            type=["txt", "pdf", "jpg", "jpeg", "png", "webp", "gif"]
        )
        if uploaded_files:
            img_files = [f for f in uploaded_files
                         if f.name.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".gif"))]
            if img_files:
                cols = st.columns(min(len(img_files), 4))
                for i, f in enumerate(img_files):
                    f.seek(0)
                    cols[i % 4].image(f, caption=f.name, use_container_width=True)

        ready = bool(uploaded_files and api_key and project_name)
        if not ready:
            st.info("👈 프로젝트명 입력 + RFP 파일 업로드 후 시작할 수 있습니다." if api_key
                    else "👈 API 키 입력 + 프로젝트명 + RFP 파일 업로드 후 시작할 수 있습니다.")

        if st.button("🚀 1단계 시작 — RFP 분석", type="primary", disabled=not ready):
            with st.spinner("파일 처리 중..."):
                st.session_state.file_parts = build_file_parts(uploaded_files)
            st.session_state.stage = 1
            st.rerun()

    # ══ 1단계: RFP 분석 ══════════════════════════════════
    if st.session_state.stage >= 1:
        if st.session_state.stage > 1:
            show_confirmed(1, "📋 RFP 분석", st.session_state.rfp, "분석 결과")
        else:
            st.header("📋 1단계: RFP 분석")
            if not st.session_state.rfp_draft:
                with st.spinner("RFP 분석 중..."):
                    ph = st.empty()
                    rfp_parts = [types.Part(text=RFP_INSTRUCTION)] + st.session_state.file_parts
                    st.session_state.rfp_draft = call_gemini(
                        api_key, SYSTEMS["rfp"], rfp_parts, model, ph)
                st.rerun()
            else:
                st.markdown(st.session_state.rfp_draft)
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("🔄 다시 생성", key="rfp_regen", use_container_width=True):
                        st.session_state.rfp_draft = ""
                        st.rerun()
                with c2:
                    if st.button("✅ 확정 — 2단계로", key="rfp_ok",
                                 type="primary", use_container_width=True):
                        st.session_state.rfp = st.session_state.rfp_draft
                        st.session_state.stage = 2
                        st.rerun()

    # ══ 2단계: 디자인 컨셉 3가지 선택 ════════════════════
    if st.session_state.stage >= 2:
        if st.session_state.stage > 2:
            show_confirmed(2, "🎨 디자인 컨셉", st.session_state.concept, "선택된 컨셉")
        else:
            st.header("🎨 2단계: 디자인 컨셉")
            show_stage_graphic(2)
            if not st.session_state.concept_draft:
                with st.spinner("디자인 컨셉 3가지 생성 중..."):
                    ph = st.empty()
                    st.session_state.concept_draft = call_gemini(
                        api_key, SYSTEMS["concept"],
                        [types.Part(text=f"{CONCEPT_INSTRUCTION}\n\n---\n{st.session_state.rfp}")],
                        model, ph)
                st.rerun()
            else:
                st.markdown(st.session_state.concept_draft)
                st.divider()
                st.markdown("**다음 단계에 사용할 컨셉을 선택하세요:**")
                selected = st.radio("", ["컨셉 1", "컨셉 2", "컨셉 3"],
                                    horizontal=True, label_visibility="collapsed")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("🔄 다시 생성", key="concept_regen", use_container_width=True):
                        st.session_state.concept_draft = ""
                        st.rerun()
                with c2:
                    if st.button(f"✅ {selected} 확정 — 3단계로", key="concept_ok",
                                 type="primary", use_container_width=True):
                        num = selected[-1]
                        st.session_state.concept = extract_concept_section(
                            st.session_state.concept_draft, num)
                        st.session_state.stage = 3
                        st.rerun()

    # ══ 3단계: 키워드 & 무드보드 3가지 선택 ══════════════
    if st.session_state.stage >= 3:
        if st.session_state.stage > 3:
            show_confirmed(3, "🖼️ 키워드 & 무드보드", st.session_state.keywords, "선택된 키워드")
        else:
            st.header("🖼️ 3단계: 키워드 & 무드보드")
            show_stage_graphic(3)
            if not st.session_state.keywords_draft:
                with st.spinner("키워드 & 무드보드 3가지 방향 생성 중..."):
                    ph = st.empty()
                    context = f"[선택된 컨셉]\n{st.session_state.concept}"
                    st.session_state.keywords_draft = call_gemini(
                        api_key, SYSTEMS["keywords"],
                        [types.Part(text=f"{KEYWORDS_INSTRUCTION}\n\n---\n{context}")],
                        model, ph)
                st.rerun()
            else:
                st.markdown(st.session_state.keywords_draft)
                st.divider()
                st.markdown("**다음 단계에 사용할 키워드 방향을 선택하세요:**")
                selected = st.radio("", ["Option A", "Option B", "Option C"],
                                    horizontal=True, label_visibility="collapsed")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("🔄 다시 생성", key="kw_regen", use_container_width=True):
                        st.session_state.keywords_draft = ""
                        st.rerun()
                with c2:
                    if st.button(f"✅ {selected} 확정 — 4단계로", key="kw_ok",
                                 type="primary", use_container_width=True):
                        opt = selected.split()[-1]  # "A", "B", "C"
                        st.session_state.keywords = extract_keyword_option(
                            st.session_state.keywords_draft, opt)
                        st.session_state.stage = 4
                        st.rerun()

    # ══ 4단계: 페르소나 & 조닝 ════════════════════════════
    if st.session_state.stage >= 4:
        if st.session_state.stage > 4:
            show_confirmed(4, "👥 페르소나 & 조닝", st.session_state.persona, "페르소나 & 조닝")
        else:
            st.header("👥 4단계: 페르소나 & 조닝 계획")
            show_stage_graphic(4)
            if not st.session_state.persona_draft:
                with st.spinner("페르소나 및 조닝 생성 중..."):
                    ph = st.empty()
                    context = (f"[RFP 분석]\n{st.session_state.rfp}\n\n"
                               f"[선택된 컨셉]\n{st.session_state.concept}\n\n"
                               f"[선택된 키워드]\n{st.session_state.keywords}")
                    st.session_state.persona_draft = call_gemini(
                        api_key, SYSTEMS["persona"],
                        [types.Part(text=f"{PERSONA_INSTRUCTION}\n\n---\n{context}")],
                        model, ph)
                st.rerun()
            else:
                st.markdown(st.session_state.persona_draft)
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("🔄 다시 생성", key="persona_regen", use_container_width=True):
                        st.session_state.persona_draft = ""
                        st.rerun()
                with c2:
                    if st.button("✅ 확정 — 5단계로", key="persona_ok",
                                 type="primary", use_container_width=True):
                        st.session_state.persona = st.session_state.persona_draft
                        st.session_state.stage = 5
                        st.rerun()

    # ══ 5단계: Midjourney 프롬프트 ════════════════════════
    if st.session_state.stage >= 5:
        if st.session_state.stage > 5:
            show_confirmed(5, "🎬 Midjourney 프롬프트", st.session_state.midjourney, "프롬프트")
        else:
            st.header("🎬 5단계: Midjourney 프롬프트")
            if not st.session_state.midjourney_draft:
                with st.spinner("Midjourney 프롬프트 생성 중..."):
                    ph = st.empty()
                    context = (f"[선택된 컨셉]\n{st.session_state.concept}\n\n"
                               f"[선택된 키워드]\n{st.session_state.keywords}\n\n"
                               f"[조닝 계획]\n{st.session_state.persona}")
                    st.session_state.midjourney_draft = call_gemini(
                        api_key, SYSTEMS["midjourney"],
                        [types.Part(text=f"{MIDJOURNEY_INSTRUCTION}\n\n---\n{context}")],
                        model, ph)
                st.rerun()
            else:
                st.markdown(st.session_state.midjourney_draft)
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("🔄 다시 생성", key="mj_regen", use_container_width=True):
                        st.session_state.midjourney_draft = ""
                        st.rerun()
                with c2:
                    if st.button("✅ 확정 — 보고서 생성", key="mj_ok",
                                 type="primary", use_container_width=True):
                        st.session_state.midjourney = st.session_state.midjourney_draft
                        st.session_state.stage = 6
                        st.rerun()

    # ══ 6단계: 보고서 다운로드 ════════════════════════════
    if st.session_state.stage >= 6:
        st.header("📥 최종 보고서")
        st.success("🎉 모든 단계 완료!")
        if project_name:
            report, timestamp = build_report(project_name)
            filename = f"{project_name.replace(' ', '_')}_{timestamp}.md"
            st.download_button(
                label="⬇️ 마크다운 보고서 다운로드 (.md)",
                data=report.encode("utf-8"),
                file_name=filename,
                mime="text/markdown",
                type="primary",
                use_container_width=True
            )

if __name__ == "__main__":
    main()
