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
# 0. CONFIGURAÇÃO PRIMÁRIA (A PRIMEIRA COISA A RODAR - CRÍTICO)
# ==============================================================================
st.set_page_config(
    page_title="O PREGADOR", 
    layout="wide", 
    page_icon="✝️", 
    initial_sidebar_state="expanded"
)

# ==============================================================================
# [-] GENESIS PROTOCOL: INFRAESTRUTURA DE DADOS
# ==============================================================================
def _genesis_boot_protocol():
    ROOT = "Dados_Pregador_V31"
    PASTAS = {
        "SERMOES": os.path.join(ROOT, "Sermoes"),
        "GABINETE": os.path.join(ROOT, "Gabinete_Pastoral"),
        "USER": os.path.join(ROOT, "User_Data"),
        "BACKUP": os.path.join(ROOT, "Auto_Backup_Oculto"),
        "LOGS": os.path.join(ROOT, "System_Logs"),
        "BIB_CACHE": os.path.join(ROOT, "BibliaCache"),
        "MEMBROS": os.path.join(ROOT, "Membresia")
    }
    
    # 1. Criação Física das Pastas
    for p in PASTAS.values():
        os.makedirs(p, exist_ok=True)

    # 2. Arquivos Essenciais (Garante integridade)
    p_users = os.path.join(PASTAS["USER"], "users_db.json")
    if not os.path.exists(p_users):
        with open(p_users, "w") as f: 
            json.dump({"ADMIN": hashlib.sha256("admin".encode()).hexdigest()}, f)
            
    p_conf = os.path.join(PASTAS["USER"], "config.json")
    if not os.path.exists(p_conf):
        with open(p_conf, "w") as f:
            json.dump({"theme_color": "#D4AF37", "theme_mode": "Dark Cathedral", "font_size": 18, "enc_password": ""}, f)
            
    p_memb = os.path.join(PASTAS["MEMBROS"], "members.json")
    if not os.path.exists(p_memb):
        with open(p_memb, "w") as f: json.dump([], f)
        
    return PASTAS

# Executa Gênesis
DIRS = _genesis_boot_protocol()
DBS = {
    "CONFIG": os.path.join(DIRS["USER"], "config.json"),
    "USERS": os.path.join(DIRS["USER"], "users_db.json"),
    "MEMBERS": os.path.join(DIRS["MEMBROS"], "members.json")
}

# ==============================================================================
# 0. KERNEL SYSTEM OMEGA (Bibliotecas Pesadas)
# ==============================================================================
class SystemOmegaKernel:
    REQUIRED = [
        "google-generativeai", "streamlit-lottie", "Pillow", "pandas",
        "streamlit-quill", "python-docx", "reportlab", "mammoth", 
        "plotly", "cryptography", "html2docx"
    ]
    
    @staticmethod
    def _install_quiet(pkg):
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--quiet", "--no-warn-script-location"])
            return True
        except: return False

    @staticmethod
    def boot_check():
        queue = []
        for lib in SystemOmegaKernel.REQUIRED:
            try:
                if lib == "google-generativeai": __import__("google.generativeai")
                elif lib == "Pillow": __import__("PIL")
                elif lib == "python-docx": __import__("docx")
                elif lib == "streamlit-quill": __import__("streamlit_quill")
                elif lib == "plotly": __import__("plotly")
                else: __import__(lib.replace("-", "_"))
            except ImportError:
                queue.append(lib)
        
        if queue:
            placeholder = st.empty()
            placeholder.info(f"⚙️ SYSTEM OMEGA: Instalação Automática de {len(queue)} módulos...")
            for lib in queue:
                SystemOmegaKernel._install_quiet(lib)
            placeholder.empty()
            st.rerun() # Reinicia após instalar

SystemOmegaKernel.boot_check()

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from PIL import Image
try: from streamlit_quill import st_quill; QUILL_AVAILABLE=True
except: QUILL_AVAILABLE=False

