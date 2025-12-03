import streamlit as st
import os
import sys
import subprocess
import time
import json
import base64
import math
import shutil
import random
import logging
import hashlib
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO

# ==============================================================================
# 0. CONFIGURAÇÃO (LINHA 1 OBRIGATÓRIA - SYSTEM KERNEL)
# ==============================================================================
st.set_page_config(
    page_title="O PREGADOR | OMEGA", 
    layout="wide", 
    page_icon="✝️", 
    initial_sidebar_state="expanded"
)

# ==============================================================================
# [-] GENESIS PROTOCOL: INFRAESTRUTURA DE DADOS V32
# ==============================================================================
def _genesis_boot_protocol():
    ROOT = "Dados_Pregador_V32_Pro"
    DIRS = {
        "SERMOES": os.path.join(ROOT, "Sermoes"),
        "GABINETE": os.path.join(ROOT, "Gabinete_Pastoral"),
        "USER": os.path.join(ROOT, "User_Data"),
        "BACKUP": os.path.join(ROOT, "Auto_Backup_Oculto"),
        "LOGS": os.path.join(ROOT, "System_Logs"),
        "BIB_CACHE": os.path.join(ROOT, "BibliaCache"),
        "MEMBROS": os.path.join(ROOT, "Membresia")
    }
    
    # Criação Física
    for p in DIRS.values(): os.makedirs(p, exist_ok=True)

    # Garante integridade dos arquivos base
    if not os.path.exists(os.path.join(DIRS["USER"], "users_db.json")):
        with open(os.path.join(DIRS["USER"], "users_db.json"), "w") as f: 
            json.dump({"ADMIN": hashlib.sha256("admin".encode()).hexdigest()}, f)
            
    if not os.path.exists(os.path.join(DIRS["USER"], "config.json")):
        with open(os.path.join(DIRS["USER"], "config.json"), "w") as f:
            json.dump({
                "theme_bg": "#000000", 
                "theme_panel": "#0A0A0A", 
                "theme_color": "#D4AF37", 
                "font_size": 18, 
                "modules_active": {"gabinete": True, "biblioteca": True}
            }, f)

    if not os.path.exists(os.path.join(DIRS["USER"], "routines.json")):
        with open(os.path.join(DIRS["USER"], "routines.json"), "w") as f:
            json.dump(["Orar na Madrugada", "Leitura da Palavra", "Visitar Enfermos"], f)

    if not os.path.exists(os.path.join(DIRS["MEMBROS"], "members.json")):
        with open(os.path.join(DIRS["MEMBROS"], "members.json"), "w") as f: json.dump([], f)
        
    return DIRS

DIRS = _genesis_boot_protocol()
DBS = {
    "CONFIG": os.path.join(DIRS["USER"], "config.json"),
    "USERS": os.path.join(DIRS["USER"], "users_db.json"),
    "ROUTINES": os.path.join(DIRS["USER"], "routines.json"),
    "MEMBERS": os.path.join(DIRS["MEMBROS"], "members.json")
}

# ==============================================================================
# 0.1 KERNEL DEPENDENCIES
# ==============================================================================
class SystemOmegaKernel:
    REQUIRED = [
        "google-generativeai", "streamlit-lottie", "Pillow", "pandas",
        "streamlit-quill", "python-docx", "reportlab", "mammoth", 
        "plotly", "cryptography"
    ]
    @staticmethod
    def check():
        try:
            import plotly
            import streamlit_quill
            import cryptography
        except ImportError:
            for lib in SystemOmegaKernel.REQUIRED:
                try: subprocess.check_call([sys.executable, "-m", "pip", "install", lib, "--quiet"])
                except: pass
            st.rerun()

SystemOmegaKernel.check()

# Imports
import plotly.express as px
import plotly.graph_objects as go
from streamlit_quill import st_quill
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
try: import mammoth; HTML2DOCX=True
except: HTML2DOCX=False

