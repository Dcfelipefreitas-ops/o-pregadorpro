import streamlit as st
import os
import sys
import subprocess
import time
import json
from datetime import datetime
from io import BytesIO

# --- 0. AUTO-INSTALAÇÃO DE DEPENDÊNCIAS ---
def install_packages():
    required = ["google-generativeai", "duckduckgo-search", "streamlit-lottie", "fpdf", "Pillow"]
    for package in required:
        try:
            __import__(package.replace("-", "_").replace("google_generativeai", "google.generativeai").replace("Pillow", "PIL"))
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            st.rerun()

install_packages()

import google.generativeai as genai
from duckduckgo_search import DDGS
from streamlit_lottie import st_lottie
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# --- 1. CONFIGURAÇÃO INICIAL E ESTADO ---
st.set_page_config(page_title="O PREGADOR", layout="wide", page_icon="✝️", initial_sidebar_state="collapsed")

# DIRETÓRIOS E DADOS
PASTA_RAIZ = "Dados_Pregador"
PASTA_SERMOES = os.path.join(PASTA_RAIZ, "Sermoes")
PASTA_CARE = os.path.join(PASTA_RAIZ, "PastoralCare")
PASTA_AUDIO = os.path.join(PASTA_RAIZ, "Audios")
os.makedirs(PASTA_SERMOES, exist_ok=True)
os.makedirs(PASTA_CARE, exist_ok=True)
os.makedirs(PASTA_AUDIO, exist_ok=True)

# INICIALIZAÇÃO DO ESTADO DE SESSÃO
DEFAULTS = {
    "logado": False, "user": "", "page_stack": ["Home"], 
    "texto_ativo": "", "titulo_ativo": "", "slides": [], 
    "api_key": "", "avatar_bytes": None,
    "current_nav_title": "Visão Geral", "humor": "Bem",
    # Cores personalizadas pelo usuário (Automação Visual)
    "theme_font": "Inter", "theme_size": 18, "theme_color": "#ffffff" 
}

for k, v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k] = v

# --- 2. SISTEMA DE NAVEGAÇÃO "APPLE-LIKE" ---
def navigate_to(page_name, title=None):
    st.session_state['page_stack'].append(page_name)
    st.session_state['current_nav_title'] = title if title else page_name
    st.rerun()

def navigate_back():
    if len(st.session_state['page_stack']) > 1:
        st.session_state['page_stack'].pop()
        st.rerun()

def current_page():
    return st.session_state['page_stack'][-1]

