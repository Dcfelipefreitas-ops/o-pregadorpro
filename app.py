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
# [-] SYSTEM OMEGA: GENESIS PROTOCOL (AUTO-REPARO DE AMBIENTE)
# ==============================================================================
def _genesis_boot_protocol():
    ROOT = "Dados_Pregador_V31"
    STRUTURA = [
        os.path.join(ROOT, "Sermoes"),
        os.path.join(ROOT, "Gabinete_Pastoral"),
        os.path.join(ROOT, "User_Data"),
        os.path.join(ROOT, "Auto_Backup_Oculto"),
        os.path.join(ROOT, "System_Logs"),
        os.path.join(ROOT, "BibliaCache"),
        os.path.join(ROOT, "Membresia")
    ]
    for pasta in STRUTURA:
        os.makedirs(pasta, exist_ok=True)

    # Garante config
    p_config = os.path.join(ROOT, "User_Data", "config.json")
    if not os.path.exists(p_config):
        with open(p_config, "w") as f:
            json.dump({"theme_color": "#D4AF37", "font_size": 18, "enc_password": ""}, f)
    
    # Garante Banco de Membros
    p_membros = os.path.join(ROOT, "Membresia", "members.json")
    if not os.path.exists(p_membros):
        with open(p_membros, "w") as f: json.dump([], f)

    # Garante Users
    p_users = os.path.join(ROOT, "User_Data", "users_db.json")
    if not os.path.exists(p_users):
        h = hashlib.sha256("admin".encode()).hexdigest()
        with open(p_users, "w") as f: json.dump({"ADMIN": h}, f)

_genesis_boot_protocol()

