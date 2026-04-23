import streamlit as st
from google import genai
from google.genai import types
import os
from datetime import datetime
import pdfplumber
import io
from dotenv import load_dotenv

load_dotenv()

def get_api_key() -> str:
    try:
        if "GOOGLE_API_KEY" in st.secrets:
            return st.secrets["GOOGLE_API_KEY"]
    except Exception:
        pass
    return os.getenv("GOOGLE_API_KEY", "")

st.set_page_config(
    page_title="AI 공간디자인 프로세스",
    page_icon="🏛️",
    layout="wide"
)

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
            if extracted:
                text_blocks.append(f"[PDF 파일: {name}]\n{extracted}")
            else:
                text_blocks.append(f"[PDF 파일: {name}]\n(텍스트 추출 불가 — 이미지 PDF)")

        elif name.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp")):
            text_blocks.append(f"[이미지 파일: {name}] — 이미지 내 텍스트와 시각적 내용을 모두 분석해주세요.")
            image_parts.append(types.Part(inline_data=types.Blob(data=raw, mime_type=get_media_type(name))))

    parts = []
    if text_blocks:
        parts.append(types.Part(text="\n\n".join(text_blocks)))
    parts.extend(image_parts)
    return parts

# ── Gemini 호출 ────────────────────────────────────────────

