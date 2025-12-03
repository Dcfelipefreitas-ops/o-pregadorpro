# -*- coding: utf-8 -*-
"""
O PREGADOR - app.py (Versão Consolidada & Expandida - V33)
- Mantém: Geneva Protocol, PastoralMind, Gamification, JSON DB, Pastas V31.
- Adiciona: Módulo de Liturgia, Copiloto IA (Stub), Melhorias de Estabilidade.
"""
import streamlit as st
import os
import sys
import time
import json
import base64
import math
import shutil
import random
import logging
import hashlib
import re
from datetime import datetime
from io import BytesIO

# ---------------------------
# 0) PAGE CONFIG (must be first Streamlit call)
# ---------------------------
st.set_page_config(
    page_title="O PREGADOR",
    layout="wide",
    page_icon="✝️",
    initial_sidebar_state="expanded"
)

# ---------------------------
# Optional Imports / Fallbacks
# ---------------------------
CKEDITOR_AVAILABLE = False
STREAMLIT_CKEDITOR = False
QUILL_AVAILABLE = False
CRYPTO_OK = False
HTML2DOCX = None
PLOTLY_OK = False

try:
    from streamlit_ckeditor import st_ckeditor  # type: ignore
    STREAMLIT_CKEDITOR = True
    CKEDITOR_AVAILABLE = True
except Exception:
    pass

try:
    from streamlit_quill import st_quill  # type: ignore
    QUILL_AVAILABLE = True
except Exception:
    pass

try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_OK = True
except Exception:
    pass

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    CRYPTO_OK = True
except Exception:
    pass

try:
    import mammoth
    HTML2DOCX = "mammoth"
except Exception:
    try:
        from html2docx import html2docx  # type: ignore
        HTML2DOCX = "html2docx"
    except Exception:
        pass

# ---------------------------
# ROOT / GENESIS PROTOCOL (MANTIDO)
# ---------------------------
ROOT = "Dados_Pregador_V31"
DIRS = {
    "SERMOES": os.path.join(ROOT, "Sermoes"),
    "GABINETE": os.path.join(ROOT, "Gabinete_Pastoral"),
    "USER": os.path.join(ROOT, "User_Data"),
    "BACKUP": os.path.join(ROOT, "Auto_Backup_Oculto"),
    "LOGS": os.path.join(ROOT, "System_Logs"),
    "BIB_CACHE": os.path.join(ROOT, "BibliaCache"),
    "MEMBROS": os.path.join(ROOT, "Membresia"),
    "LITURGIA": os.path.join(ROOT, "Liturgias_Salvas") # Adicionado sem quebrar nada
}
DBS = {
    "CONFIG": os.path.join(DIRS["USER"], "config.json"),
    "USERS": os.path.join(DIRS["USER"], "users_db.json"),
    "SOUL": os.path.join(DIRS["GABINETE"], "soul_data.json"),
    "STATS": os.path.join(DIRS["USER"], "db_stats.json"),
    "MEMBERS_DB": os.path.join(DIRS["MEMBROS"], "members.json"),
    "LITURGIA_DB": os.path.join(DIRS["LITURGIA"], "cultos.json")
}

def _genesis_boot_protocol():
    for p in DIRS.values():
        os.makedirs(p, exist_ok=True)

    # config.json
    p_config = DBS["CONFIG"]
    if not os.path.exists(p_config):
        cfg = {
            "theme_color": "#D4AF37",
            "font_size": 18,
            "enc_password": "OMEGA_KEY_DEFAULT",
            "api_key": "",
            "backup_interval_seconds": 24 * 3600,
            "last_backup": None,
            "theme_mode": "Dark Cathedral",
            "font_family": "Inter",
            "work_mode": "Completo"
        }
        with open(p_config, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)

    # users_db.json
    p_users = DBS["USERS"]
    if not os.path.exists(p_users):
        senha_hash = hashlib.sha256("admin".encode()).hexdigest()
        with open(p_users, "w", encoding="utf-8") as f:
            json.dump({"ADMIN": senha_hash}, f, indent=2, ensure_ascii=False)

    # members.json
    p_members = DBS["MEMBERS_DB"]
    if not os.path.exists(p_members):
        with open(p_members, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2, ensure_ascii=False)
            
    # liturgia.json (Novo)
    p_lit = DBS["LITURGIA_DB"]
    if not os.path.exists(p_lit):
        with open(p_lit, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2, ensure_ascii=False)

    # metadata.json
    meta = os.path.join(DIRS["SERMOES"], "metadata.json")
    if not os.path.exists(meta):
        with open(meta, "w", encoding="utf-8") as f:
            json.dump({"sermons": []}, f, indent=2, ensure_ascii=False)