# ==============================================================================
# 1. VISUAL ENGINE V32 (THEME BUILDER + CSS INJECTOR)
# ==============================================================================
def inject_css(cfg):
    bg = cfg.get("theme_bg", "#000000")
    panel = cfg.get("theme_panel", "#090909")
    gold = cfg.get("theme_color", "#D4AF37")
    font = cfg.get("font_family", "Cinzel")
    fs = cfg.get("font_size", 18)

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Inter:wght@300;600&family=Playfair+Display&display=swap');
        
        :root {{ --main: {gold}; --bg: {bg}; --panel: {panel}; --font: '{font}'; }}
        
        .stApp {{ background-color: var(--bg); color: #EAEAEA; font-family: var(--font), sans-serif; font-size: {fs}px; }}
        
        /* Sidebar Professional */
        [data-testid="stSidebar"] {{ background-color: var(--panel); border-right: 1px solid var(--main); }}
        
        /* Inputs Dark Modern */
        .stTextInput input, .stSelectbox div, .stTextArea textarea, .stNumberInput input {{
            background-color: var(--panel) !important;
            border: 1px solid #333 !important;
            color: #EAEAEA !important;
            border-radius: 4px;
        }}
        .stTextInput input:focus {{ border-color: var(--main) !important; box-shadow: 0 0 10px var(--main); }}

        /* Botões Profissionais (Tile Style) */
        .lib-button {{
            display: inline-block; width: 100%; padding: 15px; margin: 5px 0;
            background: #111; border: 1px solid #333; color: #888; text-align: center;
            border-radius: 5px; cursor: pointer; transition: 0.3s;
        }}
        .lib-button:hover {{ border-color: var(--main); color: var(--main); background: #1a1a1a; }}
        
        /* Header Fix */
        h1, h2, h3 {{ color: var(--main) !important; font-family: 'Cinzel', serif !important; }}
        
        /* Button Streamlit Default override */
        .stButton button {{
            border: 1px solid var(--main); color: var(--main); background: transparent;
            text-transform: uppercase; font-weight: bold; width: 100%;
        }}
        .stButton button:hover {{ background: var(--main); color: #000; }}
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. IO SAFE & AUTH
# ==============================================================================
class SafeIO:
    @staticmethod
    def ler(path, default):
        try:
            if not os.path.exists(path): return default
            with open(path, 'r', encoding='utf-8') as f: return json.load(f)
        except: return default
    @staticmethod
    def salvar(path, data):
        try:
            with open(path, 'w', encoding='utf-8') as f: json.dump(data, f, indent=4)
            return True
        except: return False

def auth_login(u, p):
    users = SafeIO.ler(DBS["USERS"], {})
    if not users and u=="ADMIN" and p=="1234": return True
    h = hashlib.sha256(p.encode()).hexdigest()
    return users.get(u.upper()) == h

# ==============================================================================
# 3. GRAPHICS ENGINE V32 (FUTURE UI)
# ==============================================================================
def render_neon_radar(cats, vals, title):
    cfg = st.session_state["config"]
    color = cfg.get("theme_color", "#D4AF37")
    
    fig = go.Figure(data=go.Scatterpolar(
        r=vals, theta=cats, fill='toself',
        line=dict(color=color, width=3),
        marker=dict(color='white', size=8),
        fillcolor=f"{color}33" # 20% transparencia hex
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], color='#666', gridcolor='#333'),
            angularaxis=dict(color='#888', gridcolor='#333'),
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#EEE', family='Cinzel'),
        title=dict(text=title.upper(), x=0.5, font=dict(size=20, color=color)),
        margin=dict(t=50, b=40, l=40, r=40)
    )
    st.plotly_chart(fig, use_container_width=True)

def render_future_gauge(val, title, color):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = val,
        number = {'font': {'size': 40, 'color': color, 'family': 'Inter'}, 'suffix': "%"},
        title = {'text': title.upper(), 'font': {'size': 14, 'color': "#888", 'family': 'Inter'}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#333"},
            'bar': {'color': color, 'line': {'color': 'white', 'width': 2}},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 100], 'color': '#111'},
                {'range': [0, val], 'color': f"{color}22"} # Glow effect background
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': val
            }
        }
    ))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=20,b=20,l=20,r=20), height=200)
    st.plotly_chart(fig, use_container_width=True)

