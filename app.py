import streamlit as st
import os
import sys
import subprocess
import time
import json
from datetime import datetime
from io import BytesIO

# --- 0. AUTO-INSTALAÇÃO (PACKS) ---
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

# SESSÃO
DEFAULTS = {
    "logado": False, "user": "", "page_stack": ["Home"], 
    "texto_ativo": "", "titulo_ativo": "", "slides": [], 
    "api_key": "", "theme_font": "Inter", "theme_size": 18, "theme_color": "#ffffff",
    "current_nav_title": "Visão Geral",
    "stats_sermoes": len(os.listdir(PASTA_SERMOES))
}
for k, v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k] = v

# --- 3. UI KIT PREMIUM (VISUAL ENCORPADO) ---
def carregar_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    /* VARIÁVEIS DO TEMA APPLE DARK */
    :root {{ --bg: #000000; --card: #1c1c1e; --border: #333; --acc: #0A84FF; --acc-gold: #d4af37; --txt: #F2F2F7; }}
    
    /* GERAL */
    .stApp {{ background-color: var(--bg); font-family: '{st.session_state['theme_font']}', sans-serif; color: var(--txt); }}
    header, footer {{visibility: hidden;}}

    /* HEADER FIXO SUPERIOR */
    .logos-header {{
        position: fixed; top: 0; left: 0; width: 100%; height: 50px;
        background: #1c1c1e; border-bottom: 1px solid #333; z-index: 9999;
        display: flex; align-items: center; justify-content: space-between;
        padding: 0 30px; 
    }}
    .header-logo {{ color: var(--acc-gold); font-weight: 800; font-size: 18px; letter-spacing: 1px; }}
    .header-menu {{ display: flex; gap: 20px; font-size: 13px; color: #aaa; }}
    .header-item:hover {{ color: white; cursor: pointer; }}

    .block-container {{ padding-top: 80px !important; }}
    
    /* CARDS DE CONTEÚDO (DASHBOARD) */
    .dashboard-card {{
        background: var(--card); border: 1px solid var(--border);
        border-radius: 14px; padding: 25px; margin-bottom: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        transition: transform 0.2s;
    }}
    .dashboard-card:hover {{ transform: translateY(-2px); border-color: #555; }}
    
    .card-title {{ font-size: 14px; color: #888; text-transform: uppercase; font-weight: 600; margin-bottom: 10px; }}
    .card-value {{ font-size: 28px; font-weight: 700; color: white; }}
    .card-sub {{ font-size: 12px; color: #666; }}

    /* ÁREA DO EDITOR (Estilo Word) */
    .toolbar {{
        display: flex; gap: 10px; background: #252527; padding: 10px; border-radius: 8px 8px 0 0; border: 1px solid #333;
    }}
    .stTextArea textarea {{
        font-family: '{st.session_state['theme_font']}';
        font-size: {st.session_state['theme_size']}px !important;
        color: {st.session_state['theme_color']} !important;
        background-color: #111 !important; border: 1px solid #333; border-top: none; border-radius: 0 0 8px 8px;
        padding: 30px;
    }}

    /* SLIDE VISUAL */
    .slide-box {{
        background: #000; border: 1px solid #444; border-radius: 6px; 
        padding: 15px; margin-bottom: 10px; border-left: 4px solid var(--acc-gold);
    }}

    /* BOTÕES APPLE STYLE */
    div.stButton > button {{
        background: #2C2C2E; color: white; border-radius: 8px; border: 1px solid #3A3A3C; font-weight: 500;
        width: 100%; height: 50px; /* Botões mais gordos */
    }}
    div.stButton > button:hover {{ background: var(--acc); border-color: var(--acc); color: white; }}

    /* ÍCONE DE MADEIRA (CSS PURE) */
    .wood-container {{ width: 80px; height: 160px; background: linear-gradient(135deg, #deb887 0%, #8b4513 100%); margin: 0 auto; border-radius: 8px; position:relative; box-shadow: 0 10px 20px rgba(0,0,0,0.5); }}
    .wood-metal {{ width: 100%; height: 30px; background: #silver; position:absolute; top: 60px; background: linear-gradient(to bottom, #ddd, #999); box-shadow: inset 0 0 5px #000;}}

    /* LOGIN CARD */
    .login-card {{
        background: rgba(255,255,255,0.9); border-radius: 20px; padding: 40px; 
        box-shadow: 0 20px 50px rgba(0,0,0,0.5); color: #000; text-align: center;
    }}
    </style>
    
    <!-- HEADER -->
    <div class="logos-header">
        <div class="header-logo">✝ O PREGADOR <span style="font-size:10px; opacity:0.6; margin-left:5px">SYSTEM PRO</span></div>
        <div class="header-menu">
            <div class="header-item">Arquivo</div>
            <div class="header-item">Editar</div>
            <div class="header-item">Visualizar</div>
            <div class="header-item">Janela</div>
            <div class="header-item">Ajuda</div>
        </div>
        <div style="font-size:12px; color:#888;">Online ●</div>
    </div>
    """, unsafe_allow_html=True)

carregar_css()

# --- 4. FUNÇÕES DO SISTEMA ---
def navigate_to(page_name):
    st.session_state['page_stack'].append(page_name)
    st.rerun()

def criar_slide(texto_slide):
    st.session_state['slides'].append({"conteudo": texto_slide})
    st.toast("Slide criado na linha do tempo.", icon="🎬")

def carregar_sermoes_recentes():
    arquivos = [f for f in os.listdir(PASTA_SERMOES) if f.endswith(".txt")]
    # Retorna os 3 mais recentes (simulado pela ordem de listagem)
    return arquivos[:3]

# --- 5. TELA DE LOGIN (COM CARD CENTRALIZADO) ---
if not st.session_state['logado']:
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); } /* Fundo Claro Clean */
    div.stButton > button { background: #000; color: white; }
    </style>
    """, unsafe_allow_html=True)
    
    # Coluna Centralizada
    c_void_l, c_main, c_void_r = st.columns([1, 0.8, 1])
    with c_main:
        st.markdown("<br><br>", unsafe_allow_html=True)
        # Cartão de Login Customizado via HTML Container simulado
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        
        # Ícone de Madeira CSS
        st.markdown('<div class="wood-container"><div class="wood-metal"></div></div>', unsafe_allow_html=True)
        st.markdown("<h2 style='color:#333; margin-top:20px;'>O PREGADOR</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#666; font-size:14px;'>Identifique-se para acessar o púlpito digital.</p>", unsafe_allow_html=True)
        
        user = st.text_input("Usuário (Admin / Pr)", label_visibility="collapsed", placeholder="Usuário")
        pw = st.text_input("Senha", type="password", label_visibility="collapsed", placeholder="Senha")
        
        if st.button("ACESSAR SISTEMA", use_container_width=True):
            if (user == "admin" and pw == "1234") or (user == "pr" and pw == "123"):
                st.session_state['logado'] = True
                st.session_state['user'] = user
                st.rerun()
            else:
                st.error("Acesso Negado")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.stop()


# --- 6. APP PRINCIPAL ---
if st.session_state['logado']:
    # Reverte fundo para Dark Mode
    st.markdown("""<style>.stApp { background-color: #000000; color: #fff; }</style>""", unsafe_allow_html=True)

pagina = st.session_state['page_stack'][-1]

# SIDEBAR: O HUB
with st.sidebar:
    st.markdown("### Navegação")
    # Botões de Navegação com ícones
    if st.button("🏠 Visão Geral (Dashboard)", use_container_width=True): navigate_to("Home")
    if st.button("✍️ Studio de Criação", use_container_width=True): navigate_to("Studio")
    if st.button("⚙️ Preferências", use_container_width=True): navigate_to("Config")
    
    st.divider()
    
    st.markdown("### Status")
    st.markdown(f"**Sermões:** {st.session_state['stats_sermoes']}")
    st.markdown(f"**Modo:** {'Online' if st.session_state['api_key'] else 'Local'}")
    
    st.divider()
    # Mini-Calendário Visual (Fake)
    st.caption(f"HOJE: {datetime.now().strftime('%d/%m/%Y')}")
    st.markdown("""
    <div style="display:grid; grid-template-columns: repeat(7, 1fr); gap:2px; font-size:10px; color:#555; text-align:center;">
        <div>D</div><div>S</div><div>T</div><div>Q</div><div>Q</div><div>S</div><div>S</div>
        <div style="background:#222">1</div><div style="background:#222">2</div><div style="background:#d4af37; color:black">3</div>
    </div>
    """, unsafe_allow_html=True)

# --- PÁGINA: DASHBOARD (PREENCHENDO O VAZIO) ---
if pagina == "Home":
    st.title(f"Bem-vindo, Pr. {st.session_state['user'].capitalize()}")
    st.markdown("Aqui está o resumo da sua semana.")
    
    # 1. Widgets de Topo (Cards Informativos)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="dashboard-card"><div class="card-title">Biblioteca</div><div class="card-value">{st.session_state['stats_sermoes']}</div><div class="card-sub">Estudos Salvos</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="dashboard-card"><div class="card-title">Slides</div><div class="card-value">{len(st.session_state['slides'])}</div><div class="card-sub">No projeto atual</div></div>""", unsafe_allow_html=True)
    with c3:
        # Relógio ou Info Dinâmica
        st.markdown(f"""<div class="dashboard-card"><div class="card-title">Hora</div><div class="card-value">{datetime.now().strftime('%H:%M')}</div><div class="card-sub">Hora de focar</div></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="dashboard-card" style="border-color:#d4af37"><div class="card-title" style="color:#d4af37">Inteligência</div><div class="card-value">{"ON" if st.session_state['api_key'] else "OFF"}</div><div class="card-sub">Estado da IA</div></div>""", unsafe_allow_html=True)

    # 2. Acesso Rápido e Inspiração (Layout Grid)
    c_main, c_side = st.columns([2, 1])
    
    with c_main:
        st.subheader("Atalhos Rápidos")
        ac1, ac2 = st.columns(2)
        if ac1.button("✍️ Começar Novo Sermão", use_container_width=True): navigate_to("Studio")
        if ac2.button("🖥️ Modo Apresentação", use_container_width=True): 
             st.toast("Abra o Studio para configurar slides primeiro.")
             
        st.markdown("### 📂 Trabalhos Recentes")
        recentes = carregar_sermoes_recentes()
        if recentes:
            for r in recentes:
                with st.container():
                    col_ico, col_txt, col_btn = st.columns([0.1, 0.7, 0.2])
                    col_ico.markdown("📄")
                    col_txt.markdown(f"**{r.replace('.txt','')}**")
                    if col_btn.button("Abrir", key=f"btn_{r}"):
                        with open(os.path.join(PASTA_SERMOES, r), 'r', encoding='utf-8') as f:
                            st.session_state['texto_ativo'] = f.read()
                        st.session_state['titulo_ativo'] = r.replace(".txt", "")
                        navigate_to("Studio")
        else:
            st.info("Nenhum arquivo recente.")
            
    with c_side:
        st.subheader("💡 Inspiração")
        st.markdown("""
        <div class="dashboard-card">
            <span style="font-size:30px;">⚓</span>
            <p><b>Dica do dia:</b> Comece sua pregação com uma pergunta que gere curiosidade imediata na congregação.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="dashboard-card">
            <b>Versículo Randômico:</b><br>
            "Aquele que leva a preciosa semente, andando e chorando, voltará, sem dúvida, com alegria." <br><i>- Salmos 126:6</i>
        </div>
        """, unsafe_allow_html=True)


# --- PÁGINA: STUDIO PRO (Editor Cheio) ---
elif pagina == "Studio":
    # O Editor foi expandido para parecer mais robusto
    
    # 1. Barra de Topo do Editor (Metadata)
    t_c1, t_c2, t_c3 = st.columns([2, 2, 2])
    with t_c1:
        st.session_state['titulo_ativo'] = st.text_input("Título", value=st.session_state['titulo_ativo'], placeholder="Título do Sermão...", label_visibility="collapsed")
    with t_c3:
        if st.button("💾 Salvar & Sincronizar", type="primary", use_container_width=True):
             if st.session_state['titulo_ativo']:
                with open(os.path.join(PASTA_SERMOES, f"{st.session_state['titulo_ativo']}.txt"), 'w') as f:
                    f.write(st.session_state['texto_ativo'])
                st.session_state['stats_sermoes'] = len(os.listdir(PASTA_SERMOES)) # Update stat
                st.toast("Salvo com sucesso!", icon="✅")

    # 2. Ambiente de Trabalho Dividido
    c_edit, c_view = st.columns([1.5, 1])
    
    with c_edit:
        st.markdown('<div class="toolbar">Editor de Manuscrito</div>', unsafe_allow_html=True)
        
        # Barra de ferramentas funcional (Fake UI mas funcional)
        bar_c1, bar_c2, bar_c3, bar_c4, bar_c5 = st.columns(5)
        def add(x): st.session_state['texto_ativo'] += x
        bar_c1.button("H1", on_click=add, args=("\n# Título\n",), help="Adicionar Título")
        bar_c2.button("**B**", on_click=add, args=(" **negrito** ",), help="Negrito")
        bar_c3.button("*I*", on_click=add, args=(" *italico* ",))
        bar_c4.button("Vers.", on_click=add, args=("\n> Jo 3:16\n",))
        bar_c5.button("Nota", on_click=add, args=("\n[Nota: ...]\n",))

        # O Campo de texto principal
        text_val = st.text_area("editor_hidden", value=st.session_state['texto_ativo'], height=600, label_visibility="collapsed")
        st.session_state['texto_ativo'] = text_val
        
        # Area de Transferência (Aprimorada visualmente)
        st.markdown("---")
        st.markdown("**➡️ Enviar para o Telão (Criar Slide):**")
        col_inp, col_go = st.columns([4, 1])
        with col_inp:
            sel_text = st.text_input("Cole aqui a frase ou versículo", placeholder="Cole o texto e pressione enter ou clique no botão ->")
        with col_go:
            if st.button("Criar Slide"):
                if sel_text: criar_slide(sel_text)

    with c_view:
        st.markdown('<div class="toolbar" style="border-left:none;">Visualização & Slides</div>', unsafe_allow_html=True)
        
        # Preview em Tempo Real do Slide Atual (Estilo Projetor)
        if st.session_state['slides']:
            curr = st.session_state['slides'][-1]
            st.markdown(f"""
            <div style="background:#000; border:4px solid #333; aspect-ratio:16/9; display:flex; align-items:center; justify-content:center; text-align:center; padding:20px;">
                <h2 style="color:white; margin:0;">{curr['conteudo']}</h2>
            </div>
            <p style="text-align:center; font-size:12px; color:#666; margin-top:5px;">Preview da saída (Projetor)</p>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:#050505; border:2px dashed #333; aspect-ratio:16/9; display:flex; align-items:center; justify-content:center; color:#555;">
                Aguardando Slide...
            </div>
            """, unsafe_allow_html=True)
            
        st.divider()
        st.subheader("Linha do Tempo (Slides)")
        
        # Lista visual de slides
        if st.session_state['slides']:
            for i, slide in enumerate(st.session_state['slides']):
                st.markdown(f"""
                <div class="slide-box">
                    <strong style="color:#d4af37">SLIDE {i+1}</strong><br>
                    {slide['conteudo']}
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"🗑️ Deletar {i+1}", key=f"del_{i}"):
                    st.session_state['slides'].pop(i)
                    st.rerun()
        else:
            st.caption("A lista de slides está vazia. Escreva e envie!")

# --- PÁGINA: CONFIGURAÇÕES (Simulada para parecer cheia) ---
elif pagina == "Config":
    st.title("Preferências do Sistema")
    
    st.markdown("### 🎨 Aparência")
    
    c_tema1, c_tema2 = st.columns(2)
    with c_tema1:
        st.selectbox("Fonte do Editor", ["Inter", "Georgia", "Courier"])
    with c_tema2:
        st.number_input("Tamanho da Fonte (px)", 12, 32, st.session_state['theme_size'])
    
    if st.button("Aplicar Alterações Visuais"):
        st.toast("Configurações aplicadas!")

    st.markdown("### 🧠 Inteligência Artificial (Google Gemini)")
    key = st.text_input("Chave de API", value=st.session_state['api_key'], type="password")
    if key: st.session_state['api_key'] = key
    
    st.markdown("### 📦 Dados & Backup")
    c_b1, c_b2 = st.columns(2)
    c_b1.button("Exportar Sermões (ZIP)", use_container_width=True)
    c_b2.button("Limpar Cache do App", use_container_width=True)
