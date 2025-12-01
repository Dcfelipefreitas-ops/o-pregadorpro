import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai
import os
import requests
from streamlit_lottie import st_lottie
import time

# --- 1. CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="O Pregador", layout="wide", page_icon="✝️")

# --- 2. SISTEMA DE LOGIN ---
# Usuários e Senhas (Simples)
USUARIOS = {
    "admin": "1234",
    "pastor": "pregar",
    "obreiro": "jesus"
}

def verificar_login():
    if 'logado' not in st.session_state:
        st.session_state['logado'] = False
        st.session_state['usuario_atual'] = ''

    if not st.session_state['logado']:
        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            st.markdown("## 🔐 Acesso Restrito")
            st.info("Entre com seu usuário e senha.")
            user = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            
            if st.button("Entrar"):
                if user in USUARIOS and USUARIOS[user] == senha:
                    st.session_state['logado'] = True
                    st.session_state['usuario_atual'] = user
                    st.rerun()
                else:
                    st.error("Acesso Negado.")
        return False
    return True

if not verificar_login():
    st.stop()

USUARIO_ATUAL = st.session_state['usuario_atual']

# --- 3. CONFIGURAÇÃO VISUAL & ARQUIVOS ---
PASTA_RAIZ = "Banco_Sermoes"
PASTA_USER = os.path.join(PASTA_RAIZ, USUARIO_ATUAL)

if not os.path.exists(PASTA_USER):
    os.makedirs(PASTA_USER)

# Animações
def load_lottieurl(url):
    try: return requests.get(url).json()
    except: return None

anim_book = load_lottieurl("https://lottie.host/5a666e37-d2c4-4a47-98d9-247544062a4d/lB6y7y6a1W.json")
anim_ai = load_lottieurl("https://lottie.host/93310461-1250-482f-87d9-482a46696d5b/6u0v8v5j2a.json")

# CSS Estilo TheWord
st.markdown("""
    <style>
    .block-container {padding-top: 1rem;}
    [data-testid="stSidebar"] {background-color: #262730;}
    .stTextArea textarea {
        font-family: 'Georgia', serif;
        font-size: 18px !important;
        background-color: #1e1e1e;
        color: #e0e0e0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNÇÕES INTELIGENTES ---
def consultar_gemini(prompt, chave):
    if not chave: return "⚠️ Coloque a chave API no menu lateral."
    try:
        genai.configure(api_key=chave)
        model = genai.GenerativeModel('gemini-pro')
        return model.generate_content(prompt).text
    except Exception as e: return f"Erro Google: {e}"

def buscar_noticias(tema):
    try:
        results = DDGS().news(keywords=tema, region="br-pt", max_results=3)
        return results
    except: return None

# --- 5. INTERFACE DO APP ---

# BARRA LATERAL
with st.sidebar:
    st_lottie(anim_book, height=60, key="logo")
    st.write(f"Bem-vindo, **{USUARIO_ATUAL.upper()}**")
    
    if st.button("Sair (Logout)"):
        st.session_state['logado'] = False
        st.rerun()
        
    st.divider()
    with st.expander("🔐 Chave Google (API)"):
        api_key = st.text_input("Cole aqui", type="password")
        
    st.markdown("---")
    arquivos = [f for f in os.listdir(PASTA_USER) if f.endswith(".txt")]
    arquivo_atual = st.radio("Meus Sermões:", ["+ Novo Estudo"] + arquivos)

# ÁREA PRINCIPAL
col_editor, col_tools = st.columns([2.5, 1.5])

# EDITOR (ESQUERDA)
with col_editor:
    titulo_padrao = ""
    conteudo_padrao = ""
    
    if arquivo_atual != "+ Novo Estudo":
        titulo_padrao = arquivo_atual.replace(".txt", "")
        try:
            with open(os.path.join(PASTA_USER, arquivo_atual), "r") as f:
                conteudo_padrao = f.read()
        except: pass
        
    novo_titulo = st.text_input("Título", value=titulo_padrao)
    texto = st.text_area("Esboço", value=conteudo_padrao, height=650)
    
    if st.button("💾 Salvar na Nuvem", type="primary"):
        if novo_titulo:
            with open(os.path.join(PASTA_USER, f"{novo_titulo}.txt"), "w") as f:
                f.write(texto)
            st.toast("Estudo salvo com segurança!", icon="✅")

# FERRAMENTAS (DIREITA)
with col_tools:
    aba1, aba2, aba3 = st.tabs(["📖 Bíblia", "🏛️ Contexto", "📰 Notícias"])
    
    with aba1:
        st.caption("Comparar Versões")
        ref = st.text_input("Ref (ex: Jo 3:16)")
        if st.button("Comparar"):
            resp = consultar_gemini(f"Compare {ref} em NVI, Almeida e Grego/Hebraico. Destaque diferenças.", api_key)
            st.markdown(resp)
            
    with aba2:
        st.caption("Análise Profunda")
        if st.button("Analisar Texto"):
            with st.status("Estudando...", expanded=True):
                st_lottie(anim_ai, height=50)
                analise = consultar_gemini(f"Faça uma exegese teológica e histórica de: {texto[:500]}...", api_key)
                st.markdown(analise)
                
    with aba3:
        st.caption("Atualidades")
        tema = st.text_input("Tema Atual:")
        if st.button("Buscar Notícias"):
            noticias = buscar_noticias(tema)
            if noticias:
                st.success("Encontrado:")
                for n in noticias:
                    st.markdown(f"- [{n['title']}]({n['url']})")
                
                st.write("---")
                ponte = consultar_gemini(f"Crie uma ilustração para sermão ligando o tema '{tema}' a estas notícias: {noticias}", api_key)
                st.write(ponte)
            else:
                st.warning("Nada encontrado hoje.")
                
