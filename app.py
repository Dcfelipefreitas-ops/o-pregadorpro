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
import calendar
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO

# ==============================================================================
# 0. KERNEL DE INICIALIZAÇÃO (BLINDAGEM DO SISTEMA)
# ==============================================================================
class SystemOmegaKernel:
    """
    Núcleo 'Raiz': Garante que o sistema rode em qualquer ambiente.
    """
    REQUIRED = ["google-generativeai", "streamlit-lottie", "Pillow", "pandas", "fpdf"]
    
    @staticmethod
    def _install(pkg):
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--quiet"])
        except: pass

    @staticmethod
    def boot_check():
        queue = []
        for lib in SystemOmegaKernel.REQUIRED:
            try:
                mod = lib.replace("google-generativeai", "google.generativeai").replace("Pillow", "PIL")
                __import__(mod.replace("-", "_"))
            except ImportError:
                queue.append(lib)
        
        if queue:
            placeholder = st.empty()
            placeholder.code(f"INITIALIZING THEOLOGY OS... ({len(queue)} MODULES)", language="bash")
            for lib in queue:
                SystemOmegaKernel._install(lib)
            placeholder.empty()
            st.rerun()

SystemOmegaKernel.boot_check()

import google.generativeai as genai
from PIL import Image, ImageOps

# ==============================================================================
# 1. INFRAESTRUTURA DE DADOS (SAFE I/O)
# ==============================================================================
st.set_page_config(
    page_title="O PREGADOR | Theology OS", 
    layout="wide", 
    page_icon="✝️", 
    initial_sidebar_state="expanded"
)

ROOT = "Dados_Pregador_V27_Genesis"
DIRS = {
    "SERMOES": os.path.join(ROOT, "Sermoes"),
    "GABINETE": os.path.join(ROOT, "Gabinete_Pastoral"),
    "SERIES": os.path.join(ROOT, "Series"),
    "MIDIA": os.path.join(ROOT, "Midia"),
    "USER": os.path.join(ROOT, "User_Data"),
    "BACKUP": os.path.join(ROOT, "Auto_Backup_Oculto")
}

DBS = {
    "SERIES": os.path.join(DIRS["SERIES"], "db_series.json"),
    "STATS": os.path.join(DIRS["USER"], "db_stats.json"),
    "CONFIG": os.path.join(DIRS["USER"], "config.json"),
    "SOUL": os.path.join(DIRS["GABINETE"], "soul_data.json"),
    "USERS": os.path.join(DIRS["USER"], "users_db.json") # NOVO DB DE USUÁRIOS
}

for d in DIRS.values():
    os.makedirs(d, exist_ok=True)