_genesis_boot_protocol()

# ---------------------------
# Logging
# ---------------------------
os.makedirs(DIRS["LOGS"], exist_ok=True)
logging.basicConfig(
    filename=os.path.join(DIRS["LOGS"], "system.log"),
    level=logging.INFO,
    format='%(asctime)s|%(levelname)s|%(message)s'
)

# ---------------------------
# Safe IO helpers
# ---------------------------
def read_json(path, default):
    try:
        if not os.path.exists(path):
            return default
        with open(path, "r", encoding="utf-8") as f:
            txt = f.read().strip()
            return json.loads(txt) if txt else default
    except Exception as e:
        logging.exception(f"read_json error: {e}")
        return default

def write_json(path, data):
    try:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        os.replace(tmp, path)
        try:
            shutil.copy2(path, os.path.join(DIRS["BACKUP"], os.path.basename(path) + ".bak"))
        except Exception:
            pass
        return True
    except Exception as e:
        logging.exception(f"write_json error: {e}")
        return False

# ---------------------------
# Utilities & Crypto
# ---------------------------
def safe_filename(name):
    s = (name or "").strip()
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^0-9A-Za-z_\-\.]", "", s)
    return s or "file"

def normalize_font_name(fname):
    if not fname: return "Inter"
    return fname.split(",")[0].strip().strip("'\"")

def encrypt_aes(password, plaintext):
    if not CRYPTO_OK: return None
    key = hashlib.sha256(password.encode()).digest()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    return base64.b64encode(nonce + ct).decode("utf-8")

def encrypt_sermon_aes(password, plaintext):
    return encrypt_aes(password, plaintext)

# ---------------------------
# Export helpers
# ---------------------------
def export_html_to_docx_better(title, html_content, out_path):
    if HTML2DOCX == "mammoth":
        try:
            with open(out_path, "wb") as docx_file:
                results = mammoth.convert_to_docx(html_content)
                docx_file.write(results.value)
            return True
        except Exception: return False
    elif HTML2DOCX == "html2docx":
        try:
            with open(out_path, "wb") as f: f.write(html2docx(html_content))
            return True
        except Exception: return False
    else:
        try:
            from docx import Document # type: ignore
            doc = Document()
            doc.add_heading(title, 1)
            plain = re.sub(r"<.*?>", "", html_content)
            doc.add_paragraph(plain)
            doc.save(out_path)
            return True
        except Exception: return False

def export_text_to_pdf(title, text, out_path):
    try:
        from reportlab.lib.pagesizes import letter # type: ignore
        from reportlab.pdfgen import canvas # type: ignore
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
    except Exception: return False

# ---------------------------
# Plot helpers
# ---------------------------
def plot_radar_chart(categories, values, title):
    if PLOTLY_OK:
        try:
            theme_color = st.session_state["config"].get("theme_color", "#D4AF37")
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself', line_color=theme_color, marker=dict(size=6)))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                polar=dict(radialaxis=dict(range=[0,100], gridcolor="#222")),
                margin=dict(l=10, r=10, t=30, b=10),
                title=dict(text=title, font=dict(color=theme_color, family="Cinzel"))
            )
            st.plotly_chart(fig, use_container_width=True)
            return
        except Exception: pass
    st.write(f"{title}: {list(zip(categories, values))}")

def plot_gauge(value, title):
    if PLOTLY_OK:
        try:
            theme_color = st.session_state["config"].get("theme_color", "#D4AF37")
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=value,
                title={'text': title},
                gauge={'axis': {'range': [0,100]}, 'bar': {'color': theme_color}, 'bgcolor': "#111"}
            ))
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=10,b=10))
            st.plotly_chart(fig, use_container_width=True)
            return
        except Exception: pass
    st.write(f"{title}: {value}%")

