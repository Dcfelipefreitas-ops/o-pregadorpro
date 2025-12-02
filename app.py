import streamlit as st
import os
import sys
import subprocess
import time
import json
from datetime import datetime
from io import BytesIO

# --- 0. DEPENDÊNCIAS (Sem Alteração) ---
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

# --- 1. CONFIG DO APP ---
st.set_page_config(page_title="O PREGADOR", layout="wide", page_icon="✝️", initial_sidebar_state="expanded")

# --- 2. SISTEMA DE DADOS (Pastas) ---
PASTA_RAIZ = "Dados_Pregador"
PASTA_SERMOES = os.path.join(PASTA_RAIZ, "Sermoes")
PASTA_CARE = os.path.join(PASTA_RAIZ, "PastoralCare")
os.makedirs(PASTA_SERMOES, exist_ok=True)
os.makedirs(PASTA_CARE, exist_ok=True)

# INICIALIZAÇÃO DA SESSÃO
DEFAULTS = {
    "logado": False, "user": "", "page_stack": ["Home"], 
    "texto_ativo": "", "titulo_ativo": "", "slides": [], 
    "api_key": "", "theme_font": "Merriweather", "theme_size": 20, "theme_color": "#e0e0e0",
    "current_nav_title": "Visão Geral",
    "stats_sermoes": len(os.listdir(PASTA_SERMOES))
}
for k, v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k] = v

# --- 3. ESTILIZAÇÃO UI/UX PRO (CROSS EDITION) ---
def carregar_css():
    st.markdown(f"""
    <style>
    /* IMPORTS: FONTE RICA (SERIFADA) E MODERNA */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700&family=Merriweather:ital,wght@0,300;0,700;1,400&display=swap');
    
    /* VARIÁVEIS DO TEMA */
    :root {{ 
        --bg-main: #050505; --bg-card: #141414; 
        --border: #2a2a2a; --gold: #d4af37; 
        --text: #eeeeee; --blue-acc: #3b82f6; 
    }}
    
    /* ESTILO GERAL APP */
    .stApp {{ background-color: var(--bg-main); font-family: 'Inter', sans-serif; color: var(--text); }}
    
    /* ESCONDER COMPONENTES PADRÃO */
    header, footer, .stDeployButton {{ display: none; visibility: hidden; }}
    
    /* === STUDIO EDITOR CSS (ESTILO WYSIWYG) === */
    /* Toolbar Superior (Parecida com Word/Docs) */
    .wysiwyg-toolbar {{
        display: flex; gap: 8px; align-items: center; padding: 10px 15px;
        background: #1f1f1f; border-bottom: 1px solid #333;
        border-radius: 10px 10px 0 0; position: sticky; top: 0; z-index: 100;
    }}
    
    .toolbar-btn {{
        background: #2b2b2b; color: #ccc; border: 1px solid #444; 
        border-radius: 5px; padding: 5px 12px; font-size: 14px; font-weight: 600; cursor: pointer;
        transition: all 0.2s;
    }}
    .toolbar-btn:hover {{ background: #3b3b3b; color: var(--gold); border-color: var(--gold); }}

    /* Área de Texto Principal */
    .stTextArea textarea {{
        font-family: '{st.session_state['theme_font']}', serif;
        font-size: {st.session_state['theme_size']}px !important;
        line-height: 1.7; color: {st.session_state['theme_color']} !important;
        background-color: #121212 !important; border: 1px solid #333 !important; 
        border-top: none !important; /* Cola na toolbar */
        border-radius: 0 0 10px 10px;
        padding: 40px; box-shadow: inset 0 0 20px rgba(0,0,0,0.5);
    }}
    
    /* === SLIDE TIMELINE (LATERAL DIREITA) === */
    .timeline-container {{ 
        border-left: 1px solid #333; height: 100%; padding-left: 15px; 
    }}
    .slide-card-mini {{
        background: #000; border: 1px solid #444; border-left: 3px solid var(--gold);
        padding: 15px; margin-bottom: 12px; border-radius: 6px; position: relative;
    }}
    .slide-number {{ position: absolute; top: 5px; right: 8px; color: #666; font-size: 10px; }}
    .slide-content-preview {{ font-size: 13px; color: #bbb; line-height: 1.4; font-family: 'Inter'; }}

    /* === HEADER NAVEGAÇÃO === */
    .nav-bar {{
        display: flex; align-items: center; justify-content: space-between;
        background: rgba(20,20,20, 0.95); backdrop-filter: blur(10px);
        height: 60px; width: 100%; position: fixed; top: 0; left: 0; z-index: 999;
        border-bottom: 1px solid #333; padding: 0 40px;
    }}
    .brand-logo {{ font-family: 'Inter', sans-serif; font-weight: 800; font-size: 16px; color: var(--gold); letter-spacing: 2px; }}

    .block-container {{ padding-top: 80px !important; }}
    
    /* MODAL DE LOGIN ( CRUZ ESTILO APPLE) */
    .login-container {{
        background: #0a0a0a; border: 1px solid #222; border-radius: 20px; padding: 50px; text-align: center;
        box-shadow: 0 20px 60px rgba(0,0,0,1); max-width: 400px; margin: auto;
    }}
    .gold-cross-icon {{ font-size: 60px; color: #d4af37; margin-bottom: 20px; display: inline-block; text-shadow: 0 0 30px rgba(212, 175, 55, 0.2); }}

    /* BOTÕES GERAIS */
    div.stButton > button {{
        background: #1e1e1e; border: 1px solid #333; color: #ccc; border-radius: 6px;
    }}
    div.stButton > button:hover {{ border-color: var(--gold); color: white; }}
    </style>
    
    <div class="nav-bar">
        <div class="brand-logo">✝ O PREGADOR</div>
        <div style="font-size:12px; color:#555;">SYSTEM 8.0 • STUDIO PRO</div>
    </div>
    """, unsafe_allow_html=True)

