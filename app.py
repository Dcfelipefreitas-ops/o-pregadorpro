# -*- coding: utf-8 -*-
"""
===============================================================================
 O PREGADOR | SYSTEM OMEGA – ACESSO LIVRE (SEM LOGIN / SEM SENHA)
===============================================================================
"""

# ==============================================================================
# 00. IMPORTAÇÕES BÁSICAS
# ==============================================================================
import streamlit as st
import os
import json
import logging
from datetime import datetime, timezone

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
# OBS: estes módulos (app_modules/core.py, visual.py, dashboard.py) não foram
# enviados nesta conversa, então não pude revisar o conteúdo deles. O import
# de "AccessGate" foi removido abaixo porque o login deixou de existir — se
# app_modules/auth.py só era usado para isso, ele nem precisa mais ser
# importado aqui.
from app_modules.core import (
    genesis_filesystem_integrity_check,
    DB_FILES,
    _read_json_safe,
    _write_json_atomic,
    DIRECTORY_STRUCTURE,
)
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
            # CORREÇÃO: abrir o arquivo com "with" para garantir que ele
            # seja fechado corretamente (antes o handle ficava aberto).
            with open(f, "r", encoding="utf-8") as fh:
                return json.load(fh)
        data = {
            "user": user,
            "calling": "",
            "tradition": "Reformada",
            # CORREÇÃO: datetime.utcnow() está depreciado a partir do
            # Python 3.12. Usamos datetime.now(timezone.utc) no lugar.
            "created": datetime.now(timezone.utc).isoformat(),
            "history": [],
        }
        self.save(user, data)
        return data

    def save(self, user, data):
        with open(
            os.path.join(self.PATH, f"{user}.json"), "w", encoding="utf-8"
        ) as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)


IDENTITY_CORE = SpiritualIdentity()

# ==============================================================================
# 07. ACESSO LIVRE — SEM LOGIN, SEM SENHA
# ==============================================================================
# Antes o sistema exigia login/registro com senha (hash sha256) antes de
# liberar o app. Isso foi removido por completo. Agora o app entra direto
# em um usuário padrão local, sem tela de autenticação.
DEFAULT_USER = "PASTOR"

if "current_user" not in st.session_state:
    st.session_state["current_user"] = DEFAULT_USER
    IDENTITY_CORE.load(DEFAULT_USER)

# ==============================================================================
# 08. SIDEBAR
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
            "Configurações",
        ],
    )

# ==============================================================================
# 09. ROTAS PRINCIPAIS
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
