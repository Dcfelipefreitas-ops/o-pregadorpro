import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai
import os
import requests
from streamlit_lottie import st_lottie
import time
import json

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
        return "⚠️ Coloque la clave API en Configuração."
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

PROFILE_PATH = os.path.join(PASTA_USUARIO, "profile.json")

def load_profile():
    if os.path.exists(PROFILE_PATH):
        try:
            with open(PROFILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_profile(profile):
    try:
        with open(PROFILE_PATH, "w", encoding="utf-8") as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

# estilo del editor
st.markdown("""
<style>
.stTextArea textarea {font-family: 'Georgia', serif; font-size: 18px;}
.sidebar-section {padding:8px 4px; margin-bottom:8px;}
</style>
""", unsafe_allow_html=True)

# Sidebar reestructurada: resumen + secciones claras
with st.sidebar:
    # Logo / animación
    try:
        if anim_book:
            st_lottie(anim_book, height=80)
    except Exception:
        pass

    st.markdown(f"### Hola, **{USUARIO_ATUAL.upper()}**")

    # Cargar perfil existente
    profile = load_profile()
    nombre_display = profile.get("nombre", "")
    apellido_display = profile.get("apellido", "")
    iglesia_display = profile.get("iglesia", "")
    correo_display = profile.get("correo", "")

    # Resumen compacto
    st.markdown("##### Perfil")
    st.markdown(f"- **Nombre:** {nombre_display} {apellido_display}" if (nombre_display or apellido_display) else "- Nome não configurado")
    st.markdown(f"- **Iglesia:** {iglesia_display}" if iglesia_display else "- Igreja não configurada")
    st.markdown(f"- **Correo:** {correo_display}" if correo_display else "- E-mail não configurado")
    st.divider()

    # Perfil (edición)
    with st.expander("🧾 Editar Perfil", expanded=False):
        p_nombre = st.text_input("Nombre", value=profile.get("nombre",""), key="p_nombre")
        p_apellido = st.text_input("Apellido", value=profile.get("apellido",""), key="p_apellido")
        p_telefono = st.text_input("Teléfono", value=profile.get("telefono",""), key="p_telefono")
        p_direccion = st.text_input("Dirección", value=profile.get("direccion",""), key="p_direccion")
        p_iglesia = st.text_input("Iglesia", value=profile.get("iglesia",""), key="p_iglesia")
        p_ministerios = st.text_input("Ministerios (separar por comas)", value=",".join(profile.get("ministerios",[])) if profile.get("ministerios") else "", key="p_ministerios")
        p_correo = st.text_input("Correo electrónico", value=profile.get("correo",""), key="p_correo")
        if st.button("Guardar Perfil"):
            new_profile = {
                "nombre": p_nombre.strip(),
                "apellido": p_apellido.strip(),
                "telefono": p_telefono.strip(),
                "direccion": p_direccion.strip(),
                "iglesia": p_iglesia.strip(),
                "ministerios": [m.strip() for m in p_ministerios.split(",")] if p_ministerios else [],
                "correo": p_correo.strip()
            }
            if save_profile(new_profile):
                st.success("Perfil guardado.")
                st.experimental_rerun()
            else:
                st.error("Error ao salvar o perfil.")
    st.divider()

    # Mis estudios (lista de archivos)
    st.markdown("##### Meus Estudos")
    arquivos = [f for f in os.listdir(PASTA_USUARIO) if f.endswith('.txt')]
    arquivos.sort()
    arquivo_atual = st.radio("Selecionar estudo", ["+ Novo"] + arquivos, key="sidebar_arquivos")

    st.divider()

    # Configuração: API Key e utilidades
    with st.expander("⚙️ Configuração", expanded=False):
        # persistir API key em session para uso em IA
        api_key_val = st.text_input("🔑 Clave Google (API)", type="password", key="api_key_input", value=st.session_state.get("api_key",""))
        if st.button("Guardar Configuração"):
            st.session_state["api_key"] = api_key_val
            st.success("Configuração salva na sessão.")
    st.divider()

    # Logout al final
    if st.button("Sair / Logout"):
        st.session_state['logado'] = False
        st.rerun()

# Main layout: editor y herramientas
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
            st.experimental_rerun()

with col_tools:
    aba1, aba2 = st.tabs(["🔍 Web", "🤖 IA"])
    with aba1:
        q = st.text_input("Pesquisa:")
        if st.button("Buscar"):
            st.info(buscar_web(q))
    with aba2:
        if st.button("Analisar Texto"):
            prompt = f"Analise: {texto}"
            chave = st.session_state.get("api_key", "")
            resp = consultar_gemini(prompt, chave)
            st.write(resp)

st.markdown("---")
st.caption("Versão limpa: `app_clean.py` — execute com o venv e instale dependências antes.")
