import streamlit as st
from .core import _read_json_safe, DB_FILES
from .utils import TextUtils


def inject_visual_core():
    cfg = _read_json_safe(DB_FILES["CONFIG"])
    theme_color = cfg.get("theme_color", "#D4AF37")
    font_main = TextUtils.normalize_font(cfg.get("font_family", "Inter"))

    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Inter:wght@300;400;600&display=swap');

    /* ==========================================================
       01. VARIÁVEIS DE TEMA
       ========================================================== */
    :root {{
        --gold: {theme_color};
        --gold-dim: {theme_color}40;
        --gold-soft: {theme_color}22;
        --gold-hover: {theme_color}CC;

        --bg-dark: #070707;
        --bg-elevated: #111111;
        --card-bg: #0e0e0e;
        --card-bg-hover: #131313;
        --border-subtle: #1a1a1a;
        --border-strong: #262626;

        --text-main: #e8e3d8;
        --muted: #bdb6a8;
        --muted-dim: #8a8478;

        --font-body: '{font_main}', Inter, sans-serif;
        --font-head: 'Cinzel', serif;

        --radius-sm: 6px;
        --radius-md: 10px;
        --radius-lg: 14px;

        --shadow-card: 0 4px 14px rgba(0, 0, 0, 0.45);
        --shadow-button: 0 2px 6px rgba(0, 0, 0, 0.5);
        --shadow-button-hover: 0 4px 14px var(--gold-dim);
    }}

    /* ==========================================================
       02. BASE / ESTRUTURA
       ========================================================== */
    .stApp {{
        background-color: var(--bg-dark);
        color: var(--muted);
        font-family: var(--font-body);
    }}

    .main .block-container {{
        padding-top: 2rem;
    }}

    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    ::-webkit-scrollbar-track {{
        background: var(--bg-dark);
    }}
    ::-webkit-scrollbar-thumb {{
        background: var(--border-strong);
        border-radius: 8px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: var(--gold-dim);
    }}

    /* ==========================================================
       03. TIPOGRAFIA
       ========================================================== */
    h1, h2, h3, h4 {{
        font-family: var(--font-head) !important;
        color: var(--gold) !important;
        letter-spacing: 0.8px;
    }}

    h1 {{ border-bottom: 1px solid var(--border-subtle); padding-bottom: 0.4rem; }}

    p, span, label, .stMarkdown {{
        color: var(--text-main);
    }}

    a {{ color: var(--gold); }}
    a:hover {{ color: var(--gold-hover); }}

    /* ==========================================================
       04. BOTÕES — visual mais realista (profundidade, hover, clique)
       ========================================================== */
    .stButton > button {{
        position: relative;
        border: 1px solid var(--gold-dim);
        color: var(--gold);
        background: linear-gradient(180deg, #161616 0%, #0c0c0c 100%);
        padding: 0.5rem 1.1rem;
        border-radius: var(--radius-sm);
        font-weight: 600;
        letter-spacing: 0.3px;
        box-shadow: var(--shadow-button), inset 0 1px 0 rgba(255, 255, 255, 0.04);
        transition: transform 0.12s ease, box-shadow 0.18s ease,
                    background 0.18s ease, border-color 0.18s ease, color 0.18s ease;
    }}

    .stButton > button:hover {{
        background: linear-gradient(180deg, var(--gold) 0%, var(--gold-hover) 100%);
        color: #14110a;
        border-color: var(--gold);
        box-shadow: var(--shadow-button-hover), inset 0 1px 0 rgba(255, 255, 255, 0.15);
        transform: translateY(-1px);
    }}

    .stButton > button:active {{
        transform: translateY(0px);
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.6), inset 0 1px 3px rgba(0, 0, 0, 0.4);
    }}

    .stButton > button:focus:not(:active) {{
        outline: none;
        box-shadow: 0 0 0 2px var(--gold-soft), var(--shadow-button);
    }}

    .stButton > button:disabled {{
        opacity: 0.4;
        box-shadow: none;
        transform: none;
    }}

    /* Botão de submit dentro de formulários — leve destaque para diferenciar */
    .stFormSubmitButton > button {{
        border: 1px solid var(--gold);
        background: linear-gradient(180deg, #1a1608 0%, #0c0c0c 100%);
    }}

    /* ==========================================================
       05. CAMPOS DE ENTRADA (text_input, text_area, selectbox, etc.)
       ========================================================== */
    .stTextInput > div > div > input,
    .stTextArea textarea,
    .stNumberInput input,
    .stDateInput input {{
        background-color: var(--bg-elevated) !important;
        color: var(--text-main) !important;
        border: 1px solid var(--border-strong) !important;
        border-radius: var(--radius-sm) !important;
    }}

    .stTextInput > div > div > input:focus,
    .stTextArea textarea:focus {{
        border-color: var(--gold) !important;
        box-shadow: 0 0 0 1px var(--gold-dim) !important;
    }}

    .stSelectbox > div > div,
    .stMultiSelect > div > div {{
        background-color: var(--bg-elevated) !important;
        border: 1px solid var(--border-strong) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-main) !important;
    }}

    /* Slider / select_slider */
    .stSlider [data-baseweb="slider"] > div > div {{
        background: var(--gold-dim) !important;
    }}

    /* Checkbox e radio */
    .stCheckbox label, .stRadio label {{
        color: var(--text-main) !important;
    }}

    /* ==========================================================
       06. CARDS / CONTAINERS
       ========================================================== */
    .tech-card {{
        background: linear-gradient(180deg, rgba(18, 18, 18, 0.9), rgba(12, 12, 12, 0.8));
        border: 1px solid var(--border-subtle);
        padding: 18px;
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-card);
        transition: border-color 0.18s ease, transform 0.18s ease;
    }}

    .tech-card:hover {{
        border-color: var(--gold-dim);
    }}

    .login-container {{
        text-align: center;
        padding: 32px;
        border-radius: var(--radius-lg);
        background: linear-gradient(180deg, rgba(10, 10, 10, 0.6), rgba(5, 5, 5, 0.6));
        border-top: 3px solid var(--gold);
        box-shadow: var(--shadow-card);
    }}

    .prime-logo {{
        width: 120px;
        height: 120px;
        display: block;
        margin: 0 auto 12px auto;
        filter: drop-shadow(0 0 6px var(--gold-dim));
    }}

    /* ==========================================================
       07. SIDEBAR
       ========================================================== */
    [data-testid="stSidebar"] {{
        background-color: var(--bg-elevated);
        border-right: 1px solid var(--border-subtle);
    }}

    [data-testid="stSidebar"] * {{
        color: var(--text-main);
    }}

    /* ==========================================================
       08. ABAS (st.tabs)
       ========================================================== */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
        border-bottom: 1px solid var(--border-subtle);
    }}

    .stTabs [data-baseweb="tab"] {{
        background-color: transparent;
        color: var(--muted-dim);
        border-radius: var(--radius-sm) var(--radius-sm) 0 0;
        padding: 8px 16px;
    }}

    .stTabs [aria-selected="true"] {{
        color: var(--gold) !important;
        border-bottom: 2px solid var(--gold) !important;
    }}

    /* ==========================================================
       09. EXPANDER
       ========================================================== */
    .streamlit-expanderHeader, [data-testid="stExpander"] summary {{
        background-color: var(--card-bg) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-main) !important;
    }}

    /* ==========================================================
       10. ALERTAS (success / error / warning / info)
       ========================================================== */
    div[data-testid="stAlert"] {{
        border-radius: var(--radius-sm);
        border: 1px solid var(--border-subtle);
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
