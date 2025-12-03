# -*- coding: utf-8 -*-
"""
O PREGADOR - App consolidado (Bug Fix & Clean Up)
Versão: Stable V32
"""

import streamlit as st
import os, sys, time, json, base64, math, shutil, random, logging, hashlib, re, subprocess
from datetime import datetime
from io import BytesIO

# ---------------------------------------------------------------------
# 0. PAGE CONFIG - OBRIGATÓRIO SER A PRIMEIRA LINHA
# ---------------------------------------------------------------------
st.set_page_config(page_title="O PREGADOR", layout="wide", page_icon="✝️", initial_sidebar_state="expanded")

# ---------------------------------------------------------------------
# OPTIONAL IMPORTS / FALLBACKS
# ---------------------------------------------------------------------
try:
    import plotly.graph_objects as go
    import plotly.express as px
except Exception:
    go = px = None

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

# ---------------------------------------------------------------------
# SYSTEM KERNEL (Gerenciador de Dependências)
# ---------------------------------------------------------------------
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
    SystemOmegaKernel.inject_pwa_headers()
except Exception:
    pass

# Imports Tardios (após verificação)
try:
    import pandas as pd
    from PIL import Image, ImageOps
except: pass

# ---------------------------------------------------------------------
# ROOT / GENESIS PROTOCOL
# ---------------------------------------------------------------------
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

def _genesis():
    base_dirs = list(DIRS.values())
    for p in base_dirs:
        os.makedirs(p, exist_ok=True)
    
    # Arquivos Base
    if not os.path.exists(DBS["CONFIG"]):
        default_cfg = {
            "theme_color": "#D4AF37", "font_size": 18, "enc_password": "OMEGA_KEY_DEFAULT",
            "api_key": "", "backup_interval_seconds": 24*3600, "last_backup": None,
            "theme_mode": "Dark Cathedral", "font_family": "Inter", "work_mode": "Completo"
        }
        with open(DBS["CONFIG"], "w", encoding="utf-8") as f:
            json.dump(default_cfg, f, indent=2, ensure_ascii=False)
            
    if not os.path.exists(DBS["USERS"]):
        with open(DBS["USERS"], "w", encoding="utf-8") as f:
            admin_hash = hashlib.sha256("admin".encode()).hexdigest()
            json.dump({"ADMIN": admin_hash}, f, indent=2, ensure_ascii=False)
            
    if not os.path.exists(DBS["MEMBERS_DB"]):
        with open(DBS["MEMBERS_DB"], "w", encoding="utf-8") as f: json.dump([], f)
        
    if not os.path.exists(os.path.join(DIRS["SERMOES"], "metadata.json")):
        with open(os.path.join(DIRS["SERMOES"], "metadata.json"), "w", encoding="utf-8") as f:
            json.dump({"sermons": []}, f)

_genesis()

logging.basicConfig(filename=os.path.join(DIRS["LOGS"], "system.log"), level=logging.INFO, format='%(asctime)s|%(levelname)s|%(message)s')

# ---------------------------------------------------------------------
# SAFE IO helpers
# ---------------------------------------------------------------------
class SafeIO:
    @staticmethod
    def ler_json(path, default):
        try:
            if not os.path.exists(path): return default
            with open(path, "r", encoding="utf-8") as f:
                c = f.read().strip()
                return json.loads(c) if c else default
        except Exception:
            return default

    @staticmethod
    def salvar_json(path, data):
        try:
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            os.replace(tmp, path)
            try:
                shutil.copy2(path, os.path.join(DIRS["BACKUP"], os.path.basename(path) + ".bak"))
            except: pass
            return True
        except Exception as e:
            logging.error(f"write_json error {e}")
            return False

# ---------------------------------------------------------------------
# UTILITIES & CRYPTO
# ---------------------------------------------------------------------
def safe_filename(name):
    s = (name or "").strip()
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^0-9A-Za-z_\-\.]", "", s)
    return s or "file"

def encrypt_aes(password, plaintext):
    if not CRYPTO_OK: return None
    key = hashlib.sha256(password.encode()).digest()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    return base64.b64encode(nonce + ct).decode("utf-8")