# ---------------------------
# Access Control (MANTIDO)
# ---------------------------
class AccessControl:
    DEFAULT_USERS = {"ADMIN": hashlib.sha256("admin".encode()).hexdigest()}

    @staticmethod
    def _hash(text): return hashlib.sha256(text.encode()).hexdigest()

    @staticmethod
    def get_users():
        return read_json(DBS["USERS"], AccessControl.DEFAULT_USERS)

    @staticmethod
    def register(username, password, method="local"):
        users = read_json(DBS["USERS"], {})
        if not username: return False, "Nome vazio."
        if username.upper() in users: return False, "JÁ EXISTE."
        if method == "local":
            users[username.upper()] = AccessControl._hash(password)
        else:
            users[username.upper()] = {"method": method, "value": password}
        write_json(DBS["USERS"], users)
        return True, "REGISTRO OK."

    @staticmethod
    def login(username, password):
        users = read_json(DBS["USERS"], {})
        if not users and username.upper() == "ADMIN" and password == "1234": return True
        stored = users.get(username.upper())
        if stored is None: return False
        if isinstance(stored, str):
            if len(stored) == 64: return stored == AccessControl._hash(password)
            else: return stored == password
        elif isinstance(stored, dict):
            if stored.get("method") in ("google", "apple", "email"): return stored.get("value") == password
        return False

# ---------------------------
# Logic: Geneva, PastoralMind, Gamification (MANTIDO)
# ---------------------------
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
        return [v for k, v in GenevaProtocol.DB.items() if k in text.lower()]

class PastoralMind:
    @staticmethod
    def check_burnout():
        data = read_json(DBS["SOUL"], {"historico": []})
        hist = data.get("historico", [])[-10:]
        bad = sum(1 for h in hist if h.get('humor') in ["Cansaço 🌖", "Ira 😠", "Ansiedade 🌪️", "Tristeza 😢"])
        if bad >= 6: return "CRÍTICO", "#FF3333"
        if bad >= 3: return "ALERTA", "#FFAA00"
        return "OPERACIONAL", "#33FF33"

    @staticmethod
    def registrar(humor):
        data = read_json(DBS["SOUL"], {"historico": [], "diario": []})
        data.setdefault("historico", []).append({"data": datetime.now().strftime("%Y-%m-%d"), "humor": humor})
        write_json(DBS["SOUL"], data)

class Gamification:
    @staticmethod
    def add_xp(amount):
        stats = read_json(DBS["STATS"], {"xp": 0, "nivel": 1})
        stats["xp"] = stats.get("xp", 0) + amount
        stats["nivel"] = int(math.sqrt(stats["xp"]) * 0.2) + 1
        write_json(DBS["STATS"], stats)

# ---------------------------
# NOVO: Copiloto IA (Mockup Integrado)
# ---------------------------
class AICopilotStub:
    @staticmethod
    def generate_outline(title, context):
        time.sleep(1)
        return f"""
        <b>Esboço Sugerido para: {title}</b><br>
        <i>Contexto: {context}</i><hr>
        I. Introdução: O Problema Humano<br>
        II. A Resposta Divina (Exegese)<br>
        III. Aplicação Prática para a Igreja<br>
        IV. Conclusão e Apelo
        """

    @staticmethod
    def check_theology(text):
        time.sleep(1)
        alerts = GenevaProtocol.scan(text)
        if alerts:
            return "<br>".join(alerts)
        return "Nenhum desvio doutrinário óbvio detectado pelo protocolo básico."

# ---------------------------
# Backup Functions
# ---------------------------
def backup_local():
    try:
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        bk_base = os.path.join(DIRS["BACKUP"], f"backup_{now}")
        shutil.make_archive(bk_base, 'zip', ROOT)
        return bk_base + ".zip"
    except Exception: return None

def auto_backup_if_due():
    cfg = read_json(DBS["CONFIG"], {})
    last = cfg.get("last_backup")
    now = time.time()
    interval = cfg.get("backup_interval_seconds", 24 * 3600)
    if not last or (now - last) > interval:
        bk = backup_local()
        cfg["last_backup"] = now
        write_json(DBS["CONFIG"], cfg)

