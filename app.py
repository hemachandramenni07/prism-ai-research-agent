import streamlit as st
import requests
import html
import re
from main import research


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Prism",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# RELEVANT IMAGE
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def get_relevant_image(search_query: str, max_results: int = 15):
    """
    Find one clean representative image from Wikimedia Commons.

    The function deliberately avoids newspaper screenshots, logos,
    posters, charts, maps, collages and other non-representative
    images. It returns the best matching image or None.
    """

    if not search_query or not search_query.strip():
        return None

    try:
        url = "https://commons.wikimedia.org/w/api.php"

        params = {
            "action": "query",
            "generator": "search",
            "gsrsearch": search_query,
            "gsrnamespace": 6,
            "gsrlimit": max_results,
            "prop": "imageinfo",
            "iiprop": "url|mime|size|extmetadata",
            "iiurlwidth": 1400,
            "format": "json",
        }

        response = requests.get(
            url,
            params=params,
            timeout=12,
            headers={
                "User-Agent": (
                    "AI-Research-Agent/1.0 "
                    "(research application)"
                )
            },
        )
        response.raise_for_status()

        pages = (
            response.json()
            .get("query", {})
            .get("pages", {})
        )

        unwanted_words = {
            "newspaper",
            "screenshot",
            "screen shot",
            "article",
            "headline",
            "poster",
            "advertisement",
            "advert",
            "logo",
            "map",
            "chart",
            "graph",
            "diagram",
            "document",
            "report",
            "magazine",
            "thumbnail",
            "collage",
            "infographic",
            "ticket",
            "schedule",
            "table",
            "flag",
        }

        query_words = [
            word.lower()
            for word in re.findall(
                r"[a-zA-Z0-9]+",
                search_query,
            )
            if len(word) > 2
        ]

        candidates = []

        for page in pages.values():
            title = page.get("title", "")
            title_lower = title.lower()

            if any(
                bad_word in title_lower
                for bad_word in unwanted_words
            ):
                continue

            image_info = page.get("imageinfo", [])
            if not image_info:
                continue

            info = image_info[0]
            mime = info.get("mime", "")

            if not mime.startswith("image/"):
                continue

            image_url = (
                info.get("thumburl")
                or info.get("url")
            )

            if not image_url:
                continue

            width = info.get("width", 0) or 0
            height = info.get("height", 0) or 0

            if width < 500 or height < 300:
                continue

            clean_title = (
                title
                .replace("File:", "")
                .strip()
                .lower()
            )

            score = 0

            for word in query_words:
                if word in clean_title:
                    score += 10

            if width >= 1200:
                score += 4
            elif width >= 900:
                score += 2

            if height >= 700:
                score += 3

            if width > 0 and height > 0:
                aspect_ratio = width / height

                # Prefer normal landscape photographs.
                if 1.25 <= aspect_ratio <= 2.2:
                    score += 5

            candidates.append(
                {
                    "url": image_url,
                    "title": title.replace("File:", "").strip(),
                    "score": score,
                }
            )

        if not candidates:
            return None

        candidates.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return candidates[0]

    except Exception:
        # Image failure must never stop the research application.
        return None