try: from cryptography.hazmat.primitives.ciphers.aead import AESGCM; CRYPTO_OK=True
except: CRYPTO_OK=False

try: import mammoth; HTML2DOCX_ENGINE = "mammoth"
except: 
    try: import html2docx; HTML2DOCX_ENGINE = "html2docx"
    except: HTML2DOCX_ENGINE = None

# ==============================================================================
# 1. SEGURANÇA E ARMAZENAMENTO (CLASSES DO SEU CÓDIGO)
# ==============================================================================
class SafeIO:
    @staticmethod
    def ler_json(caminho, default_return):
        try:
            if not os.path.exists(caminho): return default_return
            with open(caminho, 'r', encoding='utf-8') as f:
                c = f.read().strip()
                return json.loads(c) if c else default_return
        except Exception: return default_return

    @staticmethod
    def salvar_json(caminho, dados):
        try:
            if os.path.exists(caminho):
                try: shutil.copy2(caminho, os.path.join(DIRS["BACKUP"], os.path.basename(caminho) + ".bak"))
                except: pass
            
            with open(caminho, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            return False

def encrypt_sermon_aes(password, plaintext):
    if not CRYPTO_OK: return "ERR: Biblio crypto não instalada"
    try:
        key = hashlib.sha256(password.encode()).digest()
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        ct = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
        return base64.b64encode(nonce + ct).decode('utf-8')
    except Exception as e: return str(e)

class AccessControl:
    @staticmethod
    def _hash(text): return hashlib.sha256(text.encode()).hexdigest()
    
    @staticmethod
    def register(username, password):
        users = SafeIO.ler_json(DBS['USERS'], {})
        if username.upper() in users: return False, "Usuário duplicado."
        users[username.upper()] = AccessControl._hash(password)
        saved = SafeIO.salvar_json(DBS['USERS'], users) # Grava na hora
        return saved, "Registrado com sucesso."

    @staticmethod
    def login(username, password):
        users = SafeIO.ler_json(DBS['USERS'], {})
        if not users and username.upper() == "ADMIN" and password == "1234": return True
        hashed = AccessControl._hash(password)
        stored = users.get(username.upper())
        if stored: return stored == password if len(stored)!=64 else stored == hashed
        return False

# ==============================================================================
# 2. MOTOR GRÁFICO & VISUAL (THEWORD STYLE)
# ==============================================================================
def inject_css(config_dict):
    c = config_dict.get("theme_color", "#D4AF37")
    mode = config_dict.get("theme_mode", "Dark Cathedral")
    font = config_dict.get("font_family", "Cinzel")
    sz = config_dict.get("font_size", 18)

    if mode == "Dark Cathedral":
        bg, pnl, txt = "#000000", "#090909", "#EAEAEA"
    elif mode == "Pergaminho (Sepia)":
        bg, pnl, txt = "#F4ECD8", "#E8DFCA", "#2b2210"
    else: 
        bg, pnl, txt = "#FFFFFF", "#F5F5F5", "#111111"

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Inter:wght@300;600&family=Playfair+Display&display=swap');
        
        :root {{ --gold: {c}; --bg: {bg}; --pnl: {pnl}; --txt: {txt}; --fbase: {sz}px; --ffam: '{font}', sans-serif; }}
        
        .stApp {{ background-color: var(--bg); color: var(--txt); font-family: var(--ffam); font-size: var(--fbase); }}
        
        .stTextInput input, .stSelectbox div, .stTextArea textarea {{
            background-color: var(--pnl) !important;
            border: 1px solid #333 !important;
            color: var(--txt) !important;
        }}
        .stTextInput input:focus {{ border-color: var(--gold) !important; }}
        
        [data-testid="stSidebar"] {{ background-color: var(--pnl); border-right: 1px solid var(--gold); }}
        
        h1, h2, h3 {{ color: var(--gold) !important; font-family: 'Cinzel', serif !important; }}
        
        .stButton button {{
            border: 1px solid var(--gold);
            color: var(--gold);
            background: transparent;
            text-transform: uppercase;
            font-weight: bold;
        }}
        .stButton button:hover {{ background: var(--gold); color: #000; }}
        
        /* PWA Header fixo */
        header {{visibility: hidden !important;}} 
    </style>
    """, unsafe_allow_html=True)

# GRÁFICOS (Recuperados)
def plot_radar(cats, vals, title):
    cfg = st.session_state["config"]
    fig = go.Figure(data=go.Scatterpolar(r=vals, theta=cats, fill='toself', line_color=cfg['theme_color']))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100]), bgcolor='rgba(0,0,0,0)'),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=cfg.get("theme_mode", "Dark") == "Dark Cathedral" and "#EEE" or "#222"),
        title=title, margin=dict(t=30, b=30, l=30, r=30)
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_gauge_linear(val, title, color):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = val,
        title = {'text': title, 'font': {'size': 24, 'color': color}},
        gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': color}, 'bgcolor': "rgba(0,0,0,0)"}
    ))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "#EEE"}, height=150)
    st.plotly_chart(fig, use_container_width=True)

# ==============================================================================
# 3. LÓGICA PRINCIPAL (LOGIN + SISTEMA)
# ==============================================================================
# Carregar Configuração antes do render
config_data = SafeIO.ler_json(DBS["CONFIG"], {})
st.session_state["config"] = config_data
inject_css(config_data)

# SISTEMA DE LOGIN BLINDADO
if "logado" not in st.session_state: st.session_state["logado"] = False

if not st.session_state["logado"]:
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        st.markdown("<br>", unsafe_allow_html=True)
        gold = config_data.get("theme_color", "#D4AF37")
        # CRUZ RESTAURADA
        st.markdown(f"""
        <center>
            <svg width="80" height="120" viewBox="0 0 100 150">
                <rect x="45" y="10" width="10" height="130" fill="{gold}" />
                <rect x="20" y="40" width="60" height="10" fill="{gold}" />
                <circle cx="50" cy="45" r="5" fill="#000" stroke="{gold}" stroke-width="2"/>
            </svg>
            <h1 style="font-family:'Cinzel'; margin:0;">SYSTEM OMEGA</h1>
        </center>
        """, unsafe_allow_html=True)
        
        tab_log, tab_reg = st.tabs(["ACESSO", "REGISTRO"])
        with tab_log:
            u = st.text_input("Credencial")
            p = st.text_input("Chave", type="password")
            if st.button("ENTRAR", use_container_width=True):
                if AccessControl.login(u, p):
                    st.session_state["logado"] = True
                    st.session_state["user_id"] = u.upper()
                    st.rerun()
                else: st.error("Acesso Negado.")
        
        with tab_reg:
            rn = st.text_input("Novo ID")
            rp = st.text_input("Nova Chave", type="password")
            if st.button("REGISTRAR", use_container_width=True):
                ok, msg = AccessControl.register(rn, rp)
                if ok: st.success(msg)
                else: st.warning(msg)
    st.stop()

# ==============================================================================
# 4. MÓDULOS DO PASTOR (O Código que você queria)
# ==============================================================================
with st.sidebar:
    st.markdown(f"<div style='text-align:center; padding:10px; border:1px solid #333;'>PASTOR: <b>{st.session_state['user_id']}</b></div>", unsafe_allow_html=True)
    menu = st.radio("MENU", ["Cuidado Pastoral", "Gabinete (Editor)", "Biblioteca", "Configurações"])
    st.markdown("---")
    if st.button("SAIR"): 
        st.session_state["logado"] = False
        st.rerun()

# --- MÓDULO 1: CUIDADO PASTORAL ---
if menu == "Cuidado Pastoral":
    st.title("🛡️ Cuidado Pastoral")
    t1, t2, t3 = st.tabs(["Dashboard", "Rebanho", "Saúde Interna"])
    
    with t1:
        c1, c2 = st.columns([2, 1])
        with c1:
            cats = ['Fé', 'Comunhão', 'Serviço', 'Missões', 'Doutrina']
            vals = [random.randint(50, 95) for _ in cats]
            plot_radar(cats, vals, "Radar da Igreja")
        with c2:
            st.markdown("**Tarefas Rápidas:**")
            st.checkbox("Orar (Manhã)")
            st.checkbox("Estudo Bíblico")

    with t2:
        membros = SafeIO.ler_json(DBS["MEMBERS"], [])
        with st.expander("➕ Adicionar Nova Ovelha", expanded=False):
            with st.form("new_sheep"):
                nm = st.text_input("Nome")
                stt = st.selectbox("Status", ["Comungante", "Não-Comungante", "Visitante"])
                if st.form_submit_button("Salvar Ficha"):
                    membros.append({"Nome": nm, "Status": stt, "Data": datetime.now().strftime("%d/%m")})
                    SafeIO.salvar_json(DBS["MEMBERS"], membros)
                    st.rerun()
        if membros: st.dataframe(pd.DataFrame(membros), use_container_width=True)

    with t3: # Teoria da Permissão (Restaurada)
        st.markdown("**Teoria da Permissão: Diagnóstico**")
        c_sld, c_grf = st.columns(2)
        with c_sld:
            p_fail = st.slider("Permissão p/ FALHAR", 0, 100, 50)
            p_feel = st.slider("Permissão p/ SENTIR", 0, 100, 50)
            p_rest = st.slider("Permissão p/ DESCANSAR", 0, 100, 50)
            p_succ = st.slider("Permissão p/ SUCESSO", 0, 100, 50)
        with c_grf:
            avg = (p_fail + p_feel + p_rest + p_succ) / 4
            plot_gauge_linear(avg, "Índice de Graça", config_data['theme_color'])

# --- MÓDULO 2: GABINETE (Editor Completo) ---
elif menu == "Gabinete (Editor)":
    st.title("📝 Gabinete da Palavra")
    
    col_sel, col_edit = st.columns([1, 3])
    files = [f for f in os.listdir(DIRS["SERMOES"]) if f.endswith(".txt")]
    with col_sel:
        sel = st.selectbox("Abrir:", ["- Novo -"] + files)
    
    txt_val = ""
    ttl_val = ""
    if sel != "- Novo -":
        try:
            with open(os.path.join(DIRS["SERMOES"], sel), 'r', encoding='utf-8') as f: txt_val = f.read()
            ttl_val = sel.replace(".txt", "")
        except: pass
    
    with col_edit:
        final_ttl = st.text_input("Título", value=ttl_val)
        if QUILL_AVAILABLE:
            final_txt = st_quill(value=txt_val, html=True)
        else:
            final_txt = st.text_area("Texto", value=txt_val, height=400)
            
        c_save, c_enc = st.columns(2)
        if c_save.button("SALVAR"):
            with open(os.path.join(DIRS["SERMOES"], f"{final_ttl}.txt"), 'w', encoding='utf-8') as f: f.write(final_txt)
            st.success("Salvo.")
        
        if c_enc.button("ENCRIPTAR"):
            pw = st.session_state["config"].get("enc_password")
            if pw:
                res = encrypt_sermon_aes(pw, final_txt)
                with open(os.path.join(DIRS["GABINETE"], f"{final_ttl}.enc"), 'w', encoding='utf-8') as f: f.write(res)
                st.success("Protegido com AES.")
            else: st.error("Configure uma senha primeiro.")

# --- MÓDULO 3: BIBLIOTECA ---
elif menu == "Biblioteca":
    st.title("📚 Biblioteca")
    st.info("Módulo de Arquivos Indexados Ativo.")

# --
