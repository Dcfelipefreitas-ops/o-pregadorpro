# -*- coding: utf-8 -*-
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
# 0. CONFIGURAÇÃO INICIAL (OBRIGATÓRIO SER A PRIMEIRA LINHA EXECUTÁVEL)
# ==============================================================================
st.set_page_config(
    page_title="O PREGADOR",
    layout="wide",
    page_icon="✝️",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# O PREGADOR - SYSTEM OMEGA (V31 -> V32 Consolidated)
# ==============================================================================
# Imports opcionais (serão tentados instalar pelo kernel se falharem)
try:
    import google.generativeai as genai
except Exception:
    genai = None

try:
    import plotly.express as px
    import plotly.graph_objects as go
except Exception:
    px = go = None

try:
    from PIL import Image, ImageOps
except Exception:
    Image = None

# ==============================================================================
# GENESIS PROTOCOL: cria pastas e arquivos mestres
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

    # config.json
    p_config = os.path.join(ROOT, "User_Data", "config.json")
    if not os.path.exists(p_config):
        with open(p_config, "w", encoding="utf-8") as f:
            json.dump({
                "theme_color": "#D4AF37",
                "font_size": 18,
                "enc_password": "OMEGA_KEY_DEFAULT",
                "api_key": "",
                "backup_interval_seconds": 24 * 3600,
                "last_backup": None
            }, f, indent=2, ensure_ascii=False)

    # users_db.json
    p_users = os.path.join(ROOT, "User_Data", "users_db.json")
    if not os.path.exists(p_users):
        senha_hash = hashlib.sha256("admin".encode()).hexdigest()
        with open(p_users, "w", encoding="utf-8") as f:
            json.dump({"ADMIN": senha_hash}, f, indent=2, ensure_ascii=False)

    # members.json
    p_members = os.path.join(ROOT, "Membresia", "members.json")
    if not os.path.exists(p_members):
        with open(p_members, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2, ensure_ascii=False)

    # metadata.json
    p_meta = os.path.join(ROOT, "Sermoes", "metadata.json")
    if not os.path.exists(p_meta):
        with open(p_meta, "w", encoding="utf-8") as f:
            json.dump({"sermons": []}, f, indent=2, ensure_ascii=False)

_genesis_boot_protocol()

# ==============================================================================
# SystemOmegaKernel: Gerenciador de Dependências e Headers
# ==============================================================================
class SystemOmegaKernel:
    REQUIRED = [
        "google-generativeai", "streamlit-lottie", "Pillow", "pandas",
        "streamlit-quill", "python-docx", "reportlab", "mammoth", "plotly", "cryptography"
    ]

    @staticmethod
    def _install_quiet(pkg):
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--quiet"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            return False

    @staticmethod
    def boot_check():
        missing = []
        for lib in SystemOmegaKernel.REQUIRED:
            mod = lib.replace("google-generativeai", "google.generativeai").replace("Pillow", "PIL").replace("python-docx", "docx").replace("streamlit-quill", "streamlit_quill")
            try:
                __import__(mod.split(".")[0])
            except Exception:
                missing.append(lib)
        if missing:
            placeholder = st.empty()
            placeholder.info(f"⚙️ System Omega: Atualizando dependências... ({len(missing)} pacotes)")
            for pkg in missing:
                SystemOmegaKernel._install_quiet(pkg)
            placeholder.empty()

    @staticmethod
    def inject_pwa_headers():
        st.markdown("""
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes">
        """, unsafe_allow_html=True)

try:
    SystemOmegaKernel.boot_check()
except Exception:
    pass

# ==============================================================================
# Imports Tardios (após boot_check)
# ==============================================================================
try:
    from streamlit_quill import st_quill
    QUILL_AVAILABLE = True
except Exception:
    QUILL_AVAILABLE = False

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    CRYPTO_OK = True
except Exception:
    CRYPTO_OK = False

try:
    import mammoth
    HTML2DOCX = "mammoth"
except Exception:
    try:
        from html2docx import html2docx
        HTML2DOCX = "html2docx"
    except Exception:
        HTML2DOCX = None

# ==============================================================================
# 1. INFRAESTRUTURA (Pastas e Caminhos)
# ==============================================================================
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
for p in DIRS.values(): os.makedirs(p, exist_ok=True)

logging.basicConfig(filename=os.path.join(DIRS["LOGS"], "system.log"), level=logging.INFO, format='%(asctime)s|%(levelname)s|%(message)s')

# ==============================================================================
# 2. SAFE IO
# ==============================================================================
class SafeIO:
    @staticmethod
    def ler_json(caminho, default_return):
        try:
            if not os.path.exists(caminho): return default_return
            with open(caminho, 'r', encoding='utf-8') as f:
                c = f.read().strip()
                return json.loads(c) if c else default_return
        except Exception:
            return default_return

    @staticmethod
    def salvar_json(caminho, dados):
        try:
            tmp = caminho + ".tmp"
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
            os.replace(tmp, caminho)
            try:
                shutil.copy2(caminho, os.path.join(DIRS["BACKUP"], os.path.basename(caminho) + ".bak"))
            except Exception:
                pass
            return True
        except Exception:
            return False

# ==============================================================================
# 3. VISUAL / CSS
# ==============================================================================
def inject_css_from_config(cfg):
    color = cfg.get("theme_color", "#D4AF37")
    font_sz = cfg.get("font_size", 18)
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700&family=Cinzel:wght@500;800&display=swap');
        :root{{--gold:{color};--bg:#000;--panel:#0A0A0A;--txt:#EAEAEA;}}
        .stApp{{background:#000; color:var(--txt); font-family:'Inter',sans-serif; font-size:{font_sz}px; padding-bottom:40px;}}
        [data-testid="stSidebar"]{{background:var(--panel); border-right:1px solid #111;}}
        .prime-logo{{width:120px;height:120px;display:block;margin:0 auto;}}
        .login-title{{font-family:Cinzel; color:var(--gold); text-align:center; letter-spacing:6px;}}
        .tech-card{{background:#090909;border:1px solid #111;border-left:3px solid var(--gold);padding:18px;border-radius:6px;margin-bottom:12px;}}
        @media (max-width: 600px) {{
            .stApp{{font-size:14px !important;}}
            .prime-logo{{width:90px;height:90px;}}
        }}
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 4. HELPERS (Crypto, PDF, Charts)
# ==============================================================================
def encrypt_sermon_aes(password, plaintext):
    if not CRYPTO_OK: return None
    key = hashlib.sha256(password.encode()).digest()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
    return base64.b64encode(nonce + ct).decode('utf-8')

def export_html_to_docx_better(title, html_content, out_path):
    if HTML2DOCX == "mammoth":
        with open(out_path, "wb") as docx_file:
            results = mammoth.convert_to_docx(html_content)
            docx_file.write(results.value)
    elif HTML2DOCX == "html2docx":
        from html2docx import html2docx
        with open(out_path, "wb") as f:
            f.write(html2docx(html_content))
    else:
        try:
            from docx import Document
            doc = Document()
            doc.add_heading(title, 1)
            import re
            plain = re.sub(r"<.*?>", "", html_content)
            doc.add_paragraph(plain)
            doc.save(out_path)
        except Exception:
            with open(out_path.replace(".docx", ".txt"), "w", encoding="utf-8") as f:
                f.write(html_content)

def export_text_to_pdf(title, text, out_path):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        c = canvas.Canvas(out_path, pagesize=letter)
        width, height = letter
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, height - 60, title)
        c.setFont("Helvetica", 10)
        y = height - 90
        for line in text.splitlines():
            if y < 60:
                c.showPage()
                y = height - 60
            c.drawString(40, y, line[:120])
            y -= 14
        c.save()
        return True
    except Exception:
        try:
            from fpdf import FPDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=title, ln=1)
            for line in text.splitlines():
                pdf.multi_cell(0, 7, line)
            pdf.output(out_path)
            return True
        except Exception:
            return False

def plot_radar_chart(categories, values, title):
    try:
        import plotly.graph_objects as go
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself', line_color=st.session_state["config"]["theme_color"]))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', polar=dict(radialaxis=dict(range=[0,100])))
        st.plotly_chart(fig, use_container_width=True)
    except Exception:
        st.write(f"{title}: {list(zip(categories, values))}")

def plot_gauge(value, title, theme_color):
    try:
        import plotly.graph_objects as go
        fig = go.Figure(go.Indicator(mode="gauge+number", value=value, title={'text': title}, gauge={'axis': {'range': [0,100]}, 'bar': {'color': theme_color}}))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    except Exception:
        st.write(f"{title}: {value}%")

# ==============================================================================
# 5. PARSERS (Mantidos)
# ==============================================================================
def get_bible_verse(ref, prefer='ARA', allow_online=True):
    return {"source":"demo", "text": f"Texto bíblico simulado para {ref}."}

def parse_theword_export(path):
    return "Texto extraído simulado."

def index_user_books(folder=None):
    return []

# ==============================================================================
# 6. ACCESS CONTROL (mantido, com registro OAuth simulados)
# ==============================================================================
class AccessControl:
    DEFAULT_USERS = {"ADMIN": hashlib.sha256("admin".encode()).hexdigest()}

    @staticmethod
    def _hash(text): return hashlib.sha256(text.encode()).hexdigest()

    @staticmethod
    def get_users():
        return SafeIO.ler_json(DBS["USERS"], AccessControl.DEFAULT_USERS)

    @staticmethod
    def register(username, password, method="local"):
        users = SafeIO.ler_json(DBS['USERS'], {})
        if username.upper() in users:
            return False, "USUÁRIO JÁ EXISTE."
        if method == "local":
            users[username.upper()] = AccessControl._hash(password)
        else:
            users[username.upper()] = {"method": method, "value": password}
        SafeIO.salvar_json(DBS['USERS'], users)
        logging.info(f"Novo registro: {username} via {method}")
        return True, "REGISTRO OK."

    @staticmethod
    def login(username, password):
        users = SafeIO.ler_json(DBS['USERS'], {})
        if not users and username.upper() == "ADMIN" and password == "1234":
            return True
        stored = users.get(username.upper())
        if stored is None:
            return False
        if isinstance(stored, str):
            if len(stored) == 64:
                return stored == AccessControl._hash(password)
            else:
                return stored == password
        elif isinstance(stored, dict):
            if stored.get("method") in ("google", "apple", "email"):
                return stored.get("value") == password
            return False
        return False

# ==============================================================================
# 7. LOGIC (Geneva, PastoralMind, Gamification)
# ==============================================================================
class GenevaProtocol:
    DB = {
        "prosperidade": "⚠️ ALERTA: Teologia da Prosperidade.",
        "eu decreto": "⚠️ ALERTA: Quebra de Soberania Divina.",
        "mérito": "⚠️ ALERTA: Pelagianismo (Sola Gratia).",
        "energia": "⚠️ ALERTA: Terminologia Nova Era."
    }
    @staticmethod
    def scan(text):
        if not text: return []
        return [v for k,v in GenevaProtocol.DB.items() if k in text.lower()]

class PastoralMind:
    @staticmethod
    def check_burnout():
        data = SafeIO.ler_json(DBS["SOUL"], {"historico": []})
        hist = data.get("historico", [])[-10:]
        bad = sum(1 for h in hist if h.get('humor') in ["Cansaço 🌖", "Ira 😠", "Ansiedade 🌪️", "Tristeza 😢"])
        if bad >= 6: return "CRÍTICO", "#FF3333"
        if bad >= 3: return "ALERTA", "#FFAA00"
        return "OPERACIONAL", "#33FF33"

    @staticmethod
    def registrar(humor):
        data = SafeIO.ler_json(DBS["SOUL"], {"historico": [], "diario": []})
        data.setdefault("historico", []).append({"data": datetime.now().strftime("%Y-%m-%d"), "humor": humor})
        SafeIO.salvar_json(DBS["SOUL"], data)

class Gamification:
    @staticmethod
    def add_xp(amount):
        stats = SafeIO.ler_json(DBS["STATS"], {"xp": 0, "nivel": 1})
        stats["xp"] = stats.get("xp", 0) + amount
        stats["nivel"] = int(math.sqrt(stats["xp"]) * 0.2) + 1
        SafeIO.salvar_json(DBS["STATS"], stats)

# ==============================================================================
# 8. BACKUP & SYNC (placeholders)
# ==============================================================================
def backup_local():
    try:
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        bk_base = os.path.join(DIRS["BACKUP"], f"backup_{now}")
        shutil.make_archive(bk_base, 'zip', ROOT)
        bk_name = bk_base + ".zip"
        logging.info(f"Backup criado: {bk_name}")
        return bk_name
    except Exception as e:
        logging.error(f"Erro backup: {e}")
        return None

def sync_to_google_drive(file_path):
    # TODO: configure Google Drive API
    return False

def sync_to_icloud(file_path):
    # TODO: configure iCloud / pyicloud
    return False

def auto_backup_if_due():
    cfg = SafeIO.ler_json(DBS["CONFIG"], {})
    last = cfg.get("last_backup")
    now = time.time()
    interval = cfg.get("backup_interval_seconds", 24 * 3600)
    if not last or (now - last) > interval:
        bk = backup_local()
        cfg["last_backup"] = now
        SafeIO.salvar_json(DBS["CONFIG"], cfg)
        return bk
    return None

# ==============================================================================
# 9. STARTUP
# ==============================================================================
if "config" not in st.session_state:
    st.session_state["config"] = SafeIO.ler_json(DBS["CONFIG"], {"theme_color": "#D4AF37", "font_size": 18, "enc_password": "", "api_key": "", "backup_interval_seconds": 24*3600})

inject_css_from_config(st.session_state["config"])

if "logado" not in st.session_state: st.session_state["logado"] = False
if "user_name" not in st.session_state: st.session_state["user_name"] = "ADMIN"
if "texto_ativo" not in st.session_state: st.session_state["texto_ativo"] = ""
if "titulo_ativo" not in st.session_state: st.session_state["titulo_ativo"] = ""

try:
    auto_backup_if_due()
except Exception:
    pass

# ==============================================================================
# 10. LOGIN UI (mantendo nomes e painel original)
# ==============================================================================
if not st.session_state["logado"]:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        gold = st.session_state["config"].get("theme_color", "#D4AF37")
        st.markdown(f"""
        <svg class="prime-logo" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="45" stroke="{gold}" stroke-width="3" fill="none" />
            <line x1="50" y1="25" x2="50" y2="75" stroke="{gold}" stroke-width="3" />
            <line x1="35" y1="40" x2="65" y2="40" stroke="{gold}" stroke-width="3" />
        </svg>
        <div class="login-title">O PREGADOR</div>
        <div style="text-align:center;font-size:10px;color:#555;letter-spacing:4px;margin-bottom:20px;">SYSTEM V31 | SHEPHERD EDITION</div>
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
                else:
                    st.error("NEGO A VOS CONHECER.")
        with t2:
            st.markdown("Registre uma nova conta — **novo usuário pode usar Google / Apple / Email / Senha**")
            nu = st.text_input("Novo ID", key="reg_nu")
            reg_method = st.radio("Método de registro", ["Senha (local)", "Google (OAuth)", "Apple (OAuth)", "Email (verificação)"], index=0)
            if reg_method == "Senha (local)":
                np = st.text_input("Nova Senha", type="password", key="reg_np")
                if st.button("CRIAR USUÁRIO (Local)", use_container_width=True):
                    ok, msg = AccessControl.register(nu, np, method="local")
                    if ok: st.success(msg)
                    else: st.error(msg)
            elif reg_method == "Google (OAuth)":
                if st.button("Registrar via Google"):
                    token = f"google_user_{nu}_{int(time.time())}"
                    ok, msg = AccessControl.register(nu, token, method="google")
                    if ok: st.success("Registrado via Google (simulado).")
                    else: st.error(msg)
            elif reg_method == "Apple (OAuth)":
                if st.button("Registrar via Apple"):
                    token = f"apple_user_{nu}_{int(time.time())}"
                    ok, msg = AccessControl.register(nu, token, method="apple")
                    if ok: st.success("Registrado via Apple (simulado).")
                    else: st.error(msg)
            else:
                email_addr = st.text_input("Email (para confirmação)", key="reg_email")
                if st.button("Registrar via Email"):
                    token = f"email_user_{email_addr}_{int(time.time())}"
                    ok, msg = AccessControl.register(nu, token, method="email")
                    if ok: st.success("Registrado via Email (simulado).")
                    else: st.error(msg)
    st.stop()

# ==============================================================================
# 11. MAIN APP shell (menu)
# ==============================================================================
if "hide_menu" not in st.session_state:
    st.session_state["hide_menu"] = False
c_main, c_tog = st.columns([0.9, 0.1])
with c_tog:
    if st.button("☰"):
        st.session_state["hide_menu"] = not st.session_state["hide_menu"]

if not st.session_state["hide_menu"]:
    menu = st.sidebar.radio("SISTEMA", ["Cuidado Pastoral", "Gabinete Pastoral", "Biblioteca", "Configurações"], index=0)
    st.sidebar.divider()
    if st.sidebar.button("LOGOUT"):
        st.session_state["logado"] = False
        st.rerun()
else:
    menu = "Cuidado Pastoral"

# HUD
status_b, cor_b = PastoralMind.check_burnout()
dia_liturgico = "DOMINGO - DIA DO SENHOR" if datetime.now().weekday() == 6 else "DIA FERIAL"
col_h1, col_h2 = st.columns([3,1])
with col_h1:
    st.markdown(f"<span style='color:#666; font-size:10px;'>LITURGIA:</span> <span style='font-family:Cinzel'>{dia_liturgico}</span>", unsafe_allow_html=True)
with col_h2:
    st.markdown(f"<div style='text-align:right;'><span style='color:#666; font-size:10px;'>VITALIDADE:</span> <span style='color:{cor_b}'>{status_b}</span></div>", unsafe_allow_html=True)
st.markdown("---")

# ==============================================================================
# 12. MÓDULO: CUIDADO PASTORAL
# ==============================================================================
if menu == "Cuidado Pastoral":
    st.title("🛡️ Cuidado Pastoral Dinâmico")
    tab_painel, tab_rebanho, tab_teoria, tab_tools = st.tabs(["📊 Painel do Pastor","🐑 Meu Rebanho","⚖️ Teoria da Permissão","🛠️ Ferramentas"])

    with tab_painel:
        c1, c2 = st.columns([2,1])
        with c1:
            st.markdown('<div class="tech-card">', unsafe_allow_html=True)
            st.subheader("Estado Geral da Igreja")
            cats = ['Espiritual','Emocional','Físico','Financeiro','Relacional']
            vals = [random.randint(40,90) for _ in cats]
            plot_radar_chart(cats, vals, "Saúde do Corpo")
            st.markdown('</div>', unsafe_allow_html=True)
            st.warning("⚠️ **Alerta Preventivo:** Irmão João não acessa o devocional há 5 dias.")
        with c2:
            st.markdown('<div class="tech-card">', unsafe_allow_html=True)
            st.subheader("Rotina Pastoral Semanal")
            tasks = ["Revisar pedidos de oração", "Planejar semana", "Visitas", "Estudo bíblico"]
            for t in tasks: st.checkbox(t)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.subheader("📊 Estatísticas Pastorais")
        stats = SafeIO.ler_json(DBS.get("STATS"), {"nivel":1,"xp":0,"members_count":0})
        members = SafeIO.ler_json(DBS["MEMBERS_DB"], [])
        stats["members_count"] = len(members)
        SafeIO.salvar_json(DBS.get("STATS"), stats)
        st.metric("Nível", stats.get("nivel",1))
        st.metric("XP", stats.get("xp",0))
        st.metric("Membros registrados", stats.get("members_count",0))

    with tab_rebanho:
        st.markdown("### Gestão de Ovelhas Baseada em Necessidades")
        members = SafeIO.ler_json(DBS["MEMBERS_DB"], [])
        with st.expander("➕ Nova Ovelha"):
            with st.form("add_member"):
                nm = st.text_input("Nome")
                stt = st.selectbox("Status", ["Comungante","Não-Comungante"])
                note = st.text_area("Observação")
                if st.form_submit_button("Salvar"):
                    members.append({"Nome": nm, "Status": stt, "Data": datetime.now().strftime("%d/%m"), "Nota": note})
                    SafeIO.salvar_json(DBS["MEMBERS_DB"], members)
                    st.success("Ovelha adicionada.")
                    st.experimental_rerun()
        if members:
            df = pd.DataFrame(members)
            st.dataframe(df, use_container_width=True)

        st.markdown("### Caminhos de Crescimento")
        c_path1, c_path2, c_path3 = st.columns(3)
        if c_path1.button("🌱 Trilha: Novo Convertido"):
            st.success("Trilha 'Novo Convertido' ativada.")
        if c_path2.button("🛡️ Trilha: Vencendo a Ansiedade"):
            st.success("Trilha 'Vencendo a Ansiedade' ativada.")
        if c_path3.button("📚 Trilha: Teologia Reformada"):
            st.success("Trilha 'Teologia Reformada' ativada.")

    with tab_teoria:
        st.markdown("### ⚖️ O Pastor também é Ovelha")
        col_input, col_viz = st.columns([1,1])
        with col_input:
            p_fail = st.slider("Permissão para FALHAR (Graça)",0,100,50)
            p_feel = st.slider("Permissão para SENTIR (Humanidade)",0,100,50)
            p_rest = st.slider("Permissão para DESCANSAR (Limite)",0,100,50)
            p_succ = st.slider("Permissão para SUCESSO (Dignidade)",0,100,50)
            if st.button("RODAR SCAN DIAGNÓSTICO"):
                score = (p_fail+p_feel+p_rest+p_succ)/4
                st.session_state['perm_score'] = score
        with col_viz:
            score = st.session_state.get('perm_score',50)
            plot_gauge(score, "Índice de Permissão Interna", st.session_state["config"]["theme_color"])
            if score < 40:
                st.error("MODO SOBREVIVÊNCIA: Risco de Burnout.")
            elif score < 70:
                st.warning("EM PROGRESSO: Ainda há legalismo interno.")
            else:
                st.success("LIBERDADE NA GRAÇA: Identidade saudável.")

    with tab_tools:
        st.markdown("### Ferramentas de Discipulado")
        e1 = st.expander("💬 Chat Pastoral & Pedidos")
        e2 = st.expander("🧩 Devocionais Interativos")
        with e1:
            st.text_area("Enviar mensagem...")
            st.button("Enviar Broadcast")
        with e2:
            st.markdown("**Desafio da Semana:** Ler Salmo 23.")
            st.radio("Quiz Bíblico", ["Isaías","Ezequiel","Jeremias"])
        st.divider()
        if st.button("Criar Backup Manual"):
            bkfile = backup_local()
            if bkfile: st.success(f"Backup salvo: {bkfile}")
            else: st.error("Falha ao criar backup.")
        if st.button("Sincronizar com Google Drive (se configurado)"):
            st.info("Sincronização simulada. Configure credenciais para ativar.")
        if st.button("Sincronizar com iCloud (se configurado)"):
            st.info("Sincronização simulada. Configure credenciais para ativar.")

# ==============================================================================
# 13. MÓDULO: GABINETE PASTORAL
# ==============================================================================
elif menu == "Gabinete Pastoral":
    st.title("📝 Gabinete Pastoral")
    METADATA_PATH = os.path.join(DIRS["SERMOES"], "metadata.json")
    if not os.path.exists(METADATA_PATH):
        SafeIO.salvar_json(METADATA_PATH, {"sermons": []})
    
    with st.expander("Configurações do Editor"):
        fs = st.slider("Fonte", 12, 30, 18)
        autosave = st.checkbox("Autosave", True)

    c_tit, c_tags = st.columns([3,1])
    st.session_state["titulo_ativo"] = c_tit.text_input("Título", st.session_state.get("titulo_ativo",""))
    st.session_state["last_tags"] = c_tags.text_input("Tags", ",".join(st.session_state.get("last_tags", []))).split(",")

    st.markdown("Importar (TheWord/Logos/PDF/DOCX):")
    up = st.file_uploader("Arquivo", label_visibility="collapsed", accept_multiple_files=False)

    if QUILL_AVAILABLE:
        content = st_quill(value=st.session_state.get("texto_ativo",""), key="editor_quill", height=400)
    else:
        content = st.text_area("Editor", st.session_state.get("texto_ativo",""), height=400)

    if content != st.session_state.get("texto_ativo",""):
        st.session_state["texto_ativo"] = content
        if autosave and st.session_state["titulo_ativo"]:
            try:
                fn = f"{st.session_state['titulo_ativo']}.txt"
                with open(os.path.join(DIRS["SERMOES"], fn), 'w', encoding="utf-8") as f: f.write(content)
                st.toast("Autosave realizado.", icon="💾")
            except Exception:
                pass

    c_save, c_exp = st.columns(2)
    with c_save:
        if st.button("Salvar"):
            fn = f"{st.session_state['titulo_ativo']}.txt"
            with open(os.path.join(DIRS["SERMOES"], fn), 'w', encoding="utf-8") as f: f.write(content)
            st.success("Salvo.")
        if st.button("Encriptar (Senha na Config)"):
            pw = st.session_state["config"].get("enc_password")
            if pw:
                enc = encrypt_sermon_aes(pw, content) if CRYPTO_OK else None
                with open(os.path.join(DIRS["GABINETE"], f"{st.session_state['titulo_ativo']}.enc"), 'w', encoding="utf-8") as f:
                    f.write(enc if enc else "")
                st.success("Encriptado.")
            else:
                st.error("Defina senha na config.")
    with c_exp:
        if st.button("Exportar DOCX"):
            fn = f"{st.session_state['titulo_ativo']}.docx"
            path = os.path.join(DIRS["SERMOES"], fn)
            export_html_to_docx_better(st.session_state['titulo_ativo'], content, path)
            try:
                with open(path, "rb") as f:
                    st.download_button("Baixar DOCX", f, file_name=fn)
            except Exception:
                st.error("Erro ao preparar download do DOCX.")
        if st.button("Exportar PDF"):
            fn = f"{st.session_state['titulo_ativo']}.pdf"
            path = os.path.join(DIRS["SERMOES"], fn)
            ok = export_text_to_pdf(st.session_state['titulo_ativo'], content, path)
            if ok:
                with open(path, "rb") as f:
                    st.download_button("Baixar PDF", f, file_name=fn)
            else:
                st.error("Falha na exportação para PDF (libs ausentes).")

# ==============================================================================
# 14. MÓDULO: BIBLIOTECA
# ==============================================================================
elif menu == "Biblioteca":
    st.title("📚 Biblioteca Reformada")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Busca Online (Google Books)")
        q = st.text_input("Termo (ex: Teologia Pactual)")
        if st.button("Buscar"):
            st.info("Conectando à API (simulado).")
    with col2:
        st.subheader("Arquivos Locais")
        books = index_user_books(DIRS["BIB_CACHE"])
        if books:
            st.write(books)
        else:
            st.info("Nenhum livro local indexado (use importar).")
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown('<div class="tech-card">Bíblias</div>', unsafe_allow_html=True)
    c2.markdown('<div class="tech-card">Comentários</div>', unsafe_allow_html=True)
    c3.markdown('<div class="tech-card">Dicionários</div>', unsafe_allow_html=True)
    c4.markdown('<div class="tech-card">PDFs Locais</div>', unsafe_allow_html=True)

# ==============================================================================
# 15. MÓDULO: CONFIGURAÇÕES
# ==============================================================================
elif menu == "Configurações":
    st.title("⚙️ Configurações")
    cfg = st.session_state["config"]
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Visual")
        nc = st.color_picker("Cor do Tema", cfg.get("theme_color", "#D4AF37"))
        nf = st.number_input("Tamanho Fonte", 12, 30, cfg.get("font_size", 18))
        nm = st.selectbox("Modo (apenas informativo)", ["Dark Cathedral","Pergaminho (Sepia)","Holy Light (Claro)"])
    with c2:
        st.markdown("### Segurança & Backup")
        npw = st.text_input("Senha Mestra de Encriptação", type="password", value=cfg.get("enc_password",""))
        api_key = st.text_input("API Key (Google - opcional)", value=cfg.get("api_key",""), type="password")
        interval_days = st.number_input("Intervalo de backup (dias)", 1, 30, int(cfg.get("backup_interval_seconds", 24*3600)//86400))
    if st.button("Salvar Tudo"):
        cfg["theme_color"] = nc
        cfg["font_size"] = nf
        cfg["theme_mode"] = nm
        cfg["enc_password"] = npw
        cfg["api_key"] = api_key
        cfg["backup_interval_seconds"] = int(interval_days * 24 * 3600)
        SafeIO.salvar_json(DBS["CONFIG"], cfg)
        st.success("Configurações salvas. Reinicie o app para aplicar totalmente quando necessário.")

# ==============================================================================
# 16. FINAL NOTES
# ==============================================================================
st.markdown("<br><br>", unsafe_allow_html=True)
st.caption("Sistema O PREGADOR — Versão consolidada. Configure Google Drive / iCloud externamente para sincronização automática quando desejar.")
