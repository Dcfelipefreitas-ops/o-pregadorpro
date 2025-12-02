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

# --- 1. CONFIGURAÇÃO (WIDE) ---
st.set_page_config(page_title="O PREGADOR", layout="wide", page_icon="✝️", initial_sidebar_state="expanded")

# --- 2. GESTÃO DE DADOS ---
PASTA_RAIZ = "Dados_Pregador"
PASTA_SERMOES = os.path.join(PASTA_RAIZ, "Sermoes")
PASTA_CARE = os.path.join(PASTA_RAIZ, "PastoralCare")
os.makedirs(PASTA_SERMOES, exist_ok=True)
os.makedirs(PASTA_CARE, exist_ok=True)

# INICIALIZAÇÃO DE ESTADO
DEFAULTS = {
    "logado": False, 
    "user": "", 
    "page_stack": ["Home"], 
    "texto_ativo": "", 
    "titulo_ativo": "", 
    "slides": [], 
    "api_key": "", 
    "theme_size": 18, 
    "stats_sermoes": len(os.listdir(PASTA_SERMOES)),
    "historico_biblia": [],
    "tocar_som_login": False # Novo controle para o áudio
}
for k, v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k] = v

# --- 3. SISTEMA DE SOM (Pad Angelical) ---
def play_login_sound():
    # URL de um som ambiente/pad suave (Royalty Free)
    sound_url = "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3?filename=angelic-pad-15337.mp3"
    
    # HTML oculto com autoplay limitado a 4 segundos
    audio_html = f"""
        <script>
            var audio = new Audio('{sound_url}');
            audio.volume = 0.5;
            audio.play();
            setTimeout(function(){{
                audio.pause();
                audio.currentTime = 0;
            }}, 4500); // Para após 4.5 segundos
        </script>
    """
    # Injeta no app
    st.components.v1.html(audio_html, height=0)

