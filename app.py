import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai
import os
import requests
import PyPDF2

# --- 1. CONFIGURAÇÃO GERAL ---
st.set_page_config(page_title="O Pregador", layout="wide", page_icon="✝️", initial_sidebar_state="expanded")

# --- 2. IMPORTAÇÃO E SEGURANÇA DE ARQUIVOS ---
try:
    from streamlit_lottie import st_lottie
    LOTTIE_OK = True
except ImportError:
    LOTTIE_OK = False

def load_lottie(url):
    if not LOTTIE_OK: return None
    try:
        r = requests.get(url, timeout=1.5)
        return r.json() if r.status_code == 200 else None
    except: return None

# Tenta carregar chave da API dos segredos do sistema automaticamente
API_KEY_AUTOMATICA = None
if "GOOGLE_API_KEY" in st.secrets:
    API_KEY_AUTOMATICA = st.secrets["GOOGLE_API_KEY"]

# --- 3. ESTILO VISUAL PROFISSIONAL (DARK CLEAN) ---
st.markdown("""
<style>
/* Reset */
header, footer {visibility: hidden;}
.block-container {padding-top: 1rem; padding-bottom: 0rem; max-width: 98%;}

/* Cores Principais */
.stApp {background-color: #111111;} /* Preto quase total */

/* Barra Lateral */
[data-testid="stSidebar"] {
    background-color: #1a1a1a;
    border-right: 1px solid #333;
}

/* O Editor de Texto */
.stTextArea textarea {
    font-family: 'Georgia', serif;
    font-size: 19px !important;
    line-height: 1.6 !important;
    background-color: #202020;
    color: #e0e0e0;
    border: 1px solid #333;
    padding: 15px;
    border-radius: 4px;
}
.stTextArea textarea:focus {
    border-color: #C5A059; /* Dourado suave */
}

/* Botões */
.stButton button {
    border-radius: 4px;
    font-weight: 600;
    background-color: #2b2b2b;
    color: white;
    border: 1px solid #444;
}
.stButton button:hover {
    border-color: #C5A059;
    color: #C5A059;
}

/* Abas */
.stTabs [aria-selected="true"] {
    background-color: #C5A059 !important;
    color: #000 !important;
}
</style>
""", unsafe_allow_html=True)

# --- 4. LOGIN ---
USUARIOS = {"admin": "1234", "pastor": "pregar", "obreiro":"jesus"}

def tela_login():
    if 'logado' not in st.session_state:
        st.session_state['logado'] = False
        st.session_state['user'] = ''
        
    if not st.session_state['logado']:
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("<h1 style='text-align: center'>✝️ O Pregador</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #888'>Ferramenta de Estudos Expositivos</p>", unsafe_allow_html=True)
            
            with st.form("frm_login"):
                u = st.text_input("Usuário")
                s = st.text_input("Senha", type="password")
                if st.form_submit_button("Entrar", type="primary"):
                    if u in USUARIOS and USUARIOS[u] == s:
                        st.session_state['logado'] = True
                        st.session_state['user'] = u
                        st.rerun()
                    else: st.error("Dados incorretos.")
        return False
    return True

if not tela_login(): st.stop()

# --- 5. LÓGICA DO SISTEMA ---
USER = st.session_state['user']
PASTA = os.path.join("Banco_Sermoes", USER)
if not os.path.exists(PASTA): os.makedirs(PASTA)

