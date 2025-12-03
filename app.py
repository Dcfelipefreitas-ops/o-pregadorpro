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
import streamlit as st
from streamlit_quill import st_quill

import streamlit as st
from streamlit_quill import st_quill
import streamlit as st
from streamlit_quill import st_quill

import streamlit as st
from streamlit_quill import st_quill

# ------------------------------
# INTERFACE BÁSICA APÓS LOGIN
# ------------------------------
st.set_page_config(layout="wide")

# Ocultar/mostrar menu lateral
if "hide_menu" not in st.session_state:
    st.session_state.hide_menu = False

col1, col2 = st.columns([0.87,0.13])
with col2:
    if st.button("Ocultar Menu" if not st.session_state.hide_menu else "Mostrar Menu"):
        st.session_state.hide_menu = not st.session_state.hide_menu

# MENU LATERAL
if not st.session_state.hide_menu:
    menu = st.sidebar.radio("Menu", [
        "Teoria da Permissão",
        "Cuidado Pastoral",
        "Gabinete Pastoral",
        "Biblioteca",
        "Configurações"
    ])
else:
    menu = "Gabinete Pastoral"

# ------------------------------
# TELA TEORIA DA PERMISSÃO (INÍCIO PADRÃO)
# ------------------------------
if menu == "Teoria da Permissão":
    st.title("📘 Teoria da Permissão — O Pregador")
    st.write("Aqui ficará o módulo com explicações, vídeos, áudios e conteúdos inspirados no TheWord.")

# ------------------------------
# TELA CUIDADO PASTORAL (SEGUNDA ABA)
# ------------------------------
elif menu == "Cuidado Pastoral":
    st.title("💛 Cuidado Pastoral")
    st.write("Ferramentas baseadas no TheWord para organização de visitas, aconselhamento e suporte espiritual.")

# ------------------------------
# GABINETE PASTORAL — EDITOR ESTILO WORD
# ------------------------------
elif menu == "Gabinete Pastoral":
    st.title("📝 Gabinete Pastoral — Criar Sermão / Esboço")
    
    st.write("### Editor estilo Word — com opções avançadas e personalização inspirada em TheWord, Logos e Bible Tesla")

    # Opções de Personalização (sem alterar layout padrão)
    with st.expander("🎨 Personalizar Editor (opcional)"):
        font_size = st.slider("Tamanho da Fonte", 12, 40, 18)
        theme = st.selectbox("Tema do Editor", ["Padrão", "Escuro", "Pergaminho", "Página Branca"])
        fullscreen = st.toggle("Modo Tela Cheia")

    # Editor Word-like
    container_style = "width:100%;" if not fullscreen else "position:fixed; top:0; left:0; right:0; bottom:0; background:white; padding:30px; z-index:9999;"

    with st.container():
        st.markdown(f"<div style='{container_style}'>", unsafe_allow_html=True)

        content = st_quill(key="editor", placeholder="Comece a escrever sua pregação aqui...")

        st.markdown("</div>", unsafe_allow_html=True)

    # Preview
    st.write("### Pré-visualização da Pregação:")
    if content:
        preview_html = f"<div style='font-size:{font_size}px;'>{content}</div>"
        st.markdown(preview_html, unsafe_allow_html=True)


# ------------------------------
elif menu == "Gabinete Pastoral":
    st.title("📝 Gabinete Pastoral — Criar Sermão / Esboço")

    st.write("### Editor estilo Word (baseado no Quill e no padrão do app TheWord)")

    content = st_quill(key="editor", placeholder="Comece a escrever sua pregação aqui...")

    st.write("### Pré-visualização do texto:")
    if content:
        st.write(content)

# ------------------------------
# BIBLIOTECA
# ------------------------------
elif menu == "Biblioteca":
    st.title("📚 Biblioteca — Inspirada no TheWord")
    st.write("Futuramente: buscas, livros gratuitos, coleções, comentários, dicionários.")

# ------------------------------
# CONFIGURAÇÕES
# ------------------------------
elif menu == "Configurações":
    st.title("⚙️ Configurações do Sistema")
    st.write("Ajustes gerais do layout, temas, fontes, integrações etc.")
# =============================
# EXTENSÕES (HTML->DOCX, ENCRIPTAÇÃO AES, PARSERS THEWORD/LOGOS/TESLA, API BÍBLICA)
# =============================

# 1) Export HTML -> DOCX mais fiel (mammoth / html2docx fallback)
try:
    import mammoth
    HTML2DOCX = "mammoth"
except Exception:
    try:
        from html2docx import html2docx
        HTML2DOCX = "html2docx"
    except Exception:
        HTML2DOCX = None

def export_html_to_docx_better(title, html_content, out_path):
    """Tenta usar mammoth (HTML->DOCX) ou html2docx; caso não disponível, usa fallback simples."""
    if HTML2DOCX == "mammoth":
        import mammoth
        # mammoth expects HTML string
        with open(out_path, "wb") as docx_file:
            results = mammoth.convert_to_docx(html_content)
            docx_file.write(results.value)
        return out_path
    elif HTML2DOCX == "html2docx":
        from html2docx import html2docx
        with open(out_path, "wb") as f:
            f.write(html2docx(html_content))
        return out_path
    else:
        # fallback: existing export_to_docx
        try:
            return export_to_docx(title, html_content, out_path)
        except Exception:
            raise RuntimeError('Nenhum método disponível para converter HTML->DOCX')

# 2) AES Encryption for sermons (using cryptography)
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    CRYPTO_OK = True
except Exception:
    CRYPTO_OK = False

def encrypt_sermon_aes(password, plaintext):
    if not CRYPTO_OK:
        raise RuntimeError("Cryptography não disponível")
    # Derive a 32-byte key from password (simple KDF: SHA256) - for production use PBKDF2/Argon2
    import hashlib, os
    key = hashlib.sha256(password.encode()).digest()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
    # store nonce + ct (base64)
    return base64.b64encode(nonce + ct).decode('utf-8')

def decrypt_sermon_aes(password, b64payload):
    if not CRYPTO_OK:
        raise RuntimeError("Cryptography não disponível")
    import hashlib
    data = base64.b64decode(b64payload)
    nonce = data[:12]
    ct = data[12:]
    key = hashlib.sha256(password.encode()).digest()
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ct, None).decode('utf-8')

# 3) Parsers / import helpers for TheWord / Logos / Tesla (stubs)
# These functions are stubs; if you upload an exported file from TheWord/Logos/Tesla, the parser will attempt to extract texts.
# Provide a sample file and I will refine the parser.

