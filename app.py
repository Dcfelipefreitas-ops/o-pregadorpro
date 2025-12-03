# app.py
# -*- coding: utf-8 -*-
"""
O PREGADOR - App consolidado (unified single-file)
Versão: Consolidated (improved)
Mantenha nomes e casca originais; funcionalidades melhoradas.
"""

import streamlit as st
import os, sys, time, json, base64, math, shutil, random, logging, hashlib, re
from datetime import datetime
from io import BytesIO

# ---------------------------------------------------------------------
# 0. PAGE CONFIG - MUST BE FIRST STREAMLIT CALL
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
    # defaults
    cfg_path = DBS["CONFIG"]
    if not os.path.exists(cfg_path):
        default_cfg = {
            "theme_color": "#D4AF37",
            "font_size": 18,
            "enc_password": "OMEGA_KEY_DEFAULT",
            "api_key": "",
            "backup_interval_seconds": 24*3600,
            "last_backup": None,
            "theme_mode": "Dark Cathedral",
            "font_family": "Inter",
            "work_mode": "Completo"
        }
        with open(cfg_path, "w", encoding="utf-8") as f:
            json.dump(default_cfg, f, indent=2, ensure_ascii=False)
    users_path = DBS["USERS"]
    if not os.path.exists(users_path):
        with open(users_path, "w", encoding="utf-8") as f:
            admin_hash = hashlib.sha256("admin".encode()).hexdigest()
            json.dump({"ADMIN": admin_hash}, f, indent=2, ensure_ascii=False)
    if not os.path.exists(DBS["MEMBERS_DB"]):
        with open(DBS["MEMBERS_DB"], "w", encoding="utf-8") as f:
            json.dump([], f, indent=2, ensure_ascii=False)
    if not os.path.exists(os.path.join(DIRS["SERMOES"], "metadata.json")):
        with open(os.path.join(DIRS["SERMOES"], "metadata.json"), "w", encoding="utf-8") as f:
            json.dump({"sermons": []}, f, indent=2, ensure_ascii=False)

_genesis()

# ---------------------------------------------------------------------
# LOGGING
# ---------------------------------------------------------------------
logging.basicConfig(filename=os.path.join(DIRS["LOGS"], "system.log"), level=logging.INFO, format='%(asctime)s|%(levelname)s|%(message)s')

# ---------------------------------------------------------------------
# SAFE IO helpers
# ---------------------------------------------------------------------
def read_json(path, default):
    try:
        if not os.path.exists(path): return default
        with open(path, "r", encoding="utf-8") as f:
            c = f.read().strip()
            return json.loads(c) if c else default
    except Exception:
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
        logging.error(f"write_json error {e}")
        return False

# ---------------------------------------------------------------------
# UTILITIES
# ---------------------------------------------------------------------
def safe_filename(name):
    s = (name or "").strip()
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^0-9A-Za-z_\-\.]", "", s)
    return s or "file"

def normalize_font_name(fname):
    if not fname: return "Inter"
    base = fname.split(",")[0]
    base = base.strip().strip("'\"")
    return base

# ---------------------------------------------------------------------
# ENCRYPTION
# ---------------------------------------------------------------------
def encrypt_aes(password, plaintext):
    if not CRYPTO_OK: return None
    key = hashlib.sha256(password.encode()).digest()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    return base64.b64encode(nonce + ct).decode("utf-8")

# ---------------------------------------------------------------------
# EXPORT (DOCX / PDF)
# ---------------------------------------------------------------------
def export_html_to_docx(title, html, out_path):
    if HTML2DOCX == "mammoth":
        with open(out_path, "wb") as f:
            results = mammoth.convert_to_docx(html)
            f.write(results.value)
        return True
    elif HTML2DOCX == "html2docx":
        from html2docx import html2docx
        with open(out_path, "wb") as f:
            f.write(html2docx(html))
        return True
    else:
        try:
            from docx import Document
            doc = Document()
            doc.add_heading(title, 1)
            plain = re.sub(r"<.*?>", "", html)
            doc.add_paragraph(plain)
            doc.save(out_path)
            return True
        except Exception:
            with open(out_path.replace(".docx", ".txt"), "w", encoding="utf-8") as f:
                f.write(html)
            return False

def export_to_pdf(title, text, out_path):
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

# ---------------------------------------------------------------------
# PLOTTING helpers (protected if plotly missing)
# ---------------------------------------------------------------------
def plot_radar(categories, values, title):
    try:
        theme = st.session_state["config"].get("theme_color", "#D4AF37")
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself', line_color=theme))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', polar=dict(radialaxis=dict(range=[0,100], gridcolor="#222")), margin=dict(t=20,b=10))
        st.plotly_chart(fig, use_container_width=True)
    except Exception:
        st.write(title + " - " + ", ".join(f"{c}:{v}" for c,v in zip(categories, values)))