def call_gemini_stream(api_key: str, system_prompt: str, parts: list,
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
        st.error(f"❌ API 오류 상세: {str(e)}")
        st.stop()
    placeholder.markdown(result)
    return result

# ── 프롬프트 정의 ──────────────────────────────────────────

SYSTEMS = {
    "rfp": "당신은 15년 경력의 공간디자인 전문가입니다. 클라이언트 RFP를 분석해 프로젝트의 핵심 요소를 구조화합니다. 한국어로 답변하세요.",
    "concept": "당신은 크리에이티브 디렉터로서 공간디자인 컨셉을 개발하는 전문가입니다. 한국어로 답변하세요.",
    "keywords": "당신은 공간디자인 전문가이자 비주얼 디렉터입니다. 디자인 컨셉을 구체적인 키워드와 시각 레퍼런스로 표현합니다. 한국어로 답변하세요.",
    "persona": "당신은 UX 리서처와 공간 플래너를 겸하는 전문가입니다. 사용자 경험 중심으로 공간을 설계합니다. 한국어로 답변하세요.",
    "midjourney": "당신은 AI 이미지 생성 전문가이자 공간 렌더링 전문가입니다. Midjourney 프롬프트를 최적화합니다. 한국어 설명과 영어 프롬프트를 함께 제공하세요.",
}

RFP_INSTRUCTION = (
    "다음 RFP 문서를 분석하여 아래 항목을 구조화해주세요.\n\n"
    "## 📋 RFP 분석 결과\n\n"
    "### 1. 프로젝트 개요\n- 프로젝트명 / 유형\n- 공간 규모 및 위치\n- 프로젝트 목적\n\n"
    "### 2. 클라이언트 정보\n- 클라이언트 특성\n- 브랜드 아이덴티티\n\n"
    "### 3. 타겟 사용자\n- 주요 사용자 그룹\n- 사용자 행동 패턴\n\n"
    "### 4. 공간 요구사항\n- 필수 공간 구성\n- 기능적 요구사항\n- 제약조건\n\n"
    "### 5. 디자인 방향 힌트\n- 언급된 스타일/무드\n- 레퍼런스\n\n"
    "### 6. 핵심 과제\n- 해결할 디자인 문제\n- 기회 요소\n\n[첨부 RFP 문서]"
)

CONCEPT_INSTRUCTION = (
    "위 RFP 분석을 바탕으로 3가지 차별화된 디자인 방향성을 제시해주세요.\n\n"
    "## 🎨 디자인 방향성 및 컨셉\n\n"
    "### 컨셉 1: [컨셉명]\n**핵심 철학:**\n**디자인 스토리:**\n**주요 감성:**\n**공간 경험:**\n**차별점:**\n\n"
    "### 컨셉 2: [컨셉명]\n(동일 구조)\n\n"
    "### 컨셉 3: [컨셉명]\n(동일 구조)\n\n"
    "각 컨셉은 서로 뚜렷하게 차별화되어야 합니다.\n\n[RFP 분석 결과]"
)

KEYWORDS_INSTRUCTION = (
    "위 3가지 디자인 컨셉을 바탕으로 각 컨셉의 키워드와 무드보드 구성을 작성해주세요.\n\n"
    "## 🖼️ 디자인 키워드 및 무드보드\n\n"
    "### 컨셉 [N]: [컨셉명]\n\n"
    "**디자인 키워드 (10개):**\n1. \n2. \n...\n\n"
    "**컬러 팔레트:**\n- 메인: \n- 서브: \n- 액센트: \n\n"
    "**소재 & 텍스처:**\n\n"
    "**무드보드 이미지 방향 (5장):**\n1. [이미지 설명 및 검색 키워드]\n2. \n3. \n4. \n5. \n\n"
    "[디자인 컨셉]"
)

PERSONA_INSTRUCTION = (
    "위 프로젝트의 디자인 컨셉을 바탕으로 페르소나와 조닝 계획을 작성해주세요.\n\n"
    "## 👥 페르소나 & 경험 시나리오\n\n"
    "### 페르소나 1\n**이름 / 나이 / 직업:**\n**라이프스타일:**\n**공간 사용 목적:**\n"
    "**경험 시나리오 (입장 → 이동 → 체류 → 퇴장):**\n>\n\n"
    "### 페르소나 2\n(동일 구조)\n\n"
    "### 페르소나 3 (선택)\n(동일 구조)\n\n"
    "---\n\n## 🗺️ 조닝 계획 다이어그램\n\n"
    "### 공간 구성 원칙\n\n"
    "### 조닝 다이어그램 (텍스트)\n```\n"
    "┌─────────────────────────────────┐\n│           전체 공간              │\n"
    "│  ┌──────┐  ┌──────┐  ┌──────┐  │\n│  │Zone A│  │Zone B│  │Zone C│  │\n"
    "│  └──────┘  └──────┘  └──────┘  │\n└─────────────────────────────────┘\n```\n\n"
    "### 각 Zone 상세\n**Zone A - [존명]:**\n- 면적 비율:\n- 주요 기능:\n- 타겟 페르소나:\n- 디자인 특성:\n\n"
    "(Zone B, C 동일 구조)\n\n[RFP 분석 + 디자인 컨셉]"
)

MIDJOURNEY_INSTRUCTION = (
    "위 조닝 계획의 각 Zone에 맞는 Midjourney 프롬프트를 생성해주세요.\n\n"
    "## 🎬 조닝별 렌더링 & Midjourney 프롬프트\n\n"
    "### Zone [X] - [존명]\n\n"
    "**렌더링 방향:**\n- 촬영 앵글:\n- 조명 설정:\n- 강조 요소:\n\n"
    "**Midjourney 프롬프트:**\n```\n"
    "/imagine [상세 영어 프롬프트], interior design, [style keywords], [lighting], "
    "[camera angle], [material details], photorealistic, 8k, architectural visualization "
    "--ar 16:9 --v 6.1 --stylize 200\n```\n\n"
    "**네거티브 프롬프트:**\n```\n--no people, clutter, dark shadows, low quality\n```\n\n"
    "> 💡 프롬프트를 그대로 복사하여 Discord Midjourney 봇에 붙여넣기 하세요.\n\n"
    "[컨셉 + 조닝 계획]"
)

# ── 보고서 생성 ────────────────────────────────────────────

def build_report(project_name: str, results: dict) -> tuple[str, str]:
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M")
    report = f"""# AI 공간디자인 프로세스 보고서
**프로젝트:** {project_name}
**생성일시:** {now.strftime("%Y년 %m월 %d일 %H:%M")}

---

{results.get("rfp", "")}

---

{results.get("concept", "")}

---

{results.get("keywords", "")}

---

{results.get("persona", "")}

---

{results.get("midjourney", "")}

---
*본 보고서는 AI 공간디자인 프로세스 시스템으로 자동 생성되었습니다.*
"""
    return report, timestamp

# ── UI ────────────────────────────────────────────────────

def main():
    st.title("🏛️ AI 공간디자인 프로세스")
    st.caption("RFP 분석 → 컨셉 도출 → 키워드/무드보드 → 페르소나/조닝 → Midjourney 프롬프트")

    with st.sidebar:
        st.header("📁 프로젝트 정보")
        project_name = st.text_input("프로젝트명", placeholder="예: 강남 카페 리뉴얼 2025")
        model = st.selectbox(
            "AI 모델 선택",
            ["gemini-2.0-flash", "gemini-2.5-pro"],
            help="2.0-flash: 빠름 (권장) | 2.5-pro: 최고 품질"
        )
        st.divider()
        st.markdown("**지원 파일 형식**")
        st.markdown("- 텍스트 `.txt`\n- PDF `.pdf`\n- 이미지 `.jpg` `.png` `.webp`")
        st.markdown("이미지 내 텍스트도 자동으로 인식합니다.")

        st.divider()
        preset_key = get_api_key()
        if preset_key:
            api_key = preset_key
            st.success("✅ API 연결됨")
        else:
            st.header("⚙️ API 설정")
            api_key = st.text_input(
                "Google API Key",
                type="password",
                help="aistudio.google.com 에서 무료 발급"
            )

    st.header("📤 RFP 문서 업로드")
    uploaded_files = st.file_uploader(
        "파일을 드래그하거나 클릭하여 업로드 (여러 파일 동시 가능)",
        accept_multiple_files=True,
        type=["txt", "pdf", "jpg", "jpeg", "png", "webp", "gif"]
    )

    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)}개 파일 업로드 완료")
        img_files = [f for f in uploaded_files
                     if f.name.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".gif"))]
        if img_files:
            cols = st.columns(min(len(img_files), 4))
            for i, f in enumerate(img_files):
                f.seek(0)
                cols[i % 4].image(f, caption=f.name, use_container_width=True)

    ready = bool(uploaded_files and api_key and project_name)
    if not ready:
        if not project_name:
            st.info("👈 왼쪽에서 프로젝트명을 입력해주세요.")
        elif not uploaded_files:
            st.info("⬆️ RFP 문서를 업로드해주세요.")
        elif not api_key:
            st.info("👈 왼쪽에서 Google API 키를 입력해주세요.")

    if st.button("🚀 디자인 프로세스 시작", type="primary", disabled=not ready):
        results = {}

        with st.spinner("파일 처리 중..."):
            file_parts = build_file_parts(uploaded_files)

        # 1단계: RFP 분석
        st.header("📋 1단계: RFP 분석")
        with st.expander("분석 결과", expanded=True):
            ph = st.empty()
            rfp_parts = [types.Part(text=RFP_INSTRUCTION)] + file_parts
            results["rfp"] = call_gemini_stream(
                api_key, SYSTEMS["rfp"], rfp_parts, model, ph
            )
        st.success("✅ RFP 분석 완료")

        # 2단계: 디자인 컨셉
        st.header("🎨 2단계: 디자인 방향성 및 컨셉")
        with st.expander("컨셉 결과", expanded=True):
            ph = st.empty()
            results["concept"] = call_gemini_stream(
                api_key, SYSTEMS["concept"],
                [types.Part(text=f"{CONCEPT_INSTRUCTION}\n\n---\n{results['rfp']}")],
                model, ph
            )
        st.success("✅ 컨셉 도출 완료")

        # 3단계: 키워드 & 무드보드
        st.header("🖼️ 3단계: 디자인 키워드 및 무드보드")
        with st.expander("키워드 결과", expanded=True):
            ph = st.empty()
            results["keywords"] = call_gemini_stream(
                api_key, SYSTEMS["keywords"],
                [types.Part(text=f"{KEYWORDS_INSTRUCTION}\n\n---\n{results['concept']}")],
                model, ph
            )
        st.success("✅ 키워드 및 무드보드 완료")

        # 4단계: 페르소나 & 조닝
        st.header("👥 4단계: 페르소나 & 조닝 계획")
        with st.expander("페르소나 & 조닝 결과", expanded=True):
            ph = st.empty()
            context = f"[RFP 분석]\n{results['rfp']}\n\n[디자인 컨셉]\n{results['concept']}"
            results["persona"] = call_gemini_stream(
                api_key, SYSTEMS["persona"],
                [types.Part(text=f"{PERSONA_INSTRUCTION}\n\n---\n{context}")],
                model, ph
            )
        st.success("✅ 페르소나 및 조닝 완료")

        # 5단계: Midjourney 프롬프트
        st.header("🎬 5단계: Midjourney 프롬프트")
        with st.expander("프롬프트 결과", expanded=True):
            ph = st.empty()
            context = f"[디자인 컨셉]\n{results['concept']}\n\n[조닝 계획]\n{results['persona']}"
            results["midjourney"] = call_gemini_stream(
                api_key, SYSTEMS["midjourney"],
                [types.Part(text=f"{MIDJOURNEY_INSTRUCTION}\n\n---\n{context}")],
                model, ph
            )
        st.success("✅ Midjourney 프롬프트 완료")

        # 보고서 저장
        st.header("📥 보고서 저장")
        report, timestamp = build_report(project_name, results)
        filename = f"{project_name.replace(' ', '_')}_{timestamp}.md"

        st.download_button(
            label="⬇️ 마크다운 보고서 다운로드 (.md)",
            data=report.encode("utf-8"),
            file_name=filename,
            mime="text/markdown",
            type="primary"
        )

        st.balloons()
        st.success(f"🎉 완료! `{filename}` 파일을 다운로드하세요.")

if __name__ == "__main__":
    main()