def build_image_query(topic: str, user_query: str) -> str:
    """
    Build a conservative image query.

    For a person/topic such as Cristiano Ronaldo, this tends to
    request a clean portrait/action photograph instead of news
    screenshots. For other topics it uses the research topic.
    """

    text = f"{topic} {user_query}".lower()

    if "cristiano ronaldo" in text or "ronaldo" in text:
        return "Cristiano Ronaldo football"

    if "lionel messi" in text or "messi" in text:
        return "Lionel Messi football"

    return topic


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       GLOBAL
       ======================================================== */

    .stApp {
        background:
            radial-gradient(
                circle at 8% 15%,
                rgba(105, 65, 235, 0.22),
                transparent 32%
            ),
            radial-gradient(
                circle at 92% 18%,
                rgba(0, 195, 220, 0.17),
                transparent 32%
            ),
            radial-gradient(
                circle at 78% 82%,
                rgba(190, 70, 210, 0.15),
                transparent 35%
            ),
            linear-gradient(
                135deg,
                #080A12 0%,
                #0B101C 48%,
                #080B13 100%
            );

        min-height: 100vh;
        color: #E9EDF5;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 45px;
        padding-bottom: 100px;
    }


    /* ========================================================
       PRISM ICE CUBE
       ======================================================== */

    .prism-title-row {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 18px;
        margin-top: 4px;
        margin-bottom: 8px;
    }

    .ice-cube-wrap {
        width: 58px;
        height: 58px;
        perspective: 420px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex: 0 0 auto;
    }

    .ice-cube {
        width: 42px;
        height: 42px;
        position: relative;
        transform-style: preserve-3d;
        will-change: transform;
        animation:
            iceRevolve 7s linear infinite,
            iceFloat 3.2s ease-in-out infinite;
        filter:
            drop-shadow(0 0 7px rgba(150, 235, 255, 0.65))
            drop-shadow(0 0 18px rgba(100, 170, 255, 0.38));
    }

    .ice-face {
        position: absolute;
        width: 42px;
        height: 42px;
        border: 1px solid rgba(215, 250, 255, 0.78);
        background:
            linear-gradient(
                135deg,
                rgba(220, 250, 255, 0.72),
                rgba(105, 205, 255, 0.32) 45%,
                rgba(120, 130, 255, 0.20)
            );
        box-shadow:
            inset 0 0 14px rgba(225, 250, 255, 0.24);
        backdrop-filter: blur(2px);
    }

    .ice-front  { transform: translateZ(21px); }
    .ice-back   { transform: rotateY(180deg) translateZ(21px); }
    .ice-right  { transform: rotateY(90deg) translateZ(21px); }
    .ice-left   { transform: rotateY(-90deg) translateZ(21px); }
    .ice-top    { transform: rotateX(90deg) translateZ(21px); }
    .ice-bottom { transform: rotateX(-90deg) translateZ(21px); }

    .ice-spark {
        position: absolute;
        width: 4px;
        height: 4px;
        border-radius: 50%;
        background: #d9fbff;
        box-shadow: 0 0 9px #9eefff;
        animation: iceSpark 2.4s ease-in-out infinite;
    }

    .ice-spark.one {
        top: 5px;
        right: 2px;
    }

    .ice-spark.two {
        bottom: 3px;
        left: 1px;
        animation-delay: 0.8s;
    }

    .ice-spark.three {
        top: 26px;
        left: -6px;
        animation-delay: 1.5s;
    }

    @keyframes iceRevolve {
        0% {
            transform: rotateX(-16deg) rotateY(0deg) rotateZ(2deg);
        }
        25% {
            transform: rotateX(8deg) rotateY(90deg) rotateZ(-1deg);
        }
        50% {
            transform: rotateX(-10deg) rotateY(180deg) rotateZ(2deg);
        }
        75% {
            transform: rotateX(10deg) rotateY(270deg) rotateZ(-1deg);
        }
        100% {
            transform: rotateX(-16deg) rotateY(360deg) rotateZ(2deg);
        }
    }

    @keyframes iceFloat {
        0%, 100% {
            translate: 0 3px;
        }
        50% {
            translate: 0 -6px;
        }
    }

    @keyframes iceSpark {
        0%, 100% {
            opacity: 0.25;
            transform: scale(0.7);
        }
        50% {
            opacity: 1;
            transform: scale(1.35);
        }
    }

    @media (prefers-reduced-motion: reduce) {
        .ice-cube {
            animation: none;
            transform: rotateX(-12deg) rotateY(-25deg) rotateZ(2deg);
        }

        .ice-spark {
            animation: none;
            opacity: 0.7;
        }
    }

    /* ========================================================
       HERO
       ======================================================== */

    .hero-title {
        text-align: center;
        font-size: 48px;
        font-weight: 750;
        letter-spacing: -1.5px;
        margin-bottom: 8px;

        background:
            linear-gradient(
                90deg,
                #FFFFFF,
                #9DEAFF,
                #B9A8FF,
                #FFFFFF
            );

        background-size: 250% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;

        animation:
            titleGradient 9s ease infinite;
    }

    @keyframes titleGradient {
        0% {
            background-position: 0% center;
        }

        50% {
            background-position: 100% center;
        }

        100% {
            background-position: 0% center;
        }
    }

    .hero-subtitle {
        text-align: center;
        color: #8F9BAD;
        font-size: 16px;
        margin-bottom: 42px;
    }

    /* ========================================================
       INPUT
       ======================================================== */

    .search-label {
        color: #CBD4E2;
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 8px;
    }

    textarea {
        background: rgba(8, 11, 18, 0.90) !important;
        color: #E8EDF5 !important;
        border: 1px solid rgba(120, 140, 180, 0.25) !important;
        border-radius: 12px !important;
        font-size: 16px !important;
        line-height: 1.65 !important;
    }

    textarea:focus {
        border-color: #7887FF !important;
        box-shadow:
            0 0 0 1px #7887FF,
            0 0 28px rgba(110, 125, 255, 0.16) !important;
    }

    div.stButton > button {
        height: 50px;
        border-radius: 10px;
        border: 1px solid rgba(125, 140, 255, 0.55);
        background:
            linear-gradient(
                90deg,
                #4658C8,
                #6171E7
            );
        color: white;
        font-size: 15px;
        font-weight: 650;
        box-shadow:
            0 8px 25px rgba(70, 80, 190, 0.22);
        transition: all 0.25s ease;
    }

    div.stButton > button:hover {
        transform: translateY(-2px);
        border-color: #95A2FF;
        box-shadow:
            0 10px 32px rgba(80, 95, 220, 0.30);
    }

    /* ========================================================
       SECTIONS
       ======================================================== */

    .section-title {
        color: #E0E7F2;
        font-size: 23px;
        font-weight: 650;
        margin-top: 42px;
        margin-bottom: 12px;
    }

    .section-line {
        height: 1px;
        background:
            linear-gradient(
                90deg,
                rgba(120, 140, 180, 0.35),
                rgba(120, 140, 180, 0.04),
                transparent
            );
        margin-bottom: 20px;
    }

    /* ========================================================
       TOPIC
       ======================================================== */

    .topic-box {
        background:
            linear-gradient(
                135deg,
                rgba(29, 36, 56, 0.80),
                rgba(15, 20, 32, 0.78)
            );
        border: 1px solid rgba(120, 145, 190, 0.22);
        border-radius: 14px;
        padding: 22px 25px;
        color: #EDF1F7;
        font-size: 23px;
        font-weight: 650;
        line-height: 1.45;
        overflow-wrap: anywhere;
    }

    /* ========================================================
       IMAGE
       ======================================================== */

    .image-caption {
        color: #7F8A9C;
        font-size: 12px;
        margin-top: 7px;
        text-align: center;
    }

    [data-testid="stImage"] {
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid rgba(120, 140, 180, 0.20);
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.22);
    }

    /* ========================================================
       SUMMARY
       ======================================================== */

    .summary-card {
        background:
            linear-gradient(
                135deg,
                rgba(20, 27, 42, 0.94),
                rgba(13, 18, 29, 0.92)
            );

        border-left: 3px solid #7283FF;
        border-radius: 12px;
        padding: 24px 28px;
        color: #C9D2DF;
        font-size: 17px;
        line-height: 1.9;
        box-shadow: 0 10px 32px rgba(0, 0, 0, 0.16);
        overflow-wrap: anywhere;
        word-break: normal;
    }

    .summary-card > div:last-child {
        color: #C9D2DF;
        font-size: 17px;
        line-height: 1.9;
        overflow-wrap: anywhere;
        white-space: normal;
    }

    .summary-label {
        color: #AAB8FF;
        font-size: 14px;
        font-weight: 650;
        margin-bottom: 14px;
    }

    /* ========================================================
       SOURCES
       ======================================================== */

    .source-item {
        background: rgba(18, 24, 36, 0.72);
        border: 1px solid rgba(110, 130, 165, 0.16);
        border-radius: 10px;
        padding: 15px 20px;
        margin-bottom: 10px;
    }

    .source-number {
        color: #8795FF;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1px;
        margin-bottom: 5px;
    }

    .source-name {
        color: #D1D8E4;
        font-size: 15px;
        line-height: 1.55;
        overflow-wrap: anywhere;
    }

    /* ========================================================
       TOOLS
       ======================================================== */

    .tool-item {
        display: inline-block;
        background: rgba(38, 45, 66, 0.72);
        border: 1px solid rgba(110, 125, 190, 0.25);
        border-radius: 7px;
        padding: 7px 12px;
        margin-right: 7px;
        margin-bottom: 7px;
        color: #BBC6D9;
        font-size: 13px;
    }

    /* ========================================================
       REPORT
       ======================================================== */

    div[data-testid="stExpander"] {
        background: rgba(12, 17, 27, 0.72);
        border: 1px solid rgba(115, 135, 175, 0.20);
        border-radius: 13px;
        overflow: hidden;
    }

    .report-content {
        padding: 15px 22px 25px 22px;
    }

    .report-content p {
        color: #C8D1DE;
        font-size: 16px;
        line-height: 2.0;
        margin-bottom: 22px;
    }

    .report-content h1,
    .report-content h2,
    .report-content h3 {
        color: #E5EBF4;
        margin-top: 34px;
        margin-bottom: 16px;
    }

    /* ========================================================
       DOWNLOAD
       ======================================================== */

    div.stDownloadButton > button {
        height: 46px;
        border-radius: 9px;
        background: rgba(30, 37, 52, 0.90);
        border: 1px solid rgba(120, 140, 175, 0.25);
        color: #D1D9E5;
        font-weight: 550;
    }

    div.stDownloadButton > button:hover {
        background: rgba(44, 52, 72, 0.95);
        border-color: #7583B2;
        color: white;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HERO
# ============================================================

st.markdown(
    '''
    <div class="prism-title-row">
        <div class="ice-cube-wrap">
            <div class="ice-cube">
                <div class="ice-face ice-front"></div>
                <div class="ice-face ice-back"></div>
                <div class="ice-face ice-right"></div>
                <div class="ice-face ice-left"></div>
                <div class="ice-face ice-top"></div>
                <div class="ice-face ice-bottom"></div>
                <span class="ice-spark one"></span>
                <span class="ice-spark two"></span>
                <span class="ice-spark three"></span>
            </div>
        </div>
        <div class="hero-title">Prism</div>
    </div>
    ''',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="hero-subtitle">'
    'Research. Analyze. Understand.'
    '</div>',
    unsafe_allow_html=True,
)


# ============================================================
# INPUT
# ============================================================

st.markdown(
    '<div class="search-label">Research question</div>',
    unsafe_allow_html=True,
)

query = st.text_area(
    "Research question",
    label_visibility="collapsed",
    placeholder="Ask anything you want to research...",
    height=120,
)

research_button = st.button(
    "🔎  Start Research",
    type="primary",
    use_container_width=True,
)


# ============================================================
# RUN RESEARCH
# ============================================================

if research_button:

    if not query.strip():
        st.warning("Please enter a research question.")

    else:
        # Clear the previous result so an old research result
        # cannot remain visible while a new one is running.
        st.session_state.pop("research_response", None)

        with st.spinner(
            "Researching, analyzing and preparing your report..."
        ):
            try:
                result = research(query.strip())

                # main.py is expected to return a dictionary.
                if not isinstance(result, dict):
                    raise TypeError(
                        "research() must return a dictionary."
                    )

                required_keys = {
                    "topic",
                    "summary",
                    "detailed_report",
                    "sources",
                    "tools_used",
                    "save_result",
                    "filename",
                }

                missing_keys = required_keys - set(result.keys())

                if missing_keys:
                    raise KeyError(
                        "research() is missing: "
                        + ", ".join(sorted(missing_keys))
                    )

                st.session_state["research_response"] = result

            except Exception as exc:
                st.error(
                    f"Research failed: {exc}"
                )


# ============================================================
# DISPLAY RESULT
# ============================================================

if "research_response" in st.session_state:

    response = st.session_state["research_response"]

    topic = str(response.get("topic", "Untitled Research"))
    summary = str(response.get("summary", ""))
    detailed_report = str(
        response.get("detailed_report", "")
    )
    sources = response.get("sources", []) or []
    tools_used = response.get("tools_used", []) or []
    filename = str(response.get("filename", "research.txt"))
    save_result = str(
        response.get("save_result", "")
    )

    # ========================================================
    # RELEVANT IMAGE
    # ========================================================

    image_query = build_image_query(
        topic,
        query,
    )

    image_result = get_relevant_image(
        image_query
    )

    if image_result:
        st.image(
            image_result["url"],
            use_container_width=True,
        )

        st.markdown(
            '<div class="image-caption">'
            'Representative image • Wikimedia Commons'
            '</div>',
            unsafe_allow_html=True,
        )

    # ========================================================
    # TOPIC
    # ========================================================

    st.markdown(
        '<div class="section-title">📌 Topic</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-line"></div>',
        unsafe_allow_html=True,
    )

    # Use Streamlit text rendering instead of putting model
    # content directly into HTML. This prevents HTML/code from
    # appearing accidentally and keeps long text wrapped.
    safe_topic_html = html.escape(topic).replace("\n", "<br>")

    st.markdown(
        f'<div class="topic-box">{safe_topic_html}</div>',
        unsafe_allow_html=True,
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    st.markdown(
        '<div class="section-title">📝 Research Summary</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-line"></div>',
        unsafe_allow_html=True,
    )

    # Escape model text before placing it in custom HTML.
    # This prevents accidental HTML/code from breaking the layout.
    safe_summary_html = (
        html.escape(summary)
        .replace("\n\n", "<br><br>")
        .replace("\n", "<br>")
    )

    st.markdown(
        f"""
        <div class="summary-card">
            <div class="summary-label">🧠 Key Finding</div>
            <div>{safe_summary_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ========================================================
    # SOURCES
    # ========================================================

    st.markdown(
        '<div class="section-title">📚 Sources</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-line"></div>',
        unsafe_allow_html=True,
    )

    if sources:
        for index, source in enumerate(
            sources,
            start=1,
        ):
            safe_source = html.escape(
                str(source)
            )

            st.markdown(
                f"""
                <div class="source-item">
                    <div class="source-number">
                        SOURCE {index}
                    </div>
                    <div class="source-name">
                        {safe_source}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.caption(
            "No sources were reported by the research agent."
        )

    # ========================================================
    # TOOLS USED
    # ========================================================

    st.markdown(
        '<div class="section-title">🛠️ Tools Used</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-line"></div>',
        unsafe_allow_html=True,
    )

    if tools_used:
        for tool_name in tools_used:
            safe_tool = html.escape(
                str(tool_name)
            )

            st.markdown(
                f"""
                <span class="tool-item">
                    🔧 {safe_tool}
                </span>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.caption("No tools were reported.")

    # ========================================================
    # DETAILED RESEARCH
    # ========================================================

    st.markdown(
        '<div class="section-title">📖 Detailed Research</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-line"></div>',
        unsafe_allow_html=True,
    )

    with st.expander(
        "📄 Open Full Research Report",
        expanded=True,
    ):
        st.markdown(
            '<div class="report-content">',
            unsafe_allow_html=True,
        )

        # Markdown rendering allows the model's headings and
        # paragraphs to remain properly formatted.
        st.markdown(
            detailed_report
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True,
        )

    # ========================================================
    # RESEARCH FILE
    # ========================================================

    st.markdown(
        '<div class="section-title">💾 Research File</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-line"></div>',
        unsafe_allow_html=True,
    )

    st.caption(
        f"Saved as: {filename}"
    )

    st.download_button(
        label="⬇️ Download Research",
        data=detailed_report,
        file_name=filename,
        mime="text/plain",
        use_container_width=True,
    )

    if save_result:
        st.success(save_result)
