import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai
import os
import requests
import time
import PyPDF2  # Biblioteca para ler PDFs

# --- 0. CONFIGURAÇÃO GERAL E PROTEÇÃO CONTRA FALHAS ---
st.set_page_config(page_title="O Pregador Supremo", layout="wide", page_icon="✝️")

# Tenta carregar Lottie sem quebrar o app
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

# Animações (Só carrega se a internet deixar)
anim_livro = load_lottie_safe("https://lottie.host/5a666e37-d2c4-4a47-98d9-247544062a4d/lB6y7y6a1W.json")
anim_ia = load_lottie_safe("https://lottie.host/93310461-1250-482f-87d9-482a46696d5b/6u0v8v5j2a.json")

# --- 1. DESIGN PROFISSIONAL (CSS "MIDNIGHT") ---
st.markdown("""
    <style>
    /* Remover cabeçalho padrão */
    header, footer {visibility: hidden;}
    .block-container {padding-top: 1rem;}
    
    /* Fundo Geral */
    .stApp {background-color: #0e1117;}
    
    /* Barra Lateral com Borda Dourada */
    [data-testid="stSidebar"] {
        background-color: #1a1c24;
        border-right: 2px solid #C5A059;
    }
    
    /* Editor de Texto Premium */
    .stTextArea textarea {
        font-family: 'Georgia', serif;
        font-size: 19px !important;
        line-height: 1.6 !important;
        background-color: #1a1b21;
        color: #e0e0e0;
        border: 1px solid #333;
        border-radius: 5px;
        padding: 15px;
    }
    
    /* Abas Douradas */
    .stTabs [aria-selected="true"] {
        background-color: #C5A059 !important;
        color: black !important;
    }
    
    /* Botões */
    .stButton button {
        border-radius: 5px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton button:hover {
        border-color: #C5A059;
        color: #C5A059;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SISTEMA DE LOGIN ---
USUARIOS = {"admin": "1234", "pastor": "pregar"}

def check_login():
    if 'logado' not in st.session_state:
        st.session_state.update({'logado': False, 'user': ''})

    if not st.session_state['logado']:
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            st.write("")
            if anim_livro: st_lottie(anim_livro, height=120, key="intro")
            st.markdown("<h2 style='text-align:center'>Acesso Restrito</h2>", unsafe_allow_html=True)
            
            with st.form("login"):
                u = st.text_input("Usuário")
                s = st.text_input("Senha", type="password")
                if st.form_submit_button("Entrar", type="primary"):
                    if u in USUARIOS and USUARIOS[u] == s:
                        st.session_state['logado'] = True
                        st.session_state['user'] = u
                        st.rerun()
                    else:
                        st.error("Dados inválidos.")
        return False
    return True

if not check_login(): st.stop()

# --- 3. CONFIGURAÇÃO DE ARQUIVOS ---
USER = st.session_state['user']
PASTA = os.path.join("Banco_Sermoes", USER)
if not os.path.exists(PASTA): os.makedirs(PASTA)

# --- 4. FUNÇÕES INTELIGENTES (CÉREBRO) ---
def gemini(prompt, api_key):
    if not api_key: return "⚠️ Configurações > Cole sua API Key do Google."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        return model.generate_content(prompt).text
    except Exception as e: return f"Erro IA: {e}"

def buscar_news(tema):
    try: return DDGS().news(keywords=tema, region="br-pt", max_results=3)
    except: return []

def ler_pdf(arquivo_upload):
    """Extrai texto de um PDF enviado"""
    try:
        reader = PyPDF2.PdfReader(arquivo_upload)
        texto = ""
        # Lê apenas as primeiras 10 páginas para não travar
        for i, page in enumerate(reader.pages):
            if i > 10: break 
            texto += page.extract_text()
        return texto
    except: return "Erro ao ler PDF."

# --- 5. INTERFACE PRINCIPAL ---

# SIDEBAR
with st.sidebar:
    st.markdown(f"### ✝️ O Pregador")
    st.caption(f"Logado: {USER.upper()}")
    
    if st.button("Sair"):
        st.session_state['logado'] = False
        st.rerun()
    
    with st.expander("🔑 Chave Google (Obrigatório)"):
        api_key = st.text_input("Cole aqui", type="password")
        
    st.markdown("---")
    try: arquivos = [f for f in os.listdir(PASTA) if f.endswith(".txt")]
    except: arquivos = []
    
    selecao = st.radio("Seus Estudos:", ["+ Novo Rascunho"] + arquivos)

# TELA PRINCIPAL
c_editor, c_tools = st.columns([2.5, 1.5])

# EDITOR DE TEXTO (ESQUERDA)
with c_editor:
    tit_padrao = ""
    txt_padrao = ""
    
    if selecao != "+ Novo Rascunho":
        tit_padrao = selecao.replace(".txt", "")
        try:
            with open(os.path.join(PASTA, selecao), "r") as f: txt_padrao = f.read()
        except: pass

    st.markdown("#### 📝 Editor de Esboço")
    titulo = st.text_input("Título", value=tit_padrao, placeholder="Ex: O Poder da Cruz")
    texto = st.text_area("Papel", value=txt_padrao, height=650, label_visibility="collapsed")
    
    if st.button("💾 GRAVAR NA NUVEM", type="primary"):
        if titulo:
            with open(os.path.join(PASTA, f"{titulo}.txt"), "w") as f: f.write(texto)
            st.toast("Estudo Salvo!", icon="✅")
            st.balloons()

# FERRAMENTAS AVANÇADAS (DIREITA)
with c_tools:
    st.markdown("#### 🧰 Ferramentas")
    aba1, aba2, aba3, aba4 = st.tabs(["📖 Bíblia", "🗣️ Tradutor", "📰 News", "📚 Livros PDF"])
    
    # ABA 1: BÍBLIA & CONTEXTO
    with aba1:
        st.caption("Raio-X Teológico")
        ref = st.text_input("Versículo:", placeholder="Jo 3:16")
        if st.button("Analisar Versículo"):
            if anim_ia: st_lottie(anim_ia, height=50, key="l1")
            res = gemini(f"Faça uma exegese completa de: {ref}. Traga o grego/hebraico e contexto histórico.", api_key)
            st.markdown(res)

    # ABA 2: TRADUTOR (NOVIDADE)
    with aba2:
        st.caption("Traduzir citações ou textos")
        texto_trad = st.text_area("Cole o texto (Inglês, Espanhol, etc):")
        if st.button("Traduzir para Português"):
            with st.spinner("Traduzindo..."):
                res = gemini(f"Traduza este texto para um português teológico culto: {texto_trad}", api_key)
                st.info(res)
                
    # ABA 3: NOTÍCIAS
    with aba3:
        st.caption("Atualidades para Ilustração")
        tema = st.text_input("Tema:", placeholder="Ex: Ansiedade")
        if st.button("Buscar Fatos"):
            news = buscar_news(tema)
            if news:
                for n in news: st.markdown(f"🔹 [{n['title']}]({n['url']})")
                st.markdown("---")
                st.write(gemini(f"Crie uma ilustração para sermão usando essas notícias: {news}", api_key))
            else: st.warning("Nada encontrado.")

    # ABA 4: LEITOR DE LIVROS PDF (NOVIDADE)
    with aba4:
        st.caption("Estudar Livro PDF")
        st.info("Suba um livro do seu computador para a IA ler.")
        pdf_file = st.file_uploader("Arraste o PDF aqui", type="pdf")
        
        if pdf_file:
            if st.button("Ler e Resumir"):
                with st.spinner("Lendo livro..."):
                    conteudo_livro = ler_pdf(pdf_file)
                    st.success("Livro lido!")
                    st.markdown("---")
                    res = gemini(f"Aqui está um trecho de um livro cristão: '{conteudo_livro[:3000]}'. Resuma os pontos principais para meu sermão.", api_key)
                    st.markdown(res)
