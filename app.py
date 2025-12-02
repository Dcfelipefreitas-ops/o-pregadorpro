import streamlit as st
import os
import sys
import subprocess
import time
import json
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
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="O PREGADOR", layout="wide", page_icon="✝️", initial_sidebar_state="collapsed")

# --- 2. GESTÃO DE DADOS ---
PASTA_RAIZ = "Dados_Pregador"
PASTA_SERMOES = os.path.join(PASTA_RAIZ, "Sermoes")
PASTA_CARE = os.path.join(PASTA_RAIZ, "PastoralCare")
os.makedirs(PASTA_SERMOES, exist_ok=True)
os.makedirs(PASTA_CARE, exist_ok=True)

# SESSÃO
DEFAULTS = {
    "logado": False, "user": "", "page_stack": ["Home"], 
    "texto_ativo": "", "titulo_ativo": "", "slides": [], 
    "api_key": "", "theme_size": 18, 
    "stats_sermoes": len(os.listdir(PASTA_SERMOES)),
    "historico_biblia": [], "humor": "Neutro",
    "tocar_som": False
}
for k, v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k] = v

# --- 3. SISTEMA DE SOM ATMOSFÉRICO (HEAVENLY PAD) ---
def play_heaven_sound():
    # Som ambiental suave, estilo worship/oração, sem trombetas
    sound_url = "https://cdn.pixabay.com/download/audio/2023/09/20/audio_5b98096575.mp3?filename=angelic-ambient-169586.mp3"
    
    st.markdown(f"""
        <audio autoplay style="display:none;">
            <source src="{sound_url}" type="audio/mp3">
        </audio>
        <script>
            // Hack para garantir volume baixo e suave
            var audio = document.querySelector("audio");
            audio.volume = 0.4;
            setTimeout(function(){{ audio.pause(); }}, 6000);
        </script>
    """, unsafe_allow_html=True)

# --- 4. ENGINE TEOLÓGICA IA ---
def cerebro_pregador(prompt, key, context="teologico"):
    if not key: return "⚠️ Conecte a Chave Mestra nas Configurações (Canto Direito)."
    try:
        genai.configure(api_key=key)
        
        sys_msg = "Você é um assistente teológico."
        if context == "emocional":
            humor = st.session_state['humor']
            sys_msg = f"O pastor está se sentindo {humor}. Aja como um mentor espiritual sábio (estilo Eugene Peterson ou Spurgeon). Acolha a emoção, dê um conselho curto e um versículo balsâmico."
        elif context == "adobe":
            sys_msg = "Gere 3 prompts criativos para imagem baseados neste texto bíblico, estilo cinemático e moderno."

        model = genai.GenerativeModel("gemini-pro")
        return model.generate_content(f"{sys_msg}\nEntrada: {prompt}").text
    except Exception as e: return f"Erro: {e}"