# ==============================================================================
# 4. APP LOGIC
# ==============================================================================
# Boot Config
config = SafeIO.ler(DBS["CONFIG"], {})
st.session_state["config"] = config
inject_css(config)

# LOGIN
if "logado" not in st.session_state: st.session_state["logado"] = False
if not st.session_state["logado"]:
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        gold = config.get("theme_color")
        st.markdown(f"""<center><h1 style='color:{gold}; border-bottom:2px solid {gold}'>OMEGA SYSTEM</h1><p>ACCESS PROTOCOL V32</p></center>""", unsafe_allow_html=True)
        u = st.text_input("ID")
        p = st.text_input("CODE", type="password")
        if st.button("EXECUTE"):
            if auth_login(u, p):
                st.session_state["logado"] = True
                st.rerun()
            else: st.error("ACCESS DENIED")
    st.stop()

# MAIN INTERFACE
with st.sidebar:
    st.markdown(f"**PASTORAL UNIT: CONNECTED**")
    menu = st.radio("MÓDULOS", ["Rotina & Cuidado", "Gabinete (Editor)", "Biblioteca", "Configurações Master"])
    if st.button("SAIR DO SISTEMA"):
        st.session_state["logado"] = False
        st.rerun()

# ------------------------------------------------------------------------------
# MÓDULO 1: ROTINA E CUIDADO PASTORAL
# ------------------------------------------------------------------------------
if menu == "Rotina & Cuidado":
    st.title("🛡️ Cuidado Pastoral Avançado")
    t1, t2, t3 = st.tabs(["📝 Minha Rotina", "⚖️ Teoria da Permissão", "🐑 Gestão Rebanho"])
    
    # ROTINAS PERSONALIZADAS (O que você pediu: botão de + e customização)
    with t1:
        st.subheader("Gerenciador de Tarefas Ministeriais")
        routines = SafeIO.ler(DBS["ROUTINES"], [])
        
        c_add1, c_add2 = st.columns([4, 1])
        new_task = c_add1.text_input("Adicionar nova tarefa à rotina:", placeholder="Ex: Estudar Hebraico...")
        if c_add2.button("➕ ADICIONAR"):
            if new_task and new_task not in routines:
                routines.append(new_task)
                SafeIO.salvar(DBS["ROUTINES"], routines)
                st.success("Tarefa Adicionada.")
                st.rerun()
        
        st.markdown("---")
        # Renderiza checkboxes
        for r in routines:
            c_check, c_del = st.columns([5, 0.5])
            c_check.checkbox(f"📍 {r}", key=r)
            if c_del.button("✕", key=f"del_{r}"):
                routines.remove(r)
                SafeIO.salvar(DBS["ROUTINES"], routines)
                st.rerun()

    # TEORIA DA PERMISSÃO (GRÁFICOS FUTURISTAS)
    with t2:
        st.subheader("Bio-Feedback Emocional (Future UI)")
        
        c_sld, c_gfx = st.columns(2)
        with c_sld:
            st.markdown("#### Input de Dados")
            p1 = st.slider("Graça (Falhar)", 0, 100, 50)
            p2 = st.slider("Humanidade (Sentir)", 0, 100, 50)
            p3 = st.slider("Limites (Descansar)", 0, 100, 50)
            p4 = st.slider("Dignidade (Sucesso)", 0, 100, 50)
        
        with c_gfx:
            avg = (p1 + p2 + p3 + p4) / 4
            render_future_gauge(avg, "Nível de Permissão Interna", config.get("theme_color"))
            
            # Radar pequeno
            render_neon_radar(["Falhar", "Sentir", "Descansar", "Sucesso"], [p1,p2,p3,p4], "Espectro")

    # REBANHO
    with t3:
        st.subheader("Gestão de Almas")
        memb = SafeIO.ler(DBS["MEMBERS"], [])
        with st.expander("Cadastrar Ovelha", expanded=False):
            with st.form("f_memb"):
                nm = st.text_input("Nome")
                stt = st.selectbox("Status", ["Membro", "Visitante"])
                if st.form_submit_button("Salvar"):
                    memb.append({"Nome": nm, "Status": stt, "Data": datetime.now().strftime("%Y-%m-%d")})
                    SafeIO.salvar(DBS["MEMBERS"], memb)
                    st.rerun()
        if memb: st.dataframe(pd.DataFrame(memb), use_container_width=True)

