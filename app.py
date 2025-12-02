import streamlit as st
import time

# 1. CONFIGURAÇÃO (PRIMEIRA COISA DO ARQUIVO)
st.set_page_config(page_title="O Pregador", layout="wide", page_icon="✝️")

# 2. IMPORTAÇÕES DEPOIS DO CONFIG
from duckduckgo_search import DDGS
import google.generativeai as genai
import os
import requests
import PyPDF2

# 3. FUNÇÕES SEGURAS (Sem risco de erro)
def try_lottie():
    try:
        from streamlit_lottie import st_lottie
        return st_lottie
    except: return None

_st_lottie = try_lottie()

def get_animation(url):
    try:
        r = requests.get(url, timeout=1)
        return r.json() if r.status_code == 200 else None
    except: return None

# 4. CSS INJETADO DE FORMA SEGURA
st.markdown("""
<style>
    /* Reset Geral */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {padding-top: 2rem;}
    
    /* Cores e Fundo */
    .stApp {background-color: #0e1117;}
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1a1c24;
        border-right: 2px solid #C5A059;
    }
    
    /* Editor de Texto */
    .stTextArea textarea {
        font-family: 'Georgia', serif;
        font-size: 19px !important;
        background-color: #1a1b21;
        color: #e0e0e0;
        border: 1px solid #444;
        border-radius: 4px;
        padding: 15px;
    }
    
    /* Botões */
    .stButton button {
        border-radius: 4px;
        font-weight: 600;
        transition: 0.2s;
    }
    .stButton button:hover {
        border-color: #C5A059;
        color: #C5A059;
    }
</style>
""", unsafe_allow_html=True)

# 5. ESTADO E LOGIN
if 'logado' not in st.session_state:
    st.session_state.update({'logado': False, 'user': ''})

USUARIOS = {"admin": "1234", "pastor": "pregar"}
anim_livro = get_animation("https://lottie.host/5a666e37-d2c4-4a47-98d9-247544062a4d/lB6y7y6a1W.json")

def tela_login():
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.write("")
        st.write("")
        if _st_lottie and anim_livro:
            _st_lottie(anim_livro, height=100, key="intro")
        else:
            st.title("✝️")
            
        st.markdown("<h3 style='text-align:center; color:#ccc'>Acesso Restrito</h3>", unsafe_allow_html=True)
        
        with st.form("frm_login"):
            u = st.text_input("Usuário")
            s = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar", type="primary"):
                if u in USUARIOS and USUARIOS[u] == s:
                    st.session_state['logado'] = True
                    st.session_state['user'] = u
                    st.rerun()
                else:
                    st.error("Erro no login.")

if not st.session_state['logado']:
    tela_login()
    st.stop()

# 6. APP PRINCIPAL (SÓ CARREGA SE LOGADO)
USER = st.session_state['user']
PASTA = os.path.join("Banco_Sermoes", USER)
if not os.path.exists(PASTA): os.makedirs(PASTA)

def gemini(prompt, api):
    if not api: return "⚠️ Falta API Key."
    try:
        genai.configure(api_key=api)
        return genai.GenerativeModel('gemini-pro').generate_content(prompt).text
    except Exception as e: return f"Erro: {e}"

def news_search(term):
    try: return DDGS().news(keywords=term, region="br-pt", max_results=3)
    except: return []

def pdf_read(file):
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for i, page in enumerate(reader.pages):
            if i > 15: break
            text += page.extract_text()
        return text
    except: return "Erro PDF"

# MENU LATERAL
with st.sidebar:
    st.subheader("✝️ O Pregador")
    st.caption(f"Usuário: {USER}")
    if st.button("Sair"):
        st.session_state['logado'] = False
        st.rerun()
        
    with st.expander("🔑 Chave Google API"):
        api_key = st.text_input("Cole aqui", type="password")
        
    st.markdown("---")
    try: arqs = [f for f in os.listdir(PASTA) if f.endswith(".txt")]
    except: arqs = []
    escolha = st.radio("Seus Estudos:", ["+ Novo"] + arqs)

# ÁREA DE TRABALHO
c_edit, c_tools = st.columns([2, 1])

with c_edit:
    t_val = ""
    c_val = ""
    if escolha != "+ Novo":
        t_val = escolha.replace(".txt", "")
        try:
            with open(os.path.join(PASTA, escolha), "r") as f: c_val = f.read()
        except: pass
        
    st.markdown("#### 📝 Rascunho")
    titulo = st.text_input("Título", value=t_val)
    texto = st.text_area("Texto", value=c_val, height=600, label_visibility="collapsed")
    
    if st.button("💾 GRAVAR NA NUVEM", type="primary"):
        if titulo:
            with open(os.path.join(PASTA, f"{titulo}.txt"), "w") as f: f.write(texto)
            st.toast("Salvo!", icon="✅")

with c_tools:
    t1, t2, t3, t4 = st.tabs(["📖", "🗣️", "📰", "📚"])
    
    with t1:
        st.caption("Bíblia/Exegese")
        ref = st.text_input("Ref:")
        if st.button("Analisar"):
            st.info(gemini(f"Exegese de {ref}", api_key))
            
    with t2:
        st.caption("Tradutor")
        txt = st.text_area("Texto:")
        if st.button("Traduzir"):
            st.success(gemini(f"Traduza para PT Teológico: {txt}", api_key))
            
    with t3:
        st.caption("Notícias")
        tm = st.text_input("Tema:")
        if st.button("Buscar"):
            res = news_search(tm)
            if res:
                for n in res: st.markdown(f"- [{n['title']}]({n['url']})")
                st.write(gemini(f"Ilustre com: {res}", api_key))
            else: st.warning("Nada.")
            
    with t4:
        st.caption("PDF")
        pdf = st.file_uploader("Upload", type="pdf")
        if pdf and st.button("Ler"):
            cont = pdf_read(pdf)
            st.markdown(gemini(f"Resuma: {cont[:2000]}", api_key))