# --- 5. UI KIT: APPLE DARK & ADOBE STYLE ---
def carregar_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;500;700&family=Merriweather:ital,wght@0,300;0,700;1,400&display=swap');
    
    /* REMOVER SIDEBAR PADRÃO PARA TER MENU SUPERIOR */
    [data-testid="stSidebar"] {{ display: none; }}
    
    :root {{ --bg: #050507; --panel: #161618; --acc: #0A84FF; --gold: #d4af37; --text: #F5F5F7; }}
    
    .stApp {{ 
        background-color: var(--bg); 
        font-family: 'SF Pro Display', -apple-system, sans-serif; 
        color: var(--text);
        background-image: radial-gradient(circle at 50% 0%, #1a1a2e 0%, #000 60%);
        background-attachment: fixed;
    }}
    
    header, footer {{ display: none !important; }}

    /* MENU HORIZONTAL INTEGRADO (BARRA DE CONTROLE) */
    .control-bar {{
        display: flex; gap: 5px; background: rgba(30,30,30,0.7); backdrop-filter: blur(20px);
        padding: 10px 20px; border-bottom: 1px solid #333; margin: -50px -20px 20px -20px;
        align-items: center; justify-content: space-between;
    }}
    
    /* BOTÕES DO MENU (PARECE ABA DO BROWSER/APP) */
    div.stButton > button {{
        background: transparent; border: none; color: #888; font-weight: 500; font-size: 14px;
        transition: 0.3s; padding: 5px 15px; box-shadow: none;
    }}
    div.stButton > button:hover {{ color: white; background: #333; border-radius: 6px; }}
    div.stButton > button:focus {{ color: var(--gold); border-bottom: 2px solid var(--gold); background:transparent; border-radius: 0; }}

    /* CARD EMOCIONAL (HOME) */
    .mood-card {{
        background: rgba(255,255,255,0.05); border: 1px solid #333; border-radius: 16px;
        padding: 30px; text-align: center; margin-top: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5); backdrop-filter: blur(10px);
    }}

    /* EDITOR "ZEN MODE" */
    .editor-container .stTextArea textarea {{
        background: #000 !important; color: #ddd !important; border: none !important;
        font-family: 'Merriweather', serif; font-size: 19px !important; line-height: 1.8;
        padding: 40px 10vw; /* Centralizado com margem de respiro */
        box-shadow: none;
    }}
    /* Tira a borda vermelha/azul padrão do focus */
    .stTextArea textarea:focus {{ outline: none !important; border: none !important; box-shadow: none !important; }}

    /* ADOBE STYLE SOCIAL */
    .adobe-panel {{ background: #1e1e1e; border-left: 1px solid #333; height: 100%; padding: 20px; }}
    .adobe-canvas {{ 
        background-image: linear-gradient(45deg, #222 25%, transparent 25%), linear-gradient(-45deg, #222 25%, transparent 25%), linear-gradient(45deg, transparent 75%, #222 75%), linear-gradient(-45deg, transparent 75%, #222 75%);
        background-size: 20px 20px; background-color: #333; 
        border: 1px solid #000; border-radius: 4px; display:flex; justify-content:center; align-items:center; min-height: 400px;
    }}

    /* CRUZ LOGIN ANIMADA */
    @keyframes glow {{ 0% {{text-shadow: 0 0 10px #d4af37;}} 50% {{text-shadow: 0 0 30px #ffd700;}} 100% {{text-shadow: 0 0 10px #d4af37;}} }}
    .holy-cross {{ font-size: 70px; color: #d4af37; animation: glow 4s infinite; display: block; text-align: center; }}

    </style>
    """, unsafe_allow_html=True)

carregar_css()

# --- 6. FUNÇÃO NAVEGAÇÃO SUPERIOR ---
def render_menu_top():
    # Cria uma barra escura no topo com os botões
    with st.container():
        # Usando colunas para simular a barra
        c1, c2, c3, c4, c5, c6 = st.columns([0.5, 1, 1, 1, 1, 4])
        
        with c1:
            st.markdown("<span style='color:#d4af37; font-weight:bold; font-size:20px; line-height:40px;'>✝</span>", unsafe_allow_html=True)
        
        # Botões de Navegação que atualizam o estado
        if c2.button("🏠 Início / Cuidado"): navigate("Home")
        if c3.button("✍️ Sermão"): navigate("Studio")
        if c4.button("🎨 Adobe Social"): navigate("Social")
        if c5.button("📚 Teologia"): navigate("Bible")
        # Espaço vazio c6
        
    st.markdown("<div style='height:1px; background:#333; width:100%; margin-bottom:20px'></div>", unsafe_allow_html=True)

def navigate(page):
    st.session_state['page_stack'].append(page)
    st.rerun()

def get_current_page():
    return st.session_state['page_stack'][-1]

# --- 7. TELA DE LOGIN (COM GIF/CINEMATOGRAPH) ---
if not st.session_state['logado']:
    # Fundo Clean Futurista
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown('<div class="holy-cross">✝</div>', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center; color:white; letter-spacing:4px; font-weight:300'>O PREGADOR</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#555; font-size:12px'>SISTEMA PASTORAL INTEGRADO</p>", unsafe_allow_html=True)
        
        with st.form("login_f"):
            u = st.text_input("Identidade", placeholder="...", label_visibility="collapsed")
            p = st.text_input("Senha", type="password", placeholder="...", label_visibility="collapsed")
            if st.form_submit_button("ENTRAR NA GLÓRIA", type="primary", use_container_width=True):
                if (u == "admin" and p == "1234") or (u == "pr" and p == "123"):
                    st.session_state['logado'] = True
                    st.session_state['user'] = u
                    st.session_state['tocar_som'] = True
                    st.rerun()
                else: st.error("Acesso Negado.")
    st.stop()

# --- TRIGGER SOM (PÓS LOGIN) ---
if st.session_state.get('tocar_som'):
    play_heaven_sound()
    st.session_state['tocar_som'] = False

# --- 8. APLICAÇÃO PRINCIPAL ---
render_menu_top() # Barra Fixa Horizontal Integrada
pagina = get_current_page()

# >>> PAGE: HOME / CUIDADO PASTORAL <<<
if pagina == "Home":
    st.markdown(f"## Paz seja convosco, {st.session_state['user'].capitalize()}.")
    
    # 1. CUIDADO PASTORAL (EM PRIMEIRO LUGAR)
    st.markdown('<div class="mood-card">', unsafe_allow_html=True)
    st.subheader("❤️ Como está o seu coração hoje, pastor?")
    
    col_feel = st.columns(5)
    humores = ["Muito Bem ☀️", "Grato 🙏", "Cansado 😓", "Ansioso 🌫️", "No Deserto 🏜️"]
    
    # Seleção de humor
    novo_humor = st.radio("Selecione:", humores, horizontal=True, label_visibility="collapsed")
    if novo_humor != st.session_state['humor']:
        st.session_state['humor'] = novo_humor
    
    # Resposta da IA (Terapêutica)
    if st.session_state['api_key']:
        if st.button("Receber palavra de ânimo"):
            with st.spinner("Ouvindo o alto..."):
                msg = cerebro_pregador("", st.session_state['api_key'], "emocional")
                st.info(msg)
                
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 2. Resumo Rápido
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown("#### 📂 Seus Últimos Sermões")
        sermoes = [f for f in os.listdir(PASTA_SERMOES) if f.endswith('.txt')]
        if sermoes:
            for s in sermoes[:3]:
                if st.button(f"📄 {s.replace('.txt','')}", key=s):
                    with open(os.path.join(PASTA_SERMOES, s), 'r') as f: st.session_state['texto_ativo'] = f.read()
                    st.session_state['titulo_ativo'] = s.replace('.txt','')
                    navigate("Studio")
        else: st.caption("Nenhum sermão escrito.")
        
    with c2:
        st.markdown("#### Configurações Rápidas")
        k = st.text_input("Chave IA (API)", value=st.session_state['api_key'], type="password")
        if k: st.session_state['api_key'] = k


# >>> PAGE: STUDIO (LIMPO & FOCADO) <<<
elif pagina == "Studio":
    # Foco total: Sem gráficos, apenas texto e slides.
    
    # Barra de Título (Discreta)
    c_tit, c_save = st.columns([4, 1])
    with c_tit:
        st.session_state['titulo_ativo'] = st.text_input("Tema da Mensagem", value=st.session_state['titulo_ativo'], placeholder="Título...", label_visibility="collapsed")
    with c_save:
        if st.button("Guardar", type="primary", use_container_width=True):
            if st.session_state['titulo_ativo']:
                with open(os.path.join(PASTA_SERMOES, f"{st.session_state['titulo_ativo']}.txt"), 'w') as f:
                    f.write(st.session_state['texto_ativo'])
                st.toast("Guardado no cofre.", icon="✨")

    # Layout: Editor (80%) | Configs Estudo (20%)
    col_editor, col_ferramentas = st.columns([3, 1])
    
    with col_editor:
        st.markdown('<div class="editor-container">', unsafe_allow_html=True)
        # Editor limpo "Zen"
        txt = st.text_area("zen_editor", value=st.session_state['texto_ativo'], height=700, label_visibility="collapsed", placeholder="Escreva seu sermão aqui...")
        st.session_state['texto_ativo'] = txt
        st.markdown('</div>', unsafe_allow_html=True)

    with col_ferramentas:
        st.markdown("### Configurações de Estudo")
        st.caption("Apenas o essencial para não distrair.")
        
        # Slides Rápidos
        st.info("📺 **Projetor**")
        slide_in = st.text_area("Texto p/ Slide", height=100, placeholder="Cole frase aqui...")
        if st.button("Gerar Slide"):
            st.session_state['slides'].append({"conteudo": slide_in})
            st.toast("Slide Criado")
            
        st.divider()
        st.caption(f"Slides Criados: {len(st.session_state['slides'])}")
        
        if st.toggle("Ver Corretor PT-BR"):
            st.caption("O corretor é nativo do navegador. Linhas vermelhas aparecerão no texto.")


# >>> PAGE: ADOBE SOCIAL CREATIVE <<<
elif pagina == "Social":
    st.markdown("## Creative Cloud (Social)")
    
    # Layout Adobe: Canvas no meio, Ferramentas na direita
    col_canvas, col_props = st.columns([3, 1])
    
    with col_canvas:
        st.markdown('<div class="adobe-canvas"><span style="color:#555">Pré-visualização da Imagem</span></div>', unsafe_allow_html=True)
        
    with col_props:
        st.markdown('<div class="adobe-panel">', unsafe_allow_html=True)
        st.markdown("### Camadas")
        
        txt_layer = st.text_area("Texto Principal", "Jesus é o caminho.")
        font_color = st.color_picker("Cor Texto", "#ffffff")
        bg_upload = st.file_uploader("Fundo (Img)", type=['png','jpg'])
        
        st.divider()
        if st.button("Renderizar (Export)", use_container_width=True, type="primary"):
            st.toast("Renderizando em 1080x1080...")
            # (Aqui entraria a lógica PIL de render, simplificado para manter o foco UI)
            st.success("Imagem pronta (Mockup)")
            
        st.markdown('</div>', unsafe_allow_html=True)


# >>> PAGE: BIBLE (TEOLOGIA) <<<
elif pagina == "Bible":
    st.markdown("## Centro Teológico")
    # Apenas o essencial de pesquisa
    t_ref = st.text_input("Pesquisa Bíblica (Exegese)", placeholder="Ex: Salmo 23")
    if t_ref and st.button("Pesquisar"):
        res = cerebro_pregador(f"Exegese de {t_ref}", st.session_state['api_key'])
        st.write(res)
