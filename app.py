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
import re
from datetime import datetime, timedelta
from io import BytesIO

# ==============================================================================
# 0. KERNEL DE INICIALIZAÇÃO E BLINDAGEM (System Omega V30)
# ==============================================================================
class SystemOmegaKernel:
    """Gerencia dependências críticas e integridade do ambiente."""
    REQUIRED = [
        "google-generativeai", "streamlit-lottie", "Pillow", "pandas",
        "streamlit-quill", "python-docx", "reportlab", "mammoth"
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
                # Normalização de nomes para import
                mod = lib.replace("google-generativeai", "google.generativeai") \
                         .replace("Pillow", "PIL") \
                         .replace("python-docx", "docx") \
                         .replace("streamlit-quill", "streamlit_quill")
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

# Executa verificação de boot
SystemOmegaKernel.boot_check()

# Imports Seguros pós-boot
import google.generativeai as genai
from PIL import Image, ImageOps
try:
    from streamlit_quill import st_quill
    QUILL_OK = True
except ImportError:
    QUILL_OK = False

try:
    from docx import Document
    DOCX_OK = True
except ImportError:
    DOCX_OK = False

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    PDF_OK = True
except ImportError:
    PDF_OK = False

# ==============================================================================
# 1. INFRAESTRUTURA DE DADOS (NASA SAFE I/O)
# ==============================================================================
st.set_page_config(
    page_title="O PREGADOR | V30", 
    layout="wide", 
    page_icon="✝️", 
    initial_sidebar_state="expanded"
)
SystemOmegaKernel.inject_pwa_headers()

ROOT = "Dados_Pregador_V30"
DIRS = {
    "SERMOES": os.path.join(ROOT, "Sermoes"),
    "GABINETE": os.path.join(ROOT, "Gabinete_Pastoral"),
    "SERIES": os.path.join(ROOT, "Series"),
    "MIDIA": os.path.join(ROOT, "Midia"),
    "USER": os.path.join(ROOT, "User_Data"),
    "BACKUP": os.path.join(ROOT, "Backups_Encriptados"),
    "LOGS": os.path.join(ROOT, "Flight_Logs")
}
DBS = {
    "SERIES": os.path.join(DIRS["SERIES"], "db_series.json"),
    "STATS": os.path.join(DIRS["USER"], "db_stats.json"),
    "CONFIG": os.path.join(DIRS["USER"], "config.json"),
    "SOUL": os.path.join(DIRS["GABINETE"], "soul_data.json"),
    "USERS": os.path.join(DIRS["USER"], "users_db.json"),
    "BRAIN": os.path.join(DIRS["GABINETE"], "brain_structure.json")
}

for d in DIRS.values():
    os.makedirs(d, exist_ok=True)

# Logging Robusto
logging.basicConfig(
    filename=os.path.join(DIRS["LOGS"], "system.log"), 
    level=logging.INFO, 
    format='%(asctime)s|%(levelname)s|%(message)s'
)

class SafeIO:
    """I/O Atômico com proteção contra corrupção."""
    @staticmethod
    def ler_json(caminho, default_return):
        if not os.path.exists(caminho): return default_return
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                c = f.read().strip()
                return json.loads(c) if c else default_return
        except Exception as e:
            logging.error(f"Read Error {caminho}: {e}")
            return default_return

    @staticmethod
    def salvar_json(caminho, dados):
        try:
            tmp = caminho + ".tmp"
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
            os.replace(tmp, caminho)
            # Backup Rotativo Simples
            shutil.copy2(caminho, os.path.join(DIRS["BACKUP"], os.path.basename(caminho) + ".bak"))
            return True
        except Exception as e:
            logging.error(f"Write Error {caminho}: {e}")
            return False

# ==============================================================================
# 2. DESIGN SYSTEM (Dark Cathedral)
# ==============================================================================
def inject_css(color="#D4AF37", font_sz=18):
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700&family=Playfair+Display:wght@600&family=Cinzel:wght@500;800&family=JetBrains+Mono&display=swap');
        
        :root {{ --gold: {color}; --gold-glow: rgba(212, 175, 55, 0.2); --neon-gold: #FFD700; --bg: #000000; --panel: #0A0A0A; --border: #1F1F1F; --text: #EAEAEA; }}
        
        .stApp {{ background-color: var(--bg); background-image: radial-gradient(circle at 50% -20%, #1a1200 0%, #000 70%); color: var(--text); font-family: 'Inter', sans-serif; }}
        [data-testid="stSidebar"] {{ background-color: #050505; border-right: 1px solid var(--border); }}
        
        @keyframes holy-pulse {{ 0% {{ filter: drop-shadow(0 0 5px var(--gold-glow)); transform: scale(1); }} 50% {{ filter: drop-shadow(0 0 20px var(--gold)); transform: scale(1.02); }} 100% {{ filter: drop-shadow(0 0 5px var(--gold-glow)); transform: scale(1); }} }}
        .prime-logo {{ width: 140px; height: 140px; margin: 0 auto 20px auto; animation: holy-pulse 4s infinite ease-in-out; display: block; }}
        
        .tech-card {{ background: #090909; border: 1px solid var(--border); border-left: 2px solid var(--gold); border-radius: 4px; padding: 25px; margin-bottom: 20px; }}
        
        /* Quill e Inputs */
        .editor-wrapper textarea, .stTextArea textarea {{ font-family: 'Playfair Display', serif !important; font-size: {font_sz}px !important; background-color: #050505 !important; color: #ccc !important; }}
        .stTextInput input, .stSelectbox div {{ background-color: #0A0A0A !important; border: 1px solid #222 !important; color: #eee !important; }}
        .stButton button {{ border-radius: 2px !important; text-transform: uppercase; font-weight: 700; background: #111; color: #888; border: 1px solid #333; }}
        .stButton button:hover {{ border-color: var(--gold); color: var(--gold); }}
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. CORE LOGIC (BACKEND)
# ==============================================================================

class AccessControl:
    @staticmethod
    def _hash(text): return hashlib.sha256(text.encode()).hexdigest()

    @staticmethod
    def login(username, password):
        users = SafeIO.ler_json(DBS["USERS"], {})
        # Admin Default (senha: 1234)
        if not users and username.upper() == "ADMIN" and password == "1234": return True
        
        u_upper = username.upper().strip()
        hashed = AccessControl._hash(password)
        
        if u_upper in users:
            stored = users[u_upper]
            if len(stored) != 64: return stored == password # Legado
            return stored == hashed
        return False

    @staticmethod
    def register(username, password):
        users = SafeIO.ler_json(DBS["USERS"], {})
        if username.upper() in users: return False, "JÁ EXISTE."
        users[username.upper()] = AccessControl._hash(password)
        SafeIO.salvar_json(DBS["USERS"], users)
        return True, "REGISTRADO."

class PastoralMind:
    @staticmethod
    def check_burnout():
        data = SafeIO.ler_json(DBS["SOUL"], {"historico": [], "scans": []})
        scans = data.get("scans", [])
        hist = data.get("historico", [])[-10:]
        
        perm_score = scans[-1].get("score", 50) if scans else 50
        bad_humor = sum(1 for h in hist if h['humor'] in ["Cansaço 🌖", "Ira 😠", "Ansiedade 🌪️", "Tristeza 😢"])
        
        if bad_humor >= 6 or perm_score < 30: return "CRÍTICO", "#FF3333"
        if bad_humor >= 3 or perm_score < 60: return "ALERTA", "#FFAA00"
        return "OPERACIONAL", "#33FF33"
    
    @staticmethod
    def registrar_humor(humor):
        data = SafeIO.ler_json(DBS["SOUL"], {"historico": [], "scans": []})
        data["historico"].append({"data": datetime.now().strftime("%Y-%m-%d"), "humor": humor})
        SafeIO.salvar_json(DBS["SOUL"], data)

class PermissionEngine:
    @staticmethod
    def diagnosticar(f, s, d, suc):
        avg = (f + s + d + suc) / 4
        feedback = "Equilibrado."
        if avg < 30: feedback = "Modo de Sobrevivência: Risco de Burnout."
        elif avg < 60: feedback = "Em progresso: Lute contra o legalismo."
        else: feedback = "Liberdade na Graça: Identidade saudável."
        
        data = SafeIO.ler_json(DBS["SOUL"], {"historico": [], "scans": []})
        data.setdefault("scans", []).append({
            "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "score": avg,
            "detalhes": {"falhar": f, "sentir": s, "descansar": d, "sucesso": suc},
            "feedback": feedback
        })
        SafeIO.salvar_json(DBS["SOUL"], data)
        return feedback, avg

class BrainDivider:
    """Gerenciamento Modular do Studio."""
    @staticmethod
    def load():
        return SafeIO.ler_json(DBS["BRAIN"], {"modules": [{"id": "core", "role": "kernel", "desc": "Núcleo Primário"}]}).get("modules", [])
    
    @staticmethod
    def generate(count, prefix):
        data = SafeIO.ler_json(DBS["BRAIN"], {"modules": []})
        for i in range(count):
            data["modules"].append({
                "id": f"{prefix}_{i}",
                "role": random.choice(["logic", "memory", "perception"]),
                "desc": f"Auto-generated partition {i}",
                "created": datetime.now().isoformat()
            })
        SafeIO.salvar_json(DBS["BRAIN"], data)
        return len(data["modules"])

class Gamification:
    @staticmethod
    def add_xp(amount):
        stats = SafeIO.ler_json(DBS["STATS"], {"xp": 0, "nivel": 1})
        stats["xp"] += amount
        stats["nivel"] = int(math.sqrt(stats["xp"]) * 0.2) + 1
        SafeIO.salvar_json(DBS["STATS"], stats)

class SessionPersistence:
    """Autosave de Sessão"""
    @staticmethod
    def save():
        if not st.session_state.get("user_name"): return
        path = os.path.join(DIRS["USER"], f"session_{st.session_state['user_name']}.json")
        keys = ["logado", "user_name", "texto_ativo", "titulo_ativo", "config"]
        data = {k: st.session_state[k] for k in keys if k in st.session_state}
        SafeIO.salvar_json(path, data)

    @staticmethod
    def load(user):
        path = os.path.join(DIRS["USER"], f"session_{user}.json")
        data = SafeIO.ler_json(path, {})
        for k, v in data.items(): st.session_state[k] = v

# ==============================================================================
# 4. STARTUP E LOGIN
# ==============================================================================
if "config" not in st.session_state:
    st.session_state["config"] = SafeIO.ler_json(DBS["CONFIG"], {"theme_color": "#D4AF37", "font_size": 18, "api_key": ""})

inject_css(st.session_state["config"]["theme_color"], st.session_state["config"]["font_size"])

# Inicializa Session State
defaults = {"logado": False, "user_name": "", "texto_ativo": "", "titulo_ativo": "", "last_tags": []}
for k, v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v

if not st.session_state["logado"]:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        gold = st.session_state["config"]["theme_color"]
        st.markdown(f"""
        <svg class="prime-logo" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="45" stroke="{gold}" stroke-width="3" fill="none" />
            <line x1="50" y1="25" x2="50" y2="75" stroke="{gold}" stroke-width="3" />
            <line x1="35" y1="40" x2="65" y2="40" stroke="{gold}" stroke-width="3" />
        </svg>
        <div style="text-align:center; font-family:'Cinzel'; color:#fff; font-size:24px; letter-spacing:8px;">O PREGADOR</div>
        <div style="text-align:center;font-size:10px;color:#555;letter-spacing:4px;margin-bottom:20px;">SYSTEM V30 | REFORMATION UPDATE</div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["ENTRAR", "CRIAR ACESSO"])
        with tab1:
            with st.form("login_form"):
                u = st.text_input("Identidade")
                p = st.text_input("Credencial", type="password")
                if st.form_submit_button("INICIAR", type="primary", use_container_width=True):
                    if AccessControl.login(u, p):
                        st.session_state["logado"] = True
                        st.session_state["user_name"] = u.upper()
                        SessionPersistence.load(u.upper())
                        st.rerun()
                    else: st.error("Acesso Negado.")
        with tab2:
            with st.form("reg_form"):
                nu = st.text_input("Novo Usuário")
                np = st.text_input("Nova Senha", type="password")
                if st.form_submit_button("REGISTRAR"):
                    ok, msg = AccessControl.register(nu, np)
                    if ok: st.success(msg)
                    else: st.error(msg)
    st.stop()

# ==============================================================================
# 5. APLICAÇÃO PRINCIPAL (UI & MÓDULOS)
# ==============================================================================

# --- Sidebar ---
with st.sidebar:
    # Avatar
    avatar_path = os.path.join(DIRS["USER"], "avatar.png")
    if os.path.exists(avatar_path):
        with open(avatar_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(f'<div style="text-align:center"><img src="data:image/png;base64,{b64}" style="width:100px; border-radius:50%; border:2px solid {st.session_state["config"]["theme_color"]}"></div>', unsafe_allow_html=True)
    
    st.markdown(f"<center><b>{st.session_state['user_name']}</b></center>", unsafe_allow_html=True)
    st.markdown("---")
    
    menu = st.radio("NAVEGAÇÃO", [
        "Dashboard", 
        "Teoria da Permissão", 
        "Gabinete Pastoral", 
        "Studio Expositivo", 
        "Biblioteca", 
        "Configurações"
    ], label_visibility="collapsed")
    
    st.markdown("---")
    if st.button("LOGOUT (SALVAR)", use_container_width=True):
        SessionPersistence.save()
        st.session_state["logado"] = False
        st.rerun()

# --- Header Status ---
stat, cor = PastoralMind.check_burnout()
c_h1, c_h2 = st.columns([3, 1])
c_h1.markdown(f"**LITURGIA:** {datetime.now().strftime('%A').upper()}")
c_h2.markdown(f"<div style='text-align:right; color:{cor}'>STATUS: {stat}</div>", unsafe_allow_html=True)
st.markdown("---")

# --- Módulos ---

if menu == "Dashboard":
    st.title("Painel de Controle")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
        humor = st.selectbox("Check-in da Alma", ["Plenitude 🕊️", "Gratidão 🙏", "Cansaço 🌖", "Ira 😠", "Ansiedade 🌪️"], label_visibility="collapsed")
        if st.button("REGISTRAR"):
            PastoralMind.registrar_humor(humor)
            Gamification.add_xp(10)
            st.success("Registrado.")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
        stats = SafeIO.ler_json(DBS["STATS"], {"xp":0, "nivel":1})
        st.markdown(f"### Nível Teológico: {stats['nivel']}")
        st.progress(min(stats['xp'] % 100, 100))
        st.caption("A jornada é longa, mas a graça é suficiente.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("Arquivos Recentes")
    try:
        files = sorted([f for f in os.listdir(DIRS["SERMOES"]) if f.endswith(".txt")], key=lambda x: os.path.getmtime(os.path.join(DIRS["SERMOES"], x)), reverse=True)[:3]
        cols = st.columns(3)
        for i, f in enumerate(files):
            cols[i].markdown(f"📄 {f}")
    except: pass

elif menu == "Teoria da Permissão":
    st.title("Teoria da Permissão: Diagnóstico")
    with st.markdown('<div class="tech-card">', unsafe_allow_html=True):
        c1, c2 = st.columns(2)
        p1 = c1.slider("Permissão para FALHAR", 0, 100, 50)
        p2 = c1.slider("Permissão para SENTIR", 0, 100, 50)
        p3 = c2.slider("Permissão para DESCANSAR", 0, 100, 50)
        p4 = c2.slider("Permissão para SUCESSO", 0, 100, 50)
        
        if st.button("EXECUTAR SCAN DIAGNÓSTICO", use_container_width=True, type="primary"):
            fb, sc = PermissionEngine.diagnosticar(p1, p2, p3, p4)
            st.metric("Índice de Permissão", f"{int(sc)}/100")
            if sc < 50: st.error(fb)
            else: st.success(fb)
            Gamification.add_xp(20)

elif menu == "Gabinete Pastoral":
    st.title("Gabinete Pastoral (Word-like Editor)")
    
    # Barra de Ferramentas Superior
    c_title, c_tools = st.columns([3, 1])
    st.session_state["titulo_ativo"] = c_title.text_input("Título do Sermão", st.session_state["titulo_ativo"])
    
    with c_tools:
        st.caption("Exportar:")
        cx1, cx2 = st.columns(2)
        if cx1.button("DOCX"):
            if not DOCX_OK: st.error("Lib ausente.")
            else:
                doc = Document()
                doc.add_heading(st.session_state["titulo_ativo"], 0)
                doc.add_paragraph(st.session_state["texto_ativo"]) # Simples text dump
                buf = BytesIO()
                doc.save(buf)
                st.download_button("Baixar", buf.getvalue(), f"{st.session_state['titulo_ativo']}.docx")
        
        if cx2.button("PDF"):
            if not PDF_OK: st.error("Lib ausente.")
            else:
                buf = BytesIO()
                c = canvas.Canvas(buf, pagesize=A4)
                c.drawString(72, 800, st.session_state["titulo_ativo"])
                textobj = c.beginText(72, 780)
                # Quebra de linha simples
                for line in st.session_state["texto_ativo"].split('\n'):
                    textobj.textLine(line[:90])
                c.drawText(textobj)
                c.save()
                st.download_button("Baixar", buf.getvalue(), f"{st.session_state['titulo_ativo']}.pdf")

    # Editor Principal (Quill)
    if QUILL_OK:
        content = st_quill(
            value=st.session_state["texto_ativo"],
            placeholder="Escreva sua pregação...",
            key="quill_editor"
        )
        # Autosave Logic
        if content != st.session_state["texto_ativo"]:
            st.session_state["texto_ativo"] = content
            # Salvar no disco
            fname = f"{st.session_state['titulo_ativo'] or 'SemTitulo'}.txt"
            with open(os.path.join(DIRS["SERMOES"], fname), 'w', encoding='utf-8') as f:
                f.write(content)
            SessionPersistence.save()
    else:
        st.warning("Editor Avançado indisponível. Usando modo texto.")
        st.session_state["texto_ativo"] = st.text_area("Editor", st.session_state["texto_ativo"], height=500)

elif menu == "Studio Expositivo":
    st.title("Studio Expositivo & Brain Divider")
    
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown("### Brain Divider (Modularização)")
        qt = st.number_input("Gerar novas partições neurais", 1, 100, 5)
        if st.button("EXPANDIR CAPACIDADE"):
            total = BrainDivider.generate(qt, "cortex")
            st.success(f"Cérebro expandido para {total} módulos.")
        
        mods = BrainDivider.load()
        st.json(mods[-5:], expanded=False)

    with c2:
        st.markdown("### Geneva Protocol")
        alerta = st.text_input("Verificação Doutrinária (Frase)")
        if alerta:
            if "decreto" in alerta.lower() or "determino" in alerta.lower():
                st.error("⚠️ ALERTA: Quebra de Soberania Divina.")
            else:
                st.success("✅ Frase aprovada.")

elif menu == "Biblioteca":
    st.title("Biblioteca de Estudo Comparativo")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Texto Base")
        st.text_area("Hebraico / Grego / NVI", height=300, key="txt_base")
    with c2:
        st.subheader("Comentários")
        st.text_area("Notas Teológicas", height=300, key="txt_com")
    
    st.info("💡 Arraste arquivos JSON do TheWord para a pasta 'Gabinete_Pastoral' para integração futura.")

elif menu == "Configurações":
    st.title("Configurações do Sistema")
    with st.expander("🔐 ACESSAR PAINEL DE HARDWARE & UI", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            nc = st.color_picker("Cor do Tema", st.session_state["config"]["theme_color"])
            nf = st.slider("Tamanho da Fonte", 12, 32, st.session_state["config"]["font_size"])
        with c2:
            nk = st.text_input("API Key (Google)", type="password", value=st.session_state["config"]["api_key"])
        
        if st.button("SALVAR E REINICIAR KERNEL", type="primary"):
            st.session_state["config"].update({"theme_color": nc, "font_size": nf, "api_key": nk})
            SafeIO.salvar_json(DBS["CONFIG"], st.session_state["config"])
            st.rerun()

# Hook Final de Salvamento
SessionPersistence.save()