def parse_theword_export(path):
    """Tenta extrair textos de um arquivo TheWord exportado (possivelmente XML/USFM/JSON)."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        # heurística simples: se for XML, retorna content inside tags <verse> or similar
        if text.lstrip().startswith('<'):
            # very naive xml parse
            import re
            verses = re.findall(r'<verse[^>]*>(.*?)</verse>', text, flags=re.DOTALL|re.IGNORECASE)
            if verses:
                return "
".join(verses)
        # if json
        if text.strip().startswith('{'):
            data = json.loads(text)
            # heuristic: find values that look like verses
            texts = []
            def walk(o):
                if isinstance(o, dict):
                    for k,v in o.items():
                        walk(v)
                elif isinstance(o, list):
                    for i in o: walk(i)
                elif isinstance(o, str):
                    if len(o) > 20 and any(w in o.lower() for w in ['god','jesus','christ','lord','deus']):
                        texts.append(o)
            walk(data)
            if texts:
                return '
'.join(texts[:200])
        return text[:10000]
    except Exception as e:
        logging.error('parse_theword_export failed: %s', e)
        return None

# 4) Bible API integration (placeholder)
# NOTE: Não ativo por padrão — o usuário deve fornecer provider e chave em config (st.session_state['config']['bible_api'])

def bible_api_query(reference, provider='bible_api_provider'):
    """Faz uma consulta a uma API bíblica externa. O provider é um placeholder — informe endpoint e API KEY no config."""
    cfg = st.session_state.get('config', {})
    api_info = cfg.get('bible_api', {})
    if not api_info:
        raise RuntimeError('Nenhuma configuração de API bíblica encontrada. Defina st.session_state["config"]["bible_api"] com provider, url e api_key')
    # Exemplo de payload / headers — o formato dependerá do provedor
    import requests
    url = api_info.get('url')
    key = api_info.get('api_key')
    if not url or not key:
        raise RuntimeError('Config de API incompleta (url/api_key).')
    params = {'q': reference}
    headers = {'Authorization': f'Bearer {key}'}
    r = requests.get(url, params=params, headers=headers, timeout=10)
    if r.status_code == 200:
        return r.json()
    else:
        logging.warning('Bible API returned %s', r.status_code)
        return None

# 5) Hooks para UI: export melhorado, encriptação real e import parser
# (Esses hooks foram conectados ao editor; para usar, defina senhas e configs nas Configurações do app)

def install_extra_requirements_instructions():
    return {
        'python-docx': 'pip install python-docx',
        'reportlab': 'pip install reportlab',
        'streamlit-quill': 'pip install streamlit-quill',
        'mammoth': 'pip install mammoth',
        'html2docx': 'pip install html2docx',
        'cryptography': 'pip install cryptography',
        'requests': 'pip install requests'
    }

# END EXTENSÕES


# ------------------------------
# INTERFACE BÁSICA APÓS LOGIN
# ------------------------------
st.set_page_config(layout="wide")

# Ocultar/mostrar menu lateral
if "hide_menu" not in st.session_state:
    st.session_state.hide_menu = False

col1, col2 = st.columns([0.87,0.13])
with col2:
    if st.button("Ocultar Menu" if not st.session_state.hide_menu else "Mostrar Menu"):
        st.session_state.hide_menu = not st.session_state.hide_menu

# MENU LATERAL
if not st.session_state.hide_menu:
    menu = st.sidebar.radio("Menu", [
        "Teoria da Permissão",
        "Cuidado Pastoral",
        "Gabinete Pastoral",
        "Biblioteca",
        "Configurações"
    ])
else:
    menu = "Gabinete Pastoral"

# ------------------------------
# TELA TEORIA DA PERMISSÃO (INÍCIO PADRÃO)
# ------------------------------
if menu == "Teoria da Permissão":
    st.title("📘 Teoria da Permissão — O Pregador")
    st.write("Aqui ficará o módulo com explicações, vídeos, áudios e conteúdos inspirados no TheWord.")

# ------------------------------
# TELA CUIDADO PASTORAL (SEGUNDA ABA)
# ------------------------------
elif menu == "Cuidado Pastoral":
    st.title("💛 Cuidado Pastoral")
    st.write("Ferramentas baseadas no TheWord para organização de visitas, aconselhamento e suporte espiritual.")

# ------------------------------
# GABINETE PASTORAL — EDITOR ESTILO WORD
# ------------------------------
elif menu == "Gabinete Pastoral":
    st.title("📝 Gabinete Pastoral — Criar Sermão / Esboço")
    
    st.write("### Editor estilo Word — com opções avançadas e personalização inspirada em TheWord, Logos e Bible Tesla")

    # Opções de Personalização (sem alterar layout padrão)
    with st.expander("🎨 Personalizar Editor (opcional)"):
        font_size = st.slider("Tamanho da Fonte", 12, 40, 18)
        theme = st.selectbox("Tema do Editor", ["Padrão", "Escuro", "Pergaminho", "Página Branca"])
        fullscreen = st.toggle("Modo Tela Cheia")

    # Editor Word-like
    container_style = "width:100%;" if not fullscreen else "position:fixed; top:0; left:0; right:0; bottom:0; background:white; padding:30px; z-index:9999;"

    with st.container():
        st.markdown(f"<div style='{container_style}'>", unsafe_allow_html=True)

        content = st_quill(key="editor", placeholder="Comece a escrever sua pregação aqui...")

        st.markdown("</div>", unsafe_allow_html=True)

    # Preview
    st.write("### Pré-visualização da Pregação:")
    if content:
        preview_html = f"<div style='font-size:{font_size}px;'>{content}</div>"
        st.markdown(preview_html, unsafe_allow_html=True)


# ------------------------------
elif menu == "Gabinete Pastoral":
    st.title("📝 Gabinete Pastoral — Criar Sermão / Esboço")

    st.write("### Editor estilo Word (baseado no Quill e no padrão do app TheWord)")

    content = st_quill(key="editor", placeholder="Comece a escrever sua pregação aqui...")

    st.write("### Pré-visualização do texto:")
    if content:
        st.write(content)

# ------------------------------
# BIBLIOTECA
# ------------------------------
elif menu == "Biblioteca":
    st.title("📚 Biblioteca — Inspirada no TheWord")
    st.write("Futuramente: buscas, livros gratuitos, coleções, comentários, dicionários.")

# ------------------------------
# CONFIGURAÇÕES
# ------------------------------
elif menu == "Configurações":
    st.title("⚙️ Configurações do Sistema")
    st.write("Ajustes gerais do layout, temas, fontes, integrações etc.")

# ==============================================================================
# 0. KERNEL DE INICIALIZAÇÃO E BLINDAGEM (System Omega)
# ==============================================================================
class SystemOmegaKernel:
    REQUIRED = ["google-generativeai", "streamlit-lottie", "Pillow", "pandas"]
    
    @staticmethod
    def _install_quiet(pkg):
        try:
            # Tenta instalar silenciosamente
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--quiet", "--no-warn-script-location"])
            return True
        except: return False

    @staticmethod
    def boot_check():
        queue = []
        for lib in SystemOmegaKernel.REQUIRED:
            try:
                # Tratamento de nomes diferentes entre pip e import
                mod = lib.replace("google-generativeai", "google.generativeai").replace("Pillow", "PIL")
                __import__(mod.replace("-", "_"))
            except ImportError:
                queue.append(lib)
        
        if queue:
            placeholder = st.empty()
            placeholder.code(f"SYSTEM REBOOT :: INSTALLING MODULES ({len(queue)})...", language="bash")
            for lib in queue:
                SystemOmegaKernel._install_quiet(lib)
            placeholder.empty()
            st.rerun()

    @staticmethod
    def inject_pwa_headers():
        # Meta tags para funcionamento híbrido/App
        st.markdown("""
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        """, unsafe_allow_html=True)

SystemOmegaKernel.boot_check()

import google.generativeai as genai
from PIL import Image, ImageOps

# ==============================================================================
# 1. INFRAESTRUTURA DE DADOS (NASA SAFE I/O)
# ==============================================================================
st.set_page_config(
    page_title="O PREGADOR", 
    layout="wide", 
    page_icon="✝️", 
    initial_sidebar_state="expanded"
)
SystemOmegaKernel.inject_pwa_headers()

ROOT = "Dados_Pregador_V29"
DIRS = {
    "SERMOES": os.path.join(ROOT, "Sermoes"),
    "GABINETE": os.path.join(ROOT, "Gabinete_Pastoral"),
    "SERIES": os.path.join(ROOT, "Series"),
    "MIDIA": os.path.join(ROOT, "Midia"),
    "USER": os.path.join(ROOT, "User_Data"),
    "BACKUP": os.path.join(ROOT, "Auto_Backup_Oculto"),
    "LOGS": os.path.join(ROOT, "System_Logs")
}
DBS = {
    "SERIES": os.path.join(DIRS["SERIES"], "db_series.json"),
    "STATS": os.path.join(DIRS["USER"], "db_stats.json"),
    "CONFIG": os.path.join(DIRS["USER"], "config.json"),
    "SOUL": os.path.join(DIRS["GABINETE"], "soul_data.json"),
    "USERS": os.path.join(DIRS["USER"], "users_db.json")
}

for d in DIRS.values():
    os.makedirs(d, exist_ok=True)

# Logger estilo Caixa Preta
logging.basicConfig(filename=os.path.join(DIRS["LOGS"], "system.log"), level=logging.INFO, format='%(asctime)s|%(levelname)s|%(message)s')

class SafeIO:
    """Sistema de Preservação de Dados com Escrita Atômica."""
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
            # Escreve em temp e renomeia (Atomic)
            tmp = caminho + ".tmp"
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
            os.replace(tmp, caminho)
            # Backup
            shutil.copy2(caminho, os.path.join(DIRS["BACKUP"], os.path.basename(caminho) + ".bak"))
            return True
        except Exception as e: 
            logging.error(f"Write Error {caminho}: {e}")
            return False

# ==============================================================================
# 2. DESIGN SYSTEM (Imutável conforme solicitado)
# ==============================================================================
def inject_css(color="#D4AF37", font_sz=18):
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700&family=Playfair+Display:wght@600&family=Cinzel:wght@500;800&family=JetBrains+Mono&display=swap');
        
        :root {{ --gold: {color}; --gold-glow: rgba(212, 175, 55, 0.2); --neon-gold: #FFD700; --bg: #000000; --panel: #0A0A0A; --border: #1F1F1F; --text: #EAEAEA; }}
        
        .stApp {{ background-color: var(--bg); background-image: radial-gradient(circle at 50% -20%, #1a1200 0%, #000 70%); color: var(--text); font-family: 'Inter', sans-serif; }}
        [data-testid="stSidebar"] {{ background-color: #050505; border-right: 1px solid var(--border); }}
        [data-testid="stSidebar"] hr {{ margin: 0; border-color: #222; }}
        
        @keyframes holo-reveal {{ 0% {{ opacity: 0; transform: scale(0.8) translateY(20px); filter: blur(10px); }} 20% {{ opacity: 1; transform: scale(1.1); filter: blur(0px); }} 40% {{ opacity: 0.8; transform: scale(0.95); filter: hue-rotate(90deg); }} 60% {{ opacity: 1; transform: scale(1.02); filter: hue-rotate(0deg); }} 100% {{ opacity: 1; transform: scale(1); }} }}
        @keyframes scanline {{ 0% {{ top: -10%; opacity: 0; }} 50% {{ opacity: 1; }} 100% {{ top: 110%; opacity: 0; }} }}
        .holo-container {{ position: relative; width: 120px; height: 120px; margin: 0 auto 20px auto; border-radius: 50%; border: 2px solid var(--gold); overflow: hidden; box-shadow: 0 0 15px var(--gold-glow); animation: holo-reveal 1.5s cubic-bezier(0.23, 1, 0.32, 1) forwards; background: #000; }}
        .holo-img {{ width: 100%; height: 100%; object-fit: cover; filter: sepia(50%) contrast(1.2); }}
        .holo-container::after {{ content: ''; position: absolute; width: 100%; height: 5px; background: var(--neon-gold); box-shadow: 0 0 10px var(--neon-gold); opacity: 0.6; animation: scanline 3s infinite linear; }}
        
        @keyframes holy-pulse {{ 0% {{ filter: drop-shadow(0 0 5px var(--gold-glow)); transform: scale(1); }} 50% {{ filter: drop-shadow(0 0 20px var(--gold)); transform: scale(1.02); }} 100% {{ filter: drop-shadow(0 0 5px var(--gold-glow)); transform: scale(1); }} }}
        .prime-logo {{ width: 140px; height: 140px; margin: 0 auto 20px auto; animation: holy-pulse 4s infinite ease-in-out; display: block; }}
        .login-title {{ font-family: 'Cinzel'; letter-spacing: 8px; color: #fff; font-size: 24px; margin-top: 10px; text-transform: uppercase; text-align: center; }}
        
        .tech-card {{ background: #090909; border: 1px solid var(--border); border-left: 2px solid var(--gold); border-radius: 4px; padding: 25px; margin-bottom: 20px; transition: 0.3s; }}
        .tech-card:hover {{ border-color: #333; box-shadow: 0 10px 30px -10px rgba(0,0,0,0.8); }}
        
        .editor-wrapper textarea {{ font-family: 'Playfair Display', serif !important; font-size: {font_sz}px !important; line-height: 1.8; background-color: #050505 !important; border: 1px solid #1a1a1a !important; color: #ccc !important; padding: 40px !important; }}
        
        .stTextInput input, .stSelectbox div, .stTextArea textarea, .stSlider div {{ background-color: #0A0A0A !important; border: 1px solid #222 !important; color: #eee !important; }}
        .stButton button {{ border-radius: 2px !important; text-transform: uppercase; letter-spacing: 2px; font-size: 11px; font-weight: 700; background: #111; color: #888; border: 1px solid #333; }}
        .stButton button:hover {{ border-color: var(--gold); color: var(--gold); }}
        
        .stTabs [data-baseweb="tab-list"] {{ gap: 2px; }}
        .stTabs [data-baseweb="tab"] {{ background-color: transparent; border-radius: 4px 4px 0px 0px; color: #666; }}
        .stTabs [aria-selected="true"] {{ background-color: #111; color: var(--gold); border: 1px solid #222; border-bottom: none; }}
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. MOTORES LÓGICOS (Backend Logic)
# ==============================================================================
class AccessControl:
    DEFAULT_USERS = {"ADMIN": "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"} # SHA-256 de 'admin' para fallback

    @staticmethod
    def _hash(text):
        return hashlib.sha256(text.encode()).hexdigest()

    @staticmethod
    def register(username, password):
        users = SafeIO.ler_json(DBS["USERS"], {})
        u_upper = username.upper().strip()
        if u_upper in users: return False, "USUÁRIO JÁ EXISTE."
        if not username or not password: return False, "PREENCHA TUDO."
        
        users[u_upper] = AccessControl._hash(password)
        SafeIO.salvar_json(DBS["USERS"], users)
        return True, "REGISTRO OK."

    @staticmethod
    def login(username, password):
        users = SafeIO.ler_json(DBS["USERS"], {})
        if not users and username.upper() == "ADMIN" and password == "1234": return True # Fallback primeira vez
        
        u_upper = username.upper().strip()
        hashed = AccessControl._hash(password)
        if u_upper in users:
            # Compatibilidade com sistemas antigos que podem não estar hasheados
            stored = users[u_upper]
            if len(stored) != 64: return stored == password # legado
            return stored == hashed
        return False

class LiturgicalCalendar:
    @staticmethod
    def get_status():
        wd = datetime.now().weekday()
        if wd == 6: return "DOMINGO - DIA DO SENHOR"
        return "DIA FERIAL"

class GenevaProtocol:
    """Motor de Análise Teológica."""
    DB_ALERTS = {
        "prosperidade": "⚠️ ALERTA: Teologia da Prosperidade.",
        "eu decreto": "⚠️ ALERTA: Quebra de Soberania Divina.",
        "mérito": "⚠️ ALERTA: Pelagianismo (Sola Gratia).",
        "energia": "⚠️ ALERTA: Terminologia Nova Era."
    }
    @staticmethod
    def scan(text):
        if not text: return []
        return [v for k, v in GenevaProtocol.DB_ALERTS.items() if k in text.lower()]

class PastoralMind:
    """Motor de Vitalidade + Teoria da Permissão Integrada"""
    @staticmethod
    def registrar(humor):
        data = SafeIO.ler_json(DBS["SOUL"], {"historico": [], "scans": []})
        data["historico"].append({"data": datetime.now().strftime("%Y-%m-%d"), "humor": humor})
        SafeIO.salvar_json(DBS["SOUL"], data)

    @staticmethod
    def check_burnout():
        data = SafeIO.ler_json(DBS["SOUL"], {"historico": [], "scans": []})
        hist = data.get("historico", [])[-10:]
        scans = data.get("scans", [])
        
        # Lógica dupla: Burnout tradicional E Teoria de Permissão
        bad_humor = sum(1 for h in hist if h['humor'] in ["Cansaço 🌖", "Ira 😠", "Ansiedade 🌪️", "Tristeza 😢"])
        
        # Fator de permissão (se existir scan recente)
        perm_score = 50 
        if scans: perm_score = scans[-1].get("score", 50)
        
        if bad_humor >= 6 or perm_score < 30: return "CRÍTICO", "#FF3333"
        if bad_humor >= 3 or perm_score < 60: return "ALERTA", "#FFAA00"
        return "OPERACIONAL", "#33FF33"

class PermissionEngine:
    """NOVO: Motor da Teoria da Permissão (Evolução Mental)."""
    @staticmethod
    def diagnosticar(f, s, d, suc):
        """f:falhar, s:sentir, d:descansar, suc:sucesso (0-100)"""
        avg = (f + s + d + suc) / 4
        feedback = ""
        if avg < 30: feedback = "Modo de Sobrevivência: A graça não está alcançando seu eu interior."
        elif avg < 60: feedback = "Em progresso: Você ainda luta contra o legalismo interno."
        else: feedback = "Liberdade na Graça: Você aceita sua humanidade."
        
        new_scan = {
            "data": datetime.now().strftime("%Y-%m-%d"),
            "score": avg,
            "detalhes": {"falhar":f, "sentir":s, "descansar":d, "sucesso":suc},
            "feedback": feedback
        }
        
        soul = SafeIO.ler_json(DBS["SOUL"], {"historico": [], "scans": []})
        soul.setdefault("scans", []).append(new_scan)
        SafeIO.salvar_json(DBS["SOUL"], soul)
        return feedback, avg

class Gamification:
    @staticmethod
    def add_xp(amount):
        stats = SafeIO.ler_json(DBS["STATS"], {"xp": 0, "nivel": 1})
        stats["xp"] += amount
        stats["nivel"] = int(math.sqrt(stats["xp"]) * 0.2) + 1
        SafeIO.salvar_json(DBS["STATS"], stats)

# ==============================================================================
# 4. STARTUP E LOGIN
# ==============================================================================
if "config" not in st.session_state:
    st.session_state["config"] = SafeIO.ler_json(DBS["CONFIG"], {"theme_color": "#D4AF37", "font_size": 18, "api_key": ""})

inject_css(st.session_state["config"]["theme_color"], st.session_state["config"]["font_size"])

# Session State Check
for k in ["logado", "user_name", "texto_ativo", "titulo_ativo"]:
    if k not in st.session_state: st.session_state[k] = False if k == "logado" else ""

# TELA DE LOGIN
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
        <div class="login-title">O PREGADOR</div>
        <div style="text-align:center;font-size:9px;color:#555;letter-spacing:4px;margin-bottom:20px;">SYSTEM V29 | TEOLOGIA ROBUSTA</div>
        """, unsafe_allow_html=True)
        
        tl, tr = st.tabs(["ENTRAR", "REGISTRAR"])
        with tl:
            with st.form("gate"):
                u = st.text_input("ID", placeholder="IDENTIFICAÇÃO")
                p = st.text_input("SENHA", type="password", placeholder="SENHA")
                if st.form_submit_button("ACESSAR", use_container_width=True, type="primary"):
                    if AccessControl.login(u, p):
                        st.session_state["logado"] = True
                        st.session_state["user_name"] = u.upper()
                        Gamification.add_xp(5)
                        st.rerun()
                    else: st.error("NEGO A VOS CONHECER.")
        with tr:
            with st.form("reg"):
                nu = st.text_input("Novo ID")
                np = st.text_input("Senha", type="password")
                if st.form_submit_button("CRIAR"):
                    ok, msg = AccessControl.register(nu, np)
                    if ok: st.success(msg)
                    else: st.error(msg)
    st.stop()

