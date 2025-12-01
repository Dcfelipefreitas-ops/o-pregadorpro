import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai
import os
import requests
import time
import PyPDF2

# --- 1. CONFIGURAÇÃO GERAL ---
st.set_page_config(page_title="O Pregador Supremo", layout="wide", page_icon="✝️")

# --- 2. IMPORTAÇÃO SEGURA DE ANIMAÇÕES ---
try:
    from streamlit_lottie import st_lottie
    LOTTIE_OK = True
except ImportError:
    LOTTIE_OK = False

def load_lottie_safe(url):
    if not LOTTIE_OK: return None
    try:
        r = requests.get(url, timeout=1.0)
        return r.json() if r.status_code == 200 else None
    except: return None

# Carrega animações
anim_livro = load_lottie_safe("https://lottie.host/5a666e37-d2c4-4a47-98d9-247544062a4d/lB6y7y6a1W.json")
anim_ia = load_lottie_safe("https://lottie.host/93310461-1250-482f-87d9-482a46696d5b/6u0v8v5j2a.json")

# --- 3. ESTILO VISUAL (CSS) ---
st.markdown("""
    <style>
    header, footer {visibility: hidden;}
    .block-container {padding-top: 1rem;}
    .stApp {background-color: #0e1117;}
    [data-testid="stSidebar"] {
        background-color: #1a1c24;
        border-right: 2px solid #C5A059;
    }
    .stTextArea textarea {
        font-family: 'Georgia', serif;
        font-size: 19px !important;
        background-color: #1a1b21;
        color: #e0e0e0;
        border: 1px solid #333;
        border-radius: 5px;
        padding: 15px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #C5A059 !important;
        color: black !important;
    }
    .stButton button {
        border-radius: 5px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOGIN ---
USUARIOS = {"admin": "1234", "pastor": "pregar"}

def check_login():
    if 'logado' not in st.session_state:
        st.session_state.update({'logado': False, 'user': ''})

    if not st.session_state['logado']:
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            st.write("")
            if anim_livro:
                st_lottie(anim_livro, height=120, key="intro")
            else:
                st.markdown("<h1 style='text-align:center'>✝️</h1>", unsafe_allow_html=True)
            
            st.markdown("<h3 style='text-align:center'>Acesso Restrito</h3>", unsafe_allow_html=True)
            
            with st.form("login"):
                u = st.text_input("Usuário")
                s = st.text_input("Senha", type="password")
                if st.form_submit_button("Entrar", type="primary"):
                    if u in USUARIOS and USUARIOS[u] == s:
                        st.session_state['logado'] = True
                        st.session_state['user'] = u
                        st.rerun()
                    else:
                        st.error("Dados incorretos.")
        return False
    return True

if not check_login(): st.stop()

# --- 5. LÓGICA DO APP ---
USER = st.session_state['user']
PASTA = os.path.join("Banco_Sermoes", USER)
if not os.path.exists(PASTA): os.makedirs(PASTA)

def gemini(prompt, api_key):
    if not api_key: return "⚠️ Cole sua API Key no menu."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        return model.generate_content(prompt).text
    except Exception as e: return f"Erro IA: {e}"

def buscar_news(tema):
    try: return DDGS().news(keywords=tema, region="br-pt", max_results=3)
    except: return []

def ler_pdf(arquivo):
    try:
        reader = PyPDF2.PdfReader(arquivo)
        texto = ""
        for i, page in enumerate(reader.pages):
            if i > 15: break 
            texto += page.extract_text()
        return texto
    except: return "Erro leitura PDF."

# --- 6. INTERFACE ---
with st.sidebar:
    st.markdown("### ✝️ O Pregador")
    st.caption(f"Logado: {USER.upper()}")
    
    if st.button("Sair"):
        st.session_state['logado'] = False
        st.rerun()
    
    with st.expander("🔑 Chave Google API"):
        api_key = st.text_input("Cole aqui", type="password")
        
    st.markdown("---")
    try: arquivos = [f for f in os.listdir(PASTA) if f.endswith(".txt")]
    except: arquivos = []
    
    selecao = st.radio("Biblioteca:", ["+ Novo Rascunho"] + arquivos)

c_editor, c_tools = st.columns([2.5, 1.5])

# EDITOR
with c_editor:
    tit_padrao = ""
    txt_padrao = ""
    
    if selecao != "+ Novo Rascunho":
        tit_padrao = selecao.replace(".txt", "")
        try:
            with open(os.path.join(PASTA, selecao), "r") as f: txt_padrao = f.read()
        except: pass

    st.markdown("#### 📝 Editor de Esboço")
    titulo = st.text_input("Título", value=tit_padrao)
    texto = st.text_area("Papel", value=txt_padrao, height=600, label_visibility="collapsed")
    
    if st.button("💾 GRAVAR NA NUVEM", type="primary"):
        if titulo:
            with open(os.path.join(PASTA, f"{titulo}.txt"), "w") as f: f.write(texto)
            st.toast("Estudo Salvo!", icon="✅")

# FERRAMENTAS
with c_tools:
    st.markdown("#### 🧰 Ferramentas")
    aba1, aba2, aba3, aba4 = st.tabs(["📖", "🗣️", "📰", "📚"])
    
    # BÍBLIA
    with aba1:
        st.caption("Exegese")
        ref = st.text_input("Versículo:", placeholder="Jo 3:16")
        if st.button("Analisar"):
            if anim_ia: st_lottie(anim_ia, height=50, key="l1")
            st.markdown(gemini(f"Exegese completa de: {ref}", api_key))

    # TRADUTOR
    with aba2:
        st.caption("Tradutor Teológico")
        txt_trad = st.text_area("Texto em outra língua:")
        if st.button("Traduzir"):
            st.info(gemini(f"Traduza para português culto: {txt_trad}", api_key))

    # NOTÍCIAS
    with aba3:
        st.caption("Atualidades")
        tema = st.text_input("Tema:")
        if st.button("Buscar Fatos"):
            news = buscar_news(tema)
            if news:
                for n in news: st.markdown(f"🔹 [{n['title']}]({n['url']})")
                st.write(gemini(f"Ilustração com: {news}", api_key))
            else: st.warning("Nada achado.")

    # PDF
    with aba4:
        st.caption("Ler Livro PDF")
        pdf = st.file_uploader("Arraste o PDF", type="pdf")
        if pdf and st.button("Ler e Resumir"):
            cont = ler_pdf(pdf)
            st.success("Lido!")
            st.markdown(gemini(f"Resuma este livro cristão: {cont[:3000]}", api_key))
