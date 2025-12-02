import streamlit as st
import json
import os
import requests
import PyPDF2
from gtts import gTTS
import tempfile

# --- 1. STATE & CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="O Pregador", layout="wide", page_icon="🧷", initial_sidebar_state="expanded")

# Inicializar Variáveis de Personalização
if 'layout_split' not in st.session_state: st.session_state['layout_split'] = 60 # 60% Editor
if 'bg_url' not in st.session_state: st.session_state['bg_url'] = "https://images.unsplash.com/photo-1497294815431-9365093b7331?q=80&w=2070&auto=format&fit=crop" # Fundo Clean
if 'blur_level' not in st.session_state: st.session_state['blur_level'] = 20

# Importação Segura
try:
    from duckduckgo_search import DDGS
    import google.generativeai as genai
except: pass

# --- 2. APPLE DESIGN SYSTEM (CSS AVANÇADO) ---
st.markdown(f"""
<style>
    /* FONTE APPLE SF PRO (Similar) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    /* WALLPAPER PERSONALIZÁVEL */
    [data-testid="stAppViewContainer"] {{
        background-image: url("{st.session_state['bg_url']}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    /* MODAL DE VIDRO (GLASSMORPHISM) */
    [data-testid="stSidebar"], .stTextArea textarea, .block-container, div[data-testid="stExpander"] {{
        background: rgba(20, 20, 30, 0.75) !important;
        backdrop-filter: blur({st.session_state['blur_level']}px);
        -webkit-backdrop-filter: blur({st.session_state['blur_level']}px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
    }}

    /* REMOVER PADS */
    .block-container {{padding-top: 1.5rem; max-width: 95%;}}
    header, footer {{visibility: hidden;}}

    /* BARRA LATERAL ESTILO MAC */
    [data-testid="stSidebar"] {{
        border-right: 1px solid rgba(255, 255, 255, 0.05);
        margin: 10px;
        height: 98vh;
    }}

    /* TEXT AREAS PREMIUM */
    .stTextArea textarea {{
        color: #f1f1f1;
        font-size: 17px;
        line-height: 1.6;
        padding: 20px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
    }}
    .stTextArea textarea:focus {{
        border-color: #0A84FF; /* Apple Blue */
        box-shadow: 0 0 15px rgba(10, 132, 255, 0.3);
    }}

    /* BOTÕES IOS STYLE */
    .stButton button {{
        background-color: rgba(255,255,255,0.1);
        color: white;
        border-radius: 10px;
        border: none;
        font-weight: 500;
        transition: 0.2s;
        padding: 8px 16px;
    }}
    .stButton button:hover {{
        background-color: #0A84FF;
        color: white;
        transform: scale(1.02);
    }}

    /* TÍTULO COM O PREGADOR */
    .brand-title {{
        font-size: 28px;
        font-weight: 800;
        background: -webkit-linear-gradient(#fff, #aaa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }}
    
    /* SLIDERS E CONFIGURAÇÕES */
    .stSlider {{ padding-bottom: 20px; }}

</style>
""", unsafe_allow_html=True)

# --- 3. LÓGICA DO SISTEMA ---

# Sessão do Usuário
if 'texto_ativo' not in st.session_state: st.session_state['texto_ativo'] = ""
if 'titulo_ativo' not in st.session_state: st.session_state['titulo_ativo'] = ""

# Funções Backend
def gemini_pro(prompt, key, system=""):
    if not key: return "⚠️ Configurações > Adicionar Chave API."
    try:
        genai.configure(api_key=key)
        return genai.GenerativeModel('gemini-1.5-flash').generate_content(f"{system}\n\n{prompt}").text
    except Exception as e: return f"Erro: {e}"

def buscar_biblia(ref):
    try:
        r = requests.get(f"https://bible-api.com/{ref}?translation=almeida", timeout=2)
        if r.status_code == 200: return r.json()
    except: return None

# --- 4. TELA DE LOGIN CLEAN ---
def login():
    if 'logado' not in st.session_state: st.session_state['logado'] = False
    
    if not st.session_state['logado']:
        c1,c2,c3 = st.columns([1,2,1])
        with c2:
            st.markdown("<br><br><br>", unsafe_allow_html=True)
            # O LOGO PREGADOR 🧷
            st.markdown("<h1 style='text-align:center; font-size: 60px'>🧷</h1>", unsafe_allow_html=True)
            st.markdown("<h2 style='text-align:center;'>O PREGADOR</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align:center; color:#888'>Entre na sua área de trabalho</p>", unsafe_allow_html=True)
            
            with st.form("apple_login"):
                u = st.text_input("ID Apple/User")
                p = st.text_input("Password", type="password")
                if st.form_submit_button("Entrar", type="primary"):
                    if (u=="admin" and p=="1234") or (u=="pastor" and p=="pregar"):
                        st.session_state['user'] = u
                        st.session_state['logado'] = True
                        st.rerun()
                    else: st.error("Incorreto.")
        return False
    return True

if not login(): st.stop()

# --- 5. INTERFACE PRINCIPAL ---

# 5.1 BARRA LATERAL (SETTINGS & ARQUIVOS)
USER = st.session_state['user']
PASTA = os.path.join("Banco_Sermoes", USER)
if not os.path.exists(PASTA): os.makedirs(PASTA)

with st.sidebar:
    st.markdown(f"<div class='brand-title'>🧷 PREGADOR</div>", unsafe_allow_html=True)
    st.caption(f"Usuário: {USER}")
    
    tab_files, tab_settings = st.tabs(["📂 Arquivos", "⚙️ Ajustes"])
    
    with tab_files:
        try: docs = [f.replace(".txt","") for f in os.listdir(PASTA) if f.endswith(".txt")]
        except: docs = []
        sel = st.radio("Biblioteca:", ["+ Novo Projeto"] + docs)
        if st.button("Sair"):
            st.session_state['logado'] = False
            st.rerun()

    with tab_settings:
        st.write("**Visual**")
        # CONTROLE DE LAYOUT (O USUÁRIO DECIDE O TAMANHO)
        split_val = st.slider("Tamanho do Editor", 30, 80, st.session_state['layout_split'])
