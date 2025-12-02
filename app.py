import streamlit as st
import os
import sys
import subprocess
import time
import json
import base64
from datetime import datetime
from io import BytesIO

# --- 0. DEPENDÊNCIAS ---
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
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="O PREGADOR", layout="wide", page_icon="✝️", initial_sidebar_state="collapsed")

# --- 2. GESTÃO DE DADOS ---
PASTA_RAIZ = "Dados_Pregador"
PASTA_SERMOES = os.path.join(PASTA_RAIZ, "Sermoes")
PASTA_CARE = os.path.join(PASTA_RAIZ, "PastoralCare")
os.makedirs(PASTA_SERMOES, exist_ok=True)
os.makedirs(PASTA_CARE, exist_ok=True)

# SESSÃO & PERFIL
DEFAULTS = {
    "logado": False, "user": "", "page_stack": ["Dashboard"], 
    "texto_ativo": "", "titulo_ativo": "", "slides": [], 
    "api_key": "", "theme_size": 18, 
    "stats_sermoes": len(os.listdir(PASTA_SERMOES)),
    "historico_biblia": [], "humor": "Neutro",
    "tocar_som": False,
    "user_avatar": None, # Armazena bytes da foto
    "user_name": "Pastor"
}
for k, v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k] = v

# --- 3. HELPER: CONVERTER IMAGEM PARA EXIBIÇÃO ---
def img_to_base64(img_bytes):
    encoded = base64.b64encode(img_bytes).decode()
    return f"data:image/png;base64,{encoded}"

# --- 4. SISTEMA DE SOM ATMOSFÉRICO ---
def play_heaven_sound():
    sound_url = "https://cdn.pixabay.com/download/audio/2023/09/20/audio_5b98096575.mp3?filename=angelic-ambient-169586.mp3"
    st.markdown(f"""
        <audio autoplay style="display:none;">
            <source src="{sound_url}" type="audio/mp3">
        </audio>
        <script>
            var audio = document.querySelector("audio");
            audio.volume = 0.4;
            setTimeout(function(){{ audio.pause(); }}, 6000);
        </script>
    """, unsafe_allow_html=True)

# --- 5. ENGINE TEOLÓGICA IA ---
def cerebro_pregador(prompt, key, context="teologico"):
    if not key: return "⚠️ Sistema Offline: Conecte a API Key em Settings."
    try:
        genai.configure(api_key=key)
        sys_msg = "Você é um assistente teológico de alta precisão."
        if context == "emocional":
            humor = st.session_state['humor']
            sys_msg = f"O usuário está sentindo: {humor}. Responda com sabedoria pastoral profunda, calma e bíblica."
        elif context == "creative":
            sys_msg = "Atue como um diretor de arte cristão. Sugira conceitos visuais modernos."

        model = genai.GenerativeModel("gemini-pro")
        return model.generate_content(f"{sys_msg}\nInput: {prompt}").text
    except Exception as e: return f"Erro no Link Neural: {e}"