# ---------------------------------------------------------------------
# EXPORT HELPERS
# ---------------------------------------------------------------------
def export_html_to_docx_better(title, html_content, out_path):
    if HTML2DOCX == "mammoth":
        with open(out_path, "wb") as f:
            results = mammoth.convert_to_docx(html_content)
            f.write(results.value)
    elif HTML2DOCX == "html2docx":
        from html2docx import html2docx
        with open(out_path, "wb") as f: f.write(html2docx(html_content))
    else:
        # Fallback simples
        try:
            from docx import Document
            doc = Document()
            doc.add_heading(title, 1)
            plain = re.sub(r"<.*?>", "", html_content)
            doc.add_paragraph(plain)
            doc.save(out_path)
        except:
            with open(out_path.replace(".docx", ".txt"), "w", encoding="utf-8") as f:
                f.write(html_content)

def export_text_to_pdf(title, text, out_path):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        c = canvas.Canvas(out_path, pagesize=letter)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, 750, title)
        c.setFont("Helvetica", 10)
        y = 730
        for line in text.splitlines():
            if y < 60:
                c.showPage()
                y = 750
            c.drawString(40, y, line[:100])
            y -= 14
        c.save()
        return True
    except:
        return False

# ---------------------------------------------------------------------
# PLOTTING
# ---------------------------------------------------------------------
def plot_radar(categories, values, title):
    try:
        theme = st.session_state["config"].get("theme_color", "#D4AF37")
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself', line_color=theme))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', polar=dict(radialaxis=dict(range=[0,100], gridcolor="#333")), margin=dict(t=20,b=10))
        st.plotly_chart(fig, use_container_width=True)
    except:
        st.write("Gráfico indisponível (Bibliotecas faltando)")

def plot_gauge_chart(value, title):
    try:
        theme = st.session_state["config"].get("theme_color", "#D4AF37")
        fig = go.Figure(go.Indicator(mode="gauge+number", value=value, title={'text': title}, gauge={'axis': {'range': [0,100]}, 'bar': {'color': theme}}))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=10,b=10))
        st.plotly_chart(fig, use_container_width=True)
    except:
        st.write(f"{title}: {value}%")

# ---------------------------------------------------------------------
# BIBLE & BOOKS
# ---------------------------------------------------------------------
def index_books(folder=None):
    folder = folder or DIRS["BIB_CACHE"]
    books = []
    try:
        for f in os.listdir(folder):
            if f.lower().endswith((".pdf", ".docx", ".txt", ".epub")):
                books.append(f)
    except: pass
    return books

# ---------------------------------------------------------------------
# ACCESS CONTROL
# ---------------------------------------------------------------------
class AccessControl:
    @staticmethod
    def _hash(txt): return hashlib.sha256(txt.encode()).hexdigest()

    @staticmethod
    def register(username, password, method="local"):
        if not username: return False, "Nome vazio."
        users = SafeIO.ler_json(DBS["USERS"], {})
        if username.upper() in users: return False, "USUÁRIO JÁ EXISTE."
        
        if method == "local":
            users[username.upper()] = AccessControl._hash(password)
        else:
            users[username.upper()] = {"method": method, "value": password}
        SafeIO.salvar_json(DBS["USERS"], users)
        return True, "REGISTRO OK."

    @staticmethod
    def login(username, password):
        users = SafeIO.ler_json(DBS["USERS"], {})
        if not users and username.upper() == "ADMIN" and password == "1234": return True
        
        stored = users.get(username.upper())
        if stored is None: return False
        
        if isinstance(stored, str): # Hash antigo ou senha
            return stored == AccessControl._hash(password) or stored == password
        elif isinstance(stored, dict): # OAuth
            return stored.get("value") == password
        return False

# ---------------------------------------------------------------------
# PASTORAL LOGIC
# ---------------------------------------------------------------------
class PastoralMind:
    @staticmethod
    def check_burnout():
        data = SafeIO.ler_json(DBS["SOUL"], {"historico": []})
        hist = data.get("historico", [])[-10:]
        bad = sum(1 for h in hist if h.get("humor") in ["Cansaço", "Ira", "Ansiedade", "Tristeza"])
        if bad >= 6: return "CRÍTICO", "#FF3333"
        if bad >= 3: return "ALERTA", "#FFAA00"
        return "OPERACIONAL", "#33FF33"