# ------------------------------------------------------------------------------
# MÓDULO 2: GABINETE (EDITOR ESTILO WORD)
# ------------------------------------------------------------------------------
elif menu == "Gabinete (Editor)":
    st.title("📝 Editor Pastoral (Word-Like)")
    
    c_list, c_ed = st.columns([1, 4])
    
    files = [f for f in os.listdir(DIRS["SERMOES"]) if f.endswith(".txt")]
    sel = c_list.radio("Arquivos:", ["Novo"] + files)
    
    content = ""
    title_val = ""
    if sel != "Novo":
        try:
            with open(os.path.join(DIRS["SERMOES"], sel), 'r') as f: content = f.read()
            title_val = sel.replace(".txt", "")
        except: pass
        
    with c_ed:
        tit = st.text_input("Título do Sermão / Documento", value=title_val)
        
        # BARRA DE FERRAMENTAS WORD COMPLETA (CONFIG DO QUILL)
        toolbar_options = [
            ['bold', 'italic', 'underline', 'strike'],        # toggled buttons
            ['blockquote', 'code-block'],
            [{'header': 1}, {'header': 2}],               # custom button values
            [{'list': 'ordered'}, {'list': 'bullet'}],
            [{'script': 'sub'}, {'script': 'super'}],      # superscript/subscript
            [{'indent': '-1'}, {'indent': '+1'}],          # outdent/indent
            [{'direction': 'rtl'}],                         # text direction
            [{'size': ['small', False, 'large', 'huge']}],  # custom dropdown
            [{'header': [1, 2, 3, 4, 5, 6, False]}],
            [{'color': []}, {'background': []}],          # dropdown with defaults from theme
            [{'font': []}],
            [{'align': []}],
            ['clean'],                                      # remove formatting button
            ['link', 'image']
        ]
        
        # O Editor agora carrega como o Word
        text_data = st_quill(
            value=content, 
            html=True, 
            key="quill_word",
            toolbar=toolbar_options, # INJETA A BARRA ESTILO WORD
        )
        
        # Ações Rápidas
        col_actions = st.columns(4)
        if col_actions[0].button("💾 SALVAR"):
            with open(os.path.join(DIRS["SERMOES"], f"{tit}.txt"), 'w') as f: f.write(text_data)
            st.success("Documento Salvo.")
            
        if col_actions[1].button("🖨️ DOCX"):
            if HTML2DOCX:
                path = os.path.join(DIRS["SERMOES"], f"{tit}.docx")
                with open(path, "wb") as f: 
                    f.write(mammoth.convert_to_docx(text_data).value)
                st.success("Convertido para Word (DOCX).")

        if col_actions[2].button("🛡️ CRIPTOGRAFAR"):
            # Usa senha do config
            pw = config.get("enc_password")
            if pw:
                # Simulação simples (Key real precisa ser 32 bytes URLSafeB64, usando Hash para simplificar)
                key = hashlib.sha256(pw.encode()).digest() 
                aes = AESGCM(key)
                nonce = os.urandom(12)
                ct = aes.encrypt(nonce, text_data.encode(), None)
                with open(os.path.join(DIRS["GABINETE"], f"{tit}.enc"), "wb") as f: f.write(nonce+ct)
                st.success("Blindado.")
            else: st.error("Defina a Senha Mestra nas Configurações.")
            
        # Simulação de "Corretor" / Revisão
        if col_actions[3].button("🔍 REVISAR"):
            wrongs = ["eu acho", "talvez", "nao", "voce"] # Lista básica
            found = [w for w in wrongs if w in text_data.lower()]
            if found: st.warning(f"Sugestões de correção: {found}")
            else: st.info("Texto parece limpo (Análise básica).")