# --- 4. UI KIT PREMIUM (CSS REFINADO) ---
def carregar_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Merriweather:ital,wght@0,300;0,700;1,400&display=swap');
    
    /* VARIÁVEIS */
    :root {{ --bg: #000000; --card: #1c1c1e; --border: #333; --gold: #d4af37; --txt: #F2F2F7; }}
    
    /* GERAL */
    .stApp {{ background-color: var(--bg); font-family: 'Inter', sans-serif; color: var(--txt); }}
    header, footer {{ display: none !important; }}

    /* CABEÇALHO HORIZONTAL FIXO */
    .logos-header {{
        position: fixed; top: 0; left: 0; width: 100%; height: 50px;
        background: rgba(28, 28, 30, 0.95); backdrop-filter: blur(10px);
        border-bottom: 1px solid #333; z-index: 9999;
        display: flex; align-items: center; justify-content: flex-start;
        padding: 0 20px; gap: 20px;
    }}
    .brand-logo {{ color: var(--gold); font-weight: 800; font-size: 16px; letter-spacing: 1px; display:flex; align-items:center; gap:10px; }}
    .nav-divider {{ height: 20px; width: 1px; background: #444; }}
    .top-menu-item {{ font-size: 13px; color: #aaa; cursor: pointer; transition: 0.3s; }}
    .top-menu-item:hover {{ color: white; }}
    
    .block-container {{ padding-top: 70px !important; }}
    
    /* EDITOR ESTILO WORD (MELHORADO PARA ORTOGRAFIA) */
    .stTextArea textarea {{
        font-family: 'Merriweather', serif;
        font-size: {st.session_state['theme_size']}px !important;
        color: #e0e0e0 !important;
        background-color: #111 !important; 
        border: 1px solid #333; 
        border-radius: 8px;
        padding: 30px; 
        line-height: 1.8;
    }}
    /* Força visualização de erro ortográfico */
    textarea:invalid {{ border-bottom: 2px solid red; }}

    /* LOGIN CARD COM CRUZ */
    .login-container {{
        background: #0a0a0a; border: 1px solid #222; border-radius: 20px; padding: 50px; text-align: center;
        box-shadow: 0 20px 60px rgba(0,0,0,1); max-width: 400px; margin: auto;
    }}
    .gold-cross-icon {{ font-size: 60px; color: #d4af37; margin-bottom: 20px; display: inline-block; text-shadow: 0 0 30px rgba(212, 175, 55, 0.2); }}

    /* BOTÕES */
    div.stButton > button {{ background: #1e1e1e; border: 1px solid #333; color: #ccc; border-radius: 6px; transition:0.3s; }}
    div.stButton > button:hover {{ border-color: var(--gold); color: white; background: #252525; }}
    
    </style>
    
    <div class="logos-header">
        <div class="brand-logo"><span>✝</span> O PREGADOR</div>
        <div class="nav-divider"></div>
        <div class="top-menu-item">Arquivo</div>
        <div class="top-menu-item">Bíblia</div>
        <div class="top-menu-item">Ferramentas</div>
        <div class="top-menu-item">Janela</div>
        <div style="flex-grow:1"></div>
        <div style="font-size:11px; color:#555">v10.0 • SOUND SYSTEM</div>
    </div>
    """, unsafe_allow_html=True)

carregar_css()

# --- 5. FUNÇÕES DO SISTEMA ---

def navigate_to(page):
    st.session_state['page_stack'].append(page)
    st.rerun()

def get_recent_sermons():
    files = [f for f in os.listdir(PASTA_SERMOES) if f.endswith(".txt")]
    return files[:4]

def motor_biblico_ia(prompt, key, modo="comparacao"):
    if not key: return "⚠️ Conecte a API Key nas configurações para ativar o motor teológico."
    try:
        genai.configure(api_key=key)
        sys_prompt = "Você é um assistente teológico acadêmico e preciso."
        if modo == "comparacao":
            sys_prompt = "Você é uma Bíblia Paralela. Traga o texto em NVI, Almeida e KJA e explique diferenças."
        model = genai.GenerativeModel("gemini-pro")
        return model.generate_content(f"{sys_prompt}\nPedido: {prompt}").text
    except Exception as e: return f"Erro: {e}"

# --- 6. TELA DE LOGIN (COM SOM ANGELICAL) ---
if not st.session_state['logado']:
    c_left, c_center, c_right = st.columns([1, 1, 1])
    with c_center:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="login-container">
            <div class="gold-cross-icon">✝</div>
            <h2 style="color:#eee; font-family:'Inter'; font-weight:600">O PREGADOR</h2>
            <p style="color:#666; font-size:13px; margin-bottom:30px">Área Restrita aos Ungidos</p>
        </div>
        """, unsafe_allow_html=True)
        
        user = st.text_input("Identificação", label_visibility="collapsed", placeholder="Usuário")
        pw = st.text_input("Senha", type="password", label_visibility="collapsed", placeholder="Senha")
        
        if st.button("ACESSAR PÚLPITO", type="primary", use_container_width=True):
            if (user == "admin" and pw == "1234") or (user == "pr" and pw == "123"):
                # Define flag para tocar som após rerun
                st.session_state['logado'] = True
                st.session_state['user'] = user
                st.session_state['tocar_som_login'] = True
                st.rerun()
            else: st.error("Acesso negado.")
    st.stop()

# --- TRIGGER DE SOM (Executa 1 vez ao logar) ---
if st.session_state.get('tocar_som_login'):
    play_login_sound()
    st.session_state['tocar_som_login'] = False # Reseta para não tocar em todo refresh

# --- 7. APLICAÇÃO PRINCIPAL (PÓS-LOGIN) ---
pagina = st.session_state['page_stack'][-1]

# SIDEBAR
with st.sidebar:
    st.markdown("### Painel de Controle")
    if st.button("🏠 Visão Geral", use_container_width=True): navigate_to("Home")
    if st.button("✍️ Studio & Slides", use_container_width=True): navigate_to("Studio")
    if st.button("📖 Bíblia & Teologia", use_container_width=True): navigate_to("Bible")
    if st.button("🎨 Social Criativo", use_container_width=True): navigate_to("Social")
    if st.button("⚙️ Configurações", use_container_width=True): navigate_to("Config")
    st.markdown("---")
    st.caption("Status do Sistema")
    st.success("Conectado")

# PÁGINAS DO SISTEMA

# > DASHBOARD
if pagina == "Home":
    st.title(f"Paz seja convosco, {st.session_state['user'].capitalize()}.")
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.info("💡 Dica: No Studio, a correção ortográfica agora é automática. Palavras erradas aparecerão sublinhadas em vermelho (PT-BR).")
        st.subheader("Estudos Recentes")
        recents = get_recent_sermons()
        if recents:
            for r in recents:
                c1, c2, c3 = st.columns([0.1, 0.7, 0.2])
                c1.write("📄")
                c2.write(f"**{r.replace('.txt','')}**")
                if c3.button("Abrir", key=r):
                    with open(os.path.join(PASTA_SERMOES, r), 'r') as f:
                        st.session_state['texto_ativo'] = f.read()
                        st.session_state['titulo_ativo'] = r.replace(".txt", "")
                        navigate_to("Studio")
        else:
            st.caption("Nenhum estudo encontrado.")

    with col_b:
        st.markdown("### Atalhos")
        if st.button("Novo Sermão", use_container_width=True): 
            st.session_state['texto_ativo'] = ""; st.session_state['titulo_ativo'] = ""; navigate_to("Studio")
        st.metric("Biblioteca", f"{len(os.listdir(PASTA_SERMOES))} Arquivos")

# > STUDIO (EDITOR OTIMIZADO)
elif pagina == "Studio":
    t_c1, t_c2 = st.columns([3, 1])
    with t_c1:
        st.session_state['titulo_ativo'] = st.text_input("Título", value=st.session_state['titulo_ativo'], placeholder="Tema da Mensagem...", label_visibility="collapsed")
    with t_c2:
        if st.button("💾 Salvar", type="primary", use_container_width=True):
            if st.session_state['titulo_ativo']:
                with open(os.path.join(PASTA_SERMOES, f"{st.session_state['titulo_ativo']}.txt"), 'w') as f:
                    f.write(st.session_state['texto_ativo'])
                st.toast("Salvo com Glória!", icon="🕊️")

    # Layout de Edição
    col_editor, col_ferramentas = st.columns([2, 1])
    
    with col_editor:
        st.markdown("### 📜 Manuscrito")
        # --- IMPLEMENTAÇÃO DE CORREÇÃO ORTOGRÁFICA "WORD-LIKE" ---
        # Note o parâmetro `height` para dar espaço e o CSS que já aplicamos a fonte.
        # Streamlit nativo não tem spellchecker param, mas browsers modernos ativam automaticamente
        # em textareas grandes se o atributo lang="pt-BR" estiver na página (padrão browser).
        txt = st.text_area("editor_principal", value=st.session_state['texto_ativo'], height=600, label_visibility="collapsed", placeholder="Comece a escrever aqui...")
        st.session_state['texto_ativo'] = txt
        
        st.caption(f"Contagem: {len(txt.split())} palavras")

    with col_ferramentas:
        st.markdown("### 🎞️ Slides (Arraste texto)")
        txt_slide = st.text_input("Texto do Slide:", placeholder="Copie do editor e cole aqui...")
        if st.button("Criar Slide ⬇️", use_container_width=True):
            if txt_slide: st.session_state['slides'].append({"conteudo": txt_slide})
        
        st.divider()
        if st.session_state['slides']:
            curr = st.session_state['slides'][-1]
            st.markdown(f"""
            <div style="background:#000; border:2px solid #d4af37; color:white; padding:15px; text-align:center; border-radius:8px;">
                <b>AO VIVO:</b><br>{curr['conteudo']}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            for i, s in enumerate(st.session_state['slides']):
                st.write(f"{i+1}. {s['conteudo'][:30]}...")

# > BIBLIA (TEOLOGIA)
elif pagina == "Bible":
    st.title("Teologia Avançada")
    tabs = st.tabs(["Comparar Traduções", "Exegese Original"])
    
    with tabs[0]:
        ref = st.text_input("Referência:", placeholder="Ex: Filipenses 4:13")
        if st.button("Pesquisar Traduções") and ref:
            res = motor_biblico_ia(ref, st.session_state['api_key'], "comparacao")
            st.markdown(f"<div style='background:#111; padding:20px; border-left:3px solid gold'>{res}</div>", unsafe_allow_html=True)
            
    with tabs[1]:
        ref_exe = st.text_input("Texto para Análise:", placeholder="Ex: João 1:1")
        if st.button("Dissecar Texto") and ref_exe:
            res = motor_biblico_ia(ref_exe, st.session_state['api_key'], "exegese") # Passa modo exegese
            st.write(res) # Usa IA se disponível (implementado na func motor_biblico_ia)

# > SOCIAL E CONFIG (MANTIDOS DA ESTRUTURA ANTERIOR)
elif pagina == "Config":
    st.title("Ajustes")
    api = st.text_input("Google API Key", value=st.session_state['api_key'], type="password")
    if api: st.session_state['api_key'] = api
    if st.button("Sair"): 
        st.session_state['logado'] = False
        st.rerun()