# ---------------------------------------------------------------------
# BACKUP
# ---------------------------------------------------------------------
def backup_local():
    try:
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        base = os.path.join(DIRS["BACKUP"], f"backup_{now}")
        shutil.make_archive(base, 'zip', ROOT)
        return base + ".zip"
    except: return None

def auto_backup_if_due():
    cfg = SafeIO.ler_json(DBS["CONFIG"], {})
    last = cfg.get("last_backup")
    now = time.time()
    interval = cfg.get("backup_interval_seconds", 24*3600)
    if not last or (now - last) > interval:
        backup_local()
        cfg["last_backup"] = now
        SafeIO.salvar_json(DBS["CONFIG"], cfg)

# ---------------------------------------------------------------------
# STARTUP STATE
# ---------------------------------------------------------------------
if "config" not in st.session_state:
    st.session_state["config"] = SafeIO.ler_json(DBS["CONFIG"], {"theme_color":"#D4AF37","font_size":18,"enc_password":"","api_key":"","backup_interval_seconds":86400,"theme_mode":"Dark Cathedral"})
if "logado" not in st.session_state: st.session_state["logado"] = False
if "user_name" not in st.session_state: st.session_state["user_name"] = "ADMIN"

try: auto_backup_if_due()
except: pass

# ---------------------------------------------------------------------
# CSS / THEME
# ---------------------------------------------------------------------
def inject_css(cfg):
    color = cfg.get("theme_color", "#D4AF37")
    font_sz = cfg.get("font_size", 18)
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700&family=Cinzel:wght@500;800&display=swap');
    :root{{--gold:{color};--bg:#000;--panel:#0A0A0A;--txt:#EAEAEA;}}
    .stApp{{background:var(--bg); color:var(--txt); font-family:'Inter',sans-serif; font-size:{font_sz}px;}}
    [data-testid="stSidebar"]{{background:#070707; border-right:1px solid #111;}}
    .prime-logo{{width:120px;height:120px;display:block;margin:0 auto;}}
    .login-title{{font-family:Cinzel, serif; color:var(--gold); text-align:center; letter-spacing:6px; font-size:20px;}}
    .tech-card{{background:#090909;border:1px solid #111;border-left:3px solid var(--gold);padding:18px;border-radius:6px;margin-bottom:12px;}}
    .member-card{{background:#080808;border:1px solid #222;padding:12px;border-radius:6px;margin-bottom:8px;}}
    .action-btn{{display:inline-block;padding:4px 8px;border:1px solid var(--gold);color:var(--gold);text-decoration:none;font-size:12px;margin-right:5px;}}
    @media (max-width:800px) {{ .stApp{{font-size:{max(14,int(font_sz-4))}px;}} .prime-logo{{width:90px;height:90px;}} }}
    </style>
    """, unsafe_allow_html=True)

inject_css(st.session_state["config"])

# ---------------------------------------------------------------------
# LOGIN UI
# ---------------------------------------------------------------------
if not st.session_state["logado"]:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1,c2,c3 = st.columns([1,1,1])
    with c2:
        gold = st.session_state["config"].get("theme_color", "#D4AF37")
        st.markdown(f"""
            <svg class="prime-logo" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <circle cx="50" cy="50" r="45" stroke="{gold}" stroke-width="3" fill="none" />
                <line x1="50" y1="25" x2="50" y2="75" stroke="{gold}" stroke-width="3" />
                <line x1="35" y1="40" x2="65" y2="40" stroke="{gold}" stroke-width="3" />
            </svg>
            <div class="login-title">O PREGADOR</div>
            <div style="text-align:center;font-size:10px;color:#888;letter-spacing:4px;margin-bottom:20px;">SYSTEM V32 | SHEPHERD EDITION</div>
        """, unsafe_allow_html=True)

        t1,t2 = st.tabs(["ENTRAR","REGISTRAR"])
        with t1:
            u = st.text_input("ID")
            p = st.text_input("Senha", type="password")
            if st.button("ACESSAR", use_container_width=True):
                if AccessControl.login(u,p):
                    st.session_state["logado"] = True
                    st.session_state["user_name"] = u.upper()
                    st.rerun()
                else: st.error("NEGO A VOS CONHECER.")
        with t2:
            st.markdown("Registre uma nova conta")
            nu = st.text_input("Novo ID", key="reg_nu")
            reg_method = st.radio("Método", ["Senha (local)","Google (OAuth)","Apple (OAuth)","Email"], index=0)
            if reg_method == "Senha (local)":
                np = st.text_input("Nova Senha", type="password", key="reg_np")
                if st.button("CRIAR USUÁRIO", use_container_width=True):
                    ok,msg = AccessControl.register(nu,np,method="local")
                    if ok: st.success(msg)
                    else: st.error(msg)
            else:
                if st.button(f"Registrar via {reg_method}"):
                    token = f"{reg_method}_{nu}_{int(time.time())}"
                    ok,msg = AccessControl.register(nu,token,method=reg_method)
                    if ok: st.success(f"Registrado via {reg_method} (simulado).")
                    else: st.error(msg)
    st.stop()

# ---------------------------------------------------------------------
# MAIN APP SHELL
# ---------------------------------------------------------------------
if "hide_menu" not in st.session_state: st.session_state["hide_menu"] = False
c_main, c_tog = st.columns([0.9,0.1])
with c_tog:
    if st.button("☰"): st.session_state["hide_menu"] = not st.session_state["hide_menu"]

if not st.session_state["hide_menu"]:
    menu = st.sidebar.radio("SISTEMA", ["Cuidado Pastoral","Gabinete Pastoral","Biblioteca","Configurações"], index=0)
    st.sidebar.divider()
    if st.sidebar.button("LOGOUT"):
        st.session_state["logado"] = False
        st.rerun()
else:
    menu = "Cuidado Pastoral"

# HUD
status_text, status_color = PastoralMind.check_burnout()
dia_lit = "DOMINGO" if datetime.now().weekday()==6 else "FERIAL"
col_h1, col_h2 = st.columns([3,1])
with col_h1: st.markdown(f"<span style='color:#888;font-size:10px;'>LITURGIA:</span> <span style='font-family:Cinzel'>{dia_lit}</span>", unsafe_allow_html=True)
with col_h2: st.markdown(f"<div style='text-align:right;'><span style='color:#888;font-size:10px;'>VITALIDADE:</span> <span style='color:{status_color}'>{status_text}</span></div>", unsafe_allow_html=True)
st.markdown("---")

# ---------------------------------------------------------------------
# MÓDULO: CUIDADO PASTORAL
# ---------------------------------------------------------------------
if menu == "Cuidado Pastoral":
    st.title("🛡️ Cuidado Pastoral Dinâmico")
    tab_painel, tab_rebanho, tab_teoria, tab_tools = st.tabs(["📊 Painel","🐑 Rebanho","⚖️ Teoria","🛠️ Ferramentas"])

    with tab_painel:
        c1,c2 = st.columns([2,1])
        with c1:
            st.markdown('<div class="tech-card">', unsafe_allow_html=True)
            st.subheader("Estado Geral")
            cats = ['Espiritual','Emocional','Físico','Financeiro','Relacional']
            vals = [random.randint(40,90) for _ in cats]
            plot_radar(cats, vals, "Saúde")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Stats rápidas
            stats = SafeIO.ler_json(DBS["STATS"], {"nivel":1,"xp":0})
            members = SafeIO.ler_json(DBS["MEMBERS_DB"], [])
            st.info(f"Membros: {len(members)} | Nível Pastoral: {stats.get('nivel',1)}")
            
        with c2:
            st.markdown('<div class="tech-card">', unsafe_allow_html=True)
            st.subheader("Rotina")
            tasks = ["Oração","Visitas","Estudo"]
            for t in tasks: st.checkbox(t)
            st.markdown('</div>', unsafe_allow_html=True)

    with tab_rebanho:
        st.markdown("### Gestão de Ovelhas")
        members = SafeIO.ler_json(DBS["MEMBERS_DB"], [])
        with st.expander("➕ Nova Ovelha"):
            with st.form("add_mem"):
                nm = st.text_input("Nome")
                stt = st.selectbox("Status", ["Comungante","Não-Comungante"])
                tel = st.text_input("Telefone")
                if st.form_submit_button("Salvar"):
                    members.append({"Nome":nm,"Status":stt,"Telefone":tel,"Data":datetime.now().strftime("%d/%m")})
                    SafeIO.salvar_json(DBS["MEMBERS_DB"], members)
                    st.success("Adicionado.")
                    st.rerun()
        
        if members:
            for i,m in enumerate(members):
                with st.expander(f"{m.get('Nome')} ({m.get('Status')})"):
                    st.write(f"Tel: {m.get('Telefone')}")
                    if st.button("Remover", key=f"rm_{i}"):
                        members.pop(i)
                        SafeIO.salvar_json(DBS["MEMBERS_DB"], members)
                        st.rerun()
        else:
            st.info("Nenhum membro cadastrado.")

    with tab_teoria:
        st.markdown("### ⚖️ Teoria da Permissão")
        c1,c2 = st.columns(2)
        with c1:
            pf = st.slider("FALHAR",0,100,50)
            ps = st.slider("SENTIR",0,100,50)
            pr = st.slider("DESCANSAR",0,100,50)
            pi = st.slider("SUCESSO",0,100,50)
        with c2:
            avg = (pf+ps+pr+pi)/4
            plot_gauge_chart(avg, "Permissão Interna")

    with tab_tools:
        st.markdown("### Ferramentas")
        st.text_area("Chat Broadcast")
        if st.button("Enviar"): st.success("Enviado.")
        st.divider()
        if st.button("Backup Manual"):
            bk = backup_local()
            if bk: st.success(f"Salvo: {bk}")

# ---------------------------------------------------------------------
# MÓDULO: GABINETE PASTORAL (Correção Bug RemoveChild + Editor Word)
# ---------------------------------------------------------------------
elif menu == "Gabinete Pastoral":
    st.title("📝 Gabinete Pastoral")
    
    if not os.path.exists(os.path.join(DIRS["SERMOES"], "metadata.json")):
        SafeIO.salvar_json(os.path.join(DIRS["SERMOES"], "metadata.json"), {"sermons": []})

    with st.expander("⚙️ Configurações do Editor"):
        fs = st.slider("Fonte", 12, 30, 18)

    c_tit, c_list = st.columns([3, 1])
    files = [f for f in os.listdir(DIRS["SERMOES"]) if f.endswith(".txt")]
    sel_file = c_list.selectbox("Arquivo:", ["- Novo -"] + files)
    
    # Lógica de Carregamento Estável (Correção Key)
    if "last_file" not in st.session_state: st.session_state["last_file"] = None
    
    content_init = ""
    if sel_file != st.session_state["last_file"]:
        if sel_file != "- Novo -":
            try:
                with open(os.path.join(DIRS["SERMOES"], sel_file), 'r', encoding='utf-8') as f:
                    content_init = f.read()
            except: content_init = ""
        st.session_state["last_file"] = sel_file
        # Reseta o conteúdo do editor para o novo arquivo usando session_state dinâmico
        st.session_state[f"quill_{sel_file}"] = content_init
    
    # Nome do documento
    doc_title = c_tit.text_input("Título", value=sel_file.replace(".txt","") if sel_file != "- Novo -" else "")

    # Editor com Toolbar Completa (Word Style)
    if QUILL_AVAILABLE:
        toolbar = [
            ['bold', 'italic', 'underline', 'strike'],
            [{'header': 1}, {'header': 2}],
            [{'list': 'ordered'}, {'list': 'bullet'}],
            [{'align': []}], [{'color': []}, {'background': []}],
            ['clean']
        ]
        # KEY DINÂMICA: Previne o erro 'Node not found' / 'removeChild'
        unique_key = f"quill_{sel_file}"
        
        content = st_quill(
            value=content_init,
            key=unique_key,
            toolbar=toolbar,
            height=500,
            html=True
        )
    else:
        content = st.text_area("Editor Texto", content_init, height=500)

    st.markdown("---")
    c1, c2 = st.columns([1, 2])
    with c1:
        if st.button("💾 SALVAR", type="primary", use_container_width=True):
            if doc_title:
                fn = f"{doc_title}.txt"
                with open(os.path.join(DIRS["SERMOES"], fn), 'w', encoding='utf-8') as f:
                    f.write(content)
                st.toast("Salvo!", icon="✅")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Título vazio.")

    with c2:
        cc1, cc2, cc3 = st.columns(3)
        if cc1.button("🔒 Encriptar"):
            pw = st.session_state["config"].get("enc_password")
            if pw:
                enc = encrypt_aes(pw, content)
                if enc:
                    with ope