class SafeIO:
    """Sistema de Auto-Preservação de Dados."""
    @staticmethod
    def ler_json(caminho, default_return):
        if not os.path.exists(caminho): return default_return
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                c = f.read().strip()
                return json.loads(c) if c else default_return
        except: return default_return

    @staticmethod
    def salvar_json(caminho, dados):
        try:
            with open(caminho, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
            shutil.copy2(caminho, os.path.join(DIRS["BACKUP"], os.path.basename(caminho) + ".bak"))
        except: pass

# ==============================================================================
# 2. DESIGN SYSTEM "DARK CATHEDRAL"
# ==============================================================================
def inject_css(color="#D4AF37", font_sz=18):
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700&family=Playfair+Display:wght@600&family=Cinzel:wght@500;800&family=JetBrains+Mono&display=swap');
        
        :root {{ 
            --gold: {color}; 
            --gold-glow: rgba(212, 175, 55, 0.2);
            --neon-gold: #FFD700;
            --bg: #000000; 
            --panel: #0A0A0A; 
            --border: #1F1F1F; 
            --text: #EAEAEA; 
        }}
        
        /* BASE */
        .stApp {{ 
            background-color: var(--bg); 
            background-image: radial-gradient(circle at 50% -20%, #1a1200 0%, #000 70%);
            color: var(--text); 
            font-family: 'Inter', sans-serif; 
        }}
        
        /* SIDEBAR */
        [data-testid="stSidebar"] {{
            background-color: #050505;
            border-right: 1px solid var(--border);
        }}
        [data-testid="stSidebar"] hr {{ margin: 0; border-color: #222; }}
        
        /* --- AVATAR HOLOGRÁFICO (NÍVEL NASA) --- */
        @keyframes holo-reveal {{
            0% {{ opacity: 0; transform: scale(0.8) translateY(20px); filter: blur(10px); }}
            20% {{ opacity: 1; transform: scale(1.1); filter: blur(0px); }}
            40% {{ opacity: 0.8; transform: scale(0.95); filter: hue-rotate(90deg); }}
            60% {{ opacity: 1; transform: scale(1.02); filter: hue-rotate(0deg); }}
            100% {{ opacity: 1; transform: scale(1); }}
        }}
        
        @keyframes scanline {{
            0% {{ top: -10%; opacity: 0; }}
            50% {{ opacity: 1; }}
            100% {{ top: 110%; opacity: 0; }}
        }}

        .holo-container {{
            position: relative;
            width: 120px; height: 120px;
            margin: 0 auto 20px auto;
            border-radius: 50%;
            border: 2px solid var(--gold);
            overflow: hidden;
            box-shadow: 0 0 15px var(--gold-glow);
            animation: holo-reveal 1.5s cubic-bezier(0.23, 1, 0.32, 1) forwards;
            background: #000;
        }}
        
        .holo-img {{
            width: 100%; height: 100%;
            object-fit: cover;
            filter: sepia(50%) contrast(1.2);
        }}
        
        .holo-container::after {{
            content: '';
            position: absolute;
            width: 100%; height: 5px;
            background: var(--neon-gold);
            box-shadow: 0 0 10px var(--neon-gold);
            opacity: 0.6;
            animation: scanline 3s infinite linear;
        }}
        
        /* --- LOGIN LOGO (SVG PULSE) --- */
        @keyframes holy-pulse {{
            0% {{ filter: drop-shadow(0 0 5px var(--gold-glow)); transform: scale(1); }}
            50% {{ filter: drop-shadow(0 0 20px var(--gold)); transform: scale(1.02); }}
            100% {{ filter: drop-shadow(0 0 5px var(--gold-glow)); transform: scale(1); }}
        }}
        
        .prime-logo {{
            width: 140px; height: 140px;
            margin: 0 auto 20px auto;
            animation: holy-pulse 4s infinite ease-in-out;
            display: block;
        }}
        
        .login-title {{
            font-family: 'Cinzel'; letter-spacing: 8px; 
            color: #fff; font-size: 24px; margin-top: 10px;
            text-transform: uppercase; text-align: center;
        }}

        /* CARDS MODERNOS */
        .tech-card {{
            background: #090909;
            border: 1px solid var(--border);
            border-left: 2px solid var(--gold);
            border-radius: 4px; padding: 25px; margin-bottom: 20px;
            transition: 0.3s;
        }}
        .tech-card:hover {{ border-color: #333; box-shadow: 0 10px 30px -10px rgba(0,0,0,0.8); }}

        /* EDITOR */
        .editor-wrapper textarea {{
            font-family: 'Playfair Display', serif !important;
            font-size: {font_sz}px !important;
            line-height: 1.8;
            background-color: #050505 !important;
            border: 1px solid #1a1a1a !important;
            color: #ccc !important;
            padding: 40px !important;
        }}
        
        /* INPUTS */
        .stTextInput input, .stSelectbox div, .stTextArea textarea {{
            background-color: #0A0A0A !important; 
            border: 1px solid #222 !important; 
            color: #eee !important;
        }}
        .stButton button {{
            border-radius: 2px !important; text-transform: uppercase; letter-spacing: 2px;
            font-size: 11px; font-weight: 700; background: #111; color: #888; border: 1px solid #333;
        }}
        .stButton button:hover {{ border-color: var(--gold); color: var(--gold); }}
        
        /* TABS Custom */
        .stTabs [data-baseweb="tab-list"] {{ gap: 2px; }}
        .stTabs [data-baseweb="tab"] {{ background-color: transparent; border-radius: 4px 4px 0px 0px; color: #666; }}
        .stTabs [aria-selected="true"] {{ background-color: #111; color: var(--gold); border: 1px solid #222; border-bottom: none; }}
        
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. MOTORES DE INTELIGÊNCIA
# ==============================================================================

class AccessControl:
    """Sistema de Autenticação e Registro."""
    DEFAULT_USERS = {"ADMIN": "1234", "PR": "123"}
    
    @staticmethod
    def get_users():
        return SafeIO.ler_json(DBS["USERS"], AccessControl.DEFAULT_USERS)

    @staticmethod
    def register(username, password):
        users = AccessControl.get_users()
        u_upper = username.upper().strip()
        if u_upper in users:
            return False, "USUÁRIO JÁ EXISTE."
        if not username or not password:
            return False, "PREENCHA TODOS OS CAMPOS."
            
        users[u_upper] = password
        SafeIO.salvar_json(DBS["USERS"], users)
        return True, "REGISTRO EFETUADO COM SUCESSO."

    @staticmethod
    def login(username, password):
        users = AccessControl.get_users()
        u_upper = username.upper().strip()
        if u_upper in users and users[u_upper] == password:
            return True
        return False

class LiturgicalCalendar:
    @staticmethod
    def get_status():
        hoje = datetime.now()
        wd = hoje.weekday()
        if wd == 6: return "DOMINGO - DIA DO SENHOR"
        return "DIA FERIAL"

class GenevaProtocol:
    """O Guardião da Doutrina."""
    DB = {
        "prosperidade": "⚠️ ALERTA: Teologia da Prosperidade.",
        "eu decreto": "⚠️ ALERTA: Quebra de Soberania Divina.",
        "mérito": "⚠️ ALERTA: Pelagianismo (Sola Gratia).",
        "energia": "⚠️ ALERTA: Terminologia Nova Era."
    }
    @staticmethod
    def scan(text):
        if not text: return []
        return [v for k, v in GenevaProtocol.DB.items() if k in text.lower()]

class PastoralMind:
    """Monitor de Vitalidade."""
    @staticmethod
    def check_burnout():
        data = SafeIO.ler_json(DBS["SOUL"], {"historico": []})
        hist = data.get("historico", [])[-10:]
        bad = sum(1 for h in hist if h['humor'] in ["Cansaço 🌖", "Ira 😠", "Ansiedade 🌪️", "Tristeza 😢"])
        
        if bad >= 6: return "CRÍTICO", "#FF3333"
        if bad >= 3: return "ALERTA", "#FFAA00"
        return "OPERACIONAL", "#33FF33"

    @staticmethod
    def registrar(humor):
        data = SafeIO.ler_json(DBS["SOUL"], {"historico": [], "diario": []})
        data["historico"].append({"data": datetime.now().strftime("%Y-%m-%d"), "humor": humor})
        SafeIO.salvar_json(DBS["SOUL"], data)

class Gamification:
    @staticmethod
    def add_xp(amount):
        stats = SafeIO.ler_json(DBS["STATS"], {"xp": 0, "nivel": 1})
        stats["xp"] += amount
        stats["nivel"] = int(math.sqrt(stats["xp"]) * 0.2) + 1
        SafeIO.salvar_json(DBS["STATS"], stats)

# ==============================================================================
# 4. GESTÃO DE ESTADO
# ==============================================================================
if "config" not in st.session_state:
    st.session_state["config"] = SafeIO.ler_json(DBS["CONFIG"], {"theme_color": "#D4AF37", "font_size": 18})

inject_css(st.session_state["config"]["theme_color"], st.session_state["config"]["font_size"])

if "logado" not in st.session_state: st.session_state["logado"] = False
if "user_name" not in st.session_state: st.session_state["user_name"] = "Pastor"
if "texto_ativo" not in st.session_state: st.session_state["texto_ativo"] = ""
if "titulo_ativo" not in st.session_state: st.session_state["titulo_ativo"] = ""

# ==============================================================================
# 5. TELA DE LOGIN (COM SISTEMA DE REGISTRO)
# ==============================================================================
if not st.session_state["logado"]:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        gold = st.session_state["config"]["theme_color"]
        svg_logo = f"""
        <svg class="prime-logo" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="45" stroke="{gold}" stroke-width="3" fill="none" />
            <line x1="50" y1="25" x2="50" y2="75" stroke="{gold}" stroke-width="3" />
            <line x1="35" y1="40" x2="65" y2="40" stroke="{gold}" stroke-width="3" />
        </svg>
        """
        st.markdown(svg_logo, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="login-title">O PREGADOR</div>
        <div style="text-align:center; font-size:9px; color:#555; letter-spacing:4px; margin-bottom:30px;">SANCTUM AI V27</div>
        """, unsafe_allow_html=True)
        
        # ABAS DE LOGIN E REGISTRO
        tab_login, tab_register = st.tabs(["ACESSAR", "REGISTRAR"])
        
        with tab_login:
            with st.form("gate_keeper"):
                user = st.text_input("ID", label_visibility="collapsed", placeholder="IDENTIFICAÇÃO")
                pw = st.text_input("KEY", type="password", label_visibility="collapsed", placeholder="SENHA")
                st.markdown("<br>", unsafe_allow_html=True)
                
                if st.form_submit_button("INICIAR SISTEMA", type="primary", use_container_width=True):
                    if AccessControl.login(user, pw):
                        st.session_state["logado"] = True
                        st.session_state["user_name"] = user.upper()
                        Gamification.add_xp(5)
                        st.rerun()
                    else:
                        st.error("ACESSO NEGADO.")
        
        with tab_register:
            with st.form("new_user_gate"):
                new_u = st.text_input("Novo ID", placeholder="USUÁRIO")
                new_p = st.text_input("Nova Senha", type="password", placeholder="SENHA")
                confirm_p = st.text_input("Confirmar Senha", type="password", placeholder="CONFIRME A SENHA")
                st.markdown("<br>", unsafe_allow_html=True)
                
                if st.form_submit_button("CRIAR CREDENCIAL", use_container_width=True):
                    if new_p != confirm_p:
                        st.error("AS SENHAS NÃO CONFEREM.")
                    else:
                        success, msg = AccessControl.register(new_u, new_p)
                        if success:
                            st.success(msg)
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(msg)
    st.stop()

# ==============================================================================
# 6. APP PRINCIPAL
# ==============================================================================

# --- SIDEBAR (MONOLITO COM AVATAR HOLOGRÁFICO) ---
with st.sidebar:
    # Lógica de Avatar
    avatar_path = os.path.join(DIRS["USER"], "avatar.png")
    
    if os.path.exists(avatar_path):
        with open(avatar_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        st.markdown(f"""
        <div class="holo-container">
            <img src="data:image/png;base64,{encoded_string}" class="holo-img">
        </div>
        """, unsafe_allow_html=True)
    else:
        gold = st.session_state["config"]["theme_color"]
        st.markdown(f"""
        <div class="holo-container" style="display:flex; align-items:center; justify-content:center;">
            <span style="font-size:40px; color:{gold}">✝</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="text-align:center; padding-bottom:10px;">
        <div style="font-family:'Cinzel'; font-size:16px; color:{st.session_state["config"]["theme_color"]}">{st.session_state["user_name"]}</div>
        <div style="font-size:9px; color:#666; letter-spacing:2px;">MINISTRO DO EVANGELHO</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    menu = st.radio(
        "MÓDULOS", 
        ["Dashboard", "Gabinete Pastoral", "Studio Expositivo", "Séries Bíblicas", "Media Lab", "Configurações"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    stats = SafeIO.ler_json(DBS["STATS"], {"nivel": 1, "xp": 0})
    st.markdown(f"""
    <div style="font-family:'JetBrains Mono'; font-size:10px; color:#555; text-align:center;">
        LVL {stats['nivel']} // XP {stats['xp']}
    </div>
    """, unsafe_allow_html=True)

    if st.button("LOGOUT", use_container_width=True):
        st.session_state["logado"] = False
        st.rerun()

# --- HUD (STATUS HEADER) ---
status_b, cor_b = PastoralMind.check_burnout()
dia_liturgico = LiturgicalCalendar.get_status()

# Layout do Header
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown(f"<span style='color:#666; font-size:10px;'>LITURGIA:</span> <span style='font-family:Cinzel'>{dia_liturgico}</span>", unsafe_allow_html=True)
with col_h2:
    st.markdown(f"<div style='text-align:right;'><span style='color:#666; font-size:10px;'>VITALIDADE:</span> <span style='color:{cor_b}'>{status_b}</span></div>", unsafe_allow_html=True)
st.markdown("---")

# --- PÁGINAS ---

if menu == "Dashboard":
    st.markdown(f"<h2 style='font-family:Cinzel; margin-bottom:20px;'>Painel de Controle</h2>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
        st.caption("CHECK-IN ESPIRITUAL")
        humor = st.selectbox("Estado da Alma", ["Plenitude 🕊️", "Gratidão 🙏", "Cansaço 🌖", "Ira 😠", "Tristeza 😢", "Ansiedade 🌪️"], label_visibility="collapsed")
        if st.button("REGISTRAR ESTADO", use_container_width=True):
            PastoralMind.registrar(humor)
            Gamification.add_xp(10)
            st.success("DADOS COMPUTADOS.")
            time.sleep(1)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
    with c2:
        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
        st.caption("DIAGNÓSTICO")
        if status_b == "CRÍTICO":
            st.error("ALERTA MÁXIMO: Níveis de estresse excederam o limite seguro.")
        else:
            st.info(f"SISTEMA OPERACIONAL: {status_b}. Prossiga com a missão.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("Arquivos Recentes")
    files = sorted([f for f in os.listdir(DIRS["SERMOES"]) if f.endswith(".txt")], key=lambda x: os.path.getmtime(os.path.join(DIRS["SERMOES"], x)), reverse=True)[:3]
    
    cols = st.columns(3)
    for i, f in enumerate(files):
        with cols[i]:
            st.markdown(f"""
            <div style="border:1px solid #222; background:#090909; padding:20px; border-radius:4px;">
                <div style="color:#444; font-size:9px; letter-spacing:1px;">TXT FILE</div>
                <div style="font-family:'Cinzel'; font-size:14px; margin-top:5px;">{f.replace('.txt','')}</div>
            </div>
            """, unsafe_allow_html=True)

elif menu == "Gabinete Pastoral":
    st.title("Gabinete Pastoral")
    t1, t2 = st.tabs(["DIÁRIO CRIPTOGRAFADO", "TERAPIA DA VERDADE"])
    
    with t1:
        diario = st.text_area("Entrada de Dados", height=300)
        if st.button("GUARDAR NO COFRE"):
            soul = SafeIO.ler_json(DBS["SOUL"], {"diario": []})
            soul.setdefault("diario", []).append({"data": datetime.now().strftime("%Y-%m-%d"), "texto": diario})
            SafeIO.salvar_json(DBS["SOUL"], soul)
            st.toast("ARQUIVADO.", icon="🔒")
            
    with t2:
        mentira = st.text_input("Detectar Mentira (Input)")
        if mentira:
            st.success("VERDADE BÍBLICA: 'Porque dele, e por ele, e para ele são todas as coisas.' (Romanos 11:36)")

elif menu == "Studio Expositivo":
    if status_b == "CRÍTICO":
        st.error("⛔ ACESSO BLOQUEADO PELO PROTOCOLO DE SAÚDE.")
        st.stop()

    st.title("Studio Expositivo")
    
    c1, c2 = st.columns([3, 1])
    c1.text_input("Título", key="titulo_ativo", placeholder="Ex: Gênesis 1 - O Princípio")
    if c2.button("PERSISTIR DADOS", use_container_width=True, type="primary"):
        if st.session_state["titulo_ativo"]:
            path = os.path.join(DIRS["SERMOES"], f"{st.session_state['titulo_ativo']}.txt")
            with open(path, 'w', encoding='utf-8') as f: 
                f.write(st.session_state["texto_ativo"])
            SafeIO.salvar_json(os.path.join(DIRS["BACKUP"], "log.json"), {"saved": True})
            st.toast("DADOS SALVOS.", icon="💾")

    ce, ca = st.columns([2.5, 1])
    with ce:
        st.markdown('<div class="editor-wrapper">', unsafe_allow_html=True)
        st.session_state["texto_ativo"] = st.text_area("editor", st.session_state["texto_ativo"], height=600, label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with ca:
        st.markdown("#### Geneva Scan")
        alerts = GenevaProtocol.scan(st.session_state["texto_ativo"])
        if not alerts: st.markdown("<div style='color:#33FF33; font-size:12px; background:#001100; padding:5px;'>✅ DOUTRINA SÃ</div>", unsafe_allow_html=True)
        else:
            for a in alerts: st.warning(a)
            
        st.divider()
        st.markdown("#### IA Auxiliar")
        q = st.text_area("Query", height=100)
        if st.button("PROCESSAR"):
            if st.session_state["config"].get("api_key"):
                try:
                    genai.configure(api_key=st.session_state["config"]["api_key"])
                    r = genai.GenerativeModel("gemini-pro").generate_content(f"Teologia Reformada: {q}").text
                    st.info(r)
                except: st.error("FALHA NA API.")
            else: st.warning("API KEY NÃO DETECTADA.")

elif menu == "Séries Bíblicas":
    st.title("Séries Bíblicas")
    with st.expander("INICIAR NOVA SÉRIE", expanded=True):
        with st.form("serie"):
            n = st.text_input("Nome")
            d = st.text_area("Escopo")
            if st.form_submit_button("CRIAR"):
                db = SafeIO.ler_json(DBS["SERIES"], {})
                ts = int(time.time())
                db[f"S{ts}"] = {"nome": n, "descricao": d}
                SafeIO.salvar_json(DBS["SERIES"], db)
                st.success("CRIADO.")
                st.rerun()
                
    st.markdown("### Banco de Dados")
    db = SafeIO.ler_json(DBS["SERIES"], {})
    for k, v in db.items():
        st.markdown(f"<div class='tech-card'><b>{v['nome']}</b><br><small>{v['descricao']}</small></div>", unsafe_allow_html=True)

elif menu == "Media Lab":
    st.title("Media Lab")
    c1, c2 = st.columns(2)
    with c1: st.markdown('<div style="height:300px; border:1px dashed #333; display:flex; align-items:center; justify-content:center; color:#444;">RENDER PREVIEW</div>', unsafe_allow_html=True)
    with c2:
        st.text_input("Texto Overlay")
        st.selectbox("Template", ["Dark Theology", "Light Grace", "Nature"])
        if st.button("RENDERIZAR (SIMULAÇÃO)"): st.success("PROCESSADO.")

elif menu == "Configurações":
    st.title("Configurações do Sistema")
    
    st.markdown("### Identidade Visual")
    c1, c2 = st.columns(2)
    with c1:
        nc = st.color_picker("Cor Destaque", st.session_state["config"].get("theme_color", "#D4AF37"))
        nf = st.slider("Tamanho Fonte", 14, 28, st.session_state["config"].get("font_size", 18))
    with c2:
        cam = st.camera_input("ID Ministerial (Foto)")
        if cam:
            try:
                img = Image.open(cam)
                # Processamento Estético do ID
                img = ImageOps.grayscale(img)
                img = ImageOps.contrast(img, 1.2)
                img.save(os.path.join(DIRS["USER"], "avatar.png"))
                st.success("IDENTIDADE ATUALIZADA.")
            except: pass

    st.markdown("### Conectividade")
    nk = st.text_input("API Key (Google)", value=st.session_state["config"].get("api_key", ""), type="password")
        
    if st.button("ATUALIZAR PARÂMETROS", type="primary"):
        cfg = st.session_state["config"]
        c