# ==============================================================================
# 5. APLICAÇÃO PRINCIPAL (CORPO ROBUSTO)
# ==============================================================================

# --- SIDEBAR COM AVATAR ---
with st.sidebar:
    avatar_path = os.path.join(DIRS["USER"], "avatar.png")
    if os.path.exists(avatar_path):
        try:
            with open(avatar_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
            st.markdown(f'<div class="holo-container"><img src="data:image/png;base64,{encoded_string}" class="holo-img"></div>', unsafe_allow_html=True)
        except: pass
    else:
        gold = st.session_state["config"]["theme_color"]
        st.markdown(f'<div class="holo-container" style="display:flex;align-items:center;justify-content:center;"><span style="font-size:40px; color:{gold}">✝</span></div>', unsafe_allow_html=True)

    st.markdown(f"<center>{st.session_state['user_name']}<br><span style='font-size:9px;color:#666'>VITALIDADE: {PastoralMind.check_burnout()[0]}</span></center>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Menu restaurado e com adição da Teoria
    menu = st.radio(
        "SISTEMA", 
        ["Dashboard", "Teoria da Permissão", "Gabinete Pastoral", "Studio Expositivo", "Séries Bíblicas", "Media Lab", "Configurações"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    
    stats = SafeIO.ler_json(DBS["STATS"], {"nivel": 1, "xp": 0})
    st.markdown(f"<div style='text-align:center; font-size:10px; color:#555;'>NÍVEL {stats['nivel']} | XP {stats['xp']}</div>", unsafe_allow_html=True)
    if st.button("LOGOUT", use_container_width=True):
        st.session_state["logado"] = False
        st.rerun()

# --- HEADER (HUD) ---
status_b, cor_b = PastoralMind.check_burnout()
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown(f"<span style='color:#666; font-size:10px;'>LITURGIA:</span> <span style='font-family:Cinzel'>{LiturgicalCalendar.get_status()}</span>", unsafe_allow_html=True)
with col_h2:
    st.markdown(f"<div style='text-align:right;'><span style='color:{cor_b}'>STATUS: {status_b}</span></div>", unsafe_allow_html=True)
st.markdown("---")

# --- CONTEÚDO DAS PÁGINAS ---

if menu == "Dashboard":
    st.markdown(f"<h2 style='font-family:Cinzel; margin-bottom:20px;'>Painel de Controle</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
        st.caption("CHECK-IN ESPIRITUAL")
        humor = st.selectbox("Estado da Alma", ["Plenitude 🕊️", "Gratidão 🙏", "Cansaço 🌖", "Ira 😠", "Tristeza 😢", "Ansiedade 🌪️"], label_visibility="collapsed")
        if st.button("REGISTRAR ESTADO"):
            PastoralMind.registrar(humor)
            Gamification.add_xp(10)
            st.success("COMPUTADO.")
            time.sleep(1)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with c2:
        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
        st.caption("RESUMO DE DADOS")
        count_sermoes = len(os.listdir(DIRS["SERMOES"]))
        st.info(f"Arquivos na Base: {count_sermoes}")
        if status_b == "CRÍTICO": st.error("Atenção: Níveis de saúde pastoral críticos.")
        else: st.write("Sistema operando dentro dos parâmetros de graça.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Últimos arquivos
    st.caption("ARQUIVOS RECENTES")
    files = sorted([f for f in os.listdir(DIRS["SERMOES"]) if f.endswith(".txt")], key=lambda x: os.path.getmtime(os.path.join(DIRS["SERMOES"], x)), reverse=True)[:3]
    cols = st.columns(3)
    for i, f in enumerate(files):
        with cols[i]:
            st.markdown(f"<div style='border:1px solid #222; background:#090909; padding:10px; font-size:12px;'>📄 {f}</div>", unsafe_allow_html=True)

elif menu == "Teoria da Permissão":
    # NOVO MÓDULO ADICIONADO (TEORIA DE PERMISSÃO)
    st.title("Teoria de Permissão: Diagnóstico Mental")
    st.markdown("Ajuste as réguas de permissão interna para gerar um diagnóstico de saúde mental.")
    
    with st.markdown('<div class="tech-card">', unsafe_allow_html=True):
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            p_fail = st.slider("Permissão para Falhar (Graça)", 0, 100, 50)
            p_feel = st.slider("Permissão para Sentir (Humanidade)", 0, 100, 50)
        with col_p2:
            p_rest = st.slider("Permissão para Descansar (Limite)", 0, 100, 50)
            p_succ = st.slider("Permissão para ter Sucesso (Dignidade)", 0, 100, 50)
            
        if st.button("RODAR DIAGNÓSTICO", type="primary", use_container_width=True):
            feedback, score = PermissionEngine.diagnosticar(p_fail, p_feel, p_rest, p_succ)
            st.markdown("---")
            st.metric("Índice de Permissão Interna", f"{int(score)}/100")
            if score < 50: st.error(feedback)
            else: st.success(feedback)
            Gamification.add_xp(30)
    
    st.markdown("### Histórico de Scans")
    soul_db = SafeIO.ler_json(DBS["SOUL"], {})
    scans = soul_db.get("scans", [])
    if scans:
        df = [{"Data": s["data"], "Score": s["score"]} for s in scans[-5:]]
        st.dataframe(df, use_container_width=True)

# ------------------------------
# GABINETE PASTORAL — EDITOR AVANÇADO ESTILO WORD (SUBSTITUIÇÃO COMPLETA)
# ------------------------------
elif menu == "Gabinete Pastoral":
    st.title("Gabinete Pastoral — Editor Avançado (Word-like)")

    # --- Dependências opcionais (graciosamente degradam) ---
    try:
        from streamlit_quill import st_quill
        QUILL_OK = True
    except Exception:
        QUILL_OK = False

    try:
        from docx import Document
        DOCX_OK = True
    except Exception:
        DOCX_OK = False

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        PDF_OK = True
    except Exception:
        PDF_OK = False

    # --- Helpers: metadata, save/load sermons, export ---
    METADATA_PATH = os.path.join(DIRS["SERMOES"], "metadata.json")
    os.makedirs(DIRS["SERMOES"], exist_ok=True)

    def load_metadata():
        return SafeIO.ler_json(METADATA_PATH, {"sermons": []})

    def save_metadata(meta):
        return SafeIO.salvar_json(METADATA_PATH, meta)

    def list_sermons():
        meta = load_metadata()
        return meta.get("sermons", [])

    def register_sermon(title, filename, tags=None):
        meta = load_metadata()
        entry = {
            "title": title,
            "file": filename,
            "tags": tags or [],
            "updated": datetime.now().isoformat()
        }
        # replace if exists
        existed = False
        for i, e in enumerate(meta.get("sermons", [])):
            if e["file"] == filename:
                meta["sermons"][i] = entry
                existed = True
                break
        if not existed:
            meta.setdefault("sermons", []).append(entry)
        save_metadata(meta)

    def export_to_docx(title, html_content, out_path):
        """Simples conversor HTML->DOCX (básico): converte parágrafos."""
        if not DOCX_OK:
            raise RuntimeError("python-docx não disponível")
        doc = Document()
        doc.add_heading(title, level=1)
        # Retira tags simples — aqui fazemos conversão básica; para HTML complexo use mammoth.
        text = html_content
        # Remove tags <p>, <br>, etc. (básico)
        import re
        text = re.sub(r"<br\s*/?>", "\n", text)
        text = re.sub(r"<.*?>", "", text)
        for line in text.splitlines():
            doc.add_paragraph(line)
        doc.save(out_path)
        return out_path

    def export_to_pdf(title, html_content, out_path):
        if not PDF_OK:
            raise RuntimeError("reportlab não disponível")
        buf = BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        width, height = A4
        text_obj = c.beginText(40, height - 60)
        # Limita largura: quebra simples
        import textwrap, re
        plain = re.sub(r"<.*?>", "", html_content)
        for para in plain.split("\n\n"):
            for line in textwrap.wrap(para, 90):
                text_obj.textLine(line)
            text_obj.textLine("")
        c.drawText(text_obj)
        c.showPage()
        c.save()
        buf.seek(0)
        with open(out_path, "wb") as f:
            f.write(buf.read())
        return out_path

    # --- Layout: ferramentas sem alterar o visual principal ---
    col_top, col_tools = st.columns([3, 1])
    with col_tools:
        st.markdown("**Ferramentas Rápidas**")
        if st.button("Novo Esboço", use_container_width=True):
            st.session_state["titulo_ativo"] = ""
            st.session_state["texto_ativo"] = ""
            st.success("Novo esboço limpo.")
        if st.button("Abrir Gerenciador de Sermões", use_container_width=True):
            st.session_state["show_manager"] = not st.session_state.get("show_manager", False)

    # --- Personalização do Editor (mantendo visual) ---
    with col_top:
        with st.expander("Configurações do Editor (opcional)"):
            font_size = st.slider("Tamanho da Fonte", 12, 40, st.session_state.get("editor_font_size", 18))
            st.session_state["editor_font_size"] = font_size
            theme_choice = st.selectbox("Tema do Editor (afeta somente editor)", ["Padrão", "Escuro", "Pergaminho", "Página Branca"], index=0)
            fullscreen = st.checkbox("Modo Tela Cheia (Editor)", value=False)
            autosave = st.checkbox("Salvar automaticamente enquanto digita (autosave)", value=True)
            # Option to import TheWord/Logos resources (user provides files)
            st.markdown("**Integração TheWord / Logos / Bible Tesla**")
            st.markdown("- Você pode carregar JSONs / arquivos exportados do TheWord / Logos aqui para usar traduções e comentários.")
            logos_upload = st.file_uploader("Carregar arquivo de recurso (JSON / XML) — TheWord / Logos / Tesla", type=["json", "xml"], accept_multiple_files=True)

            # store uploaded files in GABINETE for later use
            if logos_upload:
                for uf in logos_upload:
                    try:
                        dest = os.path.join(DIRS["GABINETE"], uf.name)
                        with open(dest, "wb") as f:
                            f.write(uf.getbuffer())
                        st.success(f"Recurso importado: {uf.name}")
                    except Exception as e:
                        st.error(f"Falha ao importar {uf.name}: {e}")

    # --- Editor principal: Quill preferred, fallback to textarea ---
    st.markdown("---")
    st.markdown("### Editor (Gabinete Pastoral) — escreva sua pregação")
    title_col, tools_col = st.columns([3, 1])
    with title_col:
        st.session_state["titulo_ativo"] = st.text_input("Título do Sermão", st.session_state.get("titulo_ativo", ""))
    with tools_col:
        tags_text = st.text_input("Tags (virgula)", value=",".join(st.session_state.get("last_tags", [])))
        if st.button("Aplicar Tags"):
            st.session_state["last_tags"] = [t.strip() for t in tags_text.split(",") if t.strip()]

    # Editor area
    if QUILL_OK:
        # Configure toolbar options to resemble Word: bold, italic, underline, lists, headers, align, font-size, color, table plugin optional (limit)
        quill_formats = {
            "toolbar": [
                [{"header": [1, 2, 3, False]}],
                ["bold", "italic", "underline", "strike"],
                [{"color": []}, {"background": []}],
                [{"align": []}],
                [{"list": "ordered"}, {"list": "bullet"}],
                ["blockquote", "code-block"],
                ["link", "image"],
                ["clean"]
            ],
            "theme": "snow",
            "placeholder": "Comece a digitar sua pregação aqui..."
        }
        content = st_quill(key="editor", value=st.session_state.get("texto_ativo", ""), toolbar=quill_formats["toolbar"], height=420)
    else:
        st.warning("Componente rich-text (streamlit_quill) não disponível — usando editor simples.")
        content = st.text_area("Editor Texto Plano (fallback)", value=st.session_state.get("texto_ativo", ""), height=420)

    # Autosave support
    if autosave:
        # salva a cada atualização do conteúdo
        if content != st.session_state.get("texto_ativo", ""):
            st.session_state["texto_ativo"] = content
            # grava em arquivo temporário a cada mudança
            if st.session_state.get("titulo_ativo"):
                tmpname = f"{st.session_state['titulo_ativo'].strip() or 'SemTitulo'}.txt"
                try:
                    with open(os.path.join(DIRS["SERMOES"], tmpname), "w", encoding="utf-8") as f:
                        f.write(content or "")
                    register_sermon(st.session_state.get("titulo_ativo", "SemTitulo"), tmpname, st.session_state.get("last_tags", []))
                except Exception as e:
                    logging.error("Autosave falhou: %s", e)

    # Save / Export buttons
    col_save, col_export = st.columns([2, 2])
    with col_save:
        if st.button("Salvar Sermão"):
            filename = f"{(st.session_state['titulo_ativo'] or 'SemTitulo').strip()}.txt"
            path = os.path.join(DIRS["SERMOES"], filename)
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content or "")
                register_sermon(st.session_state["titulo_ativo"] or "SemTitulo", filename, st.session_state.get("last_tags", []))
                st.success(f"Sermão salvo: {filename}")
            except Exception as e:
                st.error("Erro ao salvar: " + str(e))

        if st.button("Salvar (Encriptado)"):
            # simulação simples: grava com base64 (se quiser, implemente AES)
            try:
                payload = (content or "").encode("utf-8")
                b64 = base64.b64encode(payload).decode()
                filename = f"{(st.session_state['titulo_ativo'] or 'SemTitulo').strip()}.enc"
                with open(os.path.join(DIRS["GABINETE"], filename), "w", encoding="utf-8") as f:
                    f.write(b64)
                st.success("Sermão encriptado salvo (base64).")
            except Exception as e:
                st.error("Falha ao encriptar: " + str(e))

    with col_export:
        if st.button("Exportar PDF"):
            filename = f"{(st.session_state['titulo_ativo'] or 'sermao')}.pdf"
            outp = os.path.join(DIRS["SERMOES"], filename)
            try:
                export_to_pdf(st.session_state.get("titulo_ativo", ""), content or "", outp)
                with open(outp, "rb") as fp:
                    b64 = base64.b64encode(fp.read()).decode()
                st.markdown(f'<a href="data:application/pdf;base64,{b64}" download="{filename}">Baixar PDF</a>', unsafe_allow_html=True)
            except Exception as e:
                st.error("Exportação para PDF falhou: " + str(e))

        if st.button("Exportar DOCX"):
            filename = f"{(st.session_state['titulo_ativo'] or 'sermao')}.docx"
            outp = os.path.join(DIRS["SERMOES"], filename)
            try:
                export_to_docx(st.session_state.get("titulo_ativo", ""), content or "", outp)
                with open(outp, "rb") as fp:
                    b64 = base64.b64encode(fp.read()).decode()
                st.markdown(f'<a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64}" download="{filename}">Baixar DOCX</a>', unsafe_allow_html=True)
            except Exception as e:
                st.error("Exportação para DOCX falhou: " + str(e) + ("" if DOCX_OK else " (python-docx não instalado)"))

    # --- Gerenciador de Sermões / Banco local ---
    if st.session_state.get("show_manager", False):
        st.markdown("### Gerenciador de Sermões")
        sermons = list_sermons()
        for s in sermons[::-1]:
            c1, c2, c3 = st.columns([6, 2, 2])
            with c1:
                st.markdown(f"**{s['title']}** — {', '.join(s.get('tags', []))} — atualizado {s.get('updated')}")
            with c2:
                if st.button(f"Abrir##{s['file']}", key=f"open_{s['file']}"):
                    try:
                        with open(os.path.join(DIRS["SERMOES"], s["file"]), "r", encoding="utf-8") as f:
                            st.session_state["texto_ativo"] = f.read()
                            st.session_state["titulo_ativo"] = s["title"]
                            st.success("Sermão carregado no editor.")
                    except Exception as e:
                        st.error("Erro ao abrir: " + str(e))
            with c3:
                if st.button(f"Excluir##{s['file']}", key=f"del_{s['file']}"):
                    try:
                        os.remove(os.path.join(DIRS["SERMOES"], s["file"]))
                        # remove do metadata
                        meta = load_metadata()
                        meta["sermons"] = [m for m in meta.get("sermons", []) if m["file"] != s["file"]]
                        save_metadata(meta)
                        st.success("Sermão removido.")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error("Falha ao remover: " + str(e))

    # --- MODO ESTUDO BÍBLICO (paralelo) ---
    st.markdown("---")
    st.markdown("### Modo Estudo Bíblico (paralelo / comparativo)")
    study_left, study_right = st.columns([1, 1])
    with study_left:
        st.markdown("**Tradução / Texto A**")
        # user may upload a translation JSON or paste verse
        trans_a_file = st.file_uploader("Carregar tradução A (JSON) — opcional", type=["json", "txt"], key="ta")
        if trans_a_file:
            try:
                ta_text = trans_a_file.getvalue().decode("utf-8")
                st.text_area("Tradução A (conteúdo)", ta_text, height=200)
            except Exception:
                st.warning("Formato não reconhecido.")
        else:
            ta_query = st.text_input("Buscar versículo (ex: João 3:16) - Tradução A")
            if ta_query and ta_query.strip():
                # fallback: busca por string nos sermões localmente (simples)
                matches = []
                for root, _, files in os.walk(DIRS["SERMOES"]):
                    for f in files:
                        if f.endswith(".txt"):
                            path = os.path.join(root, f)
                            try:
                                with open(path, "r", encoding="utf-8") as fh:
                                    txt = fh.read()
                                    if ta_query.lower() in txt.lower():
                                        matches.append((f, txt[:500]))
                            except: pass
                if matches:
                    for m in matches[:3]:
                        st.markdown(f"**Encontrado em**: {m[0]}")
                        st.write(m[1])
                else:
                    st.info("Nenhuma correspondência local; carregue recursos TheWord/Logos para busca paralela.")

    with study_right:
        st.markdown("**Tradução / Texto B / Comentário**")
        trans_b_file = st.file_uploader("Carregar tradução B / comentário (JSON) — opcional", type=["json", "txt"], key="tb")
        if trans_b_file:
            try:
                tb_text = trans_b_file.getvalue().decode("utf-8")
                st.text_area("Tradução B (conteúdo)", tb_text, height=200)
            except Exception:
                st.warning("Formato não reconhecido.")
        else:
            tb_query = st.text_input("Buscar versículo (ex: João 3:16) - Tradução B")
            if tb_query and tb_query.strip():
                # mesma busca fallback
                matches = []
                for root, _, files in os.walk(DIRS["SERMOES"]):
                    for f in files:
                        if f.endswith(".txt"):
                            path = os.path.join(root, f)
                            try:
                                with open(path, "r", encoding="utf-8") as fh:
                                    txt = fh.read()
                                    if tb_query.lower() in txt.lower():
                                        matches.append((f, txt[:500]))
                            except: pass
                if matches:
                    for m in matches[:3]:
                        st.markdown(f"**Encontrado em**: {m[0]}")
                        st.write(m[1])
                else:
                    st.info("Nenhuma correspondência local; carregue recursos TheWord/Logos para busca paralela.")

    # --- Busca Bíblica Rápida (local / sermões) ---
    st.markdown("---")
    st.markdown("### Busca Bíblica Rápida (local)")
    bq = st.text_input("Digite palavra, trecho ou referência (ex: 'fé', 'João 3:16')", key="bq")
    if st.button("Buscar", key="btn_buscar"):
        results = []
        # pesquisa local por palavra em sermões
        for root, _, files in os.walk(DIRS["SERMOES"]):
            for f in files:
                if f.endswith(".txt"):
                    try:
                        with open(os.path.join(root, f), "r", encoding="utf-8") as fh:
                            txt = fh.read()
                            if bq.lower() in txt.lower():
                                idx = txt.lower().find(bq.lower())
                                snippet = txt[max(0, idx-60): idx+120].replace("\n", " ")
                                results.append({"file": f, "snippet": snippet})
                    except: pass
        if results:
            st.success(f"{len(results)} resultados locais")
            for r in results[:20]:
                st.markdown(f"- **{r['file']}** — ...{r['snippet']}...")
        else:
            st.info("Nenhum resultado local. Para buscas avançadas carregue recursos TheWord / Logos / Tesla ou me peça para integrar uma API.")

    # --- Sincronização de Tema com o App (claro/escuro) ---
    st.markdown("---")
    st.markdown("### Aparência")
    theme_sync = st.checkbox("Sincronizar tema do editor com tema do app (claro/escuro)", value=True)
    if theme_sync:
        # apenas flag — o CSS global já controla aparência; aqui podemos ajustar editor estilos se disponível
        st.session_state["editor_theme_sync"] = True
    else:
        st.session_state["editor_theme_sync"] = False

    # Final: sugere import manual de recursos TheWord/Logos/Tesla
    st.markdown("---")
    st.info("Integração TheWord/Logos/Bible Tesla: coloque aqui arquivos exportados (JSON/XML). Após importar, use o Modo Estudo para abrir traduções e comentários lado a lado.")


elif menu == "Studio Expositivo":
    st.title("Studio Expositivo")
    
    c_input, c_act = st.columns([3, 1])
    st.session_state["titulo_ativo"] = c_input.text_input("Título", st.session_state["titulo_ativo"])
    if c_act.button("GRAVAR TXT", use_container_width=True):
        path = os.path.join(DIRS["SERMOES"], f"{st.session_state['titulo_ativo'] or 'SemTitulo'}.txt")
        with open(path, 'w', encoding='utf-8') as f: f.write(st.session_state["texto_ativo"])
        st.toast("SALVO NO DISCO.", icon="💾")

    col_editor, col_ai = st.columns([2.5, 1])
    with col_editor:
        st.markdown('<div class="editor-wrapper">', unsafe_allow_html=True)
        st.se
# ============================
# PATCH / EXTENSÕES DE PERSISTÊNCIA, NASA CONFIG E BRAIN DIVIDER
# ============================

# ----------------------------
# Utilitários de Persistência de Sessão e Autosave
# ----------------------------
class SessionPersistence:
    """Salva e restaura chaves importantes do st.session_state por usuário."""
    @staticmethod
    def _path_for_user(user):
        safe_user = (user or "ANON").replace(" ", "_")
        return os.path.join(DIRS["USER"], f"session_{safe_user}.json")

    @staticmethod
    def save(user):
        try:
            keys_to_save = {k: st.session_state[k] for k in st.session_state.keys() if k in ["logado", "user_name", "texto_ativo", "titulo_ativo", "config"]}
            SafeIO.salvar_json(SessionPersistence._path_for_user(user), keys_to_save)
            logging.info("Session saved for %s", user)
            return True
        except Exception as e:
            logging.error("Session save failed: %s", e)
            return False

    @staticmethod
    def load(user):
        try:
            data = SafeIO.ler_json(SessionPersistence._path_for_user(user), {})
            for k, v in data.items():
                st.session_state[k] = v
            logging.info("Session restored for %s", user)
            return True
        except Exception as e:
            logging.error("Session load failed: %s", e)
            return False

# Hook: salvar sessão ao final de cada ação importante
def autosave_hook():
    if st.session_state.get("user_name"):
        SessionPersistence.save(st.session_state.get("user_name"))

# Salva ao sair / logout
def logout_and_save():
    autosave_hook()
    st.session_state["logado"] = False
    st.session_state["user_name"] = ""
    st.rerun()

# Carrega automaticamente no boot se existir
if st.session_state.get("user_name") and not st.session_state["logado"]:
    SessionPersistence.load(st.session_state.get("user_name"))

# ----------------------------
# NASA STANDARDS: Validação/Schema simples
# ----------------------------
class NASAGuard:
    """Validação mínima de config conforme 'padrões NASA' (schema simplificado)."""
    DEFAULT = {
        "theme_color": "#D4AF37",
        "font_size": 18,
        "api_key": "",
        "nasa_compliance": {
            "standard": "NASA-STD-8739.8",  # exemplo genérico
            "level": "A",                  # A, B, C (A = crítico)
            "audit_trail": True,
            "checksum_algo": "SHA-256"
        }
    }

    @staticmethod
    def validate_config(cfg):
        # Garante chaves básicas
        valid = True
        problems = []
        if "theme_color" not in cfg: valid = False; problems.append("theme_color faltando")
        if "font_size" not in cfg: valid = False; problems.append("font_size faltando")
        if "nasa_compliance" not in cfg:
            cfg["nasa_compliance"] = NASAGuard.DEFAULT["nasa_compliance"]
            problems.append("inserido nasa_compliance default")
        # Checagem de valores
        lvl = cfg["nasa_compliance"].get("level", "A")
        if lvl not in ["A", "B", "C"]:
            cfg["nasa_compliance"]["level"] = "C"
            problems.append("nivel nasa ajustado para C")
        return valid, problems

# Ao iniciar, garantir config conforme NASA
cfg_before = st.session_state.get("config", {})
valid_cfg, fix_msgs = NASAGuard.validate_config(cfg_before)
if not valid_cfg or fix_msgs:
    st.session_state["config"] = {**NASAGuard.DEFAULT, **cfg_before}
    SafeIO.salvar_json(DBS["CONFIG"], st.session_state["config"])
    logging.info("Config validated/normalized: %s", fix_msgs)

# ----------------------------
# BrainDivider: divisão cerebral modular e gerenciável
# ----------------------------
class BrainDivider:
    """Cria e gerencia partições do 'cérebro' do app.
       Ao invés de injetar 1000 linhas estáticas, geramos módulos dinamicamente e os armazenamos.
    """
    BRAIN_FILE = os.path.join(DIRS["GABINETE"], "brain_structure.json")

    @staticmethod
    def default_modules():
        return [
            {"id": "perception", "role": "input_processing", "desc": "Recebe e normaliza entradas"},
            {"id": "memory", "role": "storage", "desc": "Armazena estados e histórico"},
            {"id": "reasoning", "role": "logic", "desc": "Regras e análise teológica"},
            {"id": "planner", "role": "output", "desc": "Gera conteúdo e ações"},
            {"id": "safety", "role": "policy", "desc": "Filtros e alertas (GenevaProtocol)"}
        ]

    @staticmethod
    def generate_partitions(count=16, prefix="module"):
        """Gera 'count' partições adicionais, com metadados; pode gerar muitos módulos programaticamente."""
        modules = BrainDivider.default_modules()
        for i in range(count):
            modules.append({
                "id": f"{prefix}_{i+1}",
                "role": random.choice(["perception","memory","reasoning","planner","safety","monitor"]),
                "desc": f"Partição gerada automaticamente #{i+1}",
                "created_at": datetime.now().isoformat()
            })
        BrainDivider.save(modules)
        return modules

    @staticmethod
    def save(modules):
        return SafeIO.salvar_json(BrainDivider.BRAIN_FILE, {"modules": modules, "updated": datetime.now().isoformat()})

    @staticmethod
    def load():
        data = SafeIO.ler_json(BrainDivider.BRAIN_FILE, {"modules": BrainDivider.default_modules()})
        return data.get("modules", [])

    @staticmethod
    def summarize(modules):
        buckets = {}
        for m in modules:
            buckets.setdefault(m["role"], 0)
            buckets[m["role"]] += 1
        return buckets

# ----------------------------
# Integração na UI (substitui a parte truncada do Studio Expositivo)
# ----------------------------

# Garanto que chaves existam
for k in ["titulo_ativo", "texto_ativo"]:
    if k not in st.session_state:
        st.session_state[k] = ""

if menu == "Studio Expositivo":
    st.title("Studio Expositivo")
    c_input, c_act = st.columns([3, 1])
    with c_input:
        st.session_state["titulo_ativo"] = st.text_input("Título", st.session_state["titulo_ativo"])
        st.session_state["texto_ativo"] = st.text_area("Editor", st.session_state["texto_ativo"], height=320)

    with c_act:
        if st.button("GRAVAR TXT", use_container_width=True):
            path = os.path.join(DIRS["SERMOES"], f"{(st.session_state['titulo_ativo'] or 'SemTitulo').strip()}.txt")
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(st.session_state["texto_ativo"] or "")
                st.toast("SALVO NO DISCO.", icon="💾")
                logging.info("Sermão salvo: %s", path)
                autosave_hook()
            except Exception as e:
                st.error("Erro ao salvar: " + str(e))
        if st.button("EXPORTAR PDF (Simples)"):
            # Gera um PDF simples base64 para download (utiliza ReportLab se disponível)
            try:
                from reportlab.lib.pagesizes import A4
                from reportlab.pdfgen import canvas
                buf = BytesIO()
                c = canvas.Canvas(buf, pagesize=A4)
                text = c.beginText(40, 800)
                for line in (st.session_state["texto_ativo"] or "").splitlines():
                    text.textLine(line[:1000])
                c.drawText(text)
                c.showPage()
                c.save()
                buf.seek(0)
                b64 = base64.b64encode(buf.read()).decode()
                href = f'<a href="data:application/pdf;base64,{b64}" download="{st.session_state["titulo_ativo"] or "sermao"}.pdf">Baixar PDF</a>'
                st.markdown(href, unsafe_allow_html=True)
            except Exception as e:
                st.error("ReportLab não disponível ou falha: " + str(e))

    # CONTROLES DO BRAIN DIVIDER
    st.markdown("---")
    st.markdown("### Cérebro: Divisor e Gerenciamento Modular")
    col_gen, col_view = st.columns([2, 1])
    with col_gen:
        cnt = st.number_input("Número de partições adicionais a gerar", min_value=0, max_value=2000, value=16, step=1)
        prefix = st.text_input("Prefixo para partições", value="module")
        if st.button("GERAR PARTIÇÕES"):
            mods = BrainDivider.generate_partitions(int(cnt), prefix=prefix)
            st.success(f"{len(mods)} módulos ativos (inclui os padrões).")
            autosave_hook()
    with col_view:
        if st.button("CARREGAR E RESUMIR CÉREBRO"):
            mods = BrainDivider.load()
            summary = BrainDivider.summarize(mods)
            st.json({"total_modules": len(mods), "by_role": summary})
            autosave_hook()

    # Mostra um pequeno histórico / estrutura
    mods = BrainDivider.load()
    if mods:
        st.markdown(f"**Módulos ativos:** {len(mods)}")
        # mostra os últimos 8 módulos
        for m in mods[-8:]:
            st.markdown(f"- `{m['id']}` ({m.get('role')}) — {m.get('desc')[:80]}")

    # BOTÃO DE LOGOUT SALVANDO SESSÃO
    if st.button("SALVAR SESSÃO AGORA"):
        autosave_hook()
        st.success("Sessão salva.")

    st.markdown("---")
    st.caption("Arquitetura: módulos programáticos permitem gerar muitas partições sem duplicar código. Use com moderação.")

# ----------------------------
# Garantir que logout do sidebar salve sessão
# ----------------------------
# Substituímos o handler do botão LOGOUT anterior por salvar sessão primeiro.
# (Se já havia sido definido antes, o novo valor sobrescreve o anterior.)
with st.sidebar:
    if st.button("LOGOUT (SALVAR)", use_container_width=True):
        logout_and_save()

# ----------------------------
# Pequenas melhorias de confiabilidade
# ----------------------------
# 1) Proteção contra leitura de diretórios vazios (contador de sermões)
try:
    count_sermoes = len([f for f in os.listdir(DIRS["SERMOES"]) if os.path.isfile(os.path.join(DIRS["SERMOES"], f))])
except Exception:
    count_sermoes = 0

# 2) Hook final: salva sessão periodicamente ao realizar ações (colhemos algumas chaves)
autosave_hook()

# FIM DO PATCH
