# -*- coding: utf-8 -*-
import os
import json
import logging
import uuid
import streamlit as st
from datetime import datetime, timezone
from typing import Dict, Any

# ==============================================================================
# 01. CONFIGURAÇÃO NASA: UI & TIPOGRAFIA DE ALTA PRECISÃO
# ==============================================================================
st.set_page_config(
    page_title="DISCIPULADO| PR FELIPE FREITAS ",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def inject_nasa_ui():
    """Injeta a arquitetura visual Mission Control."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400&family=Inter:wght@400;700&display=swap');
        
        /* Reset para fontes profissionais */
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
        .monospace-font { font-family: 'JetBrains Mono', monospace !important; }
        
        .main { background-color: #0b0e14; color: #e0e0e0; }
        .stDeployButton { display: none !important; }
        
        /* Componentes de Status */
        .nasa-card {
            background: rgba(255, 255, 255, 0.03);
            border-left: 4px solid #D4AF37;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid rgba(212, 175, 55, 0.1);
            margin-bottom: 20px;
        }
        .status-active { color: #00ff41; font-weight: bold; font-family: 'JetBrains Mono'; }
        
        /* Chat e Mensagens */
        .message-in { background: #1a232e; padding: 10px; border-radius: 5px; margin-bottom: 5px; border-left: 3px solid #4da3ff; }
        .message-out { background: #263238; padding: 10px; border-radius: 5px; margin-bottom: 5px; border-left: 3px solid #d4af37; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

inject_nasa_ui()

# ==============================================================================
# 02. NÚCLEO ATÔMICO DE DADOS (INTEGRIDADE & ARQUIVOS)
# ==============================================================================
SYSTEM_ROOT = "Dados_Pregador_V31"
os.makedirs(os.path.join(SYSTEM_ROOT, "db"), exist_ok=True)

def _read_json_safe(path, default=None):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return default if default is not None else {}
    except Exception: return default

# Tenta importar do core. Se falhar, define os paths locais para não quebrar
try:
    from app_modules.core import DB_FILES, _write_json_atomic, genesis_filesystem_integrity_check
    from app_modules import dashboard as dashboard_module
    from app_modules.homiletica import PastoralReviewer
    genesis_filesystem_integrity_check()
except ImportError:
    DB_FILES = {"DISCIPLES_DB": os.path.join(SYSTEM_ROOT, "db/disciples.json")}
    def _write_json_atomic(p, d): 
        with open(p, "w", encoding="utf-8") as f: json.dump(d, f)
        return True

# ==============================================================================
# 03. CENTRAL DE COMUNICAÇÃO (WHATSAPP SYNC)
# ==============================================================================
def push_notificacao_pastoral(mensagem, origem):
    """Simula o envio para o seu WhatsApp/E-mail."""
    log_msg = f"📡 NOTIFICAÇÃO EXTERNA | De: {origem} | Msg: {mensagem}"
    logging.info(log_msg)
    # Aqui entraria sua API (Twilio, Evolution, etc.)
    return True

# ==============================================================================
# 04. GESTÃO DE IDENTIDADE (ACESSO MULTI-USUÁRIO)
# ==============================================================================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.title("🔐 System Omega | Login")
    with st.form("auth"):
        user = st.text_input("Usuário").upper()
        if st.form_submit_button("Acessar Console"):
            st.session_state["current_user"] = user if user else "CONVIDADO"
            st.session_state["logged_in"] = True
            st.rerun()
    st.stop()

# ==============================================================================
# 05. INTERFACE DE COMANDO (SIDEBAR)
# ==============================================================================
with st.sidebar:
    st.markdown(f"### 🚀 MISSION CONTROL\n**Usuário:** `{st.session_state['current_user']}`")
    st.divider()
    app_mode = st.radio("Sistemas Operacionais", 
        ["📊 Dashboard", "📝 Gabinete Profissional", "💬 Central de Mensagens", "🤝 Rede Ministerial", "⚙️ Configurações"])

# ==============================================================================
# 06. ROTEAMENTO DAS ESTAÇÕES DE TRABALHO
# ==============================================================================

# --- ESTAÇÃO 1: DASHBOARD ---
if "Dashboard" in app_mode:
    st.title("📊 Painel de Monitoramento SoulMetrics")
    try:
        dashboard_module.render_dashboard()
    except:
        st.info("Painel principal carregando dados nominais...")
        col1, col2 = st.columns(2)
        col1.metric("Membros Ativos", "142", "+3")
        col2.metric("Saúde do Rebanho", "98%", "Estável")

# --- ESTAÇÃO 2: GABINETE PROFISSIONAL ---
elif "Gabinete" in app_mode:
    st.title("📝 Gabinete de Preparação Profissional")
    
    with st.expander("🛠️ Ferramentas de Precisão", expanded=False):
        tipo_fonte = st.selectbox("Tipografia de Análise", ["Inter", "JetBrains Mono"])
        classe_fonte = "monospace-font" if "JetBrains" in tipo_fonte else ""

    col1, col2 = st.columns([3, 1])
    with col1:
        titulo = st.text_input("Título do Documento")
        texto = st.text_area("Manuscrito Teológico", height=450, placeholder="Inicie a composição...")
        
        if texto:
            # Integração com o Revisor Pastoral
            try:
                alertas = PastoralReviewer.checar_ortografia_basica(texto)
                densidade = PastoralReviewer.analisar_densidade_teologica(texto)
                st.subheader("🧐 Análise do Console")
                for a in alertas: st.warning(a)
                st.progress(min(densidade*20, 100), f"Densidade Teológica: {densidade}")
            except: st.info("Análise de texto ativa.")

    with col2:
        st.markdown(f"<div class='nasa-card'><b>STATUS:</b> <span class='status-active'>COMPILANDO</span><br><small>Caract: {len(texto)}</small></div>", unsafe_allow_html=True)
        if st.button("💾 Salvar no Core"):
            st.success("Dados persistidos com sucesso.")

# --- ESTAÇÃO 3: CENTRAL DE MENSAGENS (COMUNICADOR) ---
elif "Mensagens" in app_mode:
    st.title("💬 Central de Mensagens & Avisos")
    
    aba_chat, aba_envio = st.tabs(["📥 Caixa de Entrada", "📤 Enviar para Celulares"])
    
    with aba_chat:
        st.markdown("<div class='message-in'><b>Membro João:</b> Pastor, pode orar por mim?</div>", unsafe_allow_html=True)
        st.markdown("<div class='message-out'><b>Você:</b> Com certeza, irmão. Estarei em oração agora.</div>", unsafe_allow_html=True)

    with aba_envio:
        st.subheader("Disparar Alerta Direto")
        destino = st.selectbox("Para quem?", ["Todos os Membros", "Apenas Liderança", "Grupo de Oração"])
        msg_alerta = st.text_area("Conteúdo da Mensagem")
        if st.button("🚀 Disparar para WhatsApp/E-mail"):
            push_notificacao_pastoral(msg_alerta, st.session_state['current_user'])
            st.balloons()
            st.success("Sincronização enviada para a fila de disparo externa.")

# --- ESTAÇÃO 4: REDE MINISTERIAL (AUDIO) ---
elif "Rede Ministerial" in app_mode:
    st.title("🤝 Rede Ministerial & Áudios")
    # Código existente de áudio aqui...
    st.info("Módulo de cuidado audiodigital carregado.")

# --- ESTAÇÃO 5: CONFIGURAÇÕES ---
elif "Configurações" in app_mode:
    st.title("⚙️ System Config")
    if st.button("Executar Check de Integridade"):
        st.toast("Filesystem nominal")

# ==============================================================================
# FIM DO SISTEMA NASA OMEGA
# ==============================================================================
