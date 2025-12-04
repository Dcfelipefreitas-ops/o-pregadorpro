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

    :root {{
        --gold: {theme_color};
        --gold-dim: {theme_color}40;
        --bg-dark: #070707;
        --card-bg: #0e0e0e;
        --muted: #bdb6a8;
        --font-body: '{font_main}', Inter, sans-serif;
        --font-head: 'Cinzel', serif;
    }}

    .stApp {{
        background-color: var(--bg-dark);
        color: var(--muted);
        font-family: var(--font-body);
    }}

    h1, h2, h3, h4 {{
        font-family: var(--font-head) !important;
        color: var(--gold) !important;
        letter-spacing: 0.8px;
    }}

    .tech-card {{
        background: linear-gradient(180deg, rgba(18,18,18,0.9), rgba(12,12,12,0.8));
        border: 1px solid #1a1a1a;
        padding: 16px;
        border-radius: 8px;
    }}

    .prime-logo {{
        width: 120px; height: 120px; display:block; margin:0 auto 12px auto;
        filter: drop-shadow(0 0 6px var(--gold-dim));
    }}

    .login-container {{
        text-align:center; padding:28px; border-radius:10px;
        background: linear-gradient(180deg, rgba(10,10,10,0.6), rgba(5,5,5,0.6));
        border-top: 3px solid var(--gold);
    }}

    .stButton>button {{
        border: 1px solid var(--gold);
        color: var(--gold);
        background: transparent;
        padding: 0.4rem;
    }}
    .stButton>button:hover {{ background: var(--gold); color:#111; }}

    /* less aggressive glows */
    .stButton>button, .tech-card {{ box-shadow: none; }}

    </style>
    """
    st.markdown(css, unsafe_allow_html=True)