import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai
import os
import requests
import time

# --- TENTA IMPORTAR ANIMAÇÕES (SEM TRAVAR O APP) ---
try:
    from streamlit_lottie import st_lottie
    LOTTIE_OK = True
except ImportError:
    LOTTIE_OK = False

# --- 1. CONFIGURAÇÃO GERAL ---
st.set_page_config(page_title="O Pregador", layout="wide", page_icon="✝️")

# --- 2. SISTEMA DE LOGIN (ENTRADA LEGAL) ---
USUARIOS = {
    "admin": "1234",
    "pastor": "pregar",
    "visitante": "jesus"
}

def load_lottie_url(url):
    """Tenta baixar a animação. Se falhar, retorna None mas não trava o app."""
    if not LOTTIE_OK: return None
    try:
        r = requests.get(url, timeout=1.5)
        if r.status_code != 200: return None
        return r.json()
    except:
        return None

# Carrega animação da entrada
anim_entrada = load_lottie_url("https://lottie.host/5a666e37-d2c4-4a47-98d9-247544062a4d/lB6y7y6a1W.json")
anim_ia = load_lottie_url("https://lottie.host/93310461-1250-482f-87d9-482a46696d5b/6u0v8v5j2a.json")

def verificar_login():
    """Tela de Login com Design Bonito"""
    if 'logado' not in st.session_state:
        st.session_state['logado'] = False
        st.session_state['usuario_atual'] = ''

    if not st.session_state['logado']:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.write("")
            st.write("")
            # SE A ANIMAÇÃO CARREGOU, MOSTRA ELA. SE NÃO, MOSTRA TEXTO.
            if anim_entrada:
                st_lottie(anim_entrada, height=150, key="intro")
            else:
                st.markdown("<h1 style='text-align: center;'>✝️</h1>", unsafe_allow_html=True)
            
            st.markdown("<h2 style='text-align: center;'>Bem-vindo ao O Pregador</h2>", unsafe_allow_html=True)
            
            with st.form("login_form"):
                user = st.text_input("Usuário")
                senha = st.text_input("Senha", type="password")
                btn_entrar = st.form_submit_button("Entrar no Sistema", type="primary")
                
                if btn_entrar:
                    if user in USUARIOS and USUARIOS[user] == senha:
                        st.session_state['logado'] = True
                        st.session_state['usuario_atual'] = user
                        st.rerun()
                    else:
                        st.error("Acesso negado. Tente novamente.")
        return False
    return True

if not verificar_login():
    st.stop()

# --- DAQUI PRA BAIXO SÓ RODA DEPOIS DO LOGIN ---
USUARIO_ATUAL = st.session_state['usuario_atual']

# --- 3. CONFIGURAÇÃO DE ARQUIVOS ---
PASTA_RAIZ = "Banco_Sermoes"
PASTA_USER = os.path.join(PASTA_RAIZ, USUARIO_ATUAL)
if not os.path.exists(PASTA_USER): os.makedirs(PASTA_USER)

# --- 4. FUNÇÕES DO SISTEMA ---
def consultar_gemini(prompt, chave):
    if not chave: return "⚠️ Cole a chave API no menu."
    try:
        genai.configure(api_key=chave)
        model = genai.GenerativeModel('gemini-pro')
        return model.generate_content(prompt).text
    except Exception as e: return f"Erro Google: {e}"

def buscar_noticias(tema):
    try:
        res = DDGS().news(keywords=tema, region="br-pt", max_results=3)
        return res if res else []
    except: return []

# --- 5. VISUAL ESTILO THEWORD ---
st.markdown("""
    <style>
    .block-container {padding-top: 1rem;}
    [data-testid="stSidebar"] {background-color: #2b2b2b;}
    .stTextArea textarea {
        font-family: 'Georgia', serif;
        font-size: 18px !important;
        background-color: #1e1e1e;
        color: #e0e0e0;
        border: 1px solid #444;
    }
    </style>