# --- 3. UI KIT (CSS ESTILO IOS/MACOS + MADEIRA) ---
def carregar_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    :root {{ --bg: #000000; --card: #1c1c1e; --acc: #0A84FF; --txt: #F2F2F7; }}
    
    .stApp {{ background-color: var(--bg); font-family: '{st.session_state['theme_font']}', sans-serif; color: var(--txt); }}
    header, footer {{visibility: hidden;}}

    /* CABEÇALHO HORIZONTAL (LOGOS BIBLE STYLE) */
    .logos-header {{
        position: fixed; top: 0; left: 0; width: 100%; height: 50px;
        background: #1c1c1e; border-bottom: 1px solid #333; z-index: 9999;
        display: flex; align-items: center; justify-content: flex-start;
        padding: 0 20px; gap: 20px;
    }}
    
    .header-btn {{ 
        color: #999; font-size: 14px; font-weight: 500; cursor: pointer; padding: 5px 10px; border-radius: 6px; 
    }}
    .header-btn:hover {{ background: #333; color: white; }}
    .header-logo {{ color: #d4af37; font-weight: bold; font-size: 16px; margin-right: 20px; }}

    /* Espaço para compensar header fixo */
    .block-container {{ padding-top: 70px !important; }}
    
    /* PREGADOR DE ROUPA (Ícone Visual Custom) */
    .wood-clip {{
        width: 100px; height: 200px;
        background: linear-gradient(90deg, #d2b48c 0%, #a0522d 100%);
        border-radius: 10px;
        position: relative; margin: 0 auto 20px auto;
        box-shadow: 2px 5px 15px rgba(0,0,0,0.5);
    }}
    .wood-spring {{
        width: 80px; height: 30px; background: silver; position: absolute; top: 80px; left: 10px;
        border-radius: 5px;
    }}

    /* TEXTO PERSONALIZÁVEL */
    .stTextArea textarea {{
        font-family: '{st.session_state['theme_font']}';
        font-size: {st.session_state['theme_size']}px !important;
        color: {st.session_state['theme_color']} !important;
        background-color: #1a1a1a !important; border: 1px solid #333;
    }}

    /* Slides Preview Area */
    .slide-zone {{
        border: 2px dashed #444; border-radius: 10px; padding: 20px; text-align: center;
        background: #111; margin-top: 10px; min-height: 100px;
    }}
    </style>
    
    <!-- HEADER HORIZONTAL VISÍVEL -->
    <div class="logos-header">
        <div class="header-logo">O PREGADOR</div>
        <div class="header-btn">Arquivo</div>
        <div class="header-btn">Editar</div>
        <div class="header-btn">Exibir</div>
        <div class="header-btn">Janelas</div>
        <div class="header-btn">Ajuda</div>
    </div>
    """, unsafe_allow_html=True)

carregar_css()

# --- 4. FUNÇÕES DE SUPORTE (BACKEND SIMULADO) ---

def consultar_ia(prompt, role="teologo"):
    if not st.session_state['api_key']: return "⚠️ Adicione API Key nas Configurações."
    try:
        genai.configure(api_key=st.session_state['api_key'])
        sys = "Você é um assistente pastoral."
        model = genai.GenerativeModel("gemini-pro")
        return model.generate_content(f"{sys}\n{prompt}").text
    except Exception as e: return f"Erro: {e}"

# Salvar Slide a partir do Texto (DRAG & DROP Simulado)
def criar_slide(texto_slide):
    st.session_state['slides'].append({"conteudo": texto_slide, "img": None})
    st.toast("Slide Criado! 🎞️")

# --- 5. TELA DE LOGIN (APPLE STYLE + MADEIRA) ---
if not st.session_state['logado']:
    # Fundo Clean "Apple"
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(to bottom, #f0f0f5, #d9d9e6); color: black !important; } 
    </style>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        # Elemento Visual do "Pregador de Madeira"
        st.markdown("""
        <div class="wood-clip">
            <div class="wood-spring"></div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<h3 style='text-align:center; font-family:Helvetica; color:#333'>O Pregador</h3>", unsafe_allow_html=True)
        
        user = st.text_input("ID")
        pw = st.text_input("Passcode", type="password")
        if st.button("Entrar", type="primary", use_container_width=True):
            if (user == "admin" and pw == "1234") or (user == "pr" and pw == "123"):
                st.session_state['logado'] = True
                st.session_state['user'] = user
                st.rerun()
            else:
                st.error("Erro no login.")
    st.stop()


# --- 6. ESTRUTURA PRINCIPAL ---

# VOLTAR PARA MODO ESCURO APÓS LOGIN
if st.session_state['logado']:
     st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #F2F2F7; } 
    </style>
    """, unsafe_allow_html=True)

# SIDEBAR (Perfil e Menu Lateral Global)
with st.sidebar:
    st.markdown("### Navegação")
    if st.button("🏠 Home", use_container_width=True): navigate_to("Home", "Visão Geral")
    if st.button("✍️ Editor Studio", use_container_width=True): navigate_to("Studio", "Redação & Slides")
    if st.button("⚙️ Configurações", use_container_width=True): navigate_to("Config", "Personalização")

# NAVSTACK E CABEÇALHO AUTOMÁTICO
# (Já renderizado pelo HTML no CSS acima, aqui apenas controle lógico)
pagina = current_page()

# --- PÁGINA: HOME ---
if pagina == "Home":
    st.title(f"Bem-vindo, Pr. {st.session_state['user'].capitalize()}")
    st.info("Selecione 'Editor Studio' no menu para usar a ferramenta de slides.")

# --- PÁGINA: STUDIO (REDAÇÃO + SLIDES SIMULTÂNEOS) ---
elif pagina == "Studio":
    
    # 1. Menu de Formatação e Automação
    with st.expander("🛠️ Automação de Formatação (Estilo Pessoal)", expanded=False):
        c1, c2, c3 = st.columns(3)
        novo_size = c1.number_input("Tamanho Texto", 12, 40, st.session_state['theme_size'])
        novo_font = c2.selectbox("Fonte", ["Inter", "Georgia", "Courier New", "Arial"], index=0)
        nova_cor = c3.color_picker("Cor Texto", st.session_state['theme_color'])
        
        if c1.button("Aplicar Estilo"):
            st.session_state['theme_size'] = novo_size
            st.session_state['theme_font'] = novo_font
            st.session_state['theme_color'] = nova_cor
            st.rerun()

    # 2. Área Dividida (Texto vs Slides)
    col_texto, col_slides = st.columns([1.5, 1])
    
    with col_texto:
        st.markdown("### 📜 Manuscrito")
        texto = st.text_area("Escreva aqui seu estudo...", value=st.session_state['texto_ativo'], height=600, label_visibility="collapsed")
        st.session_state['texto_ativo'] = texto
        
        # Botão para Enviar Seleção para Slide
        # Como o Streamlit não tem 'seleção de texto' nativa no browser, usamos uma área de transferência manual
        st.markdown("---")
        st.caption("Selecionar trecho para Slide:")
        trecho = st.text_area("Copie aqui a parte do texto para virar slide:", height=100)
        if st.button("Enviar para Apresentação ➡️"):
            if trecho: criar_slide(trecho)

    with col_slides:
        st.markdown("### 🎞️ Painel de Apresentação")
        
        # Modo Projeção Prévia
        if st.session_state['slides']:
            curr_slide = st.session_state['slides'][-1]
            st.markdown(f"""
            <div style="background:black; border:2px solid #333; padding:20px; aspect-ratio:16/9; display:flex; align-items:center; justify-content:center; text-align:center; font-size:20px; color:white;">
                {curr_slide['conteudo']}
            </div>
            <small>Último slide adicionado</small>
            """, unsafe_allow_html=True)
        else:
            st.info("Nenhum slide criado. Use o campo à esquerda para enviar texto.")

        # Lista de Slides
        st.divider()
        st.markdown("**Fila de Slides**")
        for i, s in enumerate(st.session_state['slides']):
            st.text_input(f"Slide {i+1}", s['conteudo'], key=f"s_{i}")


# --- PÁGINA: CONFIG ---
elif pagina == "Config":
    st.title("Ajustes")
    k = st.text_input("Google API Key (IA)", type="password")
    if k: st.session_state['api_key'] = k
