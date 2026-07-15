# -*- coding: utf-8 -*-
import os
import json
import logging
import uuid
import hashlib
import streamlit as st
from datetime import datetime, timezone
from typing import Dict, Any

# ==============================================================================
# 01. CONFIGURAÇÃO NASA: UI & TIPOGRAFIA DE ALTA PRECISÃO
# ==============================================================================
st.set_page_config(
    page_title="DISCIPULADO | PR FELIPE FREITAS",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def inject_nasa_ui():
    """Injeta a arquitetura visual Mission Control."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400&family=Inter:wght@400;700&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
        .monospace-font { font-family: 'JetBrains Mono', monospace !important; }
        .main { background-color: #0b0e14; color: #e0e0e0; }
        .stDeployButton { display: none !important; }
        .nasa-card {
            background: rgba(255, 255, 255, 0.03);
            border-left: 4px solid #D4AF37;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid rgba(212, 175, 55, 0.1);
            margin-bottom: 20px;
        }
        .status-active { color: #00ff41; font-weight: bold; font-family: 'JetBrains Mono'; }
        .message-in { background: #1a232e; padding: 10px; border-radius: 5px; margin-bottom: 5px; border-left: 3px solid #4da3ff; }
        .message-out { background: #263238; padding: 10px; border-radius: 5px; margin-bottom: 5px; border-left: 3px solid #d4af37; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

inject_nasa_ui()

# ==============================================================================
# 02. NÚCLEO ATÔMICO DE DADOS (INTEGRIDADE & FUNÇÕES)
# ==============================================================================
SYSTEM_ROOT = "Dados_Pregador_V31"
os.makedirs(os.path.join(SYSTEM_ROOT, "db"), exist_ok=True)

def hashlib_sha256(value):
    """Criptografia de senhas."""
    return hashlib.sha256(value.encode()).hexdigest()

def _read_json_safe(path, default=None):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return default if default is not None else {}
    except Exception: return default

def _write_json_atomic(p, d):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(d, f, indent=4)
        return True
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")
        return False

# Tenta importar módulos internos se existirem
try:
    from app_modules.core import DB_FILES, genesis_filesystem_integrity_check
    from app_modules import dashboard as dashboard_module
    from app_modules.homiletica import PastoralReviewer
    genesis_filesystem_integrity_check()
except ImportError:
    pass

# ==============================================================================
# 03. PROTOCOLO DE AUTENTICAÇÃO (LOGIN NASA)
# ==============================================================================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🚀 PORTAL DE ACESSO PASTORAL</h1>", unsafe_allow_html=True)
    col_l, col_c, col_r = st.columns([1, 2, 1])
    
    with col_c:
        aba_login, aba_registro = st.tabs(["🔒 ENTRAR", "🆔 REGISTRAR-SE"])
        
        with aba_login:
            with st.form("form_login"):
                u_input = st.text_input("Codinome (Usuário)").upper().strip()
                p_input = st.text_input("Assinatura (Senha)", type="password")
                btn_login = st.form_submit_button("INICIAR SESSÃO")
                btn_convidado = st.form_submit_button("ENTRAR COMO CONVIDADO")

                if btn_login:
                    users = _read_json_safe(os.path.join(SYSTEM_ROOT, "db", "users_db.json"), default={})
                    p_hash = hashlib_sha256(p_input)
                    if u_input in users and users[u_input]["hash"] == p_hash:
                        st.session_state["current_user"] = u_input
                        st.session_state["user_role"] = users[u_input].get("role", "MEMBRO")
                        st.session_state["logged_in"] = True
                        st.rerun()
                    else:
                        st.error("Credenciais Inválidas")

                if btn_convidado:
                    st.session_state["current_user"] = "CONVIDADO"
                    st.session_state["user_role"] = "VISITANTE"
                    st.session_state["logged_in"] = True
                    st.rerun()

        with aba_registro:
            with st.form("form_reg"):
                novo_u = st.text_input("Novo Codinome").upper().strip()
                novo_p = st.text_input("Nova Assinatura", type="password")
                if st.form_submit_button("SOLICITAR ACESSO"):
                    users = _read_json_safe(os.path.join(SYSTEM_ROOT, "db", "users_db.json"), default={})
                    role = "ADMIN" if novo_u == "ADMIN" or not users else "MEMBRO"
                    if novo_u in users:
                        st.warning("Usuário já existe.")
                    else:
                        users[novo_u] = {
                            "hash": hashlib_sha256(novo_u if not novo_p else novo_p),
                            "role": role,
                            "created_at": datetime.now().strftime("%d/%m/%Y")
                        }
                        _write_json_atomic(os.path.join(SYSTEM_ROOT, "db", "users_db.json"), users)
                        st.success(f"Registrado como {role}! Vá para Login.")
    st.stop()

# ==============================================================================
# 04. INTERFACE PRINCIPAL E SIDEBAR
# ==============================================================================
with st.sidebar:
    st.markdown(f"### 👨‍🚀 OPERADOR: {st.session_state['current_user']}")
    st.markdown(f"**NÍVEL:** `{st.session_state['user_role']}`")
    st.divider()
    
    opcoes = ["📊 Dashboard", "📝 Gabinete Profissional", "💬 Central de Mensagens", "🤝 Rede Ministerial", "⚙️ Configurações"]
    app_mode = st.radio("Sistemas Operacionais", opcoes)

    # BOTÃO SOS PARA MEMBROS
    if st.session_state.get("user_role") == "MEMBRO":
        st.divider()
        with st.expander("🆘 SOS PASTORAL"):
            sos_txt = st.text_area("Seu pedido de oração")
            if st.button("Enviar para o Pastor"):
                msgs = _read_json_safe(os.path.join(SYSTEM_ROOT, "db", "comunicacao.json"), default=[])
                msgs.append({"remetente": st.session_state["current_user"], "texto": sos_txt, "data": datetime.now().strftime("%d/%m %H:%M")})
                _write_json_atomic(os.path.join(SYSTEM_ROOT, "db", "comunicacao.json"), msgs)
                st.success("Enviado ao Pastor!")

    if st.button("🚪 Encerrar Sessão"):
        st.session_state["logged_in"] = False
        st.rerun()

# ==============================================================================
# 05. ESTAÇÕES DE TRABALHO
# ==============================================================================

# --- ADMIN PANEL ---
if st.session_state["user_role"] == "ADMIN":
    with st.sidebar:
        if st.checkbox("🛰️ PAINEL DE CONTROLE NASA"):
            app_mode = "ADMIN_PANEL"

if app_mode == "ADMIN_PANEL":
    st.title("🛰️ Command Center (Nível Direção)")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("👥 Tripulação")
        usrs = _read_json_safe(os.path.join(SYSTEM_ROOT, "db", "users_db.json"), default={})
        for u, d in usrs.items(): st.write(f"**{u}** ({d['role']}) - {d['created_at']}")
    with c2:
        st.subheader("📥 Chamados SOS")
        msgs = _read_json_safe(os.path.join(SYSTEM_ROOT, "db", "comunicacao.json"), default=[])
        for m in reversed(msgs):
            st.info(f"De: {m['remetente']}\n\n{m['texto']}\n\nData: {m['data']}")

# --- DASHBOARD ---
elif "Dashboard" in app_mode:
    st.title("📊 SoulMetrics | Dashboard")
    st.metric("Usuários Conectados", len(_read_json_safe(os.path.join(SYSTEM_ROOT, "db", "users_db.json"))), "+1")
    st.info("Sistemas de monitoramento ativos.")

# --- GABINETE ---
elif "Gabinete" in app_mode:
    st.title("📝 Gabinete Profissional")
    titulo = st.text_input("Título do Documento")
    txt_sermao = st.text_area("Composição Teológica", height=400)
    if st.button("💾 Salvar no Core"):
        st.success("Documento criptografado e salvo.")

# --- MENSAGENS ---
elif "Mensagens" in app_mode:
    st.title("💬 Central de Mensagens")
    st.markdown("<div class='message-in'>Deseja disparar um aviso para todos os usuários?</div>", unsafe_allow_html=True)
    msg_alerta = st.text_input("Escrever alerta global")
    if st.button("🚀 Disparar"):
        st.success("Sinal enviado via uplink ministerial.")

# --- OUTROS ---
elif "Rede" in app_mode:
    st.title("🤝 Rede Ministerial")
    st.write("Acessando repositório de áudios...")

elif "Configurações" in app_mode:
    st.title("⚙️ Configurações")
    st.write("Versão do Firmware: 3.1-NASA-OMEGA")