# ------------------------------------------------------------------------------
# MÓDULO 3: BIBLIOTECA (BOTÕES TILES/MELHORADOS)
# ------------------------------------------------------------------------------
elif menu == "Biblioteca":
    st.title("📚 Biblioteca Digital")
    st.markdown("Acesse seus recursos de forma visual.")
    
    # Busca
    c_busca, c_act = st.columns([3, 1])
    c_busca.text_input("🔍 Pesquisar no Acervo Global (Google API)", placeholder="Digite autor, título ou tópico...")
    c_act.button("BUSCAR AGORA")
    
    st.markdown("---")
    st.subheader("Acesso Rápido (Local)")
    
    # Layout em Grid Profissional com CSS injetado
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="lib-button">📖<br>Bíblias</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="lib-button">📘<br>Comentários</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="lib-button">📜<br>Dicionários</div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="lib-button">📂<br>Meus PDFs</div>', unsafe_allow_html=True)

    st.caption("Pasta local de arquivos: " + DIRS["BIB_CACHE"])

# ------------------------------------------------------------------------------
# MÓDULO 4: CONFIGURAÇÕES MASTER (THEME BUILDER + COMANDOS)
# ------------------------------------------------------------------------------
elif menu == "Configurações Master":
    st.title("⚙️ Controle do Sistema")
    
    t_visual, t_cmds, t_sys = st.tabs(["🎨 Theme Builder (Personalizar)", "⌨️ Comandos", "💾 Sistema"])
    
    with t_visual:
        st.subheader("Construtor de Temas (Cada usuário personaliza o seu)")
        
        c1, c2, c3 = st.columns(3)
        # O usuário pode escolher tudo agora
        bg_new = c1.color_picker("Cor de Fundo (Background)", config.get("theme_bg"))
        pnl_new = c2.color_picker("Cor dos Painéis/Menu", config.get("theme_panel"))
        cor_new = c3.color_picker("Cor de Destaque (Principal)", config.get("theme_color"))
        
        font_new = st.selectbox("Família Tipográfica", ["Cinzel", "Inter", "Merriweather", "Playfair Display"], index=0)
        
        st.markdown(f"""
        <div style="background:{bg_new}; padding:20px; border:1px solid {cor_new}; border-radius:5px; color:#EEE;">
            <h3 style="color:{cor_new} !important; font-family:{font_new}; margin:0;">PREVIEW DO TEMA</h3>
            <p style="font-family:{font_new};">Assim será o texto da sua interface.</p>
            <div style="background:{pnl_new}; padding:10px; border-left:3px solid {cor_new}">Input Box Exemplo</div>
        </div>
        """, unsafe_allow_html=True)
        
    with t_cmds:
        st.subheader("Mapeamento de Módulos (Comandos)")
        st.caption("Ative ou desative funções para limpar sua interface.")
        
        active_modules = config.get("modules_active", {})
        
        # Mapeamento de Comandos "Logicos"
        c_m1, c_m2 = st.columns(2)
        m_gab = c_m1.checkbox("Ativar Editor de Texto", value=True)
        m_bib = c_m1.checkbox("Ativar Biblioteca", value=True)
        m_fin = c_m2.checkbox("Ativar Módulo Financeiro (BETA)", value=False)
        m_mid = c_m2.checkbox("Ativar Transmissão Online (BETA)", value=False)
        
    with t_sys:
        st.subheader("Credenciais & Segurança")
        np = st.text_input("Alterar Senha de Criptografia (Master Key)", value=config.get("enc_password", ""), type="password")
        if st.button("LIMPAR CACHE DO NAVEGADOR"):
            st.cache_data.clear()
            st.success("Memória Limpa.")

    # AÇÃO DE SALVAR GERAL
    st.markdown("---")
    if st.button("GRAVAR DEFINIÇÕES (SALVAR E REINICIAR)", type="primary"):
        # Salva o Theme Builder
        config["theme_bg"] = bg_new
        config["theme_panel"] = pnl_new
        config["theme_color"] = cor_new
        config["font_family"] = font_new
        config["enc_password"] = np
        config["modules_active"] = {
            "gabinete": m_gab, "biblioteca": m_bib
        }
        SafeIO.salvar(DBS["CONFIG"], config)
        st.success("Sistema Reconstruído com novos parâmetros.")
        time.sleep(1)
        st.rerun()