# ==============================================================================
# 0. KERNEL DE INICIALIZAÇÃO (System Omega V31)
# ==============================================================================
class SystemOmegaKernel:
    REQUIRED = [
        "google-generativeai", "streamlit-lottie", "Pillow", "pandas",
        "streamlit-quill", "python-docx", "reportlab", "mammoth", "plotly"
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
                mod = lib.replace("google-generativeai", "google.generativeai") \
                         .replace("Pillow", "PIL") \
                         .replace("python-docx", "docx") \
                         .replace("streamlit-quill", "streamlit_quill") \
                         .replace("plotly", "plotly")
                __import__(mod.replace("-", "_"))
            except ImportError:
                queue.append(lib)
        
        if queue:
            placeholder = st.empty()
            placeholder.code(f"SYSTEM UPDATE :: INSTALLING MODULES ({len(queue)})... PLEASE WAIT.", language="bash")
            for lib in queue:
                SystemOmegaKernel._install_quiet(lib)
            placeholder.empty()
            st.rerun()

    @staticmethod
    def inject_pwa_headers():
        st.markdown("""
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        """, unsafe_allow_html=True)

SystemOmegaKernel.boot_check()

import google.generativeai as genai
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from PIL import Image, ImageOps

# Editor Rico Opcional
try:
    from streamlit_quill import st_quill
    QUILL_AVAILABLE = True
except Exception:
    QUILL_AVAILABLE = False

# ==============================================================================
# 1. INFRAESTRUTURA DE DADOS (NASA SAFE I/O)
# ==============================================================================
st.set_page_config(page_title="O PREGADOR", layout="wide", page_icon="✝️", initial_sidebar_state="expanded")
SystemOmegaKernel.inject_pwa_headers()

ROOT = "Dados_Pregador_V31"
DIRS = {
    "SERMOES": os.path.join(ROOT, "Sermoes"),
    "GABINETE": os.path.join(ROOT, "Gabinete_Pastoral"),
    "USER": os.path.join(ROOT, "User_Data"),
    "BACKUP": os.path.join(ROOT, "Auto_Backup_Oculto"),
    "LOGS": os.path.join(ROOT, "System_Logs"),
    "BIB_CACHE": os.path.join(ROOT, "BibliaCache"),
    "MEMBROS": os.path.join(ROOT, "Membresia")
}
DBS = {
    "CONFIG": os.path.join(DIRS["USER"], "config.json"),
    "USERS": os.path.join(DIRS["USER"], "users_db.json"),
    "SOUL": os.path.join(DIRS["GABINETE"], "soul_data.json"),
    "STATS": os.path.join(DIRS["USER"], "db_stats.json"),
    "MEMBERS_DB": os.path.join(DIRS["MEMBROS"], "members.json")
}

for p in DIRS.values():
    os.makedirs(p, exist_ok=True)

logging.basicConfig(filename=os.path.join(DIRS["LOGS"], "system.log"), level=logging.INFO, format='%(asctime)s|%(levelname)s|%(message)s')

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
            tmp = caminho + ".tmp"
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
            os.replace(tmp, caminho)
            return True
        except Exception: return False

# ==============================================================================
# 2. VISUAL SYSTEM REFORMULADO (Theme Engine)
# ==============================================================================
def inject_css(config_dict):
    color = config_dict.get("theme_color", "#D4AF37")
    bg_mode = config_dict.get("theme_mode", "Dark Cathedral")
    font_fam = config_dict.get("font_family", "Inter")
    font_sz = config_dict.get("font_size", 18)
    
    # Cores
    if bg_mode == "Dark Cathedral":
        bg_hex, panel_hex, text_hex = "#000000", "#0A0A0A", "#EAEAEA"
    elif bg_mode == "Pergaminho (Sepia)":
        bg_hex, panel_hex, text_hex = "#F4ECD8", "#E8DFCA", "#2b2210"
    elif bg_mode == "Holy Light (Claro)":
        bg_hex, panel_hex, text_hex = "#FFFFFF", "#F0F2F6", "#111111"
    else: 
        bg_hex, panel_hex, text_hex = "#000000", "#0A0A0A", "#EAEAEA"

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700&family=Playfair+Display:wght@600&family=Cinzel:wght@500;800&family=Merriweather:wght@300;700&display=swap');
        
        :root {{ 
            --gold: {color}; --bg: {bg_hex}; --panel: {panel_hex}; --text: {text_hex}; --font: '{font_fam}', sans-serif;
        }}
        
        .stApp {{ background-color: var(--bg); color: var(--text); font-family: var(--font); font-size: {font_sz}px; }}
        
        [data-testid="stSidebar"] {{ background-color: var(--panel); border-right: 1px solid var(--gold); }}
        
        /* CORREÇÃO DE ALINHAMENTO DE INPUTS */
        .stTextInput input, .stSelectbox div, .stTextArea textarea {{ 
            background-color: var(--panel) !important; 
            border: 1px solid #444 !important; 
            color: var(--text) !important; 
            border-radius: 4px;
        }}
        .stTextInput input:focus, .stTextArea textarea:focus {{ border-color: var(--gold) !important; }}
        
        /* TABELAS PROFISSIONAIS */
        [data-testid="stDataFrame"] {{ border: 1px solid #333; }}
        
        h1, h2, h3 {{ color: var(--gold) !important; font-family: 'Cinzel', serif !important; }}
        
        /* ANIMAÇÃO CRUZ LOGIN */
        @keyframes holy-pulse {{ 0% {{ filter: drop-shadow(0 0 5px rgba(212, 175, 55, 0.2)); }} 50% {{ filter: drop-shadow(0 0 20px var(--gold)); }} 100% {{ filter: drop-shadow(0 0 5px rgba(212, 175, 55, 0.2)); }} }}
        .prime-logo {{ animation: holy-pulse 4s infinite ease-in-out; display: block; margin: 0 auto; }}
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. HELPERS (Crypto, Exports, Charts)
# ==============================================================================
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    CRYPTO_OK = True
except: CRYPTO_OK = False

def encrypt_sermon_aes(password, plaintext):
    if not CRYPTO_OK: return None
    key = hashlib.sha256(password.encode()).digest()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
    return base64.b64encode(nonce + ct).decode('utf-8')

# HTML -> DOCX
try:
    import mammoth
    HTML2DOCX = "mammoth"
except: HTML2DOCX = None

def export_html_to_docx_better(title, html_content, out_path):
    if HTML2DOCX == "mammoth":
        with open(out_path, "wb") as docx_file:
            results = mammoth.convert_to_docx(html_content)
            docx_file.write(results.value)
    else:
        with open(out_path, "w", encoding='utf-8') as f: f.write(html_content)

# CHART HELPERS - Atualizados para Alinhamento e Visual Moderno
def plot_radar_chart(categories, values, title):
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values, theta=categories, fill='toself',
        line_color=st.session_state["config"]["theme_color"],
        marker=dict(color='#FFFFFF'), opacity=0.8
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100], color='#555'), bgcolor='rgba(0,0,0,0)'),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#EAEAEA', family="Inter"),
        title=dict(text=title, font=dict(family="Cinzel", size=20)),
        margin=dict(l=40, r=40, t=30, b=30)
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_gauge(value, title, theme_color):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = value,
        title = {'text': title, 'font': {'size': 18, 'family': 'Cinzel', 'color': theme_color}},
        gauge = {
            'axis': {'range': [0, 100], 'tickcolor': "#555"},
            'bar': {'color': theme_color},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2, 'bordercolor': "#333",
            'steps': [{'range': [0, 100], 'color': '#111'}]
        }
    ))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "#EEE"}, margin=dict(t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

# ==============================================================================
# 5. ACCESS CONTROL (BUGFIXED)
# ==============================================================================
class AccessControl:
    @staticmethod
    def _hash(text): return hashlib.sha256(text.encode()).hexdigest()
    
    @staticmethod
    def register(username, password):
        # Lê direto do arquivo para garantir
        users = SafeIO.ler_json(DBS['USERS'], {})
        if username.upper() in users: return False, "USUÁRIO JÁ EXISTE."
        
        # Adiciona e salva imediatamente
        users[username.upper()] = AccessControl._hash(password)
        saved = SafeIO.salvar_json(DBS['USERS'], users)
        
        if saved: return True, "REGISTRO OK."
        return False, "ERRO NO DISCO."

    @staticmethod
    def login(username, password):
        users = SafeIO.ler_json(DBS['USERS'], {})
        # Admin Default (Bypass)
        if username.upper() == "ADMIN" and password == "1234" and "ADMIN" not in users: return True
        
        hashed = AccessControl._hash(password)
        stored = users.get(username.upper())
        if stored: return stored == password if len(stored)!=64 else stored == hashed
        return False

# ==============================================================================
# 6. APP LOGIC
# ==============================================================================
if "config" not in st.session_state:
    st.session_state["config"] = SafeIO.ler_json(DBS["CONFIG"], {"theme_color": "#D4AF37", "font_size": 18, "enc_password": ""})

# Injeta CSS (Nova Função Aprimorada)
inject_css(st.session_state["config"])

if "logado" not in st.session_state: st.session_state["logado"] = False
if not st.session_state["logado"]:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        gold = st.session_state["config"].get("theme_color", "#D4AF37")
        st.markdown(f"""
        <svg class="prime-logo" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" style="width:140px; height:140px;">
            <circle cx="50" cy="50" r="45" stroke="{gold}" stroke-width="3" fill="none" />
            <line x1="50" y1="25" x2="50" y2="75" stroke="{gold}" stroke-width="3" />
            <line x1="35" y1="40" x2="65" y2="40" stroke="{gold}" stroke-width="3" />
        </svg>
        <div style="font-family:'Cinzel'; text-align:center; color:#FFF; margin-top:10px; font-size:24px;">SYSTEM OMEGA</div>
        <div style="text-align:center; font-size:10px; color:#555; letter-spacing:4px; margin-bottom:20px;">SYSTEM V31 | SHEPHERD EDITION</div>
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
                else: st.error("NEGO A VOS CONHECER.")
        with t2:
            nu = st.text_input("Novo ID")
            np = st.text_input("Nova Senha", type="password")
            if st.button("CRIAR", use_container_width=True):
                ok, msg = AccessControl.register(nu, np)
                if ok: st.success(msg)
                else: st.error(msg)
    st.stop()

# MAIN APP SIDEBAR
if "hide_menu" not in st.session_state: st.session_state.hide_menu = False
c_main, c_tog = st.columns([0.9, 0.1])
with c_tog:
    if st.button("☰"): st.session_state.hide_menu = not st.session_state.hide_menu

if not st.session_state.hide_menu:
    menu = st.sidebar.radio("SISTEMA", ["Cuidado Pastoral", "Gabinete Pastoral", "Biblioteca", "Configurações"], index=0)
    st.sidebar.divider()
    if st.sidebar.button("LOGOUT"):
        st.session_state["logado"] = False
        st.rerun()
else: menu = "Cuidado Pastoral"

# ==============================================================================
# MÓDULO 1: CUIDADO PASTORAL
# ==============================================================================
if menu == "Cuidado Pastoral":
    st.title("🛡️ Cuidado Pastoral Dinâmico")
    
    tab_painel, tab_rebanho, tab_teoria, tab_tools = st.tabs(["📊 Painel do Pastor", "🐑 Meu Rebanho", "⚖️ Teoria da Permissão", "🛠️ Ferramentas"])

    with tab_painel:
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown('<div class="tech-card">', unsafe_allow_html=True)
            st.subheader("Estado Geral da Igreja")
            # Gráfico de Radar
            cats = ['Espiritual', 'Emocional', 'Físico', 'Financeiro', 'Relacional']
            vals = [random.randint(40, 90) for _ in cats] 
            plot_radar_chart(cats, vals, "Saúde do Corpo")
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.subheader("Tarefas Semanais")
            for t in ["Orar Pelos Santos", "Preparar Sermão", "Visitas"]:
                st.checkbox(t)

    with tab_rebanho:
        # CÓDIGO MELHORADO: Usa o banco de dados Members real
        FILE_MEMBROS = DBS["MEMBERS_DB"]
        membros = SafeIO.ler_json(FILE_MEMBROS, [])

        # Inputs Alinhados em Colunas
        with st.expander("➕ Adicionar Ovelha (Ficha)", expanded=False):
            with st.form("add_member_form"):
                cc1, cc2, cc3 = st.columns([2,1,1])
                nm = cc1.text_input("Nome")
                stt = cc2.selectbox("Status", ["Comungante", "Não Comungante", "Visitante"])
                nec = cc3.text_input("Necessidade")
                if st.form_submit_button("Salvar no Livro"):
                    if nm:
                        membros.append({"Nome": nm, "Status": stt, "Necessidade": nec, "Data": datetime.now().strftime("%d/%m")})
                        SafeIO.salvar_json(FILE_MEMBROS, membros)
                        st.success("Adicionado.")
                        st.rerun()

        # Tabela Profissional (Use Container Width)
        st.markdown("### Rol de Membros")
        if membros:
            df = pd.DataFrame(membros)
            st.dataframe(
                df, 
                use_container_width=True,
                column_config={"Nome": "Ovelha", "Status": "Situação", "Necessidade": "Obs. Pastoral"},
                hide_index=True
            )
        else:
            st.info("Nenhuma ovelha cadastrada no banco.")

    with tab_teoria:
        # TEORIA DA PERMISSÃO (MANTIDO E VISUAL OTIMIZADO)
        st.markdown("### ⚖️ O Pastor também é Ovelha")
        col_input, col_viz = st.columns([1, 1])
        with col_input:
            p_fail = st.slider("Permissão para FALHAR", 0, 100, 50)
            p_feel = st.slider("Permissão para SENTIR", 0, 100, 50)
            if st.button("DIAGNÓSTICO"):
                st.session_state['perm_score'] = (p_fail + p_feel) / 2
        with col_viz:
            score = st.session_state.get('perm_score', 50)
            plot_gauge(score, "Saúde Interna", st.session_state["config"]["theme_color"])

    with tab_tools:
        st.write("Ferramentas de discipulado (em desenvolvimento)")

# ==============================================================================
# MÓDULO 2: GABINETE PASTORAL (Mantido com Editor Rico)
# ==============================================================================
elif menu == "Gabinete Pastoral":
    st.title("📝 Gabinete Pastoral")
    
    METADATA_PATH = os.path.join(DIRS["SERMOES"], "metadata.json")
    
    c_tit, c_tags = st.columns([3, 1])
    st.session_state["titulo_ativo"] = c_tit.text_input("Título", st.session_state.get("titulo_ativo", ""))
    st.session_state["last_tags"] = c_tags.text_input("Tags", "Domingo, Doutrina")

    # Editor Import
    if QUILL_AVAILABLE:
        content = st_quill(value=st.session_state.get("texto_ativo", ""), key="editor_quill", height=400)
    else:
        content = st.text_area("Editor Texto", st.session_state.get("texto_ativo", ""), height=400)
    
    st.session_state["texto_ativo"] = content

    c_save, c_exp = st.columns(2)
    with c_save:
        if st.button("Salvar Sermão"):
            fn = f"{st.session_state['titulo_ativo']}.txt"
            with open(os.path.join(DIRS["SERMOES"], fn), 'w') as f: f.write(content)
            st.success(f"Salvo como {fn}")
        if st.button("Encriptar (.ENC)"):
            pw = st.session_state["config"].get("enc_password")
            if pw:
                enc = encrypt_sermon_aes(pw, content)
                with open(os.path.join(DIRS["GABINETE"], f"{st.session_state['titulo_ativo']}.enc"), 'w') as f: f.write(enc)
                st.success("Sermão Criptografado com sucesso.")
            else: st.error("Defina a Senha Mestra nas Configurações.")

# ==============================================================================
# MÓDULO 3: BIBLIOTECA (Mantido)
# ==============================================================================
elif menu == "Biblioteca":
    st.title("📚 Biblioteca Reformada")
    st.info("Conexão com Google Books API e Sistema de Indexação de PDF.")
    st.text_input("Pesquisar na Biblioteca Local...")
    
# ==============================================================================
# MÓDULO 4: CONFIGURAÇÕES (UPGRADE THEWORD STYLE)
# ==============================================================================
elif menu == "Configurações":
    st.title("⚙️ Sistema & Personalização")
    st.markdown("Ajuste a aparência e comportamento do System Omega.")
    
    cfg = st.session_state["config"]
    
    # Organização Profissional
    tab_vis, tab_layout, tab_dados, tab_adv = st.tabs([
        "🎨 Temas (Visual)", "🪟 Módulos", "💾 Backup & Dados", "🔒 Segurança"
    ])
    
    # --- ABA 1: VISUAL ---
    with tab_vis:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Estilo")
            new_theme = st.selectbox(
                "Modo de Cores (Preset)", 
                ["Dark Cathedral", "Pergaminho (Sepia)", "Holy Light (Claro)"],
                index=["Dark Cathedral", "Pergaminho (Sepia)", "Holy Light (Claro)"].index(cfg.get("theme_mode", "Dark Cathedral"))
            )
            new_color = st.color_picker("Cor de Destaque (Liturgia)", cfg.get("theme_color", "#D4AF37"))
            
        with c2:
            st.subheader("Tipografia")
            new_font = st.selectbox(
                "Fonte Principal", ["Inter", "Cinzel", "Playfair Display", "Merriweather"],
                index=["Inter", "Cinzel", "Playfair Display", "Merriweather"].index(cfg.get("font_family", "Inter"))
            )
            new_size = st.slider("Tamanho da Fonte Base", 12, 28, cfg.get("font_size", 18))
        
        # PREVIEW EM TEMPO REAL
        st.divider()
        st.markdown("**Pré-visualização:**")
        st.markdown(f"""
        <div style="background:{'#F4ECD8' if new_theme=='Pergaminho (Sepia)' else '#111'}; padding:15px; border-left:3px solid {new_color}; color:{'#222' if new_theme=='Pergaminho (Sepia)' else '#EEE'}">
            <span style="font-family:{new_font}; font-size:{new_size}px">"No princípio criou Deus o céu e a terra."</span>
        </div>""", unsafe_allow_html=True)

    # --- ABA 2: LAYOUT ---
    with tab_layout:
        st.subheader("Controle de Módulos")
        st.toggle("Mostrar Gabinete Pastoral", True)
        st.toggle("Mostrar Cuidado/Membresia", True)

    # --- ABA 3: DADOS ---
    with tab_dados:
        if st.button("Fazer Backup Completo (ZIP)"):
            st.info("Função de compressão ZIP em processamento...")

    # --- ABA 4: SEGURANÇA ---
    with tab_adv:
        st.subheader("Criptografia Master")
        new_pw = st.text_input("Senha para Encriptação AES-256", value=cfg.get("enc_password", ""), type="password")

    # SAVE
    st.markdown("---")
    if st.button("💾 APLICAR TODAS AS ALTERAÇÕES", type="primary", use_container_width=True):
        cfg["theme_mode"] = new_theme
        cfg["theme_color"] = new_color
        cfg["font_family"] = new_font
        cfg["font_size"] = new_size
        cfg["enc_password"] = new_pw
        SafeIO.salvar_json(DBS["CONFIG"], cfg)
        st.success("Configuração Salva. Recarregando...")
        time.sleep(1)
        st.rerun()