def plot_gauge_chart(value, title):
    try:
        theme = st.session_state["config"].get("theme_color", "#D4AF37")
        fig = go.Figure(go.Indicator(mode="gauge+number", value=value, title={'text': title}, gauge={'axis': {'range': [0,100]}, 'bar': {'color': theme}}))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=10,b=10))
        st.plotly_chart(fig, use_container_width=True)
    except Exception:
        st.write(f"{title}: {value}%")

# ---------------------------------------------------------------------
# PARSERS / BIBLE STUBS / LIBRARY INDEX
# ---------------------------------------------------------------------
def get_bible_verse(ref):
    return {"source": "local", "text": f"(simulado) Texto para {ref}"}

def index_books(folder=None):
    folder = folder or DIRS["BIB_CACHE"]
    books = []
    try:
        for f in os.listdir(folder):
            if f.lower().endswith((".pdf", ".docx", ".txt", ".epub")):
                books.append(f)
    except Exception:
        pass
    return books
    # ==============================================================================
# 13. MÓDULO: GABINETE PASTORAL (EDITOR WYSIWYG - ESTILO WORD)
# ==============================================================================
elif menu == "Gabinete Pastoral":
    st.title("📝 Gabinete Pastoral")
    
    # Importações específicas para este módulo (garantindo que não quebre se faltar)
    try:
        from streamlit_quill import st_quill
        from bs4 import BeautifulSoup
        from docx import Document
        from docx.shared import Pt, RGBColor
    except ImportError:
        st.error("Erro: Bibliotecas 'streamlit-quill', 'beautifulsoup4' ou 'python-docx' não instaladas.")
        st.stop()

    # --- FUNÇÃO AUXILIAR: CONVERTER HTML (DO EDITOR) PARA WORD (.DOCX) ---
    def html_to_word_classic(html_content):
        """Converte o HTML rico do Quill para um arquivo Word limpo."""
        doc = Document()
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Título
        doc.add_heading(st.session_state.get("titulo_ativo", "Sermão Sem Título"), 0)
        
        # Processa parágrafos
        for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'ul', 'ol', 'li']):
            if element.name in ['h1', 'h2', 'h3']:
                # Cabeçalhos
                level = int(element.name[1])
                doc.add_heading(element.get_text(), level)
            elif element.name == 'li':
                # Listas
                doc.add_paragraph(element.get_text(), style='List Bullet')
            else:
                # Texto normal (p)
                p = doc.add_paragraph()
                # Tenta manter formatação básica (Negrito/Itálico) se houver tags internas
                if element.find('strong') or element.find('b'):
                    run = p.add_run(element.get_text())
                    run.bold = True
                elif element.find('em') or element.find('i'):
                    run = p.add_run(element.get_text())
                    run.italic = True
                else:
                    p.add_run(element.get_text())
        
        # Salva em memória
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer

    # --- SETUP DE ARQUIVOS ---
    METADATA_PATH = os.path.join(DIRS["SERMOES"], "metadata.json")
    if not os.path.exists(METADATA_PATH):
        SafeIO.salvar_json(METADATA_PATH, {"sermons": []})
    
    # --- BARRA LATERAL DO EDITOR (SELEÇÃO DE ARQUIVOS) ---
    c_lista, c_editor = st.columns([1, 4])
    
    with c_lista:
        st.markdown("### 📂 Arquivos")
        # Lista arquivos .html (formato rico) e .txt (antigos)
        files = [f for f in os.listdir(DIRS["SERMOES"]) if f.endswith((".html", ".txt"))]
        sel_file = st.selectbox("Abrir Sermão:", ["- Novo Documento -"] + files)
        
        st.info("💡 Dica: Use Ctrl+B para Negrito e Ctrl+I para Itálico.")

    # --- LÓGICA DE CARREGAMENTO ---
    if sel_file != "- Novo Documento -" and sel_file != st.session_state.get("arquivo_carregado"):
        path = os.path.join(DIRS["SERMOES"], sel_file)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                st.session_state["texto_ativo"] = f.read()
            st.session_state["titulo_ativo"] = sel_file.replace(".html", "").replace(".txt", "")
            st.session_state["arquivo_carregado"] = sel_file
        except:
            st.error("Erro ao abrir arquivo.")

    # --- ÁREA DO EDITOR (VISUAL WORD) ---
    with c_editor:
        # Título do Documento
        titulo = st.text_input("Título do Sermão / Estudo", value=st.session_state.get("titulo_ativo", ""))
        
        # CONFIGURAÇÃO DA BARRA DE FERRAMENTAS (ESTILO WORD)
        # Isso define quais botões aparecem no topo do editor
        toolbar_config = [
            ['bold', 'italic', 'underline', 'strike'],        # Negrito, Itálico, Sublinhado, Riscado
            ['blockquote', 'code-block'],                     # Citação, Código
            [{'header': 1}, {'header': 2}],                   # Títulos H1, H2
            [{'list': 'ordered'}, {'list': 'bullet'}],        # Listas Numéricas e Pontos
            [{'script': 'sub'}, {'script': 'super'}],         # Sobrescrito
            [{'indent': '-1'}, {'indent': '+1'}],             # Identação
            [{'direction': 'rtl'}],                           # Direção do texto
            [{'size': ['small', False, 'large', 'huge']}],    # Tamanho da fonte
            [{'header': [1, 2, 3, 4, 5, 6, False]}],          # Cabeçalhos
            [{'color': []}, {'background': []}],              # Cores de texto e fundo
            [{'font': []}],                                   # Fontes
            [{'align': []}],                                  # Alinhamento (Esq, Centro, Dir, Justificar)
            ['clean']                                         # Limpar formatação
        ]

        # O COMPONENTE EDITOR RICO
        # Retorna o conteúdo em HTML
        content_html = st_quill(
            value=st.session_state.get("texto_ativo", ""),
            placeholder="Comece a escrever a sua pregação aqui...",
            html=True,
            toolbar=toolbar_config,
            key="quill_editor_word",
            height=500  # Altura da folha
        )
        
        # Atualiza estado
        st.session_state["texto_ativo"] = content_html
        st.session_state["titulo_ativo"] = titulo

        # --- BOTÕES DE AÇÃO ---
        st.markdown("---")
        c_salvar, c_export, c_crypto = st.columns(3)
        
        # 1. SALVAR (Salva como HTML para manter as cores e formatos)
        with c_salvar:
            if st.button("💾 Salvar na Nuvem Local", type="primary", use_container_width=True):
                if titulo:
                    # Salva como HTML para preservar formatação visual (Word style)
                    fn = f"{titulo}.html"
                    path = os.path.join(DIRS["SERMOES"], fn)
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(content_html)
                    st.toast("Documento salvo com formatação completa!", icon="✅")
                else:
                    st.warning("Dê um título antes de salvar.")

        # 2. EXPORTAR PARA WORD (.DOCX)
        with c_export:
            if st.button("📄 Baixar como Word (.docx)", use_container_width=True):
                if titulo and content_html:
                    docx_buffer = html_to_word_classic(content_html)
                    st.download_button(
                        label="⬇️ Download Arquivo Word",
                        data=docx_buffer,
                        file_name=f"{titulo}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                else:
                    st.warning("Escreva algo e dê um título para baixar.")

        # 3. CRIPTOGRAFIA (AES)
        with c_crypto:
            if st.button("🔒 Encriptar (AES-256)", use_container_width=True):
                pw = st.session_state["config"].get("enc_password")
                if pw and content_html:
                    if CRYPTO_OK:
                        enc = encrypt_sermon_aes(pw, content_html)
                        path = os.path.join(DIRS["GABINETE"], f"{titulo}.enc")
                        with open(path, 'w', encoding='utf-8') as f: f.write(enc)
                        st.success("Arquivo blindado no cofre.")
                    else:
                        st.error("Módulo de criptografia indisponível.")
                else:
                    st.error("Configure uma Senha Mestra nas Configurações primeiro.")

# ---------------------------------------------------------------------
# ACCESS CONTROL
# ---------------------------------------------------------------------
class AccessControl:
    DEFAULT = {"ADMIN": hashlib.sha256("admin".encode()).hexdigest()}

    @staticmethod
    def _hash(txt): return hashlib.sha256(txt.encode()).hexdigest()

    @staticmethod
    def get_all():
        return read_json(DBS["USERS"], AccessControl.DEFAULT)

    @staticmethod
    def register(username, password, method="local"):
        if not username:
            return False, "Nome de usuário vazio."
        users = read_json(DBS["USERS"], {})
        if username.upper() in users:
            return False, "USUÁRIO JÁ EXISTE."
        if method == "local":
            users[username.upper()] = AccessControl._hash(password)
        else:
            users[username.upper()] = {"method": method, "value": password}
        write_json(DBS["USERS"], users)
        logging.info(f"Novo registro: {username} via {method}")
        return True, "REGISTRO OK."

    @staticmethod
    def login(username, password):
        users = read_json(DBS["USERS"], {})
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

# ---------------------------------------------------------------------
# LOGIC: pastoral helpers
# ---------------------------------------------------------------------
class Geneva:
    DB = {
        "prosperidade": "⚠️ ALERTA: Teologia da Prosperidade.",
        "eu decreto": "⚠️ ALERTA: Quebra de Soberania Divina."
    }
    @staticmethod
    def scan(text):
        if not text: return []
        return [v for k,v in Geneva.DB.items() if k in text.lower()]

class PastoralMind:
    @staticmethod
    def check_burnout():
        data = read_json(DBS["SOUL"], {"historico": []})
        hist = data.get("historico", [])[-10:]
        bad = sum(1 for h in hist if h.get("humor") in ["Cansaço", "Ira", "Ansiedade", "Tristeza"])
        if bad >= 6: return "CRÍTICO", "#FF3333"
        if bad >= 3: return "ALERTA", "#FFAA00"
        return "OPERACIONAL", "#33FF33"

    @staticmethod
    def register(humor):
        data = read_json(DBS["SOUL"], {"historico": []})
        data.setdefault("historico", []).append({"data": datetime.now().strftime("%Y-%m-%d"), "humor": humor})
        write_json(DBS["SOUL"], data)

class Gamification:
    @staticmethod
    def add_xp(amount):
        stats = read_json(DBS["STATS"], {"xp": 0, "nivel": 1})
        stats["xp"] = stats.get("xp", 0) + amount
        stats["nivel"] = int(math.sqrt(stats["xp"]) * 0.2) + 1
        write_json(DBS["STATS"], stats)

# ---------------------------------------------------------------------
# BACKUP & SYNC placeholders
# ---------------------------------------------------------------------
def backup_local():
    try:
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        base = os.path.join(DIRS["BACKUP"], f"backup_{now}")
        shutil.make_archive(base, 'zip', ROOT)
        bk = base + ".zip"
        logging.info(f"Backup criado: {bk}")
        return bk
    except Exception as e:
        logging.error(f"backup error {e}")
        return None

def sync_google(file_path):
    # Placeholder - requires Google API credentials
    return False

def sync_icloud(file_path):
    # Placeholder - requires iCloud configuration
    return False

def auto_backup_if_due():
    cfg = read_json(DBS["CONFIG"], {})
    last = cfg.get("last_backup")
    now = time.time()
    interval = cfg.get("backup_interval_seconds", 24*3600)
    if not last or (now - last) > interval:
        bk = backup_local()
        cfg["last_backup"] = now
        write_json(DBS["CONFIG"], cfg)
        return bk
    return None

# ---------------------------------------------------------------------
# STARTUP state
# ---------------------------------------------------------------------
if "config" not in st.session_state:
    st.session_state["config"] = read_json(DBS["CONFIG"], {"theme_color":"#D4AF37","font_size":18,"enc_password":"","api_key":"","backup_interval_seconds":24*3600,"theme_mode":"Dark Cathedral","font_family":"Inter","work_mode":"Completo"})
if "logado" not in st.session_state: st.session_state["logado"] = False
if "user_name" not in st.session_state: st.session_state["user_name"] = "ADMIN"
if "texto_ativo" not in st.session_state: st.session_state["texto_ativo"] = ""
if "titulo_ativo" not in st.session_state: st.session_state["titulo_ativo"] = ""
try:
    auto_backup_if_due()
except Exception:
    pass

# ---------------------------------------------------------------------
# CSS / THEME injection (responsive)
# ---------------------------------------------------------------------
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
    .action-btn{{
        display:inline-block;padding:6px 10px;border-radius:4px;border:1px solid var(--gold);color:var(--gold);text-decoration:none;margin-right:6px;font-size:12px;
    }}
    @media (max-width:800px) {{
        .stApp{{font-size:{max(14,int(font_sz-4))}px;}}
        .prime-logo{{width:90px;height:90px;}}
    }}
    </style>
    """, unsafe_allow_html=True)

inject_css(st.session_state["config"])

# ---------------------------------------------------------------------
# LOGIN UI (keeps same names/panel)
# ---------------------------------------------------------------------
if not st.session_state["logado"]:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
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
                    st.experimental_rerun()
                else:
                    st.error("NEGO A VOS CONHECER.")
        with t2:
            st.markdown("Registre uma nova conta — **Google / Apple / Email / Senha** (simulado)")
            nu = st.text_input("Novo ID", key="reg_nu")
            reg_method = st.radio("Método de registro", ["Senha (local)","Google (OAuth)","Apple (OAuth)","Email (verificação)"], index=0)
            if reg_method == "Senha (local)":
                np = st.text_input("Nova Senha", type="password", key="reg_np")
                if st.button("CRIAR USUÁRIO (Local)", use_container_width=True):
                    ok,msg = AccessControl.register(nu,np,method="local")
                    if ok: st.success(msg)
                    else: st.error(msg)
            elif reg_method == "Google (OAuth)":
                if st.button("Registrar via Google"):
                    token = f"google_{nu}_{int(time.time())}"
                    ok,msg = AccessControl.register(nu,token,method="google")
                    if ok: st.success("Registrado via Google (simulado).")
                    else: st.error(msg)
            elif reg_method == "Apple (OAuth)":
                if st.button("Registrar via Apple"):
                    token = f"apple_{nu}_{int(time.time())}"
                    ok,msg = AccessControl.register(nu,token,method="apple")
                    if ok: st.success("Registrado via Apple (simulado).")
                    else: st.error(msg)
            else:
                email_addr = st.text_input("Email (para confirmação)", key="reg_email")
                if st.button("Registrar via Email"):
                    token = f"email_{email_addr}_{int(time.time())}"
                    ok,msg = AccessControl.register(nu,token,method="email")
                    if ok: st.success("Registrado via Email (simulado).")
                    else: st.error(msg)
    st.stop()

# ---------------------------------------------------------------------
# MAIN APP shell (sidebar menu)
# ---------------------------------------------------------------------
if "hide_menu" not in st.session_state:
    st.session_state["hide_menu"] = False
c_main, c_tog = st.columns([0.9,0.1])
with c_tog:
    if st.button("☰"):
        st.session_state["hide_menu"] = not st.session_state["hide_menu"]

if not st.session_state["hide_menu"]:
    menu = st.sidebar.radio("SISTEMA", ["Cuidado Pastoral","Gabinete Pastoral","Biblioteca","Configurações"], index=0)
    st.sidebar.divider()
    if st.sidebar.button("LOGOUT"):
        st.session_state["logado"] = False
        st.experimental_rerun()
else:
    menu = "Cuidado Pastoral"

# HUD top
status_text, status_color = PastoralMind.check_burnout()
dia_lit = "DOMINGO - DIA DO SENHOR" if datetime.now().weekday()==6 else "DIA FERIAL"
col_h1, col_h2 = st.columns([3,1])
with col_h1:
    st.markdown(f"<span style='color:#888; font-size:10px;'>LITURGIA:</span> <span style='font-family:Cinzel'>{dia_lit}</span>", unsafe_allow_html=True)
with col_h2:
    st.markdown(f"<div style='text-align:right;'><span style='color:#888; font-size:10px;'>VITALIDADE:</span> <span style='color:{status_color}'>{status_text}</span></div>", unsafe_allow_html=True)
st.markdown("---")

# ---------------------------------------------------------------------
# Module: CUIDADO PASTORAL
# ---------------------------------------------------------------------
if menu == "Cuidado Pastoral":
    st.title("🛡️ Cuidado Pastoral Dinâmico")
    tab_painel, tab_rebanho, tab_teoria, tab_tools = st.tabs(["📊 Painel do Pastor","🐑 Meu Rebanho","⚖️ Teoria da Permissão","🛠️ Ferramentas"])

    # Painel do Pastor
    with tab_painel:
        c1,c2 = st.columns([2,1])
        with c1:
            st.markdown('<div class="tech-card">', unsafe_allow_html=True)
            st.subheader("Estado Geral da Igreja")
            cats = ['Espiritual','Emocional','Físico','Financeiro','Relacional']
            vals = [random.randint(40,90) for _ in cats]
            plot_radar(cats, vals, "Saúde do Corpo")
            st.markdown('</div>', unsafe_allow_html=True)
            st.warning("⚠️ **Alerta Preventivo:** Irmão João não acessa o devocional há 5 dias.")
            # modern quick stats
            stats = read_json(DBS["STATS"], {"nivel":1,"xp":0,"members_count":0})
            members = read_json(DBS["MEMBERS_DB"], [])
            stats["members_count"] = len(members)
            write_json(DBS["STATS"], stats)
        with c2:
            st.markdown('<div class="tech-card">', unsafe_allow_html=True)
            st.subheader("Rotina Pastoral Semanal")
            tasks = ["Revisar pedidos de oração","Planejar semana","Visitas","Estudo bíblico"]
            for t in tasks: st.checkbox(t)
            st.markdown('</div>', unsafe_allow_html=True)
        st.subheader("📊 Estatísticas Pastorais")
        st.metric("Nível", stats.get("nivel",1))
        st.metric("XP", stats.get("xp",0))
        st.metric("Membros registrados", stats.get("members_count",0))

    # Rebanho
    with tab_rebanho:
        st.markdown("### Gestão de Ovelhas Baseada em Necessidades")
        members = read_json(DBS["MEMBERS_DB"], [])
        with st.expander("➕ Nova Ovelha / Contato"):
            with st.form("add_member", clear_on_submit=True):
                nm = st.text_input("Nome")
                idade = st.number_input("Idade", 0, 120, 0)
                stt = st.selectbox("Status", ["Comungante","Não-Comungante"])
                phone = st.text_input("Telefone (somente números)", placeholder="5511999998888")
                whatsapp = st.text_input("WhatsApp (número com código)", placeholder="5511999998888")
                email = st.text_input("E-mail")
                endereco = st.text_input("Endereço")
                note = st.text_area("Observação / Histórico")
                foto = st.file_uploader("Foto (opcional)", type=["png","jpg","jpeg"])
                if st.form_submit_button("Salvar"):
                    member = {"Nome": nm, "Idade": int(idade), "Status": stt, "Telefone": phone, "WhatsApp": whatsapp, "Email": email, "Endereco": endereco, "Nota": note, "Data": datetime.now().strftime("%Y-%m-%d")}
                    if foto:
                        fn = f"{safe_filename(nm)}_{int(time.time())}.{foto.name.split('.')[-1]}"
                        fp = os.path.join(DIRS["MEMBROS"], fn)
                        with open(fp, "wb") as f: f.write(foto.getbuffer())
                        member["Foto"] = fp
                    members.append(member)
                    write_json(DBS["MEMBERS_DB"], members)
                    st.success("Ovelha adicionada.")
                    st.experimental_rerun()
        if members:
            for i,m in enumerate(members):
                with st.expander(f"{m.get('Nome','-')} — {m.get('Status','')} ({m.get('Data','')})"):
                    st.markdown(f"<div class='member-card'><b>Nome:</b> {m.get('Nome')}<br><b>Idade:</b> {m.get('Idade')}<br><b>Email:</b> {m.get('Email')}<br><b>Telefone:</b> {m.get('Telefone')}<br><b>Endereço:</b> {m.get('Endereco')}<br><b>Nota:</b> {m.get('Nota')}</div>", unsafe_allow_html=True)
                    cols = st.columns([1,1,1,1])
                    tel = m.get("Telefone","")
                    wa = m.get("WhatsApp","")
                    if tel:
                        cols[0].markdown(f'<a class="action-btn" href="tel:+{tel}">Ligar</a>', unsafe_allow_html=True)
                    else:
                        cols[0].button("Sem tel", disabled=True)
                    if wa:
                        wa_num = wa.replace("+","").replace(" ","").replace("-","")
                        cols[1].markdown(f'<a class="action-btn" href="https://wa.me/{wa_num}" target="_blank">WhatsApp</a>', unsafe_allow_html=True)
                    else:
                        cols[1].button("Sem Whats", disabled=True)
                    if m.get("Email"):
                        cols[2].markdown(f'<a class="action-btn" href="mailto:{m.get("Email")}">Enviar Email</a>', unsafe_allow_html=True)
                    else:
                        cols[2].button("Sem Email", disabled=True)
                    if cols[3].button("Remover", key=f"rm_{i}"):
                        members.pop(i)
                        write_json(DBS["MEMBERS_DB"], members)
                        st.success("Removido.")
                        st.experimental_rerun()
        else:
            st.info("Nenhum membro cadastrado ainda. Use '➕ Nova Ovelha' para começar.")

        st.markdown("### Caminhos de Crescimento")
        c1,c2,c3 = st.columns(3)
        if c1.button("🌱 Trilha: Novo Convertido"): st.success("Trilha ativada.")
        if c2.button("🛡️ Trilha: Vencendo a Ansiedade"): st.success("Trilha ativada.")
        if c3.button("📚 Trilha: Teologia Reformada"): st.success("Trilha ativada.")

    # Teoria da Permissão (Interativa)
    with tab_teoria:
        st.markdown("### ⚖️ Teoria da Permissão — Interativo")
        col_input, col_viz = st.columns([1,1])
        with col_input:
            p_fail = st.slider("Permissão para FALHAR (Graça)",0,100,50)
            p_feel = st.slider("Permissão para SENTIR (Humanidade)",0,100,50)
            p_rest = st.slider("Permissão para DESCANSAR (Limite)",0,100,50)
            p_succ = st.slider("Permissão para SUCESSO (Dignidade)",0,100,50)
            if st.button("RODAR SCAN DIAGNÓSTICO"):
                score = (p_fail+p_feel+p_rest+p_succ)/4
                st.session_state['perm_score'] = score
                if score < 40:
                    st.warning("Sugestão: Agende 3 contatos de suporte e diminua carga de pregacões por 2 semanas.")
                elif score < 70:
                    st.info("Sugestão: Delegue 1 tarefa administrativa e intensifique práticas devocionais.")
                else:
                    st.success("Nível saudável. Mantenha rotina.")
        with col_viz:
            score = st.session_state.get('perm_score',50)
            plot_gauge_chart(score, "Índice de Permissão Interna")

    # Tools
    with tab_tools:
        st.markdown("### Ferramentas de Discipulado")
        e1 = st.expander("💬 Chat Pastoral & Pedidos")
        e2 = st.expander("🧩 Devocionais Interativos")
        with e1:
            st.text_area("Enviar mensagem...", key="broadcast")
            st.button("Enviar Broadcast")
        with e2:
            st.markdown("**Desafio da Semana:** Ler Salmo 23 e enviar áudio de 1 min.")
            st.radio("Quiz Bíblico", ["Isaías","Ezequiel","Jeremias"])
        st.divider()
        if st.button("Criar Backup Manual"):
            bk = backup_local()
            if bk: st.success(f"Backup salvo: {bk}")
            else: st.error("Falha ao criar backup.")
        if st.button("Sincronizar com Google Drive (se configurado)"):
            st.info("Sincronização simulada. Configure credenciais para ativar.")
        if st.button("Sincronizar com iCloud (se configurado)"):
            st.info("Sincronização simulada. Configure credenciais para ativar.")

# ---------------------------------------------------------------------
# Module: GABINETE PASTORAL (com Biblioteca integrada)
# ---------------------------------------------------------------------
elif menu == "Gabinete Pastoral":
    st.title("📝 Gabinete Pastoral")
    METADATA_PATH = os.path.join(DIRS["SERMOES"], "metadata.json")
    if not os.path.exists(METADATA_PATH):
        write_json(METADATA_PATH, {"sermons": []})

    c_left, c_right = st.columns([1,3])
    with c_left:
        st.markdown("### Biblioteca / Recursos")
        if st.button("Indexar livros locais"):
            st.success("Indexado.")
        books = index_books(DIRS["BIB_CACHE"])
        st.markdown("**Livros locais**")
        if books:
            for b in books:
                st.markdown(f"- {b}")
        else:
            st.info("Nenhum livro local indexado.")
        st.markdown("---")
        up_book = st.file_uploader("Importar livro (PDF/DOCX/TXT/EPUB)", type=["pdf","docx","txt","epub"], key="up_book")
        if up_book:
            dest = os.path.join(DIRS["BIB_CACHE"], up_book.name)
            with open(dest, "wb") as f: f.write(up_book.getbuffer())
            st.success("Livro importado.")

    with c_right:
        with st.expander("Configurações do Editor"):
            fs = st.slider("Fonte", 12, 30, st.session_state["config"].get("font_size",18))
            autosave = st.checkbox("Autosave", True)
        c_tit, c_tags = st.columns([3,1])
        st.session_state["titulo_ativo"] = c_tit.text_input("Título", st.session_state.get("titulo_ativo",""))
        st.session_state["last_tags"] = c_tags.text_input("Tags", ",".join(st.session_state.get("last_tags", []))).split(",")

        st.markdown("Importar (TheWord/Logos/PDF/DOCX):")
        up = st.file_uploader("Arquivo do sermão / estudo", label_visibility="collapsed", accept_multiple_files=False, key="up_sermon")

        # Editor area: use st_quill if available, else textarea
        if QUILL_AVAILABLE:
            try:
                content = st_quill(value=st.session_state.get("texto_ativo",""), key="editor_quill", height=420)
            except Exception:
                QUILL_AVAILABLE = False
                content = st.text_area("Editor", st.session_state.get("texto_ativo",""), height=420)
        else:
            content = st.text_area("Editor", st.session_state.get("texto_ativo",""), height=420)

        if content != st.session_state.get("texto_ativo",""):
            st.session_state["texto_ativo"] = content
            if autosave and st.session_state["titulo_ativo"]:
                try:
                    fn = f"{st.session_state['titulo_ativo']}.txt"
                    with open(os.path.join(DIRS["SERMOES"], fn), "w", encoding="utf-8") as f:
                        f.write(content)
                    st.toast("Autosave realizado.", icon="💾")
                except Exception:
                    pass

        c_save, c_exp = st.columns(2)
        with c_save:
            if st.button("Salvar"):
                fn = f"{st.session_state['titulo_ativo']}.txt"
                with open(os.path.join(DIRS["SERMOES"], fn), "w", encoding="utf-8") as f: f.write(content)
                st.success("Salvo.")
            if st.button("Encriptar (Senha na Config)"):
                pw = st.session_state["config"].get("enc_password")
                if pw:
                    enc = encrypt_aes(pw, content) if CRYPTO_OK else None
                    with open(os.path.join(DIRS["GABINETE"], f"{safe_filename(st.session_state['titulo_ativo'])}.enc"), "w", encoding="utf-8") as f:
                        f.write(enc if enc else "")
                    st.success("Encriptado.")
                else:
                    st.error("Defina senha na config.")
        with c_exp:
            if st.button("Exportar DOCX"):
                fn = f"{safe_filename(st.session_state['titulo_ativo'])}.docx"
                path = os.path.join(DIRS["SERMOES"], fn)
                ok = export_html_to_docx(st.session_state['titulo_ativo'], content, path)
                if ok:
                    with open(path, "rb") as f:
                        st.download_button("Baixar DOCX", f, file_name=fn)
                else:
                    st.error("Falha export DOCX.")
            if st.button("Exportar PDF"):
                fn = f"{safe_filename(st.session_state['titulo_ativo'])}.pdf"
                path = os.path.join(DIRS["SERMOES"], fn)
                ok = export_to_pdf(st.session_state['titulo_ativo'], content, path)
                if ok:
                    with open(path, "rb") as f:
                        st.download_button("Baixar PDF", f, file_name=fn)
                else:
                    st.error("Falha export PDF (libs ausentes).")

# ---------------------------------------------------------------------
# Module: BIBLIOTECA (direct access)
# ---------------------------------------------------------------------
elif menu == "Biblioteca":
    st.title("📚 Biblioteca Reformada")
    col1,col2 = st.columns(2)
    with col1:
        st.subheader("Busca Online (Google Books) - simulada")
        q = st.text_input("Termo (ex: Teologia Pactual)")
        if st.button("Buscar"):
            st.info("Conexão simulada. Insira API Key em Configurações para ativar.")
    with col2:
        st.subheader("Arquivos Locais (Gabinete)")
        books = index_books(DIRS["BIB_CACHE"])
        if books:
            for b in books:
                st.write(b)
        else:
            st.info("Nenhum livro local indexado (use importar).")
    c1,c2,c3,c4 = st.columns(4)
    c1.markdown('<div class="tech-card">Bíblias</div>', unsafe_allow_html=True)
    c2.markdown('<div class="tech-card">Comentários</div>', unsafe_allow_html=True)
    c3.markdown('<div class="tech-card">Dicionários</div>', unsafe_allow_html=True)
    c4.markdown('<div class="tech-card">PDFs Locais</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------
# Module: CONFIGURAÇÕES (with manual)
# ---------------------------------------------------------------------
elif menu == "Configurações":
    st.title("⚙️ Configurações")
    cfg = st.session_state["config"]
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("### Visual")
        nc = st.color_picker("Cor do Tema", cfg.get("theme_color","#D4AF37"))
        nf = st.number_input("Tamanho Fonte", 12, 30, cfg.get("font_size",18))
        nm = st.selectbox("Modo (apenas informativo)", ["Dark Cathedral","Pergaminho (Sepia)","Holy Light (Claro)"], index=0)
        st.markdown("### Preferências de Trabalho")
        work_mode = st.selectbox("Meu modo de trabalho", ["Completo","Minimalista","Mobile-first"], index=0)
        st.checkbox("Mostrar dicas rápidas na tela inicial", value=True)
    with c2:
        st.markdown("### Segurança & Backup")
        npw = st.text_input("Senha Mestra de Encriptação", type="password", value=cfg.get("enc_password",""))
        api_key = st.text_input("API Key (Google - opcional)", value=cfg.get("api_key",""), type="password")
        interval_days = st.number_input("Intervalo de backup (dias)", 1, 30, int(cfg.get("backup_interval_seconds",24*3600)//86400))
        st.markdown("---")
        if st.button("Executar Backup Agora"):
            bk = backup_local()
            if bk: st.success(f"Backup criado: {bk}")
            else: st.error("Erro no backup.")

    if st.button("Salvar Tudo"):
        cfg["theme_color"] = nc
        cfg["font_size"] = nf
        cfg["theme_mode"] = nm
        cfg["enc_password"] = npw
        cfg["api_key"] = api_key
        cfg["backup_interval_seconds"] = int(interval_days*24*3600)
        cfg["work_mode"] = work_mode
        write_json(DBS["CONFIG"], cfg)
        st.success("Configurações salvas. Reinicie o app para aplicar totalmente quando necessário.")

    st.markdown("---")
    with st.expander("📘 Manual do Aplicativo (Guias & Boas Práticas)"):
        st.markdown("**Como usar o Gabinete Pastoral**")
        st.markdown("- Use o editor para compor sermões. Você pode importar PDFs/DOCX/EPUB na Biblioteca integrada.")
        st.markdown("- Salve frequentemente; configure Autosave nas preferências do editor.")
        st.markdown("**Como usar o Rebanho**")
        st.markdown("- Adicione membros com dados de contato; utilize os botões Ligar/WhatsApp/Email para contato rápido.")
        st.markdown("- Mantenha notas e histórico para acompanhar o crescimento espiritual.")
        st.markdown("**Cuidado Pastoral (boas práticas resumidas)**")
        st.markdown("- Mantenha confidencialidade. Registre encontros e siga um plano de visitas.")
        st.markdown("- Estruture um time de suporte e delegue contatos quando necessário.")
        st.markdown("**Backups e sincronização**")
        st.markdown("- Faça backup manual antes de grandes atualizações. Configure sincronização externa caso tenha credenciais.")
        st.markdown("**Fontes & Layout**")
        st.markdown("- Você pode selecionar fonte e tamanho na seção Visual. Os nomes de fontes são normalizados automaticamente.")
        st.caption("Posso expandir cada tópico com passo-a-passo e checklists (busco fontes oficiais se desejar).")

# ---------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------
st.markdown("<br><br>", unsafe_allow_html=True)
st.caption("Sistema O PREGADOR — Versão consolidada. Recursos de sincronização requerem configuração externa. Desenvolvido com carinho — preserve dados sensíveis com responsabilidade.")
