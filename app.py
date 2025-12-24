# -*- coding: utf-8 -*-
"""
===============================================================================
 O PREGADOR | SYSTEM OMEGA – BUILD ESTÁVEL (LOGIN + REGISTRO FUNCIONAL)
===============================================================================
"""

# ==============================================================================
# 00. IMPORTAÇÕES BÁSICAS
# ==============================================================================
import streamlit as st
import os
import sys
import json
import time
import hashlib
import logging
from datetime import datetime

# ==============================================================================
# 01. CONFIGURAÇÃO DA PÁGINA (VISUAL INALTERADO)
# ==============================================================================
st.set_page_config(
    page_title="O PREGADOR | SYSTEM OMEGA",
    page_icon="✝️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def inject_word_style():
    st.markdown("""
    <style>
        .main .block-container {max-width:98%; padding:1rem;}
        .ck-editor__editable {
            min-height:700px;
            background:white;
            color:black;
        }
    </style>
    """, unsafe_allow_html=True)

inject_word_style()

# ==============================================================================
# 02. PATHS PRINCIPAIS
# ==============================================================================
SYSTEM_ROOT = "Dados_Pregador_V31"
os.makedirs(SYSTEM_ROOT, exist_ok=True)

LOG_PATH = os.path.join(SYSTEM_ROOT, "logs")
os.makedirs(LOG_PATH, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_PATH, "system.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ==============================================================================
# 03. IMPORTAÇÃO DOS MÓDULOS DO SISTEMA (ORDEM CORRETA)
# ==============================================================================
from app_modules.core import (
    genesis_filesystem_integrity_check,
    DB_FILES,
    _read_json_safe,
    _write_json_atomic,
    DIRECTORY_STRUCTURE
)

from app_modules.auth import AccessGate
from app_modules.visual import inject_visual_core
from app_modules import dashboard as dashboard_module

# ==============================================================================
# 04. INICIALIZAÇÃO DO SISTEMA
# ==============================================================================
genesis_filesystem_integrity_check()
inject_visual_core()

# ==============================================================================
# 05. BLINDAGEM DO BANCO DE USUÁRIOS (SEM NameError / KeyError)
# ==============================================================================
if "USERS" not in DB_FILES:
    USERS_DB_PATH = os.path.join(SYSTEM_ROOT, "db", "users.json")
    os.makedirs(os.path.dirname(USERS_DB_PATH), exist_ok=True)
    DB_FILES["USERS"] = USERS_DB_PATH

    if not os.path.exists(USERS_DB_PATH):
        _write_json_atomic(USERS_DB_PATH, {})
        logging.warning("DB de usuários criado automaticamente.")

# ==============================================================================
# 06. IDENTIDADE ESPIRITUAL (NÚCLEO INVISÍVEL)
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
            "created": datetime.utcnow().isoformat(),
            "history": []
        }
        self.save(user, data)
        return data

    def save(self, user, data):
        json.dump(
            data,
            open(os.path.join(self.PATH, f"{user}.json"), "w", encoding="utf-8"),
            indent=2,
            ensure_ascii=False
        )

IDENTITY_CORE = SpiritualIdentity()

# ==============================================================================
# 07. CRIAÇÃO DE CONTA (FUNCIONAL)
# ==============================================================================
def create_account(username, password):
    username = username.upper().strip()

    if not username or not password:
        return False, "Usuário e senha obrigatórios."

    users = _read_json_safe(DB_FILES["USERS"], default={})

    if username in users:
        return False, "Usuário já existe."

    users[username] = {
        "password": hashlib.sha256(password.encode()).hexdigest(),
        "created": datetime.utcnow().isoformat(),
        "active": True,
        "role": "PASTOR"
    }

    _write_json_atomic(DB_FILES["USERS"], users)
    IDENTITY_CORE.load(username)

    logging.info(f"Conta criada: {username}")
    return True, "Conta criada com sucesso."

# ==============================================================================
# 08. CONTROLE DE SESSÃO
# ==============================================================================
if "session_valid" not in st.session_state:
    st.session_state["session_valid"] = False

if "current_user" not in st.session_state:
    st.session_state["current_user"] = None

# ==============================================================================
# 09. LOGIN + REGISTRO (SEM ERRO)
# ==============================================================================
if not st.session_state["session_valid"]:
    st.title("O PREGADOR – Acesso Seguro")

    tab_login, tab_register = st.tabs(["🔐 Entrar", "🆕 Criar Conta"])

    with tab_login:
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")

        if st.button("ENTRAR"):
            if AccessGate.login_check(u, p):
                st.session_state["session_valid"] = True
                st.session_state["current_user"] = u.upper()
                IDENTITY_CORE.load(u.upper())
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")

    with tab_register:
        nu = st.text_input("Novo usuário")
        np = st.text_input("Senha", type="password")
        np2 = st.text_input("Confirmar senha", type="password")

        if st.button("CRIAR CONTA"):
            if np != np2:
                st.error("As senhas não conferem.")
            else:
                ok, msg = create_account(nu, np)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

    st.stop()

# ==============================================================================
# 10. SIDEBAR
# ==============================================================================
with st.sidebar:
    st.markdown(f"### Usuário\n**{st.session_state['current_user']}**")
    app_mode = st.radio(
        "Modo",
        [
            "Dashboard & Cuidado",
            "Gabinete de Preparação",
            "Rede Ministerial",
            "Biblioteca Digital",
            "Configurações"
        ]
    )

# ==============================================================================
# 11. ROTAS PRINCIPAIS
# ==============================================================================
if app_mode == "Dashboard & Cuidado":
    dashboard_module.render_dashboard()

elif app_mode == "Gabinete de Preparação":
    st.title("📝 Gabinete Pastoral")
    st.info("Editor preservado. Núcleo espiritual ativo.")

elif app_mode == "Rede Ministerial":
    st.title("🤝 Rede Ministerial")

elif app_mode == "Biblioteca Digital":
    st.title("📚 Biblioteca Digital")

elif app_mode == "Configurações":
    st.title("⚙️ Configurações")

# ==============================================================================
# FIM DO SISTEMA
# ==============================================================================