carregar_css()

# --- 4. FUNÇÕES INTERNAS ---
def navigate_to(page): st.session_state['page_stack'].append(page); st.rerun()
def add_slide(text): st.session_state['slides'].append({"conteudo": text}); st.toast("Slide criado na Timeline.")
def get_recent_sermons(): return [f for f in os.listdir(PASTA_SERMOES) if f.endswith(".txt")][:4]

# --- 5. TELA DE LOGIN (NOVA CRUZ APPLE-STYLE) ---
if not st.session_state['logado']:
    st.markdown("""
    <style>.stApp { background: #000 !important; }</style>
    """, unsafe_allow_html=True)
    
    col_l, col_m, col_r = st.columns([1, 1, 1])
    with col_m:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        # CONTAINER LOGIN LIMPO
        st.markdown("""
        <div class="login-container">
            <div class="gold-cross-icon">✝</div>
            <h2 style="color:white; margin:0; font-weight:600;">O PREGADOR</h2>
            <p style="color:#555; margin-bottom:30px; font-size:14px;">Identifique-se para acessar.</p>
        </div>
        """, unsafe_allow_html=True)
        
        user = st.text_input("Usuário", placeholder="ID de Pastor", label_visibility="collapsed")
        pw = st.text_input("Senha", type="password", placeholder="Chave de Acesso", label_visibility="collapsed")
        
        if st.button("ACESSAR PÚLPITO", use_container_width=True, type="primary"):
            if (user == "admin" and pw == "1234") or (user == "pr" and pw == "123"):
                st.session_state['logado'] = True; st.session_state['user'] = user; st.rerun()
            else: st.error("Acesso não autorizado.")
            
    st.stop()


# --- 6. APP PÓS-LOGIN ---
pagina = st.session_state['page_stack'][-1]

# SIDEBAR MINIMALISTA
with st.sidebar:
    st.markdown("### Navegação")
    if st.button("🏠 Central", use_container_width=True): navigate_to("Home")
    if st.button("✍️ Studio Criativo", use_container_width=True): navigate_to("Studio")
    if st.button("👥 Membros & Care", use_container_width=True): navigate_to("Care")
    if st.button("⚙️ Preferências", use_container_width=True): navigate_to("Config")
    st.markdown("---")
    st.caption("Biblioteca Local")
    st.caption(f"{len(os.listdir(PASTA_SERMOES))} Estudos Salvos")


# --- PÁGINA: CENTRAL ---
if pagina == "Home":
    st.title("Central Pastoral")
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.info("💡 **Dica de Hoje:** Comece seus esboços organizando a ideia central (A 'Big Idea'). O Studio agora possui formatação inteligente.")
        st.subheader("Trabalhos Recentes")
        rec = get_recent_sermons()
        if rec:
            for r in rec:
                with st.container():
                    col_icon, col_txt, col_act = st.columns([0.1, 0.7, 0.2])
                    col_icon.markdown("📄")
                    col_txt.markdown(f"**{r.replace('.txt','')}**")
                    if col_act.button("Editar", key=r):
                         with open(os.path.join(PASTA_SERMOES, r), 'r') as f: st.session_state['texto_ativo'] = f.read()
                         st.session_state['titulo_ativo'] = r.replace('.txt','')
                         navigate_to("Studio")
        else:
            st.caption("Sua biblioteca está vazia. Crie seu primeiro sermão!")
            
    with c2:
        st.subheader("Atalhos")
        if st.button("Novo Esboço", use_container_width=True): 
             st.session_state['texto_ativo'] = ""; st.session_state['titulo_ativo'] = ""; navigate_to("Studio")
        if st.button("Ajuda da IA", use_container_width=True): 
             st.toast("Configure sua chave API nas Configurações.")


