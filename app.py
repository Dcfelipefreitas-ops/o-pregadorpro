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
from datetime import datetime, timedelta
from io import BytesIO

# ==============================================================================
# 0. CONFIGURAÇÃO (LINHA 1 OBRIGATÓRIA)
# ==============================================================================
st.set_page_config(
    page_title="O PREGADOR", 
    layout="wide", 
    page_icon="✝️", 
    initial_sidebar_state="expanded"
)

# ==============================================================================
# [-] GENESIS PROTOCOL: AUTO-CRIAÇÃO DE PASTAS (INDISPENSÁVEL PARA RODAR)
# ==============================================================================
def _genesis_boot_protocol():
    # Caminhos originais do V31
    ROOT = "Dados_Pregador_V31"
    STRUTURA = {
        "SERMOES": os.path.join(ROOT, "Sermoes"),
        "GABINETE": os.path.join(ROOT, "Gabinete_Pastoral"),
        "USER": os.path.join(ROOT, "User_Data"),
        "BACKUP": os.path.join(ROOT, "Auto_Backup_Oculto"),
        "LOGS": os.path.join(ROOT, "System_Logs"),
        "BIB_CACHE": os.path.join(ROOT, "BibliaCache"),
        "MEMBROS": os.path.join(ROOT, "Membresia")
    }
    
    # 1. Criação das Pastas
    for pasta in STRUTURA.values():
        os.makedirs(pasta, exist_ok=True)

    # 2. Arquivos Essenciais para não dar erro de leitura
    p_users = os.path.join(STRUTURA["USER"], "users_db.json")
    if not os.path.exists(p_users):
        with open(p_users, "w") as f: json.dump({"ADMIN": hashlib.sha256("admin".encode()).hexdigest()}, f)

    p_config = os.path.join(STRUTURA["USER"], "config.json")
    if not os.path.exists(p_config):
        with open(p_config, "w") as f: json.dump({"theme_color": "#D4AF37", "font_size": 18, "enc_password": ""}, f)
        
    p_membros = os.path.join(STRUTURA["MEMBROS"], "members.json")
    if not os.path.exists(p_membros):
        with open(p_membros, "w") as f: json.dump([], f)
        
    return STRUTURA

# Inicializa pastas e recupera o dicionário de diretórios
DIRS = _genesis_boot_protocol()
DBS = {
    "CONFIG": os.path.join(DIRS["USER"], "config.json"),
    "USERS": os.path.join(DIRS["USER"], "users_db.json"),
    "SOUL": os.path.join(DIRS["GABINETE"], "soul_data.json"),
    "MEMBERS": os.path.join(DIRS["MEMBROS"], "members.json")
}

# ==============================================================================
# 0.1 KERNEL (DEPENDÊNCIAS)
# ==============================================================================
class SystemOmegaKernel:
    REQUIRED = [
        "google-generativeai", "streamlit-lottie", "Pillow", "pandas",
        "streamlit-quill", "python-docx", "reportlab", "mammoth", "plotly", "cryptography"
    ]
    @staticmethod
    def _install_quiet(pkg):
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--quiet", "--no-warn-script-location"])
        except: pass

    @staticmethod
    def boot_check():
        for lib in SystemOmegaKernel.REQUIRED:
            try:
                if lib == "google-generativeai": __import__("google.generativeai")
                elif lib == "Pillow": __import__("PIL")
                elif lib == "python-docx": __import__("docx")
                elif lib == "streamlit-quill": __import__("streamlit_quill")
                elif lib == "plotly": __import__("plotly")
                else: __import__(lib.replace("-", "_"))
            except ImportError:
                SystemOmegaKernel._install_quiet(lib)

SystemOmegaKernel.boot_check()
SystemOmegaKernel.inject_pwa_headers = lambda: st.markdown("", unsafe_allow_html=True) # Placeholder

# Imports Padrão V31
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
try: from streamlit_quill import st_quill; QUILL_AVAILABLE = True
except: QUILL_AVAILABLE = False
try: from cryptography.hazmat.primitives.ciphers.aead import AESGCM; CRYPTO_OK = True
except: CRYPTO_OK = False
try: import mammoth; HTML2DOCX = "mammoth"
except: HTML2DOCX = None

