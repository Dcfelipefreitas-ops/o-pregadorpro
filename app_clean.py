import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai
import os
import requests
from streamlit_lottie import st_lottie
import time

# Clean, single-file app (login + editor + web + IA)
st.set_page_config(page_title="O Pregador (clean)", layout="wide", page_icon="✝️")

USUARIOS = {
    "admin": "1234",
    "pastor1": "pregar",
    "convidado": "jesus",
}

def verificar_login():
    if 'logado' not in st.session_state:
        st.session_state['logado'] = False
        st.session_state['usuario_atual'] = ''
    if not st.session_state['logado']:
        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            st.markdown("## 🔐 Acesso Restrito")
            user = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            if st.button("Entrar"):
                if user in USUARIOS and USUARIOS[user] == senha:
                    st.session_state['logado'] = True
                    st.session_state['usuario_atual'] = user
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
        return False
    return True

if not verificar_login():
    st.stop()

USUARIO_ATUAL = st.session_state['usuario_atual']

def load_lottieurl(url):
    try:
        r = requests.get(url, timeout=6)
        return r.json()
    except Exception:
        return None

anim_book = load_lottieurl("https://lottie.host/5a666e37-d2c4-4a47-98d9-247544062a4d/lB6y7y6a1W.json")

def consultar_gemini(prompt, chave):
    if not chave:
        return "⚠️ Coloque a chave API no menu."
    try:
        genai.configure(api_key=chave)
        model = genai.GenerativeModel('gemini-pro')
        return model.generate_content(prompt).text
    except Exception as e:
        return f"Erro: {e}"

def buscar_web(texto):
    try:
        res = DDGS().text(texto, max_results=3)
        return "\n\n".join([f"• {r.get('title','(sem título)')}: {r.get('body','')}" for r in res]) if res else "Nada."
    except Exception as e:
        return f"Erro na busca: {e}"

PASTA_RAIZ = "Banco_de_Sermoes"
PASTA_USUARIO = os.path.join(PASTA_RAIZ, USUARIO_ATUAL)
os.makedirs(PASTA_USUARIO, exist_ok=True)

st.markdown("""
<style>
.stTextArea textarea {font-family: 'Georgia', serif; font-size: 18px;}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    try:
        if anim_book:
            st_lottie(anim_book, height=70)
    except Exception:
        pass
    st.write(f"Olá, **{USUARIO_ATUAL.upper()}**")
    if st.button("Sair / Logout"):
        st.session_state['logado'] = False
        st.rerun()
    st.divider()
    with st.expander("🔐 Chave Google"):
        api_key = st.text_input("API Key", type="password")
    arquivos = [f for f in os.listdir(PASTA_USUARIO) if f.endswith('.txt')]
    arquivo_atual = st.radio("Meus Estudos:", ["+ Novo"] + arquivos)

col_editor, col_tools = st.columns([2.5, 1.5])

with col_editor:
    titulo_padrao = ""
    conteudo_padrao = ""
    if arquivo_atual != "+ Novo":
        titulo_padrao = arquivo_atual.replace('.txt','')
        try:
            with open(os.path.join(PASTA_USUARIO, arquivo_atual), 'r', encoding='utf-8') as f:
                conteudo_padrao = f.read()
        except Exception:
            conteudo_padrao = ""
    novo_titulo = st.text_input("Título", value=titulo_padrao)
    texto = st.text_area("Esboço", value=conteudo_padrao, height=600)
    if st.button("💾 Salvar"):
        if not novo_titulo:
            st.warning("Digite um título antes de salvar.")
        else:
            with open(os.path.join(PASTA_USUARIO, f"{novo_titulo}.txt"), 'w', encoding='utf-8') as f:
                f.write(texto)
            st.success("Salvo!")

with col_tools:
    aba1, aba2 = st.tabs(["🔍 Web", "🤖 IA"])
    with aba1:
        q = st.text_input("Pesquisa:")
        if st.button("Buscar"):
            st.info(buscar_web(q))
    with aba2:
        if st.button("Analisar Texto"):
            prompt = f"Analise: {texto}"
            resp = consultar_gemini(prompt, api_key if 'api_key' in locals() else None)
            st.write(resp)

st.markdown("---")
st.caption("Versão limpa: `app_clean.py` — execute com o venv e instale dependências antes.")