# --- PÁGINA: STUDIO (REFORMULADO) ---
elif pagina == "Studio":
    # 1. CABEÇALHO DO DOCUMENTO
    t_left, t_right = st.columns([3, 1])
    with t_left:
        st.session_state['titulo_ativo'] = st.text_input("Título do Sermão", value=st.session_state['titulo_ativo'], 
                                                        placeholder="Digite o título da mensagem...", label_visibility="collapsed")
    with t_right:
        if st.button("💾 Salvar Tudo", type="primary", use_container_width=True):
             if st.session_state['titulo_ativo']:
                with open(os.path.join(PASTA_SERMOES, f"{st.session_state['titulo_ativo']}.txt"), 'w') as f:
                    f.write(st.session_state['texto_ativo'])
                st.toast("Manuscrito Salvo!", icon="✅")

    # 2. ÁREA DE CRIAÇÃO (SPLIT: TEXTO + SLIDES)
    col_editor, col_slides = st.columns([1.8, 1])
    
    with col_editor:
        # A) Toolbar "WYSIWYG" (Botões que inserem marcações Markdown)
        # CSS cuida da aparência para parecer um menu integrado
        st.markdown('<div class="wysiwyg-toolbar">', unsafe_allow_html=True)
        tb1, tb2, tb3, tb4, tb5, tb6 = st.columns(6)
        
        # Callbacks para injeção de texto
        def inject(tk): st.session_state['texto_ativo'] += tk
        
        # Botões Visuais
        tb1.button("H1", help="Título Grande", on_click=inject, args=("\n# ",))
        tb2.button("H2", help="Subtítulo", on_click=inject, args=("\n## ",))
        tb3.button("**B**", help="Negrito", on_click=inject, args=(" **texto** ",))
        tb4.button("*I*", help="Itálico", on_click=inject, args=(" *texto* ",))
        tb5.button("📖", help="Versículo (Bloco)", on_click=inject, args=("\n> Texto bíblico aqui...\n",))
        tb6.button("• Lista", help="Lista", on_click=inject, args=("\n- ",))
        st.markdown('</div>', unsafe_allow_html=True)
        
        # B) Editor Real (Text Area Colada na Toolbar)
        txt = st.text_area("editor_main", value=st.session_state['texto_ativo'], height=650, label_visibility="collapsed")
        st.session_state['texto_ativo'] = txt
        
        # C) Action Bar Inferior
        st.caption(f"Palavras: {len(txt.split())} • Caracteres: {len(txt)}")

    # 3. COLUNA DE SLIDES (TIMELINE)
    with col_slides:
        st.markdown("### 🎞️ Slides (Timeline)")
        st.markdown('<div class="timeline-container">', unsafe_allow_html=True)
        
        # Ferramenta de Criação Rápida
        st.info("💡 Dica: Copie um trecho do editor e cole abaixo.")
        new_s = st.text_area("Novo Slide:", height=80, placeholder="Cole o texto aqui...")
        if st.button("Adicionar à Apresentação ⬇️", use_container_width=True):
            if new_s: add_slide(new_s)
        
        st.divider()
        
        # Lista Visual dos Slides
        if st.session_state['slides']:
            for idx, slide in enumerate(st.session_state['slides']):
                st.markdown(f"""
                <div class="slide-card-mini">
                    <span class="slide-number">#{idx+1}</span>
                    <div class="slide-content-preview">{slide['conteudo']}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Remover", key=f"del_{idx}"):
                    st.session_state['slides'].pop(idx); st.rerun()
        else:
            st.caption("A linha do tempo está vazia.")
            
        st.markdown('</div>', unsafe_allow_html=True)


# --- OUTRAS PÁGINAS ---
elif pagina == "Config":
    st.title("Ajustes")
    c1, c2 = st.columns(2)
    with c1:
        st.number_input("Tamanho da Fonte", 14, 30, st.session_state['theme_size'], key='theme_size')
    with c2:
        st.text_input("API Key (Google)", type="password", key='api_key')
    if st.button("Salvar Preferências"): st.rerun()

elif pagina == "Care":
    st.title("Membros")
    st.info("Módulo de gestão de pessoas em construção.")