# --- 6. UI KIT: TECHNOLOGICAL DESIGN (QUANTUM STYLE) ---
def carregar_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=JetBrains+Mono:wght@400&family=Cinzel:wght@400;700&display=swap');
    
    [data-testid="stSidebar"] {{ display: none; }}
    header, footer {{ display: none !important; }}
    
    :root {{ --bg-deep: #080808; --panel: #111111; --gold: #D4AF37; --text: #EAEAEA; --border: #333; }}
    
    .stApp {{ 
        background-color: var(--bg-deep); 
        color: var(--text);
        font-family: 'Inter', sans-serif;
    }}

    /* BARRA HORIZONTAL INTELIGENTE (TOP BAR) */
    .top-nav-container {{
        background: rgba(10, 10, 10, 0.9); backdrop-filter: blur(15px);
        border-bottom: 1px solid var(--border);
        padding: 10px 20px;
        position: fixed; top: 0; left: 0; right: 0; z-index: 1000;
        display: flex; align-items: center; justify-content: space-between;
    }}
    
    /* BOTÕES DO MENU (TAB STYLE) */
    div.stButton > button {{
        background: transparent; border: none; color: #888; 
        font-size: 14px; font-weight: 500; text-transform: uppercase; letter-spacing: 1px;
        transition: all 0.3s; margin: 0 5px;
    }}
    div.stButton > button:hover {{ color: white; background: rgba(255,255,255,0.05); border-radius: 4px; }}
    div.stButton > button:focus {{ color: var(--gold); }}

    /* LOGO TECH */
    .logo-tech {{ font-family: 'Cinzel', serif; color: var(--gold); font-weight: 700; font-size: 18px; letter-spacing: 2px; }}

    /* CARDS TECNOLÓGICOS */
    .tech-card {{
        background: linear-gradient(180deg, rgba(25,25,25,0.6) 0%, rgba(10,10,10,0.8) 100%);
        border: 1px solid var(--border); border-radius: 12px;
        padding: 25px; margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    }}
    
    /* AVATAR BALL (Lado Direito) */
    .profile-ball {{
        width: 40px; height: 40px; border-radius: 50%; 
        border: 2px solid var(--border); 
        background-size: cover; background-position: center;
        transition: transform 0.2s;
    }}
    .profile-ball:hover {{ border-color: var(--gold); transform: scale(1.1); cursor: pointer; }}

    /* EDITOR LIMPO */
    .stTextArea textarea {{
        background: #000 !important; color: #ccc !important; border: 1px solid var(--border) !important;
        font-family: 'Georgia', serif; font-size: 19px; line-height: 1.8;
    }}
    
    /* ANIMAÇÃO CRUZ LOGIN */
    @keyframes pulse-gold {{ 0% {{ box-shadow: 0 0 0 0 rgba(212, 175, 55, 0.4); }} 70% {{ box-shadow: 0 0 0 20px rgba(212, 175, 55, 0); }} 100% {{ box-shadow: 0 0 0 0 rgba(212, 175, 55, 0); }} }}
    .login-circle {{
        width: 100px; height: 100px; border-radius: 50%; border: 2px solid var(--gold);
        display: flex; align-items: center; justify-content: center; margin: 0 auto 20px auto;
        animation: pulse-gold 3s infinite;
    }}
    </style>
    """, unsafe_allow_html=True)

carregar_css()

# --- 7. NAVEGAÇÃO SUPERIOR INTELIGENTE ---
def render_navbar():
    with st.container():
        # Layout: Logo | Menu Items | Perfil
        c1, c2, c3, c4, c5, c6, c_profile = st.columns([1.5, 1, 1, 1, 1, 3, 0.5])
        
        with c1:
            st.markdown(f'<div class="logo-tech">O PREGADOR <span style="font-size:10px; opacity:0.5">V12</span></div>', unsafe_allow_html=True)
        
        # Menu Navigation
        if c2.button("Dashboard"): st.session_state['page_stack'].append("Dashboard"); st.rerun()
        if c3.button("Sermons"): st.session_state['page_stack'].append("Sermons"); st.rerun()
        if c4.button("Media Lab"): st.session_state['page_stack'].append("Media"); st.rerun()
        if c5.button("Theology"): st.session_state['page_stack'].append("Theology"); st.rerun()
        
        # Perfil (A "Bolinha")
        with c_profile:
            # Se tiver avatar, mostra imagem, se não, um icone
            if st.session_state['user_avatar']:
                # Truque para fazer o botão parecer a imagem
                # Usamos HTML para renderizar, mas um botão invisível do streamlit por cima é difícil
                # Solução: Botão com texto vazio e CSS de background ou st.image clicável (não nativo).
                # Solução melhor: Um botão simples "PERFIL" que leva para config
                if st.button("👤"):
                    st.session_state['page_stack'].append("Settings")
                    st.rerun()
            else:
                if st.button("👤"): 
                    st.session_state['page_stack'].append("Settings")
                    st.rerun()

    st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True) # Espaçador

def get_page():
    return st.session_state['page_stack'][-1]

# --- 8. TELA DE LOGIN (ATMOSFÉRICA) ---
if not st.session_state['logado']:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 0.8, 1])
    with c2:
        # Visual Tecnológico
        st.markdown("""
        <div class="login-circle"><span style="font-size:40px; color:#d4af37;">✝</span></div>
        <h3 style="text-align:center; font-family:'Cinzel'; letter-spacing:4px; margin-bottom:0px;">O PREGADOR</h3>
        <p style="text-align:center; color:#555; font-size:12px; margin-bottom:30px;">ACCESS CONTROL SYSTEM</p>
        """, unsafe_allow_html=True)
        
        with st.form("access_gate"):
            user = st.text_input("Identity", label_visibility="collapsed", placeholder="Usuário")
            pw = st.text_input("Keyphrase", type="password", label_visibility="collapsed", placeholder="Senha")
            
            if st.form_submit_button("CONNECT", type="primary", use_container_width=True):
                if (user == "admin" and pw == "1234") or (user == "pr" and pw == "123"):
                    st.session_state['logado'] = True
                    st.session_state['user'] = user
                    st.session_state['tocar_som'] = True
                    st.rerun()
                else:
                    st.error("Credenciais não reconhecidas.")
    st.stop()

# Trigger Som
if st.session_state['tocar_som']:
    play_heaven_sound()
    st.session_state['tocar_som'] = False

# --- 9. PÁGINAS DO SISTEMA ---
render_navbar()
page = get_page()

# >>> PAGE: DASHBOARD (HOME) <<<
if page == "Dashboard":
    
    # Header Boas-vindas
    st.markdown(f"## Olá, {st.session_state['user_name']}.")
    
    # Área de Cuidado Pastoral (No topo, como pedido)
    st.markdown('<div class="tech-card">', unsafe_allow_html=True)
    c_mood, c_info = st.columns([2, 1])
    
    with c_mood:
        st.caption("ANÁLISE DE ESTADO VITAL (ESPIRITUAL/EMOCIONAL)")
        # Mood Selector Moderno
        humores = ["Plenitude 🕊️", "Gratidão 🙏", "Cansaço 🌙", "Ansiedade 🌊", "Deserto 🏜️"]
        novo_h = st.radio("Sintonia de hoje:", humores, horizontal=True, label_visibility="collapsed")
        
        if novo_h != st.session_state['humor']:
            st.session_state['humor'] = novo_h
            
        # IA Response
        if st.button("Receber palavra de alinhamento", type="secondary"):
            if st.session_state['api_key']:
                with st.spinner("Sincronizando..."):
                    msg = cerebro_pregador("", st.session_state['api_key'], "emocional")
                    st.success(msg)
            else:
                st.warning("IA desconectada. Configure em Settings.")

    with c_info:
        if st.session_state['user_avatar']:
            # Exibe foto de perfil renderizada se houver
            st.image(st.session_state['user_avatar'], width=100)
        st.markdown(f"**Projetos Ativos:** {len(os.listdir(PASTA_SERMOES))}")
        st.caption(f"Data: {datetime.now().strftime('%d/%m/%Y')}")
    st.markdown('</div>', unsafe_allow_html=True)

    # Acesso Rápido
    st.subheader("Central de Acesso")
    c1, c2, c3 = st.columns(3)
    if c1.button("📝 Esboco", use_container_width=True): 
        st.session_state['texto_ativo'] = ""
        st.session_state['titulo_ativo'] = ""
        st.session_state['page_stack'].append("Sermons")
        st.rerun()
    c2.button("👥 Base de Membros (Breve)", use_container_width=True, disabled=True)
    c3.button("📊 Relatórios", use_container_width=True, disabled=True)


# >>> PAGE: SERMONS (STUDIO) <<<
elif page == "Sermons":
    # Layout focado: Sem distrações.
    c_tit, c_act = st.columns([4, 1])
    with c_tit:
        st.session_state['titulo_ativo'] = st.text_input("Tema da Mensagem", value=st.session_state['titulo_ativo'], placeholder="Título...", label_visibility="collapsed")
    with c_act:
        if st.button("SALVAR", type="primary", use_container_width=True):
            if st.session_state['titulo_ativo']:
                with open(os.path.join(PASTA_SERMOES, f"{st.session_state['titulo_ativo']}.txt"), 'w') as f:
                    f.write(st.session_state['texto_ativo'])
                st.toast("Dados preservados.", icon="💾")

    # Área de Editor + Slides
    c_ed, c_sl = st.columns([2.5, 1])
    
    with c_ed:
        st.caption("MANUSCRITO PRINCIPAL")
        txt = st.text_area("editor", value=st.session_state['texto_ativo'], height=600, label_visibility="collapsed")
        st.session_state['texto_ativo'] = txt
    
    with c_sl:
        st.caption("LINHA DO TEMPO (PROJETOR)")
        # Slide Add
        new_s = st.text_area("Texto Slide", height=80, placeholder="Copie trecho...")
        if st.button("Gerar Slide", use_container_width=True):
            st.session_state['slides'].append({"conteudo": new_s})
        
        st.divider()
        if st.session_state['slides']:
            for i, s in enumerate(st.session_state['slides']):
                st.markdown(f"<div style='border-left:2px solid #D4AF37; padding-left:10px; margin-bottom:5px; font-size:12px; color:#aaa'>{s['conteudo'][:40]}...</div>", unsafe_allow_html=True)


# >>> PAGE: MEDIA LAB (ANTIGO SOCIAL) <<<
elif page == "Media":
    st.markdown("## Media Lab")
    
    col_c, col_t = st.columns([2, 1])
    
    with col_c:
        # Simulação Canvas
        st.markdown("""
        <div style="background-image: linear-gradient(45deg, #1a1a1a 25%, transparent 25%), linear-gradient(-45deg, #1a1a1a 25%, transparent 25%), linear-gradient(45deg, transparent 75%, #1a1a1a 75%), linear-gradient(-45deg, transparent 75%, #1a1a1a 75%);
        background-size: 20px 20px; background-color: #222; width:100%; height:400px; border-radius:8px; display:flex; align-items:center; justify-content:center; border:1px solid #333">
            <span style="color:#555">CANVAS PREVIEW</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col_t:
        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
        st.caption("FERRAMENTAS CRIATIVAS")
        texto_post = st.text_area("Texto do Post")
        bg_post = st.file_uploader("Imagem Fundo", type=['png','jpg'])
        if st.button("Renderizar Imagem", type="primary"):
            st.toast("Processando...")
            st.success("Imagem gerada (Simulação)")
        st.markdown('</div>', unsafe_allow_html=True)


# >>> PAGE: THEOLOGY (BÍBLIA) <<<
elif page == "Theology":
    st.markdown("## Central Teológica")
    
    st.caption("Pesquisa Avançada (Exegese / Comparação)")
    
    col_search, col_btn = st.columns([4, 1])
    termo = col_search.text_input("Referência ou Tema", placeholder="Ex: Romanos 8", label_visibility="collapsed")
    
    if col_btn.button("Pesquisar", use_container_width=True):
        res = cerebro_pregador(f"Exegese de {termo}", st.session_state['api_key'])
        st.markdown(f"<div class='tech-card'>{res}</div>", unsafe_allow_html=True)


# >>> PAGE: SETTINGS (CONFIGURAÇÃO PERFIL) <<<
elif page == "Settings":
    st.markdown("## Configurações do Sistema")
    
    st.markdown('<div class="tech-card">', unsafe_allow_html=True)
    st.subheader("👤 Perfil & Identidade")
    
    nome_in = st.text_input("Seu Nome / Título", value=st.session_state['user_name'])
    if nome_in: st.session_state['user_name'] = nome_in
    
    c_pic, c_cam = st.columns(2)
    with c_pic:
        st.caption("Upload Foto")
        pic = st.file_uploader("Carregar arquivo", type=['png','jpg','jpeg'], label_visibility="collapsed")
        if pic:
            st.session_state['user_avatar'] = Image.open(pic)
            
    with c_cam:
        st.caption("Tirar Foto")
        cam = st.camera_input("Webcam", label_visibility="collapsed")
        if cam:
            st.session_state['user_avatar'] = Image.open(cam)
            
    if st.session_state['user_avatar']:
        st.success("Avatar Atualizado! Ele aparecerá no menu.")
        
    st.divider()
    
    st.subheader("🔑 Conectividade (IA)")
    k = st.text_input("Google API Key", value=st.session_state['api_key'], type="password")
    if k: st.session_state['api_key'] = k
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("Logoff"):
        st.session_state['logado'] = False
        st.rerun()
