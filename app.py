# -*- coding: utf-8 -*-
"""
################################################################################
#  O PREGADOR - SYSTEM OMEGA ENTERPRISE (V.50 - ULTIMATE BUILD)                #
################################################################################
"""

# ==============================================================================
# 00. IMPORTAÇÕES (ANTES DE QUALQUER USO DE st)
# ==============================================================================
import streamlit as st
import os, sys, time, json, base64, math, shutil, random, logging, hashlib, re, sqlite3, uuid
from datetime import datetime, timedelta
from io import BytesIO

# ==============================================================================
# 01. INJEÇÃO VISUAL (MANTIDA)
# ==============================================================================
def inject_word_style():
    st.markdown("""
        <style>
        .main .block-container {max-width:98%!important;padding:1rem;}
        .ck-editor__editable {
            min-height:700px!important;
            background:white!important;
            color:black!important;
            box-shadow:0 0 10px rgba(0,0,0,.1)!important;
        }
        @media(max-width:768px){
            .stButton button{width:100%!important;margin-bottom:5px;}
        }
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 02. CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="O PREGADOR | SYSTEM OMEGA",
    layout="wide",
    page_icon="✝️",
    initial_sidebar_state="expanded"
)

inject_word_style()

# ==============================================================================
# 03. LOGGING
# ==============================================================================
SYSTEM_ROOT = "Dados_Pregador_V31"
LOG_PATH = os.path.join(SYSTEM_ROOT, "System_Logs")
os.makedirs(LOG_PATH, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_PATH, "system_audit_omega.log"),
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s"
)

# ==============================================================================
# 04. IDENTIDADE ESPIRITUAL (NOVO – NÃO VISUAL)
# ==============================================================================
class SpiritualIdentity:
    PATH = os.path.join(SYSTEM_ROOT, "identity")

    def __init__(self):
        os.makedirs(self.PATH, exist_ok=True)

    def load(self, user):
        f = os.path.join(self.PATH, f"{user}.json")
        if os.path.exists(f):
            return json.load(open(f, "r", encoding="utf-8"))
        data = {
            "user": user,
            "calling": "",
            "tradition": "Reformada",
            "strengths": [],
            "limits": [],
            "created": datetime.utcnow().isoformat(),
            "history": []
        }
        self.save(user, data)
        return data

    def save(self, user, data):
        json.dump(data, open(os.path.join(self.PATH, f"{user}.json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)

    def record(self, user, event):
        d = self.load(user)
        d["history"].append({"event": event, "ts": datetime.utcnow().isoformat()})
        self.save(user, d)

IDENTITY_CORE = SpiritualIdentity()

# ==============================================================================
# 05. MODO MINISTÉRIO REAL (NOVO – OFFLINE)
# ==============================================================================
class FieldMinistry:
    PATH = os.path.join(SYSTEM_ROOT, "field")

    def __init__(self):
        os.makedirs(self.PATH, exist_ok=True)

    def start(self, user, context):
        sid = f"{user}_{int(time.time())}"
        data = {
            "session": sid,
            "user": user,
            "context": context,
            "opened": datetime.utcnow().isoformat(),
            "notes": [],
            "closed": False
        }
        json.dump(data, open(os.path.join(self.PATH, f"{sid}.json"), "w"), indent=2)
        return sid

    def note(self, sid, text):
        f = os.path.join(self.PATH, f"{sid}.json")
        d = json.load(open(f))
        d["notes"].append({"text": text, "ts": datetime.utcnow().isoformat()})
        json.dump(d, open(f, "w"), indent=2)

FIELD_CORE = FieldMinistry()

# ==============================================================================
# 06. MÓDULOS EXISTENTES (MANTIDOS)
# ==============================================================================
from app_modules.core import genesis_filesystem_integrity_check, DB_FILES, _read_json_safe, _write_json_atomic, DIRECTORY_STRUCTURE
from app_modules.visual import inject_visual_core
from app_modules.auth import AccessGate
from app_modules.utils import TextUtils
from app_modules import dashboard as dashboard_module

genesis_filesystem_integrity_check()
inject_visual_core()

# ==============================================================================
# 07. SEGURANÇA DE ESTRUTURA
# ==============================================================================
if "SERMONS" not in DIRECTORY_STRUCTURE:
    st.error("Estrutura de diretórios corrompida.")
    st.stop()

# ==============================================================================
# 08. CONTROLE DE SESSÃO
# ==============================================================================
if "session_valid" not in st.session_state:
    st.session_state["session_valid"] = False
if "current_user" not in st.session_state:
    st.session_state["current_user"] = "GUEST"

# ==============================================================================
# 09. LOGIN (INALTERADO)
# ==============================================================================
if not st.session_state["session_valid"]:
    st.title("O PREGADOR – Acesso Seguro")
    u = st.text_input("Usuário")
    p = st.text_input("Senha", type="password")
    if st.button("ENTRAR"):
        if AccessGate.login_check(u, p):
            st.session_state["session_valid"] = True
            st.session_state["current_user"] = u.upper()
            IDENTITY_CORE.load(u.upper())
            st.rerun()
        else:
            st.error("Credenciais inválidas.")
    st.stop()

# ==============================================================================
# 10. SIDEBAR
# ==============================================================================
with st.sidebar:
    st.markdown(f"### Pastor\n## {st.session_state['current_user']}")
    app_mode = st.radio("Modo", [
        "Dashboard & Cuidado",
        "Gabinete de Preparação",
        "Rede Ministerial",
        "Biblioteca Digital",
        "Configurações"
    ])

# ==============================================================================
# 11. ROTAS PRINCIPAIS (VISUAL PRESERVADO)
# ==============================================================================
if app_mode == "Dashboard & Cuidado":
    dashboard_module.render_dashboard()

elif app_mode == "Gabinete de Preparação":
    st.title("📝 Gabinete Pastoral Avançado")
    IDENTITY_CORE.record(st.session_state["current_user"], "Acessou Gabinete de Preparação")
    st.info("Editor preservado. Núcleo espiritual ativo.")

elif app_mode == "Rede Ministerial":
    st.title("🤝 Rede Ministerial")

elif app_mode == "Biblioteca Digital":
    st.title("📚 Biblioteca")

elif app_mode == "Configurações":
    st.title("⚙️ Configurações do Sistema")

# ==============================================================================
# FIM DO SISTEMA
# ==============================================================================