def index_user_books(folder=None):
    folder = folder or DIRS["BIB_CACHE"]
    books = []
    try:
        for f in os.listdir(folder):
            if f.lower().endswith((".pdf", ".epub", ".txt", ".docx")):
                books.append(f)
    except Exception: pass
    return books

# ---------------------------
# STARTUP
# ---------------------------
if "config" not in st.session_state:
    st.session_state["config"] = read_json(DBS["CONFIG"], {
        "theme_color": "#D4AF37", "font_size": 18, "enc_password": "", "api_key": "",
        "backup_interval_seconds": 24 * 3600, "theme_mode": "Dark Cathedral", "font_family": "Inter"
    })

inject_font = normalize_font_name(st.session_state["config"].get("font_family", "Inter"))

def inject_css(cfg):
    color = cfg.get("theme_color", "#D4AF37")
    font_sz = cfg.get("font_size", 18)
    font_family = normalize_font_name(cfg.get("font_family", "Inter"))
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700&family=Cinzel:wght@500;800&display=swap');
    :root{{--gold:{color};--bg:#000;--panel:#0A0A0A;--txt:#EAEAEA;--font:{font_family};}}
    .stApp{{background:var(--bg); color:var(--txt); font-family:var(--font), Inter, sans-serif; font-size:{font_sz}px;}}
    [data-testid="stSidebar"]{{background:#070707; border-right:1px solid #111;}}
    .prime-logo{{width:120px;height:120px;display:block;margin:0 auto;}}
    .login-title{{font-family:Cinzel, serif; color:var(--gold); text-align:center; letter-spacing:6px; font-size:20px;}}
    .tech-card{{background:#090909;border:1px solid #111;border-left:3px solid var(--gold);padding:18px;border-radius:6px;margin-bottom:12px;}}
    .member-card{{background:#080808;border:1px solid #222;padding:12px;border-radius:6px;margin-bottom:8px;color:var(--txt);}}
    .action-btn{{display:inline-block;padding:6px 10px;border-radius:4px;border:1px solid var(--gold);color:var(--gold);text-decoration:none;margin-right:6px;font-size:12px;}}
    </style>
    """, unsafe_allow_html=True)

inject_css(st.session_state["config"])

if "logado" not in st.session_state: st.session_state["logado"] = False
if "user_name" not in st.session_state: st.session_state["user_name"] = "ADMIN"
if "texto_ativo" not in st.session_state: st.session_state["texto_ativo"] = ""
if "titulo_ativo" not in st.session_state: st.session_state["titulo_ativo"] = ""

try: auto_backup_if_due()
except: pass

# ---------------------------
# LOGIN UI (MANTIDO)
# ---------------------------
if not st.session_state["logado"]:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        gold = st.session_state["config"].get("theme_color", "#D4AF37")
        st.markdown(f"""
        <svg class="prime-logo" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="45" stroke="{gold}" stroke-width="3" fill="none" />
            <line x1="50" y1="25" x2="50" y2="75" stroke="{gold}" stroke-width="3" />
            <line x1="35" y1="40" x2="65" y2="40" stroke="{gold}" stroke-width="3" />
        </svg>
        <div class="login-title">O PREGADOR</div>
        <div style="text-align:center;font-size:10px;color:#888;letter-spacing:4px;margin-bottom:20px;">SYSTEM V33 | SHEPHERD EDITION</div>
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
            st.markdown("Registro Local ou Simulado")
            nu = st.text_input("Novo ID", key="reg_nu")
            np = st.text_input("Nova Senha", type="password", key="reg_np")
            if st.button("CRIAR USUÁRIO"):
                ok, msg = AccessControl.register(nu, np, method="local")
                if ok: st.success(msg)
                else: st.error(msg)
    st.stop()

# ---------------------------
# MAIN APP SHELL
# ---------------------------
if "hide_menu" not in st.session_state:
    st.session_state["hide_menu"] = False
c_main, c_tog = st.columns([0.9, 0.1])
with c_tog:
    if st.button("☰"):
        st.session_state["hide_menu"] = not st.session_state["hide_menu"]

if not st.session_state["hide_menu"]:
    # ADICIONADO "Liturgia" NO MENU ORIGINAL
    menu = st.sidebar.radio("SISTEMA", ["Cuidado Pastoral", "Gabinete Pastoral", "Liturgia", "Biblioteca", "Configurações"], index=0)
    st.sidebar.divider()
    if st.sidebar.button("LOGOUT"):
        st.session_state["logado"] = False
        st.rerun()
else:
    menu = "Cuidado Pastoral"

# HUD top
status_text, status_color = PastoralMind.check_burnout()
dia_lit = "DOMINGO - DIA DO SENHOR" if datetime.now().weekday() == 6 else "DIA FERIAL"
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown(f"<span style='color:#888; font-size:10px;'>LITURGIA:</span> <span style='font-family:Cinzel'>{dia_lit}</span>", unsafe_allow_html=True)
with col_h2:
    st.markdown(f"<div style='text-align:right;'><span style='color:#888; font-size:10px;'>VITALIDADE:</span> <span style='color:{status_color}'>{status_text}</span></div>", unsafe_allow_html=True)
st.markdown("---")

# ---------------------------
# Module 1: CUIDADO PASTORAL (MANTIDO 100%)
# ---------------------------
if menu == "Cuidado Pastoral":
    st.title("🛡️ Cuidado Pastoral Dinâmico")
    tab_painel, tab_rebanho, tab_teoria, tab_tools = st.tabs(["📊 Painel do Pastor", "🐑 Meu Rebanho", "⚖️ Teoria da Permissão", "🛠️ Ferramentas"])

    with tab_painel:
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown('<div class="tech-card">', unsafe_allow_html=True)
            st.subheader("Estado Geral da Igreja")
            cats = ['Espiritual', 'Emocional', 'Físico', 'Financeiro', 'Relacional']
            vals = [random.randint(40, 90) for _ in cats]
            plot_radar_chart(cats, vals, "Saúde do Corpo")
            st.markdown('</div>', unsafe_allow_html=True)
            stats = read_json(DBS["STATS"], {"nivel": 1, "xp": 0, "members_count": 0})
            members = read_json(DBS["MEMBERS_DB"], [])
            stats["members_count"] = len(members)
            write_json(DBS["STATS"], stats)
        with c2:
            st.markdown('<div class="tech-card">', unsafe_allow_html=True)
            st.subheader("Rotina Pastoral")
            tasks = ["Orar pelos membros", "Preparar Sermão", "Visitar Enfermos", "Ler a Palavra"]
            for t in tasks: st.checkbox(t)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.subheader("📊 Estatísticas")
        st.metric("XP Pastoral", stats.get("xp", 0))

    with tab_rebanho:
        st.markdown("### Gestão de Ovelhas")
        members = read_json(DBS["MEMBERS_DB"], [])
        with st.expander("➕ Nova Ovelha"):
            with st.form("add_member", clear_on_submit=True):
                nm = st.text_input("Nome")
                stt = st.selectbox("Status", ["Comungante", "Não-Comungante"])
                phone = st.text_input("Telefone")
                note = st.text_area("Nota")
                if st.form_submit_button("Salvar"):
                    members.append({"Nome": nm, "Status": stt, "Telefone": phone, "Nota": note, "Data": datetime.now().strftime("%Y-%m-%d")})
                    write_json(DBS["MEMBERS_DB"], members)
                    st.success("Salvo.")
                    st.rerun()
        
        if members:
            for i, m in enumerate(members):
                with st.expander(f"{m.get('Nome','-')} — {m.get('Status','')}"):
                    st.write(f"Tel: {m.get('Telefone','')}")
                    st.write(f"Nota: {m.get('Nota','')}")
                    if st.button("Remover", key=f"rm_{i}"):
                        members.pop(i)
                        write_json(DBS["MEMBERS_DB"], members)
                        st.rerun()
        else:
            st.info("Nenhuma ovelha cadastrada.")

    with tab_teoria:
        st.markdown("### ⚖️ O Pastor também é Ovelha")
        p_val = st.slider("Nível de Auto-Cobrança", 0, 100, 50)
        plot_gauge(100-p_val, "Nível de Graça Pessoal")

    with tab_tools:
        st.markdown("### Ferramentas Rápidas")
        if st.button("Backup Agora"):
            bk = backup_local()
            st.success(f"Backup: {bk}")

# ---------------------------
# Module 2: GABINETE PASTORAL (EXPANDIDO COM IA)
# ---------------------------
elif menu == "Gabinete Pastoral":
    st.title("📝 Gabinete Pastoral")
    
    # Layout expandido: Biblioteca na Esquerda, Editor no Meio, IA na Direita
    col_lib, col_editor, col_ai = st.columns([1, 3, 1.2])

    with col_lib:
        st.markdown("### Arquivos")
        # Listagem simples
        sermoes = [f for f in os.listdir(DIRS["SERMOES"]) if f.endswith(".html")]
        sel = st.radio("Seus Sermões", ["Novo"] + sermoes, label_visibility="collapsed")
        
        st.markdown("---")
        st.markdown("**Biblioteca Local**")
        books = index_user_books(DIRS["BIB_CACHE"])
        for b in books: st.caption(f"📖 {b}")

    # Lógica de Carregamento
    if sel == "Novo":
        # Se mudou para novo, limpa ou mantem o que estava sendo digitado se titulo for vazio
        if st.session_state.get("last_sel") != "Novo":
            st.session_state["texto_ativo"] = ""
            st.session_state["titulo_ativo"] = ""
    elif sel != st.session_state.get("last_sel"):
        try:
            with open(os.path.join(DIRS["SERMOES"], sel), "r", encoding="utf-8") as f:
                st.session_state["texto_ativo"] = f.read()
            st.session_state["titulo_ativo"] = sel.replace(".html", "")
        except: pass
    
    st.session_state["last_sel"] = sel

    with col_editor:
        # Título e Editor
        st.session_state["titulo_ativo"] = st.text_input("Título do Sermão", st.session_state.get("titulo_ativo", ""))
        
        content = st.session_state.get("texto_ativo", "")

        # Tenta usar o melhor editor disponível
        if CKEDITOR_AVAILABLE and STREAMLIT_CKEDITOR:
            content = st_ckeditor(content, key="ck_main", height=500)
        elif QUILL_AVAILABLE:
            content = st_quill(content, key="quill_main", height=500)
        else:
            content = st.text_area("Editor Texto", content, height=500)
        
        st.session_state["texto_ativo"] = content

        # Botões de Ação do Editor
        c_sv, c_pdf = st.columns(2)
        with c_sv:
            if st.button("💾 Salvar Trabalho"):
                if not st.session_state["titulo_ativo"]:
                    st.error("Defina um título.")
                else:
                    fn = safe_filename(st.session_state["titulo_ativo"]) + ".html"
                    with open(os.path.join(DIRS["SERMOES"], fn), "w", encoding="utf-8") as f:
                        f.write(content)
                    st.success("Salvo com sucesso.")
                    Gamification.add_xp(10)
        
        with c_pdf:
            if st.button("📄 Exportar DOCX"):
                fn = safe_filename(st.session_state["titulo_ativo"] or "sermao") + ".docx"
                path = os.path.join(DIRS["SERMOES"], fn)
                if export_html_to_docx_better(st.session_state["titulo_ativo"], content, path):
                    st.success(f"Exportado: {fn}")
                else:
                    st.error("Erro na exportação.")

    # Coluna Extra: IA Copiloto (Adição V33)
    with col_ai:
        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
        st.markdown("### 🤖 Copiloto")
        st.caption("Assistente Hermenêutico")
        
        if st.button("Gerar Esboço (IA)"):
            with st.spinner("Analisando..."):
                sug = AICopilotStub.generate_outline(st.session_state["titulo_ativo"], "Geral")
                st.markdown(sug, unsafe_allow_html=True)
        
        if st.button("Checar Teologia"):
            res = AICopilotStub.check_theology(content)
            st.warning(res) if "ALERTA" in res else st.success(res)

        st.markdown("---")
        st.info("Dica: Use Geneva Protocol para validar conteúdo.")
        st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# Module 3: LITURGIA (NOVO MÓDULO V33)
# ---------------------------
elif menu == "Liturgia":
    st.title("🕊️ Liturgia & Culto")
    
    # Carregar liturgias salvas
    liturgias = read_json(DBS["LITURGIA_DB"], [])
    
    tab_criador, tab_hist = st.tabs(["Criador de Liturgia", "Histórico"])
    
    with tab_criador:
        c1, c2 = st.columns([1, 1])
        if "liturgia_temp" not in st.session_state:
            st.session_state["liturgia_temp"] = []
            
        with c1:
            st.subheader("Adicionar Elemento")
            tipo = st.selectbox("Tipo", ["Louvor", "Leitura", "Oração", "Sermão", "Ceia", "Avisos"])
            desc = st.text_input("Descrição (Ex: Hino 32)")
            mins = st.number_input("Minutos", 1, 60, 5)
            if st.button("Adicionar"):
                st.session_state["liturgia_temp"].append({"tipo": tipo, "desc": desc, "min": mins})
        
        with c2:
            st.subheader("Ordem do Culto")
            if st.session_state["liturgia_temp"]:
                total = 0
                for i, item in enumerate(st.session_state["liturgia_temp"]):
                    st.markdown(f"**{i+1}. {item['tipo']}** - {item['desc']} ({item['min']} min)")
                    total += item['min']
                st.markdown(f"**Tempo Total Estimado:** {total} minutos")
                
                if st.button("Salvar Liturgia"):
                    novo_culto = {
                        "data": datetime.now().strftime("%Y-%m-%d"),
                        "itens": st.session_state["liturgia_temp"],
                        "total_min": total
                    }
                    liturgias.append(novo_culto)
                    write_json(DBS["LITURGIA_DB"], liturgias)
                    st.success("Liturgia salva no histórico!")
                    st.session_state["liturgia_temp"] = []
                    Gamification.add_xp(20)
                
                if st.button("Limpar"):
                    st.session_state["liturgia_temp"] = []
                    st.rerun()
            else:
                st.info("Adicione itens à esquerda.")

    with tab_hist:
        if liturgias:
            for l in reversed(liturgias):
                with st.expander(f"Culto de {l['data']} ({l['total_min']} min)"):
                    for item in l['itens']:
                        st.write(f"- {item['tipo']}: {item['desc']}")
        else:
            st.info("Nenhuma liturgia salva.")

# ---------------------------
# Module 4: BIBLIOTECA (MANTIDO)
# ---------------------------
elif menu == "Biblioteca":
    st.title("📚 Biblioteca Reformada")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Busca Online (Simulada)")
        q = st.text_input("Termo")
        if st.button("Buscar"):
            st.info("Conexão simulada. Insira API Key em Config para ativar.")
    with col2:
        st.subheader("Arquivos Locais")
        books = index_user_books(DIRS["BIB_CACHE"])
        if books:
            for b in books: st.write(b)
        else:
            st.info("Nenhum arquivo na pasta BibliaCache.")
            
    # Upload rápido
    up = st.file_uploader("Importar PDF/EPUB", type=["pdf", "epub", "docx"])
    if up:
        with open(os.path.join(DIRS["BIB_CACHE"], up.name), "wb") as f:
            f.write(up.getbuffer())
        st.success("Livro adicionado.")

# ---------------------------
# Module 5: CONFIGURAÇÕES (MANTIDO)
# ---------------------------
elif menu == "Configurações":
    st.title("⚙️ Configurações")
    cfg = st.session_state["config"]
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Visual")
        nc = st.color_picker("Cor Tema", cfg.get("theme_color"))
        # Salvar
        if st.button("Aplicar Cor"):
            cfg["theme_color"] = nc
            write_json(DBS["CONFIG"], cfg)
            st.rerun()

    with c2:
        st.markdown("### Dados")
        if st.button("Forçar Backup Completo"):
            bk = backup_local()
            st.success(f"Backup criado em {bk}")

# ---------------------------
# Footer
# ---------------------------
st.markdown("<br><br>", unsafe_allow_html=True)
st.caption("Sistema O PREGADOR V33 — Código Preservado & Expandido.")