# ==============================================================================
# 1. IO SEGURANÇA E ACESSO
# ==============================================================================
class SafeIO:
    @staticmethod
    def ler_json(caminho, default_return):
        try:
            if not os.path.exists(caminho): return default_return
            with open(caminho, 'r', encoding='utf-8') as f:
                c = f.read().strip()
                return json.loads(c) if c else default_return
        except: return default_return

    @staticmethod
    def salvar_json(caminho, dados):
        try:
            tmp = caminho + ".tmp"
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
            os.replace(tmp, caminho)
            return True
        except: return False

def encrypt_sermon_aes(password, plaintext):
    if not CRYPTO_OK: return "Bibliotecas de Criptografia ausentes"
    key = hashlib.sha256(password.encode()).digest()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
    return base64.b64encode(nonce + ct).decode('utf-8')

def export_html_to_docx_better(title, html_content, out_path):
    if HTML2DOCX == "mammoth":
        with open(out_path, "wb") as docx_file:
            docx_file.write(mammoth.convert_to_docx(html_content).value)

class AccessControl:
    @staticmethod
    def _hash(text): return hashlib.sha256(text.encode()).hexdigest()
    
    @staticmethod
    def register(username, password):
        users = SafeIO.ler_json(DBS['USERS'], {})
        if username.upper() in users: return False, "USUÁRIO JÁ EXISTE."
        # FIX: Salva no disco imediatamente
        users[username.upper()] = AccessControl._hash(password)
        SafeIO.salvar_json(DBS['USERS'], users)
        return True, "REGISTRO OK."

    @staticmethod
    def login(username, password):
        users = SafeIO.ler_json(DBS['USERS'], {})
        # Backdoor Admin V31
        if not users and username.upper() == "ADMIN" and password == "1234": return True
        
        hashed = AccessControl._hash(password)
        stored = users.get(username.upper())
        if stored: return stored == password if len(stored)!=64 else stored == hashed
        return False

# ==============================================================================
# 2. VISUAL SYSTEM (Dark Cathedral Original)
# ==============================================================================
def inject_css(color="#D4AF37", font_sz=18):
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700&family=Cinzel:wght@500;800&display=swap');
        
        :root {{ 
            --gold: {color}; 
            --bg: #000000; 
            --panel: #0A0A0A; 
            --text: #EAEAEA; 
        }}
        
        .stApp {{ background-color: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; font-size: {font_sz}px; }}
        [data-testid="stSidebar"] {{ background-color: #050505; border-right: 1px solid #1F1F1F; }}
        
        .stTextInput input, .stSelectbox div, .stTextArea textarea {{ 
            background-color: #0A0A0A !important; 
            border: 1px solid #222 !important; 
            color: #eee !important; 
        }}
        
        .stButton button {{ border: 1px solid var(--gold); color: var(--gold); background: transparent; text-transform: uppercase; font-weight: bold; }}
        .stButton button:hover {{ background: var(--gold); color: #000; }}
        
        h1, h2, h3 {{ color: var(--gold) !important; font-family: 'Cinzel', serif !important; }}
    </style>
    """, unsafe_allow_html=True)

# Helper Gráfico (Atualizado para Plotly mas com os dados originais)
def plot_radar_chart(categories, values, title):
    cfg = st.session_state.get("config", {})
    fig = go.Figure(go.Scatterpolar(
        r=values, theta=categories, fill='toself',
        line_color=cfg.get("theme_color", "#D4AF37")
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100]), bgcolor='rgba(0,0,0,0)'),
        paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#EAEAEA'), title=title
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_gauge(value, title, theme_color):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = value,
        title = {'text': title, 'font': {'size': 20, 'color': theme_color}},
        gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': theme_color}, 'bgcolor': "rgba(0,0,0,0)"}
    ))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "#EEE"})
    st.plotly_chart(fig, use_container_width=True)

# ==============================================================================
# 3. LÓGICA DO APP
# ==============================================================================
if "config" not in st.session_state:
    st.session_state["config"] = SafeIO.ler_json(DBS["CONFIG"], {"theme_color": "#D4AF37", "font_size": 18})

inject_css(st.session_state["config"]["theme_color"], st.session_state["config"]["font_size"])

# TELA DE LOGIN V31 (Original)
if "logado" not in st.session_state: st.session_state["logado"] = False

if not st.session_state["logado"]:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        gold = st.session_state["config"]["theme_color"]
        st.markdown(f"""
        <center>
        <svg width="100" height="100" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="45" stroke="{gold}" stroke-width="3" fill="none" />
            <line x1="50" y1="25" x2="50" y2="75" stroke="{gold}" stroke-width="3" />
            <line x1="35" y1="40" x2="65" y2="40" stroke="{gold}" stroke-width="3" />
        </svg>
        <h2 style='font-family:Cinzel; color:{gold}'>O PREGADOR</h2>
        <small>SYSTEM V31 | SHEPHERD EDITION</small>
        </center>
        """, unsafe_allow_html=True)
        
        t1, t2 = st.tabs(["ENTRAR", "REGISTRAR"])
        with t1:
            u = st.text_input("ID")
            p = st.text_input("Senha", type="password")
            if st.button("ACESSAR", use_container_width=True):
                if AccessControl.login(u, p):
                    st.session_state["logado"] = True
                    st.session_state["user_name"] = u.upper()
                    st.rerun()
                else: st.error("Acesso Negado.")
        with t2:
            nu = st.text_input("Novo ID")
            np = st.text_input("Nova Senha", type="password")
            if st.button("CRIAR"):
                ok, msg = AccessControl.register(nu, np)
                if ok: st.success(msg)
                else: st.error(msg)
    st.stop()

# MAIN MENU
c_main, c_tog = st.columns([0.9, 0.1])
if "hide_menu" not in st.session_state: st.session_state.hide_menu = False

# MENU ORIGINAL DO SEU CÓDIGO V31
menu = st.sidebar.radio("SISTEMA", ["Cuidado Pastoral", "Gabinete Pastoral", "Biblioteca", "Configurações"], index=0)
st.sidebar.divider()
if st.sidebar.button("LOGOUT"):
    st.session_state["logado"] = False
    st.rerun()

# --------------------------------------------------------------------------------
# MÓDULO 1: CUIDADO PASTORAL (ESTRUTURA ORIGINAL RESTAURADA)
# --------------------------------------------------------------------------------
if menu == "Cuidado Pastoral":
    st.title("🛡️ Cuidado Pastoral Dinâmico")
    
    # As 4 Abas que você pediu
    tab_painel, tab_rebanho, tab_teoria, tab_tools = st.tabs([
        "📊 Painel do Pastor", 
        "🐑 Meu Rebanho", 
        "⚖️ Teoria da Permissão", 
        "🛠️ Ferramentas"
    ])

    with tab_painel:
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("Estado Geral da Igreja")
            cats = ['Espiritual', 'Emocional', 'Físico', 'Financeiro', 'Relacional']
            vals = [random.randint(40, 90) for _ in cats]
            plot_radar_chart(cats, vals, "Saúde do Corpo")
            st.warning("⚠️ **Alerta:** Verifique membros inativos.")
        with c2:
            st.subheader("Rotina")
            st.checkbox("Orar")
            st.checkbox("Ler Palavra")
            st.checkbox("Visita")

    with tab_rebanho:
        st.subheader("Gestão de Ovelhas")
        # Banco de membros Real
        membros = SafeIO.ler_json(DBS["MEMBERS"], [])
        
        with st.expander("➕ Adicionar Nova Ovelha"):
            with st.form("new_ovelha"):
                n = st.text_input("Nome")
                s = st.selectbox("Necessidade", ["Vida Espiritual", "Família", "Finanças", "Emoções"])
                if st.form_submit_button("Salvar"):
                    membros.append({"Nome": n, "Necessidade": s, "Data": datetime.now().strftime("%d/%m")})
                    SafeIO.salvar_json(DBS["MEMBERS"], membros)
                    st.success("Adicionado.")
                    st.rerun()
        
        if membros:
            st.dataframe(pd.DataFrame(membros), use_container_width=True)
        else:
            st.info("Nenhuma ovelha cadastrada ainda.")

    # RESTAURADO: TEORIA DA PERMISSÃO (COM OS SLIDERS)
    with tab_teoria:
        st.markdown("### ⚖️ O Pastor também é Ovelha")
        col_input, col_viz = st.columns(2)
        with col_input:
            p_fail = st.slider("Permissão para FALHAR", 0, 100, 50)
            p_feel = st.slider("Permissão para SENTIR", 0, 100, 50)
            p_rest = st.slider("Permissão para DESCANSAR", 0, 100, 50)
            p_succ = st.slider("Permissão para SUCESSO", 0, 100, 50)
        with col_viz:
            score = (p_fail + p_feel + p_rest + p_succ) / 4
            plot_gauge(score, "Saúde Interna", st.session_state["config"]["theme_color"])

    with tab_tools:
        st.info("Ferramentas de discipulado em construção...")

# --------------------------------------------------------------------------------
# MÓDULO 2: GABINETE PASTORAL (EDITOR ORIGINAL)
# --------------------------------------------------------------------------------
elif menu == "Gabinete Pastoral":
    st.title("📝 Gabinete Pastoral")
    
    with st.expander("Configurações do Editor"):
        fs = st.slider("Fonte Editor", 12, 30, 18)

    c_tit, c_tags = st.columns([3, 1])
    st.session_state["titulo_ativo"] = c_tit.text_input("Título", st.session_state.get("titulo_ativo", ""))
    st.session_state["last_tags"] = c_tags.text_input("Tags", "Domingo, Série")

    # Lista de arquivos para abrir
    files = [f for f in os.listdir(DIRS["SERMOES"]) if f.endswith(".txt")]
    sel = st.selectbox("Abrir Recente:", ["-"] + files)
    if sel != "-":
        if st.button("Carregar"):
            with open(os.path.join(DIRS["SERMOES"], sel), 'r') as f:
                st.session_state["texto_ativo"] = f.read()
                st.session_state["titulo_ativo"] = sel.replace(".txt", "")

    # Editor
    if QUILL_AVAILABLE:
        content = st_quill(value=st.session_state.get("texto_ativo", ""), height=400)
    else:
        content = st.text_area("Texto", st.session_state.get("texto_ativo", ""), height=400)
    
    st.session_state["texto_ativo"] = content

    c_save, c_enc = st.columns(2)
    with c_save:
        if st.button("Salvar Sermão"):
            fn = f"{st.session_state['titulo_ativo']}.txt"
            path = os.path.join(DIRS["SERMOES"], fn)
            with open(path, 'w') as f: f.write(content)
            st.success("Salvo.")
            
        if st.button("Encriptar (.enc)"):
            pw = st.session_state["config"].get("enc_password")
            if pw:
                enc = encrypt_sermon_aes(pw, content)
                with open(os.path.join(DIRS["GABINETE"], f"{st.session_state['titulo_ativo']}.enc"), 'w') as f: f.write(enc)
                st.success("Encriptado.")
            else: st.error("Defina senha nas Configurações.")
            
    with c_enc:
        if st.button("Exportar DOCX"):
             fn = f"{st.session_state['titulo_ativo']}.docx"
             path = os.path.join(DIRS["SERMOES"], fn)
             if HTML2DOCX:
                 export_html_to_docx_better(fn, content, path)
                 st.success(f"DOCX gerado em {path}")

# --------------------------------------------------------------------------------
# MÓDULO 3: BIBLIOTECA
# --------------------------------------------------------------------------------
elif menu == "Biblioteca":
    st.title("📚 Biblioteca Reformada")
    st.text_input("Buscar (Integração Google Books)")
    st.markdown("#### Arquivos Locais")
    st.write(os.listdir(DIRS["BIB_CACHE"]))

# --------------------------------------------------------------------------------
# MÓDULO 4: CONFIGURAÇÕES (MANTER NOMES E ITENS ORIGINAIS)
# --------------------------------------------------------------------------------
elif menu == "Configurações":
    st.title("⚙️ Configurações")
    cfg = st.session_state["config"]
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Visual")
        nc = st.color_picker("Cor do Tema", cfg.get("theme_color", "#D4AF37"))
        nf = st.number_input("Tamanho Fonte", 12, 30, cfg.get("font_size", 18))
    with c2:
        st.markdown("### Segurança")
        npw = st.text_input("Senha Mestra de Encriptação", type="password", value=cfg.get("enc_password", ""))
    
    if st.button("Salvar Tudo"):
        cfg["theme_color"] = nc
        cfg["font_size"] = nf
        cfg["enc_password"] = npw
        SafeIO.salvar_json(DBS["CONFIG"], cfg)
        st.success("Configurações salvas. Reinicie a página.")
